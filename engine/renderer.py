'''
Renderer - manages graphical state of
the game
'''

import pyglet

class Sprite(object):
    def __init__(self, batch):
        self.batch = batch
        self.sprite = None

    def setimage(self, img):
        self.sprite = pyglet.sprite.Sprite(img, batch=batch)

    def setpos(self, x, y):
        self.sprite.x = x
        self.sprite.y = y


class Renderer(object):
    def __init__(self):
        self.batch = pyglet.batch.Batch()
        self.sprites = set()

    def new_sprite(self):
        s = Sprite(self.batch)
        self.sprites.add(s)
        return s

    def on_draw(self):
        self.batch.draw()
