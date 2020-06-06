'''
Game

Hold state that is local to a player.
(Used to be a monolith pre dependency injection, now it's functionality has been split up)

* Hold entity selection
* Translates ability buttons and autocommand into orders
* Holds the info about all players (but not the local player id)
'''

from .player import Player
from .order import *
from .modes import *

from pyarts.engine.event import Event
from pyarts.container import component

@component
class Game(object):
    depends = ['engine', 'datasrc', 'network', 'settings', 'entitymanager', 'local', 'modestack']

    def __init__(self):
        self.selection = []
        self.players = []
        self.cycle = 0
        self.latency = 16
        self.orderthisturn = None
        
        self.onselectionchange = Event()
        

    def inject(self, engine, datasrc, network, settings, entitymanager, local, modestack):
        self.engine = engine
        self.datasrc = datasrc
        self.network = network
        self.entities = entitymanager
        self.local = local
        self.modes = modestack

        datasrc.onload.add(self.init_players)
    
    def init_players(self):
        for pdata in self.datasrc.getplayers():
            player = Player()
            player.load(pdata)
            self.players.append(player)

    def save(self, sink):
        self.engine.save(sink)

        for p in self.players:
            data = p.save()
            sink.addplayer(data)

    def startturn(self):
        ''' Called when we are ready for the next turn '''
        self.cycle += 1
        self.orderthisturn = None

    def endturn(self):
        ''' Called to end the current turn '''
        p = self.local.player
        order = self.orderthisturn 
        if not order:
            order = NoOrder()

        order.cycle = self.cycle + self.latency

        p.addorder(order)
        self.network.sendorder(order)

    def order(self, order):
        assert not self.orderthisturn
        self.orderthisturn = order

    def orderfor(self, order, pid):
        p = self.players[pid]
        p.addorder(order)

    def step(self):
        '''
        If we have an order for every player then we advance to
        the next turn, and then step the engine, finally we assign
        orders to entities
        '''
        self.network.step()

        orders = [p.getorder(self.cycle) for p in self.players if p.type == Player.HUMAN]
        if not all(orders):
            print('No Order for player in cycle %d' % self.cycle) 
        else:
            self.endturn()
            
            self.engine.step()

            for p in self.players:
                order = p.getorder(self.cycle)
                p.clearorder(self.cycle)
                if order:
                    self.engine.entities.doorder(order)

            self.startturn()
            self.validate_selection()


    def select(self, ents, add):
        ''' Select ents or add ents to the current selection '''
        lp = self.local.player
        myents = set(e for e in ents if e.ownedby(lp))

        if not myents:
            # select highest ranked enemy ent
            rank = min(e.rank for e in ents)
            selection = [e for e in ents
                if e.rank == rank
                and e.appearance.visible_to(lp.tidmask)][:1]
        else:
            # select only my ents
            if add:
                # adding to the selection, use the tier of already selected ents
                myents = myents | set(self.selection)
                tier = self.selection[0].tier
            else:
                # new selection, use the highest tier
                tier = min(e.tier for e in myents)

            selection = [e for e in myents if e.tier == tier]

        
        if not selection:
            # no valid entities selected, so don't change selection
            print('no entities were selected')
            return

        for s in self.selection:
            if s.has('appearance'):
                s.appearance.selected(False)

        self.selection = selection

        for s in self.selection:
            if s.has('appearance'):
                s.appearance.selected(True)

        self.onselectionchange.emit()

    def validate_selection(self):
        valid = [s for s in self.selection if self.entities.exists(s.eid)]
        if self.selection != valid:
            self.selection = valid
            self.onselectionchange.emit()        

    def autocommand(self, target, add):
        ''' Give an autocommand on target to the selected entities '''
        if self.selection:
            if not self.selection[0].ownedby(self.local.player):
                return
            eids = [e.eid for e in self.selection]
            self.order(AutoCommandOrder(eids, target, add))

    def ability(self, idx, add):
        print(f'trying to do ability {idx}')
        ''' Do the ability at idx for the currently selected entities '''
        if not self.selection:
            # nothing selected
            print('no selection')
            return

        # grab the ability - defined by the first entity in the selection
        ent = self.selection[0]
        if not ent.has('abilities'):
            # no abilities
            print('entity has no abilities')
            return

        if not ent.ownedby(self.local.player):
            # should never happen, player doesn't own the entity
            print('entity not owned by local player')
            return

        try:
            ability = ent.abilities[idx].ability
        except IndexError:
            print('index out of bounds')
            return

        # get the ents - non group abilities cannot be done by
        # multiple entities so we pick the first
        if not ability.group:
            entids = [ent.eid]
        else:
            entids = [e.eid for e in self.selection]

        # verify if there are any entities in the selection that can actually
        # do the ability right now
        #  * do they have the same ability - for now we compare the protos
        #  * enough resourcea
        #  * cooldowns not active
        # NOTE this is a Game check, the Engine will check again when activating
        def check_ability(eid):
            e = self.engine.entities.get(eid)
            ainst = e.abilities[idx]

            if e.proto.epid != ent.proto.epid:
                print('entity does not have ability %s' % ability.name)
                return False

            if ainst.cooldown > 0:
                print('not ready - game checked it')
                return False

            if not ability.queue and ainst.wait > 0:
                print('already doing this - game checked it')
                return False

            if not ability.check_cost(e):
                print('cannot pay cost - game checked it')
                return False

            return True

        entids = [eid for eid in entids if check_ability(eid)]
        
        # create the order
        order = AbilityOrder(entids, idx, add)

        # based on ability type we either issue an order
        # or enter a new mode
        if ability.type == ability.INSTANT:
            order.add = True # instants never interrupt the current action
            self.order(order)
        elif ability.type == ability.ACTIVITY:
            self.order(order)
        elif ability.type == ability.TARGETED:
            self.modes.push_mode(TargetingMode(order, allowpos=False))
        elif ability.type == ability.BUILD:
            self.modes.push_mode(BuildMode(order, ghost=ability.ghost, allowent=False))
        elif ability.type == ability.AREA_OF_EFFECT:
            self.modes.push_mode(TargetingMode(order))
        elif ability.type == ability.STATIC:
            pass # do nothing
        else:
            raise RuntimeError('unknown ability type!')
