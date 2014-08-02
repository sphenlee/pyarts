'''
Map

Holds the state of the terrain and fog-of-war.

Right now also does rendering - this should be moved...
'''

import array

import pyglet
from pyglet import gl

from .tileset import Tileset

# some magic numbers :)
SECTOR_SZ = 32 # the number of tiles in a sector
VERTEX_SZ = 32 # the number of pixels per tile
TEX_SZ = 1 / 8.0 # the size of each tile in text units

class Sector(object):
    def __init__(self, map, x, y):
        self.map = map
        self.x = x
        self.y = y
        self.data = map.datasrc.getmapsector(x, y)

    def rendersetup(self, batch):
        tiles = self.data['tiles']

        vdata = array.array('f')
        tdata = array.array('f')
        
        for y in xrange(SECTOR_SZ):
            for x in xrange(SECTOR_SZ):
                tile = tiles[x + SECTOR_SZ*y]

                vx = x * VERTEX_SZ
                vy = y * VERTEX_SZ
                vdata.extend([
                    vx, vy,
                    vx + VERTEX_SZ, vy + VERTEX_SZ,
                    vx, vy + VERTEX_SZ,
                    vx, vy,
                    vx + VERTEX_SZ, vy,
                    vx + VERTEX_SZ, vy + VERTEX_SZ
                ])
                ty, tx = divmod(tile, 8)
                tx = tx * TEX_SZ
                ty = 1 - ty * TEX_SZ
                tdata.extend([
                    tx, ty,
                    tx + TEX_SZ, ty - TEX_SZ,
                    tx, ty - TEX_SZ,
                    tx, ty,
                    tx + TEX_SZ, ty,
                    tx + TEX_SZ, ty - TEX_SZ
                ])

        group = self.map.tileset.group
        self.vb = batch.add(SECTOR_SZ * SECTOR_SZ * 3 * 2,
            gl.GL_TRIANGLES, group, 'v2f', 't2f')

        self.vb.vertices = vdata
        self.vb.tex_coords = tdata

class Map(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc

        self.tileset = Tileset(datasrc)

        self.sectors = { }
        self.locators = set()

        self.batch = pyglet.graphics.Batch()

    
    def pos_to_sector(self, x, y):
        return x & 1024, y & 1024

    def loadsector(self, x, y):
        if (x, y) not in self.sectors:
            s = Sector(self, x, y)
            s.rendersetup(self.batch)
            self.sectors[x, y] = s

    def step(self):
        pass

    def draw(self):
        self.batch.draw()

    def place(self, locator):
        sx, sy = self.pos_to_sector(locator.x, locator.y)
        self.loadsector(sx, sy)
        self.locators.add(locator)

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