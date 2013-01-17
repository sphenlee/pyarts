'''
Map

Holds the state of the terrain and fog-of-war
'''

import pyglet
from pyglet import gl

import array

class Sector(object):
    def __init__(self):
        self.terrain = pyglet.image.load('maps/test/grass.png')

    def rendersetup(self, batch):
        self.vb = batch.add(6, gl.GL_TRIANGLES, None, 'v2f', 'c3B')

        a = array.array('f', [
            0.0, 0.0,
            100.0, 0.0,
            100.0, 100.0,
            100.0, 100.0,
            0.0, 0.0,
            0.0, 100.0,
        ])
        self.vb.vertices = a
        self.vb.colors = [255, 0, 0] * 6

class Map(object):
    def __init__(self):
        self.sectors = { }

        self.batch = pyglet.graphics.Batch()

        s = Sector()
        s.rendersetup(self.batch)
        self.sectors['0'] = s

    def render(self):
        self.batch.draw()

