'''
Map

Holds the state of the terrain and fog-of-war.

Right now also does rendering - this should be moved...
'''

import array
import ctypes

import pyglet
from pyglet import gl

from .tileset import Tileset
from .fogofwar import FogOfWar

# some magic numbers :)
SECTOR_SZ = 32 # the number of tiles in a sector
VERTEX_SZ = 32 # the number of pixels per tile
TEX_SZ = 1 / 8.0 # the size of each tile in text units

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

    def pointvisited(self, tid, pt):
        x, y = pt
        return self.visited[x + y*SECTOR_SZ] & (1 << tid)

    def pointvisible(self, tid, pt):
        x, y = pt
        return self.visible[x + y*SECTOR_SZ] & (1 << tid)

    def rendersetup(self, batch):
        tiles = self.data.get('tiles')
        if tiles is None:
            tiles = [0] * SECTOR_SZ * SECTOR_SZ

        vdata = array.array('f') # vertex data
        tdata = array.array('f') # terrain data

        for y in xrange(SECTOR_SZ):
            for x in xrange(SECTOR_SZ):
                # vertex
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
                # terrain
                tile = tiles[x + SECTOR_SZ*y]
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
        self.terrain_vb = batch.add(SECTOR_SZ * SECTOR_SZ * 3 * 2,
            gl.GL_TRIANGLES, group, 'v2f', 't2f')

        self.terrain_vb.vertices = vdata
        self.terrain_vb.tex_coords = tdata

        group = self.map.fogofwar.group
        self.fog_vb = batch.add(SECTOR_SZ * SECTOR_SZ * 3 * 2,
            gl.GL_TRIANGLES, group, 'v2f', 't2f')

        self.fog_vb.vertices = vdata

    def updatefog(self, locators, tidmask):
        fdata = array.array('f') # fog data

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

        # loop over the map and assign texture coords to create the
        # fog texture
        for y in xrange(SECTOR_SZ):
            for x in xrange(SECTOR_SZ):
                a = self.visible[ x      +  y     *SECTOR_SZ] & tidmask != 0
                b = self.visible[(x + 1) +  y     *SECTOR_SZ] & tidmask != 0
                c = self.visible[ x      + (y + 1)*SECTOR_SZ] & tidmask != 0
                d = self.visible[(x + 1) + (y + 1)*SECTOR_SZ] & tidmask != 0

                e = self.visited[ x      +  y     *SECTOR_SZ] & tidmask != 0
                f = self.visited[(x + 1) +  y     *SECTOR_SZ] & tidmask != 0
                g = self.visited[ x      + (y + 1)*SECTOR_SZ] & tidmask != 0
                h = self.visited[(x + 1) + (y + 1)*SECTOR_SZ] & tidmask != 0

                ty, tx = self.map.fogofwar.gettile(a, b, c, d, e, f, g, h)
                tx = tx * TEX_SZ
                ty = 1 - ty * TEX_SZ
                fdata.extend([
                    tx, ty,
                    tx + TEX_SZ, ty - TEX_SZ,
                    tx, ty - TEX_SZ,
                    tx, ty,
                    tx + TEX_SZ, ty,
                    tx + TEX_SZ, ty - TEX_SZ
                ])

        self.fog_vb.tex_coords = fdata

class Map(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc

        self.tileset = Tileset(datasrc)
        self.fogofwar = FogOfWar(datasrc)

        self.sectors = { }
        self.dirty = set()
        self.locators = set()

        self.batch = pyglet.graphics.Batch()

    
    def pos_to_sector(self, x, y):
        return (x >> 10), (y >> 10)

    def loadsector(self, x, y):
        if (x, y) not in self.sectors:
            s = Sector(self, x, y)
            s.rendersetup(self.batch)
            s.updatefog(self.locators, 1)
            self.sectors[x, y] = s

    def step(self):
        for x, y in self.dirty:
            self.sectors[x, y].updatefog(self.locators, 1)

        self.dirty.clear()

    def draw(self):
        self.batch.draw()

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