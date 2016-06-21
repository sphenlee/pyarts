'''
InfoPanel
'''

import pyglet
from pyglet import gl

from .cairosg import ImagePaint

from .panels.singleentitypanel import SingleEntityPanel
from .panels.multientitypanel import MultiEntityPanel
from .screen import Screen

from pyarts.container import component

@component
class InfoPanel(object):
    depends = ['datasrc', 'game']

    WIDTH = Screen.WIDTH / 2
    HEIGHT = Screen.HEIGHT / 4

    def __init__(self):
        self.display = None
        self.images = {}

    def inject(self, datasrc, game):
        self.game = game
        self.datasrc = datasrc

        self.game.onselectionchange.add(self.update)

    def getimage(self, fname):
        try:
            return self.images[fname]
        except KeyError:
            res = self.datasrc.getresource(fname)
            img = ImagePaint(res)
            self.images[fname] = img
            return img

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
