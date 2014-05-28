'''
Map

Holds the state of the terrain and fog-of-war
'''

import array

import pyglet
from pyglet import gl

from ui.util import TextureGroup

class Sector(object):
    def __init__(self):
        self.terrain = pyglet.image.load('maps/test/grass.png').get_texture()

    def rendersetup(self, batch):
        vdata = array.array('f')
        tdata = array.array('f')
        
        for x in xrange(256):
            for y in xrange(256):
                vdata.extend([
                    x, y,
                    x + 1, y + 1,
                    x, y + 1,
                    x, y,
                    x + 1, y,
                    x + 1, y + 1
                ])
                tdata.extend([
                    0, 0,
                    1, 1,
                    0, 1,
                    0, 0,
                    1, 0,
                    1, 1
                ])

        group = TextureGroup(self.terrain)
        self.vb = batch.add(256 * 256 * 3 * 2, gl.GL_TRIANGLES, group, 'v2f', 't2f')

        self.vb.vertices = vdata
        self.vb.tex_coords = tdata

class Map(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc

        self.batch = pyglet.graphics.Batch()

        self.sectors = { }
        

    def loadsector(self, x, y):
        data = self.datasrc.getmapsector(x, y)

        s = Sector(data)
        s.rendersetup(self.batch)
        self.sectors[0, 0] = s

    def draw(self):
        self.batch.draw()

