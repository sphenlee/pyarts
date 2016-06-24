'''
Manages sending orders over the network to
other players
'''

import nanomsg as nm
import msgpack
import threading

from pyarts.container import component
from pyarts.engine.target import Target

from .order import Order, AbilityOrder, AutoCommandOrder, NoOrder


class NullNetwork(object):
    '''
    Implementation used for single player, no network needed
    '''
    def __init__(self):
        pass

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
            'type': order.type,
            'ents': order.ents,
            'cycle': order.cycle,
            'pid': self.game.localpid # we only serialise orders from the local player
        }
        if order.type == Order.AUTOCOMMAND:
            obj['add'] = order.add
        elif order.type == Order.ABILITY:
            obj['idx'] = order.idx

        if order.target:
            if order.target.isent():
                obj['target'] = {'ent': order.target.ent.eid}
            else:
                obj['target'] = {'pos': order.target.pos}

        return msgpack.packb(obj)

    def deserialise(self, obj):
        if obj['type'] == Order.ABILITY:
            order = AbilityOrder(obj['ents'], obj['idx'])
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
        orders = []
        while 1:
            try:
                msg = self.soc.recv(flags=nm.DONTWAIT)
            except nm.NanoMsgAPIError as e:
                if e.errno == nm.EAGAIN:
                    return orders
                else:
                    raise
            else:
                obj = msgpack.unpackb(msg)
                pid = obj['pid']
                order = self.deserialise(obj)
                orders.append((order, pid))

    def sendorder(self, order):
        msg = self.serialise(order)
        self.soc.send(msg)

    def step(self):
        for order, pid in self.check_messages():
            self.game.orderfor(order, pid)

class MasterNetwork(NanomsgNetwork):
    '''
    Implementation used for actual multi player master
    '''
    def __init__(self, net):
        self.game = net.game
        self.entitymanager = net.entitymanager
        
        self.soc = nm.Socket(nm.BUS)
        self.soc.bind('tcp://*:6666')

class SlaveNetwork(NanomsgNetwork):
    '''
    Implementation used for actual multi player slave
    '''
    def __init__(self, net, join):
        self.game = net.game
        self.entitymanager = net.entitymanager
        
        self.soc = nm.Socket(nm.BUS)
        self.soc.connect('tcp://localhost:6666')


@component
class Network(object):
    depends = ['game', 'settings', 'entitymanager']

    def __init__(self):
        pass

    def inject(self, game, settings, entitymanager):
        self.game = game
        self.settings = settings
        self.entitymanager = entitymanager # to resolve target eids

    def load(self):
        if self.settings.server:
            self.impl = MasterNetwork(self)
        elif self.settings.join:
            self.impl = SlaveNetwork(self, self.settings.join)
        else:
            self.impl = NullNetwork()

    def sendorder(self, order):
        self.impl.sendorder(order)

    def step(self):
        self.impl.step()
