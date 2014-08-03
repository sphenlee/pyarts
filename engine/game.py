'''
Game

The game represents the entire state of a game.
It holds the local player specific information (ie. stuff that
does not need to be communicated over the network to other players)
It also holds the Engine which has all the shared stuff.
'''

from pyglet import gl


from .engine import Engine
from .camera import Camera
from .player import Player
from .order import *
from .event import Event
from .modes import *

class Game(object):
    def __init__(self, datasrc, localplayer=0):
        self.datasrc = datasrc
        self.localplayer = localplayer
        self.engine = Engine(datasrc)
        self.camera = Camera()
        self.selection = []
        self.players = []
        self.cycle = 0
        self.latency = 16
        self.orderthisturn = None

        self.modes = []
        self.push_mode(NormalMode(self))

        self.onselectionchange = Event()

    def load(self):
        self.engine.load()

        data = self.datasrc.getplayers()
        for pdata in data:
            player = Player()
            player.load(pdata)
            self.players.append(player)

        data = self.datasrc.getmisc('game.initial.state')

        look = data['camera'][str(self.localplayer)]
        self.camera.lookx = look['x']
        self.camera.looky = look['y']

    def save(self, sink):
        self.engine.save(sink)

        for p in self.players:
            data = p.save()
            sink.addplayer(data)

        data = {
            'camera' : {
                self.localplayer : {
                    'x' : self.camera.lookx,
                    'y' : self.camera.looky,
                }
            }
        }
        sink.setmisc('game.initial.state', data)

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
        p = self.players[self.localplayer]
        if not self.orderthisturn:
            self.orderthisturn = NoOrder()

        p.addorder(self.cycle + self.latency, self.orderthisturn)

    def order(self, order):
        assert not self.orderthisturn
        self.orderthisturn = order

    def step(self):
        '''
        If we have an order for every player then we advance to
        the next turn, and then step the engine, finally we assign
        orders to entities
        '''
        orders = [p.getorder(self.cycle) for p in self.players]
        if not all(orders):
            print 'No Order for player in cycle %d' % self.cycle 
        else:
            self.endturn()
            self.startturn()

            self.engine.step()

            for p in self.players:
                order = p.getorder(self.cycle)
                self.engine.entities.doorder(order)

    def render(self):
        self.camera.setup()
        self.engine.render() # FIXME - engine should not have any graphics in it

        for eid in self.selection:
            self.render_selection(eid)

    def render_selection(self, eid):
        ent = self.engine.entities.get(eid)
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
        if not add:
            del self.selection[:]

        self.selection.extend(ents)
        self.onselectionchange.emit()

    def autocommand(self, target):
        ''' Give an autocommand on target to the selected entities '''
        if self.selection:
            self.order(AutoCommandOrder(self.selection, target))

    def ability(self, idx):
        ''' Do the ability at idx for the currently selected entities '''
        if not self.selection:
            # nothing selected
            return

        ent = self.engine.entities.get(self.selection[0])
        if not ent.has('abilities'):
            # no abilities
            return

        try:
            ability = ent.abilities[idx]
        except IndexError:
            return

        # get the ents - non group abilities cannot be done by
        # multiple entities so we pick the first
        ents = self.selection
        if not ability.group:
            ents = ents[0]

        # create the order
        order = AbilityOrder(self.selection, idx)

        # based on ability type we either issue an order
        # or enter a new mode
        if ability.type == ability.INSTANT:
            self.order(order)
        elif ability.type == ability.TARGETED:
            self.push_mode(TargetingMode(self, order, allowpos=False))
        elif ability.type == ability.AREA_OF_EFFECT:
            self.push_mode(TargetingMode(self, order))
        elif ability.type == ability.STATIC:
            pass # do nothing
