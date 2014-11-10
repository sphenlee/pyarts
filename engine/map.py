'''
Map

Holds the state of the terrain and fog-of-war.

Right now also does rendering - this should be moved...
'''

import array
import time
import binascii

from .event import Event

NUM_TILES = 64 # the number of tiles in a sector
VERTEX_SZ = 32 # the number of pixels per tile
SECTOR_SZ = NUM_TILES * VERTEX_SZ

NEIGHBOURS = [ (-1, -1), (0, -1), (1, -1),
               (-1,  0),          (1,  0),
               (-1,  1), (0,  1), (1,  1) ]

def distance2(x1, y1, x2, y2):
    return (x1 - x2)**2 + (y1 - y2)**2

class Sector(object):
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
            res = map.datasrc.getresource(data['visited'])
            with open(res) as fp:
                bindata = binascii.unhexlify(fp.read().replace('\n', ''))
                self.visited = array.array('L')
                self.visited.fromstring(bindata)
        else:
            self.visited = array.array('L', init)

        self.visible = array.array('L', init)
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
        fname = 'visited_%d_%d.hex' % (self.sx, self.sy)
        datasink.addresource(fname, data)

        datasink.addmapsector(self.sx, self.sy, {
                'visited' : fname,
                'tiles' : self.tiles,
                'entities' : [loc.ent.eid for loc in self.locators]
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
        if not self.occupied():
            print 'sector is empty?'

    def occupied(self):
        return len(self.locators) > 0

    def pointvisited(self, tid, pt):
        x, y = pt
        return self.visited[x + y*NUM_TILES] & (1 << tid)

    def pointvisible(self, tid, pt):
        x, y = pt
        return self.visible[x + y*NUM_TILES] & (1 << tid)

    def updatefog(self):
        start = time.time()
        # clear visible data, needs to be recalculated from scratch
        for i in xrange(len(self.visible)):
            self.visible[i] = 0

        # loop over locators and update visible and visited state
        for loc in self.locators:
            print loc.ent, loc.x, loc.y, loc.sight
            x = loc.x/VERTEX_SZ - self.sx*NUM_TILES
            y = loc.y/VERTEX_SZ - self.sy*NUM_TILES
            r = loc.sight/VERTEX_SZ
            for i in xrange(x-r, x+r):
                for j in xrange(y-r, y+r):
                    if 0 <= i <= NUM_TILES and 0 <= j <= NUM_TILES:
                        if distance2(i, j, x, y) < r*r:
                            tid = loc.ent.team.tid
                            self.visible[i + j*NUM_TILES] |= (1 << tid)
                            self.visited[i + j*NUM_TILES] |= (1 << tid)
        print 'updated fog (%d,%d) took %fs' % (self.sx, self.sy, time.time() - start)

        self.onfogupdated.emit()

class Map(object):
    def __init__(self, eng):
        self.eng = eng
        self.datasrc = eng.datasrc

        self.sectors = { }
        self.dirty = set()
        self.locators = set()
        self.placedon = { } # locator -> set(sectors)

        self.onsectorloaded = Event()

        self.n = 0

    def load(self):
        for sx, sy in self.datasrc.getloadedsectors():
            self.loadsector(sx, sy)

    def save(self, datasink):
        for sec in self.sectors.itervalues():
            sec.save(datasink)

        datasink.setloadedsectors(self.sectors.iterkeys())

    def pos_to_sector(self, x, y):
        return (x >> 11), (y >> 11)

    def pos_to_sector_offset(self, x, y):
        return (x & 0x7ff), (y & 0x7ff)

    def loadsector(self, sx, sy):
        try:
            return self.sectors[sx, sy]
        except KeyError:
            try:
                s = Sector(self, sx, sy)
            except KeyError:
                return None
            self.sectors[sx, sy] = s
            self.dirty.add(s)
            self.onsectorloaded.emit(s)
            return s

    def step(self):
        self.n += 1
        if self.n % 10:
            for sec in self.dirty:
                sec.updatefog()

            self.dirty.clear()

    def place(self, locator):
        self.locators.add(locator)
        self.placedon[locator] = set()
        self.move(locator)

    def move(self, locator):
        x, y = locator.x, locator.y

        sx, sy = self.pos_to_sector(x, y)
        ox, oy = self.pos_to_sector_offset(x, y)

        for sec in self.placedon[locator]:
            sec.unplace(locator)
            self.dirty.add(sec)
        self.placedon[locator].clear()

        def sectorplace(dx, dy):
            sec = self.loadsector(sx + dx, sy + dy)
            if sec:
                sec.place(locator)
                self.placedon[locator].add(sec)
                self.dirty.add(sec)

        # I just love this algorithm...
        if ox - locator.sight < 0:
            dx = -1
        elif ox + locator.sight > SECTOR_SZ:
            dx = 1
        else:
            dx = 0
        if oy - locator.sight < 0:
            dy = -1
        elif oy + locator.sight > SECTOR_SZ:
            dy = 1
        else:
            dy = 0

        sectorplace(0, 0)
        if dx:
            sectorplace(dx, 0)
        if dy:
            sectorplace(0, dy)
        if dx and dy:
            sectorplace(dx, dy)

    def unplace(self, locator):
        secs = self.placedon[locator]
        for sec in secs:
            sec.locators.discard(locator)
            self.dirty.add(sec)
        del self.placedon[locator]

    def entities_in_rect(self, x1, y1, x2, y2):
        # TODO eventually this can use spatial partitioning to speed it up
        result = set()

        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1

        for loc in self.locators:
            if x1 <= loc.x <= x2:
                if y1 <= loc.y <= y2:
                    result.add(loc.ent.eid)

        return result