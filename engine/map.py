'''
Map

Holds the state of the terrain and fog-of-war.

Right now also does rendering - this should be moved...
'''

import array
import time

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
        self.data = map.datasrc.getmapsector(sx, sy)

        # fog info
        init = [0] * (NUM_TILES + 1) * (NUM_TILES + 1)
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

    def loadneighbours(self):
        ''' When a sector is occupied we need to ensure its neighbours are loaded'''
        for dx, dy in NEIGHBOURS:
            s = self.map.loadsector(self.sx + dx, self.sy + dy)
            self.neighbour[dx, dy] = s
            if s:
                s.neighbour[-dx, -dy] = self


    def place(self, locator):
        oldsec = locator.sector
        if oldsec:
            oldsec.locators.discard(locator)
            self.map.dirty.add(oldsec)

        self.locators.add(locator)
        self.map.dirty.add(self)

        self.loadneighbours()

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
        print 'updated fog, took %fs' % (time.time() - start)

        self.onfogupdated.emit()

class Map(object):
    def __init__(self, eng):
        self.eng = eng
        self.datasrc = eng.datasrc

        self.sectors = { }
        self.dirty = set()
        self.locators = set()

        self.onsectorloaded = Event()

        self.n = 0

    def load(self):
        for sx, sy in self.datasrc.getloadedsectors():
            self.loadsector(sx, sy)

    def pos_to_sector(self, x, y):
        return (x >> 11), (y >> 11)

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
        self.move(locator)

    def move(self, locator):
        sx, sy = self.pos_to_sector(locator.x, locator.y)
        sec = self.loadsector(sx, sy)
        sec.place(locator)

        self.dirty.add(sec)

    def unplace(self, locator):
        sec = locator.sector
        if sec:
            sec.locators.discard(locator)
            self.dirty.add(sec)

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