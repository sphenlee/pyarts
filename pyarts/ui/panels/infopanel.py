'''
InfoPanel
'''

import pyglet
from pyglet import gl

from .singleentitypanel import SingleEntityPanel
from .multientitypanel import MultiEntityPanel
from ..screen import Screen

from pyarts.container import component

@component
class InfoPanel(object):
    depends = ['imagecache', 'game']

    WIDTH = Screen.WIDTH / 2
    HEIGHT = Screen.HEIGHT / 4

    def __init__(self):
        self.display = None

    def inject(self, imagecache, game):
        self.game = game
        self.imagecache = imagecache

        self.game.onselectionchange.add(self.update)

    def step(self):
        if self.display:
            self.display.step()

    def update(self):
        if len(self.game.selection) == 1:
            self.display = SingleEntityPanel(self)
        elif len(self.game.selection) > 1:
            self.display = MultiEntityPanel(self)
        else:
            self.display = None

    def draw(self):
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_BLEND)
        
        #gl.glColor4f(0, 0, 0, 0.8)
        #gl.glBegin(gl.GL_QUADS)
        #gl.glVertex2f(0, 0)
        #gl.glVertex2f(0, self.HEIGHT)
        #gl.glVertex2f(self.WIDTH, self.HEIGHT)
        #gl.glVertex2f(self.WIDTH, 0)
        #gl.glEnd()

        if self.display:
            self.display.draw()
