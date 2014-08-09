'''
MapRenderer
'''

import array

import pyglet
from pyglet import gl

from .fogofwar import FogOfWar
from .util import TextureGroup, TranslateGroup

from engine.map import NUM_TILES, VERTEX_SZ

TEX_SZ = 1 / 8.0 # the size of each tile in text units


class SectorRenderer(object):
    def __init__(self, mapren, sector):
        self.mapren = mapren
        self.sector = sector

        self.sector.onfogupdated.add(self.updatefog)

    def rendersetup(self, batch, dx, dy):
        tiles = self.sector.data.get('tiles')
        if tiles is None:
            tiles = [0] * NUM_TILES * NUM_TILES

        vdata = array.array('f') # vertex data
        tdata = array.array('f') # terrain data

        for y in xrange(NUM_TILES):
            for x in xrange(NUM_TILES):
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
                tile = tiles[x + NUM_TILES*y]
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
        
        group = TranslateGroup(
            dx * NUM_TILES * VERTEX_SZ,
            dy * NUM_TILES * VERTEX_SZ,
            parent=self.mapren.tileset_group
        )

        self.terrain_vb = batch.add(NUM_TILES * NUM_TILES * 3 * 2,
            gl.GL_TRIANGLES, group, 'v2f', 't2f')

        self.terrain_vb.vertices = vdata
        self.terrain_vb.tex_coords = tdata

        group = TranslateGroup(
            dx * NUM_TILES * VERTEX_SZ,
            dy * NUM_TILES * VERTEX_SZ,
            parent=self.mapren.fogofwar.group
        )

        self.fog_vb = batch.add(NUM_TILES * NUM_TILES * 3 * 2,
            gl.GL_TRIANGLES, group, 'v2f', 't2f')

        self.fog_vb.vertices = vdata

    def updatefog(self):
        tidmask = self.mapren.tidmask
        sec = self.sector

        fdata = array.array('f') # fog data

        # loop over the map and assign texture coords to create the
        # fog texture
        for y in xrange(NUM_TILES):
            for x in xrange(NUM_TILES):
                a = sec.visible[ x      +  y     *NUM_TILES] & tidmask != 0
                b = sec.visible[(x + 1) +  y     *NUM_TILES] & tidmask != 0
                c = sec.visible[ x      + (y + 1)*NUM_TILES] & tidmask != 0
                d = sec.visible[(x + 1) + (y + 1)*NUM_TILES] & tidmask != 0

                e = sec.visited[ x      +  y     *NUM_TILES] & tidmask != 0
                f = sec.visited[(x + 1) +  y     *NUM_TILES] & tidmask != 0
                g = sec.visited[ x      + (y + 1)*NUM_TILES] & tidmask != 0
                h = sec.visited[(x + 1) + (y + 1)*NUM_TILES] & tidmask != 0

                ty, tx = self.mapren.fogofwar.gettile(a, b, c, d, e, f, g, h)
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


class MapRenderer(object):
    def __init__(self, datasrc, map, tidmask):
        self.datasrc = datasrc
        self.map = map
        self.tidmask = tidmask

        self.loadtileset()

        self.fogofwar = FogOfWar(datasrc)

        self.looksector = None # the sector being looked at
        self.renderers = [] # at most 9 sectors should be loaded

    def loadtileset(self):
        data = self.datasrc.gettileset()
        res = self.datasrc.getresource(data['texture'])
        img = pyglet.image.load(res)

        self.tileset_group = TextureGroup(img.get_texture())

    def setupsector(self, sector, dx, dy):
        sr = SectorRenderer(self, sector)
        sr.rendersetup(self.batch, dx, dy)
        sr.updatefog()
        self.renderers.append(sr)

    def lookat(self, sector):
        print 'lookat ', sector.sx, sector.sy
        # TODO don't reload every sector
        
        self.batch = pyglet.graphics.Batch()
        self.looksector = sector
        self.renderers = []

        print sector.neighbour
        for (dx, dy), sec in sector.neighbour.items():
            if sec:
                self.setupsector(sec, dx, dy)

    def draw(self):
        self.batch.draw()
