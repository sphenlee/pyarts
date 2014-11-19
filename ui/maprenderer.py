'''
MapRenderer
'''

import array
import binascii
import time

import pyglet
from pyglet import gl
from pyglet.graphics import OrderedGroup

from .fogofwar import FogOfWar
from .util import TextureGroup, TranslateGroup

from engine.map import NUM_TILES, VERTEX_SZ, SECTOR_SZ

TEX_SZ = 1 / 8.0 # the size of each tile in tex units


class SectorRenderer(object):
    def __init__(self, mapren, sector):
        self.mapren = mapren
        self.sector = sector

        self.sector.onfogupdated.add(self.updatefog)

        self.batch = pyglet.graphics.Batch()

        fname = self.sector.tiles
        if fname is None:
            tiles = [0] * NUM_TILES * NUM_TILES
        else:
            res = self.mapren.datasrc.getresource(fname)
            with open(res) as fp:
                tilesstr = binascii.unhexlify(fp.read().replace('\n', ''))
                tiles = array.array('B')
                tiles.fromstring(tilesstr)

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
        
        self.terrain_group = TranslateGroup(
            0,
            0,
            parent=self.mapren.tileset_group
        )

        self.terrain_vb = self.batch.add(NUM_TILES * NUM_TILES * 3 * 2,
            gl.GL_TRIANGLES, self.terrain_group, 'v2f', 't2f')

        self.terrain_vb.vertices = vdata
        self.terrain_vb.tex_coords = tdata

        self.fog1_group = TranslateGroup(
            0,
            0,
            parent=TextureGroup(self.mapren.fogofwar.tex, parent=OrderedGroup(3))
        )
        self.fog1_vb = self.batch.add(NUM_TILES * NUM_TILES * 3 * 2,
            gl.GL_TRIANGLES, self.fog1_group, 'v2f', 't2f')

        self.fog1_vb.vertices = vdata

        self.fog2_group = TranslateGroup(
            0,
            0,
            parent=TextureGroup(self.mapren.fogofwar.tex, parent=OrderedGroup(2))
        )
        self.fog2_vb = self.batch.add(NUM_TILES * NUM_TILES * 3 * 2,
            gl.GL_TRIANGLES, self.fog2_group, 'v2f', 't2f')

        self.fog2_vb.vertices = vdata

    def rendersetup(self, dx, dy):
        self.terrain_group.x = dx * SECTOR_SZ
        self.terrain_group.y = dy * SECTOR_SZ
        self.fog1_group.x = dx * SECTOR_SZ
        self.fog1_group.y = dy * SECTOR_SZ
        self.fog2_group.x = dx * SECTOR_SZ
        self.fog2_group.y = dy * SECTOR_SZ

    def updatefog(self):
        start = time.time()
        tidmask = self.mapren.tidmask
        sec = self.sector
        visible = sec.visible
        visited = sec.visited

        fdata1 = array.array('f') # fog data
        fdata2 = array.array('f') # fog data

        gettile = self.mapren.fogofwar.gettile

        # loop over the map and assign texture coords to create the
        # fog texture
        for y in xrange(NUM_TILES):
            for x in xrange(NUM_TILES):
                a = visible[ x      +  y     *NUM_TILES] & tidmask != 0
                b = visible[(x + 1) +  y     *NUM_TILES] & tidmask != 0
                c = visible[ x      + (y + 1)*NUM_TILES] & tidmask != 0
                d = visible[(x + 1) + (y + 1)*NUM_TILES] & tidmask != 0

                e = visited[ x      +  y     *NUM_TILES] & tidmask != 0
                f = visited[(x + 1) +  y     *NUM_TILES] & tidmask != 0
                g = visited[ x      + (y + 1)*NUM_TILES] & tidmask != 0
                h = visited[(x + 1) + (y + 1)*NUM_TILES] & tidmask != 0

                ty, tx = gettile(a, b, c, d)
                tx = tx * TEX_SZ
                ty = 1 - (ty + 2) * TEX_SZ
                fdata1.extend([
                    tx, ty,
                    tx + TEX_SZ, ty - TEX_SZ,
                    tx, ty - TEX_SZ,
                    tx, ty,
                    tx + TEX_SZ, ty,
                    tx + TEX_SZ, ty - TEX_SZ
                ])

                ty, tx = gettile(e, f, g, h)
                tx = tx * TEX_SZ
                ty = 1 - ty * TEX_SZ
                fdata2.extend([
                    tx, ty,
                    tx + TEX_SZ, ty - TEX_SZ,
                    tx, ty - TEX_SZ,
                    tx, ty,
                    tx + TEX_SZ, ty,
                    tx + TEX_SZ, ty - TEX_SZ
                ])

        #print 'updated fog renderer data, took %fs' % (time.time() - start)
        start = time.time()

        self.fog1_vb.tex_coords = fdata1
        self.fog2_vb.tex_coords = fdata2

        #print 'updated fog renderer gl, took %fs' % (time.time() - start)


class MapRenderer(object):
    def __init__(self, datasrc, map, tidmask):
        self.datasrc = datasrc
        self.map = map
        self.tidmask = tidmask

        self.loadtileset()

        self.fogofwar = FogOfWar(datasrc)

        self.looksector = None # the sector being looked at
        self.renderers = {}
        self.activerenderers = []

    def loadtileset(self):
        data = self.datasrc.gettileset()
        res = self.datasrc.getresource(data['texture'])
        img = pyglet.image.load(res)

        self.tileset_group = TextureGroup(img.get_texture(), parent=OrderedGroup(1))

    def setupsector(self, sector, dx, dy):
        try:
            sr = self.renderers[sector.sx, sector.sy]
        except KeyError:
            sr = SectorRenderer(self, sector)
            self.renderers[sector.sx, sector.sy] = sr
            sr.updatefog()

        sr.rendersetup(dx, dy)
        self.activerenderers.append(sr)
            
    def lookat(self, sector):
        print 'lookat ', sector.sx, sector.sy

        del self.activerenderers[:]
        
        self.looksector = sector

        print sector.neighbour
        self.setupsector(sector, 0, 0)
        for (dx, dy), sec in sector.neighbour.items():
            if sec:
                self.setupsector(sec, dx, dy)

    def draw(self):
        for sr in self.activerenderers:
            sr.batch.draw()

