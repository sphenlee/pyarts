'''
Sector

A piece of the map
'''

from __future__ import division

import array
import binascii
import time

from .event import Event

NUM_TILES = 32 # the number of tiles in a sector
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
    with open(res) as fp:
        return binascii.unhexlify(fp.read().replace('\n', ''))


class Sector(object):
    '''
    A sector is a piece of the map
    '''

    # constants for walkmap - if the bit is set, it is NOT walkable for that walk type
    WALK_GROUND = 0x01
    WALK_SEA = 0x02
    WALK_AIR = 0x04
    WALK_FOOT = 0x08

    def __init__(self, map, sx, sy):
        # general stuff
        self.map = map
        self.sx = sx
        self.sy = sy
        
        data = map.datasrc.getmapsector(sx, sy)

        self.tiles = data['tiles']
        self.entities = data.get('entities', ()) # this is bad - the value is eids and is not kept updated

        # fog info

        init = '\0' * 8 * (NUM_TILES + 1) * (NUM_TILES + 1)

        if 'visited' in data:
            bindata = get_hex_resource(map.datasrc, data['visited'])
            self.visited = array.array('B')
            self.visited.fromstring(bindata)
        else:
            self.visited = array.array('B', init)

        if 'walkmap' in data:
            bindata = get_hex_resource(map.datasrc, data['walkmap'])
            self.walkmap = array.array('B')
            self.walkmap.fromstring(bindata)
        else:
            self.walkmap = array.array('B', init)            

        self.visible = array.array('B', init)
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
        data = binascii.hexlify(self.visited.tostring())
        fname = 'visited/%d_%d.hex' % (self.sx, self.sy)
        datasink.addresource(fname, data)

        datasink.addmapsector(self.sx, self.sy, {
                'visited' : fname,
                'tiles' : self.tiles,
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
        for i in xrange(x-r, x+r):
            for j in xrange(y-r, y+r):
                if 0 <= i <= NUM_TILES and 0 <= j <= NUM_TILES:
                    #if distance2(i, j, x, y) <= r*r:
                    self.walkmap[i + j*NUM_TILES] |= Sector.WALK_FOOT

    def occupied(self):
        return len(self.locators) > 0

    def cellvisited(self, tid, pt):
        x, y = pt
        return self.visited[x + y*NUM_TILES] & (1 << tid)

    def cellvisible(self, tid, pt):
        x, y = pt
        return self.visible[x + y*NUM_TILES] & (1 << tid)

    def cellwalkable(self, walk, pt):
        x, y = pt
        return (self.walkmap[x + y*NUM_TILES] & walk) == 0

    def updatefog(self):
        start = time.time()
        # clear visible data, needs to be recalculated from scratch
        for i in xrange(len(self.visible)):
            self.visible[i] = 0

        # loop over locators and update visible and visited state
        for loc in self.locators:
            #print loc.ent, loc.x, loc.y, loc.sight
            x = int(loc.x/VERTEX_SZ + 0.5) - self.sx*NUM_TILES
            y = int(loc.y/VERTEX_SZ + 0.5) - self.sy*NUM_TILES
            r = int(loc.sight/VERTEX_SZ + 0.5)
            for i in xrange(x-r, x+r):
                for j in xrange(y-r, y+r):
                    if 0 <= i <= NUM_TILES and 0 <= j <= NUM_TILES:
                        if distance2(i, j, x, y) < r*r:
                            tid = loc.ent.team.tid
                            self.visible[i + j*NUM_TILES] |= (1 << tid)
                            self.visited[i + j*NUM_TILES] |= (1 << tid)
        #print 'updated fog (%d,%d) took %fs' % (self.sx, self.sy, time.time() - start)

        self.onfogupdated.emit()