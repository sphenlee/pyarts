'''
Manages sending orders over the network to
other players
'''

import nanomsg as nm
import msgpack
import threading

from pyarts.container import component
from pyarts.engine.target import Target
from pyarts.engine.event import Event

from .order import Order, AbilityOrder, AutoCommandOrder, NoOrder


class NullNetwork(object):
    '''
    Implementation used for single player, no network needed
    '''
    def __init__(self, net):
        net.ongamestart.emit()

    def sendorder(self, order):
        pass

    def step(self):
        pass


class NanomsgNetwork(object):
    '''
    Shared code between Master and Slave
    '''
    def serialise(self, order):
        obj = {
            'tag': 'order',
            'type': order.type,
            'ents': order.ents,
            'cycle': order.cycle,
            'add': order.add,
            'pid': self.game.localpid # we only serialise orders from the local player
        }
        if order.type == Order.ABILITY:
            obj['idx'] = order.idx

        if order.target:
            if order.target.isent():
                obj['target'] = {'ent': order.target.ent.eid}
            else:
                obj['target'] = {'pos': order.target.pos}

        return msgpack.packb(obj)

    def deserialise(self, obj):
        if obj['type'] == Order.ABILITY:
            order = AbilityOrder(obj['ents'], obj['idx'], obj['add'])
        elif obj['type'] == Order.AUTOCOMMAND:
            order = AutoCommandOrder(obj['ents'], obj['target'], obj['add'])
        elif obj['type'] == Order.NONE:
            order = NoOrder()

        order.cycle = obj['cycle']

        if 'target' in obj:
            target = obj['target']
            if 'ent' in target:
                ent = self.entitymanager.get(target['ent'])
                order.target = Target(ent)
            else:
                order.target = Target(tuple(target['pos']))

        return order
                
    def check_messages(self):
        msgs = []
        while 1:
            try:
                payload = self.soc.recv(flags=nm.DONTWAIT)
            except nm.NanoMsgAPIError as e:
                if e.errno == nm.EAGAIN:
                    return msgs
                else:
                    raise
            else:
                msg = msgpack.unpackb(payload)
                msgs.append(msg)

    def sendorder(self, order):
        msg = self.serialise(order)
        self.soc.send(msg)

    def send(self, msg):
        self.soc.send(msgpack.packb(msg))

    def step(self):
        for msg in self.check_messages():
            #print 'network got', msg
            tag = msg['tag']
            if tag == 'order':
                pid = msg['pid']
                order = self.deserialise(msg)
                self.handle_order(pid, order)
            elif tag == 'ready':
                self.handle_ready(msg)
            elif tag == 'startgame':
                self.handle_startgame()


class MasterNetwork(NanomsgNetwork):
    '''
    Implementation used for actual multi player master
    '''
    def __init__(self, net):
        self.net = net
        self.game = net.game
        self.entitymanager = net.entitymanager
        
        self.soc = nm.Socket(nm.PAIR)
        self.soc.bind('tcp://*:6666')

        self.waiting = sum(1 for p in self.game.players if p.type == p.HUMAN) - 1 # assume we're ready

    def handle_order(self, pid, order):
        self.game.orderfor(order, pid)

    def handle_ready(self, msg):
        print('master got ready message', self.waiting)
        self.waiting -= 1
        if self.waiting == 0:
            self.send_startgame()
            self.net.ongamestart.emit()

    def handle_startgame(self):
        pass

    def send_startgame(self):
        self.send({'tag': 'startgame'})


class SlaveNetwork(NanomsgNetwork):
    '''
    Implementation used for actual multi player slave
    '''
    def __init__(self, net, join):
        self.net = net
        self.game = net.game
        self.entitymanager = net.entitymanager
        
        self.soc = nm.Socket(nm.PAIR)
        self.soc.connect('tcp://localhost:6666')

        self.send({'tag' : 'ready'})

    def handle_order(self, pid, order):
        self.game.orderfor(order, pid)

    def handle_ready(self, msg):
        pass

    def handle_startgame(self):
        self.net.ongamestart.emit()


@component
class Network(object):
    depends = ['game', 'settings', 'entitymanager']

    def __init__(self):
        self.ongamestart = Event()

    def inject(self, game, settings, entitymanager):
        self.game = game
        settings.onload.add(self.load)
        self.entitymanager = entitymanager # to resolve target eids

    def load(self, settings):
        if settings.server:
            self.impl = MasterNetwork(self)
        elif settings.join:
            self.impl = SlaveNetwork(self, settings.join)
        else:
            self.impl = NullNetwork(self)

    def sendorder(self, order):
        self.impl.sendorder(order)

    def step(self):
        self.impl.step()
