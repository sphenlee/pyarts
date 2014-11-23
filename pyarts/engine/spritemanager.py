'''
Renderer - manages graphical state of
the game
'''

import pyglet

from .sector import SECTOR_SZ

class Sprite(object):
    def __init__(self, sm, sprite):
        self.sm = sm
        self.sprite = sprite

    def setpos(self, x, y):
        self.sprite.x = x - self.sm.offx
        self.sprite.y = y - self.sm.offy

    def offset(self, dx, dy):
        self.sprite.x += dx
        self.sprite.y += dy

SPRITE_SIZE = 128

class SpriteManager(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc
        self.batch = pyglet.graphics.Batch()
        self.sprites = set()
        self.offx = 0
        self.offy = 0

    def lookat(self, sec):
        self.setoffset(sec.sx * SECTOR_SZ, sec.sy * SECTOR_SZ)

    def setoffset(self, x, y):
        dx = self.offx - x
        dy = self.offy - y

        for s in self.sprites:
            s.offset(dx, dy)

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
