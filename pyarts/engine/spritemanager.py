'''
Renderer - manages graphical state of
the game
'''

import pyglet

from .sector import SECTOR_SZ

from pyarts.container import component

class Sprite(object):
    def __init__(self, sm, sprite, ring):
        self.sm = sm
        self.sprite = sprite
        self.ring = ring

    def setpos(self, x, y):
        self.sprite.x = x - self.sm.offx
        self.sprite.y = y - self.sm.offy
        self.ring.x = x - self.sm.offx
        self.ring.y = y - self.sm.offy

    def offset(self, dx, dy):
        self.sprite.x += dx
        self.sprite.y += dy
        self.ring.x += dx
        self.ring.y += dy

SPRITE_SIZE = 128

@component
class SpriteManager(object):
    depends = ['datasrc']

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.sprites = set()
        self.offx = 0
        self.offy = 0

    def inject(self, datasrc):
        self.datasrc = datasrc

        res = self.datasrc.getresource('res/selected-ring.png')
        self.ringimg = pyglet.image.load(res)
        
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

        ring = pyglet.sprite.Sprite(self.ringimg, batch=self.batch)
        ring.scale = float(r) / SPRITE_SIZE
        ring.visible = False

        s = Sprite(self, pygs, ring)
        self.sprites.add(s)
        return s

    def remove(self, sprite):
        sprite.sprite.delete()
        sprite.ring.delete()
        self.sprites.remove(sprite)

    def draw(self):
        self.batch.draw()
