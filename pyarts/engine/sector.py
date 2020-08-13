'''
Sector

A piece of the map
'''

import array
import binascii
import time

from pyarts.container import dynamic_component

from .event import Event

from yarts import Sector as RsSector
from pyarts.log import warn

NUM_TILES = 64  # the number of tiles in a sector
NUM_VERTS = NUM_TILES + 1  # the number of vertices in a sector
VERTEX_SZ = 32  # the number of pixels per tile
SECTOR_SZ = NUM_TILES * VERTEX_SZ

NEIGHBOURS = [(-1, -1), (0, -1), (1, -1),
              (-1,  0),          (1,  0),
              (-1,  1), (0,  1), (1,  1)]


def distance2(x1, y1, x2, y2):
    '''Euclidean distance squared'''
    return (x1 - x2)**2 + (y1 - y2)**2

# def get_hex_resource(datasrc, name):
#     '''Helper to get a hex encoded resource'''
#     res = datasrc.getresource(name)
#     with open(res, 'rb') as fp:
#         return binascii.unhexlify(fp.read().replace(b'\n', b''))


@dynamic_component
class Sector(RsSector):
    '''
    A sector is a piece of the map
    '''
    depends = ['map', 'datasrc']

    # constants for walkmap - if the bit is set,
    # it is NOT walkable for that walk type
    WALK_GROUND = 0x01
    WALK_SEA = 0x02
    WALK_AIR = 0x04
    WALK_FOOT = 0x08

    def inject(self, map, datasrc):
        self.map = map
        
        data = datasrc.getmapsector(self.sx, self.sy)
        
        self.tileset = datasrc.gettileset(data['tileset']).copy()

        # TODO - work out ggez's crazy path system!
        self.tileset['texture'] = '/' + datasrc.getresource(self.tileset['texture'])
        self.tileset['fogofwar'] = '/' + datasrc.getresource(self.tileset['fogofwar'])

        # TODO this is bad - the value is
        # eids and is not kept updated
        self.entities = data.get('entities', ())

        file = datasrc.getresource(data['file'])
        self.load(file)

        self.onfogupdated = Event()

        # locators near this sector
        self.locators = set()

        # neighbour sectors
        self.neighbour = {}
        for dx, dy in NEIGHBOURS:
            s = self.map.sectors.get((self.sx + dx, self.sy + dy))
            self.neighbour[dx, dy] = s
            if s:
                s.neighbour[-dx, -dy] = self

    def save(self, datasink):
        # TODO - save the map visited data
        # data = binascii.hexlify(self.visited.tostring())
        # fname = 'visited/%d_%d.hex' % (self.sx, self.sy)
        # datasink.addresource(fname, data)

        datasink.addmapsector(self.sx, self.sy, {
                'visited': fname,
                'entities': [loc.eid for loc in self.locators]
            })

    def loadneighbours(self):
        '''
        When a sector is occupied we need to ensure its neighbours are loaded
        '''
        for dx, dy in NEIGHBOURS:
            s = self.map.loadsector(self.sx + dx, self.sy + dy)
            self.neighbour[dx, dy] = s
            if s:
                s.neighbour[-dx, -dy] = self

    def place(self, locator):
        self.locators.add(locator)
        self.loadneighbours()

    def unplace(self, locator):
        self.locators.discard(locator)
        # if not self.occupied():
        #     print 'sector is empty?'

    def footprint(self, loc):
        x = int(loc.x/VERTEX_SZ + 0.5) - self.sx*NUM_TILES
        y = int(loc.y/VERTEX_SZ + 0.5) - self.sy*NUM_TILES
        r = int(loc.r/VERTEX_SZ + 0.5)

        super().footprint(x, y, r)

    def occupied(self):
        return len(self.locators) > 0

    def cellvisited(self, tid, pt):
        return (self.visited(pt) & (1 << tid)) > 0

    def cellvisible(self, tid, pt):
        return (self.visible(pt) & (1 << tid)) > 0

    def cellvisited_mask(self, pt):
        return self.visited(pt)

    def cellvisible_mask(self, pt):
        return self.visible(pt)

    def cellwalkable(self, walk, pt):
        return (self.walk(pt) & walk) == 0

    def updatefog(self):
        self.clear_fog()

        for loc in self.locators:
            x = int(loc.x/VERTEX_SZ + 0.5) - self.sx*NUM_TILES
            y = int(loc.y/VERTEX_SZ + 0.5) - self.sy*NUM_TILES
            r = int(loc.sight/VERTEX_SZ + 0.5)

            self.update_fog(x, y, r, loc.ent.team.tid)
