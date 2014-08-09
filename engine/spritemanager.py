'''
Renderer - manages graphical state of
the game
'''

import pyglet

class Sprite(object):
    def __init__(self, sm, sprite):
        self.sm = sm
        self.sprite = sprite

    def setpos(self, x, y):
        self.sprite.x = self.sm.offx + x
        self.sprite.y = self.sm.offy + y

SPRITE_SIZE = 128

class SpriteManager(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc
        self.batch = pyglet.graphics.Batch()
        self.sprites = set()
        self.offx = 0
        self.offy = 0

    def setoffset(self, x, y):
        dx = x - self.offx
        dy = y - self.offy

        for s in self.sprites:
            s.setpos(dx, dy)

        self.offx = x
        self.offy = y

    def new_sprite(self, imgfile, r):
        res = self.datasrc.getresource(imgfile)
        img = pyglet.image.load(res)
        pygs = pyglet.sprite.Sprite(img, batch=self.batch)
        pygs.scale = float(r) / SPRITE_SIZE
        s = Sprite(self, pygs)
        self.sprites.add(s)
        return s

    def draw(self):
        self.batch.draw()
