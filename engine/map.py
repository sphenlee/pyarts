'''
Map

Holds the state of the terrain and fog-of-war.

Right now also does rendering - this should be moved...
'''

import array

from .event import Event

SECTOR_SZ = 32 # the number of tiles in a sector
VERTEX_SZ = 32 # the number of pixels per tile

def distance2(x1, y1, x2, y2):
    return (x1 - x2)**2 + (y1 - y2)**2

class Sector(object):
    def __init__(self, map, x, y):
        self.map = map
        self.x = x
        self.y = y
        self.data = map.datasrc.getmapsector(x, y)

        init = [0] * (SECTOR_SZ + 1) * (SECTOR_SZ + 1)
        self.visited = array.array('L', init)
        self.visible = array.array('L', init)

        self.onfogupdated = Event()

        # grab neighboring sectors
        self.left  = self.map.sectors.get((x - 1, y    ))
        self.up    = self.map.sectors.get((x    , y - 1))
        self.down  = self.map.sectors.get((x    , y + 1))
        self.right = self.map.sectors.get((x + 1, y    ))
        # tell them about us
        if self.left:
            self.left.right = self
        if self.right:
            self.right.left = self
        if self.up:
            self.up.down = self
        if self.down:
            self.down.up = self

    def pointvisited(self, tid, pt):
        x, y = pt
        return self.visited[x + y*SECTOR_SZ] & (1 << tid)

    def pointvisible(self, tid, pt):
        x, y = pt
        return self.visible[x + y*SECTOR_SZ] & (1 << tid)

    def updatefog(self, locators):
        # clear visible data, needs to be recalculated from scratch
        for i in xrange(len(self.visible)):
            self.visible[i] = 0

        # loop over locators and update visible and visited state
        for loc in locators:
            x, y, r = loc.x/VERTEX_SZ, loc.y/SECTOR_SZ, loc.sight/VERTEX_SZ
            for i in xrange(x-r, x+r):
                for j in xrange(y-r, y+r):
                    if 0 < i < SECTOR_SZ and 0 < j < SECTOR_SZ:
                        if distance2(i, j, x, y) < r*r:
                            tid = loc.ent.team.tid
                            self.visible[i + j*SECTOR_SZ] |= (1 << tid)
                            self.visited[i + j*SECTOR_SZ] |= (1 << tid)

        self.onfogupdated.emit()

class Map(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc

        self.sectors = { }
        self.dirty = set()
        self.locators = set()

        self.onsectorloaded = Event()

    def pos_to_sector(self, x, y):
        return (x >> 10), (y >> 10)

    def loadsector(self, sx, sy):
        if (sx, sy) not in self.sectors:
            s = Sector(self, sx, sy)
            s.updatefog(self.locators)
            self.sectors[sx, sy] = s
            self.onsectorloaded.emit(s)

    def step(self):
        for sx, sy in self.dirty:
            self.sectors[sx, sy].updatefog(self.locators)

        self.dirty.clear()

    def place(self, locator):
        self.locators.add(locator)
        self.move(locator)

    def move(self, locator):
        sx, sy = self.pos_to_sector(locator.x, locator.y)
        self.loadsector(sx, sy)
        self.dirty.add((sx, sy))

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