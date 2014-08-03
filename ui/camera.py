'''
Camera

How the user looks at the game world
'''

from pyglet import gl

SECTOR_SZ = 1024 # size of a sector in pixels

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
        return (pos[0] - self.lookx, pos[1] - self.looky)

    def setup(self):
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(self.lookx, self.looky, 0)

    def move(self, dx, dy):
        self.lookx += dx
        self.looky += dy

        sec = self.mapren.looksector

        if self.lookx > SECTOR_SZ:
            if sec.right:
                self.lookx -= SECTOR_SZ
                self.mapren.lookat(sec.right)
            else:
                self.lookx = SECTOR_SZ

        elif self.lookx < 0:
            if sec.left:
                self.lookx += SECTOR_SZ
                self.mapren.lookat(sec.left)
            else:
                self.lookx = 0

        if self.looky > SECTOR_SZ:
            if sec.up:
                self.looky -= SECTOR_SZ
                self.mapren.lookat(sec.up)
            else:
                self.looky = SECTOR_SZ

        elif self.looky < 0:
            if sec.down:
                self.looky += SECTOR_SZ
                self.mapren.lookat(sec.down)
            else:
                self.looky = 0
