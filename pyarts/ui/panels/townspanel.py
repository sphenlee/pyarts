'''
TownsPanel

Shows towns and resource info
'''

import pyglet
from pyglet import gl

from ..screen import Screen

class TownsPanel(object):
    def __init__(self, datasrc):
        self.WIDTH = Screen.WIDTH // 4
        self.HEIGHT = Screen.HEIGHT - 36

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

    def townadded(self, team, town):
        print 'added town', team, town
        resource = self.getimage(town.race['resource_icon'])
        icon1 = pyglet.sprite.Sprite(resource, self.WIDTH * 3, self.HEIGHT, batch=self.batch)
        icon1.scale = 1/8.0

        energy = self.getimage(town.race['energy_icon'])
        icon2 = pyglet.sprite.Sprite(energy, self.WIDTH * 3.5, self.HEIGHT, batch=self.batch)
        icon2.scale = 1/8.0

        text1 = pyglet.text.Label('', x=self.WIDTH * 3 + 36, y=self.HEIGHT, batch=self.batch)
        text2 = pyglet.text.Label('', x=self.WIDTH * 3.5 + 36, y=self.HEIGHT, batch=self.batch)

        self.towns.append((text1, text2, icon1, icon2))

        self.update_resources(town)

    def update_resources(self, town):
        self.towns[0][0].text = str(town.resources.resource)
        self.towns[0][1].text = str(town.resources.energy)

    def draw(self):
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_BLEND)
        
        gl.glColor4f(0, 0, 0, 0.8)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(self.WIDTH*3, self.HEIGHT)
        gl.glVertex2f(self.WIDTH*3, Screen.HEIGHT)
        gl.glVertex2f(self.WIDTH*4, Screen.HEIGHT)
        gl.glVertex2f(self.WIDTH*4, self.HEIGHT)
        gl.glEnd()
        
        self.batch.draw()
