'''
Sector

A piece of the map
'''



import array
import binascii
import time

from .event import Event

from yarts import Sector as RsSector

NUM_TILES = 32 # the number of tiles in a sector
NUM_VERTS = NUM_TILES + 1 # the number of vertices in a sector
VERTEX_SZ = 64 # the number of pixels per tile
SECTOR_SZ = NUM_TILES * VERTEX_SZ

NEIGHBOURS = [ (-1, -1), (0, -1), (1, -1),
               (-1,  0),          (1,  0),
               (-1,  1), (0,  1), (1,  1) ]

def distance2(x1, y1, x2, y2):
    '''Euclidean distance squared'''
    return (x1 - x2)**2 + (y1 - y2)**2

def get_hex_resource(datasrc, name):
    '''Helper to get a hex encoded resource'''
    res = datasrc.getresource(name)
    with open(res, 'rb') as fp:
        return binascii.unhexlify(fp.read().replace(b'\n', b''))


class Sector(object):
    '''
    A sector is a piece of the map
    '''

    # constants for walkmap - if the bit is set, it is NOT walkable for that walk type
    WALK_GROUND = 0x01
    WALK_SEA = 0x02
    WALK_AIR = 0x04
    WALK_FOOT = 0x08

    @classmethod
    def construct(cls, map, datasrc, sx, sy):
        data = datasrc.getmapsector(sx, sy)
        tileset = datasrc.gettileset(data['tileset']).copy()

        # TODO - work out ggez's crazy path system!
        tileset['texture'] = '/' + datasrc.getresource(tileset['texture'])
        tileset['fogofwar'] = '/' + datasrc.getresource(tileset['fogofwar'])

        tiles = get_hex_resource(datasrc, data['tiles'])
        visited = get_hex_resource(datasrc, data['visited']) if 'visited' in data else None
        walkmap = get_hex_resource(datasrc, data['walkmap']) if 'walkmap' in data else None

        entities = data.get('entities', ()) # this is bad - the value is eids and is not kept updated

        peer = RsSector(sx, sy, tiles, visited, walkmap)
        return cls(peer, map, entities, tileset)


    def __init__(self, peer, map, entities, tileset):
        self.peer = peer
        self.sx = peer.sx
        self.sy = peer.sy
        self.map = map
        self.entities = entities
        self.tileset = tileset

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
        #data = binascii.hexlify(self.visited.tostring())
        #fname = 'visited/%d_%d.hex' % (self.sx, self.sy)
        #datasink.addresource(fname, data)

        datasink.addmapsector(self.sx, self.sy, {
                'visited' : fname,
                #'tiles' : self.tiles,
                'entities' : [loc.eid for loc in self.locators]
            })


    def loadneighbours(self):
        ''' When a sector is occupied we need to ensure its neighbours are loaded'''
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
        #if not self.occupied():
        #    print 'sector is empty?'

    def footprint(self, loc):
        x = int(loc.x/VERTEX_SZ + 0.5) - self.sx*NUM_TILES
        y = int(loc.y/VERTEX_SZ + 0.5) - self.sy*NUM_TILES
        r = int(loc.r/VERTEX_SZ + 0.5)

        self.peer.footprint(x, y, r)


        #for i in range(x-r, x+r):
        #    for j in range(y-r, y+r):
        #        if 0 <= i < NUM_TILES and 0 <= j < NUM_TILES:
        #            #if distance2(i, j, x, y) <= r*r:
        #            self.walkmap[i + j*NUM_TILES] |= Sector.WALK_FOOT

    def occupied(self):
        return len(self.locators) > 0

    def cellvisited(self, tid, pt):
        return self.peer.visited(pt) & (1 << tid)

    def cellvisible(self, tid, pt):
        return self.peer.visible(pt) & (1 << tid)

    def cellvisited_mask(self, pt):
        return self.peer.visited(pt)

    def cellvisible_mask(self, pt):
        return self.peer.visible(pt)

    def cellwalkable(self, walk, pt):
        return (self.peer.walk(pt) & walk) == 0

    def updatefog(self):
        self.peer.clear_fog()

        for loc in self.locators:
            x = int(loc.x/VERTEX_SZ + 0.5) - self.sx*NUM_TILES
            y = int(loc.y/VERTEX_SZ + 0.5) - self.sy*NUM_TILES
            r = int(loc.sight/VERTEX_SZ + 0.5)
        
            self.peer.update_fog(x, y, r, loc.ent.team.tid)


        # #start = time.time()
        # # clear visible data, needs to be recalculated from scratch
        # for i in range(len(self.visible)):
        #     self.visible[i] = 0

        # # loop over locators and update visible and visited state
        # for loc in self.locators:
        #     #print loc.ent, loc.x, loc.y, loc.sight
        #     x = int(loc.x/VERTEX_SZ + 0.5) - self.sx*NUM_TILES
        #     y = int(loc.y/VERTEX_SZ + 0.5) - self.sy*NUM_TILES
        #     r = int(loc.sight/VERTEX_SZ + 0.5)
        #     for i in range(x-r, x+r):
        #         for j in range(y-r, y+r):
        #             if 0 <= i < NUM_VERTS and 0 <= j < NUM_VERTS:
        #                 if distance2(i, j, x, y) < r*r:
        #                     tid = loc.ent.team.tid
        #                     self.visible[i + j*NUM_VERTS] |= (1 << tid)
        #                     self.visited[i + j*NUM_VERTS] |= (1 << tid)
        # #print 'updated fog (%d,%d) took %fs' % (self.sx, self.sy, time.time() - start)

        #self.onfogupdated.emit()


