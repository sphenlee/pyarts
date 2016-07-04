'''
Game

The game represents the entire state of a game.
It holds the local player specific information (ie. stuff that
does not need to be communicated over the network to other players)
It also holds the Engine which has all the shared stuff.
'''

from pyglet import gl

from .player import Player
from .order import *
from .modes import *

from pyarts.engine.event import Event
from pyarts.container import component

@component
class Game(object):
    depends = ['engine', 'datasrc', 'network', 'settings']

    def __init__(self):
        self.selection = []
        self.players = []
        self.cycle = 0
        self.latency = 16
        self.orderthisturn = None
        self.localpid = None

        self.modes = []
        self.push_mode(NormalMode(self))

        self.onselectionchange = Event()

    def inject(self, engine, datasrc, network, settings):
        self.engine = engine
        self.datasrc = datasrc
        self.network = network
        settings.onload.add(self.load)

        
    def load(self, settings):
        self.localpid = settings.localpid
        
        data = self.datasrc.getplayers()
        for pdata in data:
            player = Player()
            player.load(pdata)
            self.players.append(player)

    def save(self, sink):
        self.engine.save(sink)

        for p in self.players:
            data = p.save()
            sink.addplayer(data)

    @property
    def localplayer(self):
        return self.players[self.localpid]

    @property
    def mode(self):
        '''
        Get the current mode - modes decide what the
        mouse buttons and keys do
        '''
        return self.modes[-1]

    def push_mode(self, mode):
        ''' Enter a new mode '''
        self.modes.append(mode)

    def pop_mode(self):
        ''' Return to the previous mode '''
        self.modes.pop()

    def startturn(self):
        ''' Called when we are ready for the next turn '''
        self.cycle += 1
        self.orderthisturn = None

    def endturn(self):
        ''' Called to end the current turn '''
        p = self.localplayer
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
            print 'No Order for player in cycle %d' % self.cycle 
        else:
            self.endturn()
            
            self.engine.step()

            for p in self.players:
                order = p.getorder(self.cycle)
                p.clearorder(self.cycle)
                if order:
                    self.engine.entities.doorder(order)

            self.startturn()

    def render(self):
        self.engine.render() # FIXME - engine should not have any graphics in it

        for ent in self.selection:
            self.render_selection(ent)

    def render_selection(self, ent):
        loc = ent.locator

        gl.glDisable(gl.GL_TEXTURE_2D)        
        gl.glColor4f(0, 1, 0, 1)
        gl.glBegin(gl.GL_LINE_STRIP)
        gl.glVertex2f(loc.x - loc.r, loc.y - loc.r)
        gl.glVertex2f(loc.x + loc.r, loc.y - loc.r)
        gl.glVertex2f(loc.x + loc.r, loc.y + loc.r)
        gl.glVertex2f(loc.x - loc.r, loc.y + loc.r)
        gl.glVertex2f(loc.x - loc.r, loc.y - loc.r)
        gl.glEnd()

    def select(self, ents, add):
        ''' Select ents or add ents to the current selection '''
        lp = self.localplayer
        myents = [e for e in ents if e.ownedby(lp)]

        if not myents:
            # select highest ranked enemy ent
            rank = min(e.rank for e in ents)
            selection = [e for e in ents if e.rank == rank][0:]
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

        
        assert selection, 'no entities were selected'
        self.selection = selection

        self.onselectionchange.emit()

    def autocommand(self, target, add):
        ''' Give an autocommand on target to the selected entities '''
        if self.selection:
            if not self.selection[0].ownedby(self.localplayer):
                return
            eids = [e.eid for e in self.selection]
            self.order(AutoCommandOrder(eids, target, add))

    def ability(self, idx):
        ''' Do the ability at idx for the currently selected entities '''
        if not self.selection:
            # nothing selected
            return

        # grab the ability - defined by the first entity in the selection
        ent = self.selection[0]
        if not ent.has('abilities'):
            # no abilities
            return

        if not ent.ownedby(self.localplayer):
            # should never happen, player doesn't own the entity
            return

        try:
            ability = ent.abilities[idx]
        except IndexError:
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

            if e.proto.epid != ent.proto.epid:
                print 'entity does not have ability %s' % ability.name
                return False

            if e.abilities.cooldowns[idx] > 0:
                print 'not ready - game checked it'
                return False

            if not ability.check_cost(e):
                print 'cannot pay cost'
                return False

            return True

        entids = [eid for eid in entids if check_ability(eid)]
        
        # create the order
        order = AbilityOrder(entids, idx)

        # based on ability type we either issue an order
        # or enter a new mode
        if ability.type == ability.INSTANT:
            self.order(order)
        elif ability.type == ability.TARGETED:
            self.push_mode(TargetingMode(self, order, allowpos=False))
        elif ability.type == ability.BUILD:
            self.push_mode(BuildMode(self, order, ghost=ability.ghost, allowent=False))
        elif ability.type == ability.AREA_OF_EFFECT:
            self.push_mode(TargetingMode(self, order))
        elif ability.type == ability.STATIC:
            pass # do nothing
