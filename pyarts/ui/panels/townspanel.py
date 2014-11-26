'''
TownsPanel

Shows towns and resource info
'''

import pyglet
from pyglet import gl

from ..screen import Screen

class TownsPanel(object):
    WIDTH = Screen.WIDTH // 4
    HEIGHT = 128

    def __init__(self, datasrc):
        self.datasrc = datasrc

        self.batch = pyglet.graphics.Batch()
        self.towns = []

        self.images = {}
        
    def getimage(self, fname):
        try:
            return self.images[fname]
        except KeyError:
            res = self.datasrc.getresource(fname)
            img = pyglet.image.load(res)
            self.images[fname] = img
            return img

    def townadded(self, town):
        print 'added town'
        resource = self.getimage(town.race['resource_icon'])
        portrait = pyglet.sprite.Sprite(img, 100, 100, batch=self.batch)
        self.towns.append(portrait)

        
    def draw(self):
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_BLEND)
        
        gl.glPushMatrix()
        gl.glTranslatef(self.WIDTH*3, 0, 0)
        gl.glColor4f(0, 0, 0, 0.8)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(0, 0)
        gl.glVertex2f(0, self.HEIGHT)
        gl.glVertex2f(self.WIDTH, self.HEIGHT)
        gl.glVertex2f(self.WIDTH, 0)
        gl.glEnd()
        gl.glPopMatrix()

        self.batch.draw()

