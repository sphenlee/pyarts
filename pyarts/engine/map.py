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
        self.onfogupdated = Event()

        self.n = 0

    def inject(self, engine, datasrc):
        self.eng = engine
        self.datasrc = datasrc
        self.datasrc.onready.add(self.ready)

    def ready(self):
        for sx, sy in self.datasrc.getloadedsectors():
            self.loadsector(sx, sy)

    def save(self, datasink):
        for sec in self.sectors.values():
            sec.save(datasink)

        datasink.setloadedsectors(iter(self.sectors.keys()))


    # _________________________________________________________
    # TODO - work out how many of these are actually being used

    def pos_to_sector_offset(self, pos):
        off = self.pos_to_offset(*pos)
        sec = self.sector_at_pos(*pos)
        return sec, off

    def cell_to_sector_offset(self, x, y):
        off = self.cell_to_offset(x, y)
        sec = self.sector_at_cell(x, y)
        return sec, off

    # def pos_to_cell(self, x, y):
    #     return (x/VERTEX_SZ, y/VERTEX_SZ)

    # def cell_to_pos(self, x, y):
    #     return (x*VERTEX_SZ, y*VERTEX_SZ)

    def pos_to_sector(self, x, y):
        # 11 = log2(SECTOR_SZ)
        return (int(x) >> 11), (int(y) >> 11)

    def cell_to_sector(self, x, y):
        # 6 = log2(NUM_TILES)
        return (int(x) >> 6), (int(y) >> 6)

    def cell_to_offset(self, x, y):
        # 0x3f = NUM_TILES - 1
        return (int(x) & 0x3f), (int(y) & 0x3f)

    def pos_to_offset(self, x, y):
        return (int(x/VERTEX_SZ) & 0x3f), (int(y/VERTEX_SZ) & 0x3f)

    def pos_to_offset_mystery(self, x, y):
        # 0x7ff = SECTOR_SZ - 1
        return (int(x) & 0x7ff), (int(y) & 0x7ff)

    # _________________________________________________________

    def loadsector(self, sx, sy):
        try:
            return self.sectors[sx, sy]
        except KeyError:
            s = Sector.construct(self, self.datasrc, sx, sy)
            self.sectors[sx, sy] = s
            if s is not None:
                self.dirty.add(s)
                self.onsectorloaded.emit(s)
            return s

    def sector_at_pos(self, x, y):
        sx, sy = self.pos_to_sector(x, y)
        return self.sectors.get((sx, sy))

    def sector_at_cell(self, x, y):
        sx, sy = self.cell_to_sector(x, y)
        return self.sectors.get((sx, sy))


    def cell_walkable(self, walk, x, y):
        ''' used by the pathfinder in Rust '''
        sec, off = self.cell_to_sector_offset(x, y)
        if sec:
            return sec.cellwalkable(walk, off) and sec.cellvisited(0, off) # TODO - get the current tid
        else:
            return False
   

    def step(self):
        self.n += 1
        if self.n % 500:
            was_dirty = len(self.dirty) > 0

            while self.dirty:
                sec = self.dirty.pop()
                #print(f'sector {sec} is dirty')
                sec.updatefog()

            if was_dirty:
                self.onfogupdated.emit()


    def place(self, locator):
        self.locators.add(locator)
        self.placedon[locator] = set()
        self.move(locator)

    def move(self, locator):
        x, y = locator.x, locator.y

        sx, sy = self.pos_to_sector(x, y)
        ox, oy = self.pos_to_offset_mystery(x, y)

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
            if loc.placed:
                if x1 - loc.r <= loc.x <= x2 + loc.r:
                    if y1 - loc.r <= loc.y <= y2 + loc.r:
                        result.add(loc.ent)

        return result