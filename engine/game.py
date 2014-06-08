'''
Game

The game represents the entire state of a game.
It holds the local player specific information as well
as the engine.
'''

from pyglet import gl


from .engine import Engine
from .camera import Camera

class Game(object):
    def __init__(self, datasrc, localplayer=0):
        self.datasrc = datasrc
        self.localplayer = localplayer
        self.engine = Engine(datasrc)
        self.camera = Camera(800, 600)
        self.selection = []

    def load(self):
        self.engine.load()

        data = self.datasrc.getmisc('game.initial.state')

        look = data['camera'][self.localplayer]
        self.camera.lookx = look['x']
        self.camera.looky = look['y']

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


    def selectpoint(self, x, y, add=False):
        print 'select point', x, y, add
        rect = (x - 16, y - 16, x + 16, y + 16)
        ents = self.engine.map.entitiesinrect(*rect)
        self.doselection(ents, add)

    def selectrect(self, x1, y1, x2, y2, add=False):
        print 'select rect', x1, y1, x2, y2, add
        ents = self.engine.map.entitiesinrect(x1, y1, x2, y2)
        self.doselection(ents, add)

    def doselection(self, ents, add):
        if not add:
            del self.selection[:]

        self.selection.extend(ents)
        print self.selection
