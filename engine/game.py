'''
Game

The game represents the entire state of a game.
It holds the local player specific information as well
as the engine.
'''

from pyglet import gl


from .engine import Engine
from .camera import Camera
from .player import Player
from .order import *
from .event import Event

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

    def startturn(self):
        self.cycle += 1
        self.orderthisturn = None

    def endturn(self):
        p = self.players[self.localplayer]
        if not self.orderthisturn:
            self.orderthisturn = NoOrder()

        p.addorder(self.cycle + self.latency, self.orderthisturn)

    def step(self):
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
        if not add:
            del self.selection[:]

        self.selection.extend(ents)
        self.onselectionchange.emit()

    def autocommand(self, target):
        if self.selection:
            self.orderthisturn = AutoCommandOrder(self.selection, target)
