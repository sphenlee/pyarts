'''
Map

Holds the state of the terrain and fog-of-war
'''

import pyglet
from pyglet import gl

import array
import struct

class Sector(object):
    def __init__(self):
        self.terrain = pyglet.image.load('maps/test/grass.png').get_texture()

    class Group(pyglet.graphics.Group):
        def __init__(self, tex):
            super(Sector.Group, self).__init__()
            self.tex = tex

        def set_state(self):
            gl.glEnable(self.tex.target)
            gl.glBindTexture(self.tex.target, self.tex.id)

        def unset_state(self):
            gl.glDisable(self.tex.target)

    def rendersetup(self, batch):
        with open('maps/test/node.obj.raw') as fp:
            data = fp.read()

        s = struct.Struct('I')
        n, = s.unpack(data[0:4])

        vdata = array.array('f')
        vdata.fromstring(data[4:4+(n*4)])

        tdata = array.array('f')
        tdata.fromstring(data[4+(n*4):])

        group = self.Group(self.terrain)
        self.vb = batch.add(n/2, gl.GL_TRIANGLES, group, 'v2f', 't2f')

        self.vb.vertices = vdata
        self.vb.tex_coords = tdata

class Map(object):
    def __init__(self):
        self.sectors = { }

        self.batch = pyglet.graphics.Batch()

        s = Sector()
        s.rendersetup(self.batch)
        self.sectors['0'] = s

    def render(self):
        self.batch.draw()

