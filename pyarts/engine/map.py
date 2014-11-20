'''
Map

Holds the state of the terrain and fog-of-war.
'''

from .event import Event
from .sector import Sector, SECTOR_SZ



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
        if self.n % 50:
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