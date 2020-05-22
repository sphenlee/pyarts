# '''
# Renderer - manages graphical state of
# the game
# '''

# from .sector import SECTOR_SZ

from pyarts.container import component
from yarts import SpriteManager
component(SpriteManager)

# class Sprite(object):
#     def __init__(self, sm, sprite, ring):
#         self.sm = sm
#         self.sprite = sprite
#         self.ring = ring

#     def setpos(self, x, y):
#         self.sprite.x = x - self.sm.offx
#         self.sprite.y = y - self.sm.offy
#         self.ring.x = x - self.sm.offx
#         self.ring.y = y - self.sm.offy

#     def offset(self, dx, dy):
#         self.sprite.x += dx
#         self.sprite.y += dy
#         self.ring.x += dx
#         self.ring.y += dy

#     def setvisible(self, mask, selected):
#         self.sprite.visible = (mask & self.sm.tidmask)
#         self.ring.visible = selected and (mask & self.sm.tidmask)

# SPRITE_SIZE = 128

# @component
# class SpriteManager(object):
#     depends = ['datasrc', 'local']

#     def __init__(self):
#         #self.batch = pyglet.graphics.Batch()
#         self.sprites = set()
#         self.offx = 0
#         self.offy = 0

#     def inject(self, datasrc, local):
#         self.datasrc = datasrc
#         self.local = local

#         #res = self.datasrc.getresource('res/selected-ring.png')
#         #self.ringimg = pyglet.image.load(res)

#     def lookat(self, sec):
#         self.setoffset(sec.sx * SECTOR_SZ, sec.sy * SECTOR_SZ)

#     def setoffset(self, x, y):
#         dx = self.offx - x
#         dy = self.offy - y

#         for s in self.sprites:
#             s.offset(dx, dy)

#         self.offx = x
#         self.offy = y

#     @property
#     def tidmask(self):
#         return self.local.player.tidmask

#     def new_sprite(self, imgfile, r):
#         pass
#         #res = self.datasrc.getresource(imgfile)
#         #img = pyglet.image.load(res)
#         #pygs = pyglet.sprite.Sprite(img, batch=self.batch)
#         #pygs.scale = float(r) / SPRITE_SIZE

#         #ring = pyglet.sprite.Sprite(self.ringimg, batch=self.batch)
#         #ring.scale = float(r) / SPRITE_SIZE
#         #ring.visible = False

#         #s = Sprite(self, pygs, ring)
#         #self.sprites.add(s)
#         #return s

#     def remove(self, sprite):
#         pass
#         #sprite.sprite.delete()
#         #sprite.ring.delete()
#         #self.sprites.remove(sprite)

#     def draw(self):
#         pass
#         #self.batch.draw()
