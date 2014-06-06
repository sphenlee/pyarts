'''
Renderer - manages graphical state of
the game
'''

import pyglet

class Sprite(object):
    def __init__(self, sprite):
        self.sprite = sprite

    def setpos(self, x, y):
        self.sprite.x = x
        self.sprite.y = y


class Renderer(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc
        self.batch = pyglet.graphics.Batch()
        self.sprites = set()

    def new_sprite(self, imgfile):
        res = self.datasrc.getresource(imgfile)
        img = pyglet.image.load(res)
        gl = pyglet.sprite.Sprite(img, batch=self.batch)
        s = Sprite(gl)
        self.sprites.add(s)
        return s

    def draw(self):
        self.batch.draw()
