'''
Camera

How the user looks at the game world
'''

from pyglet import gl

from .screen import Screen
from ..engine.map import SECTOR_SZ

class Camera(object):
    def __init__(self, mapren, localpid):
        self.localpid = localpid
        self.lookx = 0.0
        self.looky = 0.0
        self.mapren = mapren

    def load(self, datasrc):
        data = datasrc.getmisc('camera.initial.position')
        look = data[str(self.localpid)]
        self.lookx = look['x']
        self.looky = look['y']

        # camera should not really be doing this
        sx, sy = self.mapren.map.pos_to_sector(self.lookx, self.looky)
        sec = self.mapren.map.sectors[(sx, sy)]

        self.mapren.lookat(sec)


    def save(self, sink):
        data = {
            self.localpid : {
                'x' : self.lookx,
                'y' : self.looky,
            }
        }
        sink.setmisc('camera.initial.position', data)

    def unproject(self, pos):
        print pos, self.lookx, self.looky
        looksector = self.mapren.looksector

        return (pos[0] + self.lookx + looksector.sx * SECTOR_SZ,
                pos[1] + self.looky + looksector.sy * SECTOR_SZ)

    def setup(self):
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(-self.lookx, -self.looky, 0)

    def move(self, dx, dy):
        self.lookx += dx
        self.looky += dy

        sec = self.mapren.looksector

        #print self.lookx, self.looky
        
        # this bit clamps the viewport to loaded sectors
        if self.lookx > SECTOR_SZ - Screen.WIDTH:
            if not sec.neighbour[1, 0]:
                self.lookx = SECTOR_SZ - Screen.WIDTH
        elif self.lookx < 0:
            if not sec.neighbour[-1, 0]:
                self.lookx = 0

        if self.looky > SECTOR_SZ - Screen.HEIGHT:
            if not sec.neighbour[0, 1]:
                self.looky = SECTOR_SZ - Screen.HEIGHT
        elif self.looky < 0:
            if not sec.neighbour[0, -1]:
                self.looky = 0


        # this bit moves the look point when when crosses a sector boundary
        if self.lookx < -Screen.WIDTH//2:
            if sec.neighbour[-1, 0]:
                self.lookx += SECTOR_SZ
                self.mapren.lookat(sec.neighbour[-1, 0])
        elif self.lookx > SECTOR_SZ - Screen.WIDTH//2:
            if sec.neighbour[1, 0]:
                self.lookx -= SECTOR_SZ
                self.mapren.lookat(sec.neighbour[1, 0])
        
        if self.looky < -Screen.HEIGHT//2:
            if sec.neighbour[0, -1]:
                self.looky += SECTOR_SZ
                self.mapren.lookat(sec.neighbour[0, -1])
        elif self.looky > SECTOR_SZ - Screen.HEIGHT//2:
            if sec.neighbour[0, 1]:
                self.looky -= SECTOR_SZ
                self.mapren.lookat(sec.neighbour[0, 1])
                