'''
Camera

How the user looks at the game world
'''

from ..engine.event import Event
from ..engine.map import SECTOR_SZ

from pyarts.container import component
from pyarts.log import debug


@component
class Camera(object):
    depends = ['datasrc', 'maprenderer', 'map', 'spritemanager', 'local',
               'settings']

    def __init__(self):
        self.lookx = 0
        self.looky = 0

        self.onlookpointchanged = Event()

    def inject(self, datasrc, maprenderer, map, spritemanager, local, settings):
        self.datasrc = datasrc
        self.datasrc.onload.add(self.load_data)
        self.datasrc.onready.add(self.setup_camera)

        self.mapren = maprenderer
        self.map = map
        self.sprites = spritemanager
        
        self.local = local

        settings.onload.add(self.onload)
        
    def load_data(self):
        debug('camera load data')
        data = self.datasrc.getmisc('camera.initial.position')
        look = data[str(self.local.pid)]
        self.lookx = int(look['x'])
        self.looky = int(look['y'])
        self.sx = int(look['sx'])
        self.sy = int(look['sy'])

    def onload(self, settings):
        self.WIDTH = settings.width
        self.HEIGHT = settings.height

    def setup_camera(self):
        # camera maybe should not be doing this?
        sec = self.map.loadsector(self.sx, self.sy)
        #self.mapren.look_at(sec)
        self.onlookpointchanged.emit(sec)

    def save(self, sink):
        data = {
            self.local.pid: {
                'x': self.lookx,
                'y': self.looky,
                'sx': self.sx,
                'sy': self.sy,
            }
        }
        sink.setmisc('camera.initial.position', data)

    def unproject(self, pos):
        '''
        Converts a screen point into a world point
        '''
        return (pos[0] + self.lookx + self.sx * SECTOR_SZ,
                pos[1] + self.looky + self.sy * SECTOR_SZ)

    def project(self, pos):
        '''
        Converts a world point into a screen point
        '''
        return (pos[0] - self.lookx - self.sx * SECTOR_SZ,
                pos[1] - self.looky - self.sy * SECTOR_SZ)

    def get_transform(self):
        return (-self.lookx, -self.looky)

    def move(self, dx, dy):
        self.lookx += dx
        self.looky += dy

        sec = self.mapren.looksector

        # this bit clamps the viewport to loaded sectors
        if self.lookx > SECTOR_SZ - self.WIDTH:
            if not sec.neighbour[1, 0]:
                self.lookx = SECTOR_SZ - self.WIDTH
        if self.lookx < 0:
            if not sec.neighbour[-1, 0]:
                self.lookx = 0

        if self.looky > SECTOR_SZ - self.HEIGHT:
            if not sec.neighbour[0, 1]:
                self.looky = SECTOR_SZ - self.HEIGHT
        if self.looky < 0:
            if not sec.neighbour[0, -1]:
                self.looky = 0

        # this bit moves the look point when when crosses a sector boundary
        if self.lookx < -self.WIDTH//2:
            if sec.neighbour[-1, 0]:
                self.lookx += SECTOR_SZ
                self.sx -= 1
                self.onlookpointchanged.emit(sec.neighbour[-1, 0])
        elif self.lookx > SECTOR_SZ - self.WIDTH//2:
            if sec.neighbour[1, 0]:
                self.lookx -= SECTOR_SZ
                self.sx += 1
                self.onlookpointchanged.emit(sec.neighbour[1, 0])

        if self.looky < -self.HEIGHT//2:
            if sec.neighbour[0, -1]:
                self.looky += SECTOR_SZ
                self.sy -= 1
                self.onlookpointchanged.emit(sec.neighbour[0, -1])
        elif self.looky > SECTOR_SZ - self.HEIGHT//2:
            if sec.neighbour[0, 1]:
                self.looky -= SECTOR_SZ
                self.sy += 1
                self.onlookpointchanged.emit(sec.neighbour[0, 1])
