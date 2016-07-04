'''
Map

Holds the state of the terrain and fog-of-war.
'''

from .event import Event
from .sector import Sector, SECTOR_SZ, VERTEX_SZ

from pyarts.container import component

@component
class Map(object):
    depends = ['engine', 'datasrc']
    def __init__(self):
        self.sectors = { }
        self.dirty = set()
        self.locators = set()
        self.placedon = { } # locator -> set(sectors)

        self.onsectorloaded = Event()

        self.n = 0

    def inject(self, engine, datasrc):
        self.eng = engine
        self.datasrc = datasrc
        self.datasrc.onready.add(self.ready)

    def ready(self):
        for sx, sy in self.datasrc.getloadedsectors():
            self.loadsector(sx, sy)

    def save(self, datasink):
        for sec in self.sectors.itervalues():
            sec.save(datasink)

        datasink.setloadedsectors(self.sectors.iterkeys())

    def pos_to_cell(self, x, y):
        return (x/VERTEX_SZ, y/VERTEX_SZ)

    def cell_to_pos(self, x, y):
        return (x*VERTEX_SZ, y*VERTEX_SZ)

    def pos_to_sector(self, x, y):
        return (x >> 11), (y >> 11)

    def cell_to_sector(self, x, y):
        return (x >> 5), (y >> 5)

    def cell_to_offset(self, x, y):
        return (x & 0x1f), (y &0x1f)

    def pos_to_offset(self, x, y):
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

    def sector_at_point(self, x, y):
        sx, sy = self.pos_to_sector(x, y)
        return self.sectors.get((sx, sy))

    def sector_at_cell(self, x, y):
        sx, sy = self.cell_to_sector(x, y)
        return self.sectors.get((sx, sy))

    def step(self):
        self.n += 1
        if self.n % 50:
            while self.dirty:
                sec = self.dirty.pop()
                sec.updatefog()

    def place(self, locator):
        self.locators.add(locator)
        self.placedon[locator] = set()
        self.move(locator)

    def move(self, locator):
        x, y = locator.x, locator.y

        sx, sy = self.pos_to_sector(x, y)
        ox, oy = self.pos_to_offset(x, y)

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

    def footprint(self, locator):
        try:
            secs = self.placedon[locator]
        except KeyError:
            return False
        else:
            for sec in secs:
                sec.footprint(locator)
            return True


    def entities_in_rect(self, x1, y1, x2, y2):
        # TODO eventually this can use spatial partitioning to speed it up
        result = set()

        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1

        for loc in self.locators:
            if x1 - loc.r <= loc.x <= x2 + loc.r:
                if y1 - loc.r <= loc.y <= y2 + loc.r:
                    result.add(loc.ent)

        return result