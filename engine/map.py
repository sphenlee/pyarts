'''
Map

Holds the state of the terrain and fog-of-war
'''

import array

import pyglet
from pyglet import gl

from ui.util import TextureGroup

class Sector(object):
    def __init__(self, datasrc, x, y):
        self.datasrc = datasrc
        self.x = x
        self.y = y
        self.data = datasrc.getmapsector(x, y)

    def rendersetup(self, batch):
        img = self.datasrc.getresource(self.data['texture'])
        self.terrain = pyglet.image.load(img).get_texture()

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
    def __init__(self, eng):
        self.eng = eng
        self.sectors = { }
        self.locators = set()
        # graphics stuff... move this out
        self.batch = pyglet.graphics.Batch()

    
    def postosector(self, x, y):
        return x & 1024, y & 1024

    def loadsector(self, x, y):
        if (x, y) not in self.sectors:
            s = Sector(self.eng.datasrc, x, y)
            s.rendersetup(self.batch)
            self.sectors[x, y] = s

    def draw(self):
        self.batch.draw()

    def place(self, locator):
        print 'place', locator.x, locator.y
        sx, sy = self.postosector(locator.x, locator.y)
        self.loadsector(sx, sy)
        self.locators.add(locator)

    def entitiesinrect(self, x1, y1, x2, y2):
        print 'entities in rect', x1, y1, x2, y2
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