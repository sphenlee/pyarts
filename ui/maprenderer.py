'''
MapRenderer
'''

import array

import pyglet
from pyglet import gl

from .fogofwar import FogOfWar
from .util import TextureGroup

from engine.map import SECTOR_SZ, VERTEX_SZ

TEX_SZ = 1 / 8.0 # the size of each tile in text units


class SectorRenderer(object):
    def __init__(self, mapren, sector):
        self.mapren = mapren
        self.sector = sector

        self.sector.onfogupdated.add(self.updatefog)

    def rendersetup(self, batch):
        tiles = self.sector.data.get('tiles')
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
        
        group = self.mapren.tileset_group
        self.terrain_vb = batch.add(SECTOR_SZ * SECTOR_SZ * 3 * 2,
            gl.GL_TRIANGLES, group, 'v2f', 't2f')

        self.terrain_vb.vertices = vdata
        self.terrain_vb.tex_coords = tdata

        group = self.mapren.fogofwar.group
        self.fog_vb = batch.add(SECTOR_SZ * SECTOR_SZ * 3 * 2,
            gl.GL_TRIANGLES, group, 'v2f', 't2f')

        self.fog_vb.vertices = vdata

    def updatefog(self):
        tidmask = self.mapren.tidmask
        sec = self.sector

        fdata = array.array('f') # fog data

        # loop over the map and assign texture coords to create the
        # fog texture
        for y in xrange(SECTOR_SZ):
            for x in xrange(SECTOR_SZ):
                a = sec.visible[ x      +  y     *SECTOR_SZ] & tidmask != 0
                b = sec.visible[(x + 1) +  y     *SECTOR_SZ] & tidmask != 0
                c = sec.visible[ x      + (y + 1)*SECTOR_SZ] & tidmask != 0
                d = sec.visible[(x + 1) + (y + 1)*SECTOR_SZ] & tidmask != 0

                e = sec.visited[ x      +  y     *SECTOR_SZ] & tidmask != 0
                f = sec.visited[(x + 1) +  y     *SECTOR_SZ] & tidmask != 0
                g = sec.visited[ x      + (y + 1)*SECTOR_SZ] & tidmask != 0
                h = sec.visited[(x + 1) + (y + 1)*SECTOR_SZ] & tidmask != 0

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

        self.batch = pyglet.graphics.Batch()

        self.loadtileset()

        self.fogofwar = FogOfWar(datasrc)

        self.looksector = None # the sector being looked at
        self.sectors = [] # at most 9 sectors should be loaded

        map.onsectorloaded.add(self.sectorloaded)

    def loadtileset(self):
        data = self.datasrc.gettileset()
        res = self.datasrc.getresource(data['texture'])
        img = pyglet.image.load(res)

        self.tileset_group = TextureGroup(img.get_texture())

    def sectorloaded(self, sector):
        sr = SectorRenderer(self, sector)
        sr.rendersetup(self.batch)
        self.sectors.append(sr)

    def lookat(self, sector):
        self.looksector = sector

    def draw(self):
        self.batch.draw()
