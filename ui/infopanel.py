'''
InfoPanel
'''

from pyglet import gl

from .panels.singleentitypanel import SingleEntityPanel
from .screen import Screen

class InfoPanel(object):
    WIDTH = Screen.WIDTH / 2
    HEIGHT = Screen.HEIGHT / 4

    def __init__(self, game):
        self.game = game
        self.game.onselectionchange.add(self.update)

        self.display = None

    def update(self):
        if len(self.game.selection) == 1:
            self.display = SingleEntityPanel(self.game)
        #elif len(self.game.selection) > 1:
        #    self.display = MultiEntityPanel(self.game)
        else:
            self.display = None

    def draw(self):
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_BLEND)
        
        gl.glColor4f(0, 0, 0, 0.5)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(0, 0)
        gl.glVertex2f(0, self.HEIGHT)
        gl.glVertex2f(self.WIDTH, self.HEIGHT)
        gl.glVertex2f(self.WIDTH, 0)
        gl.glEnd()

        if self.display:
            self.display.draw()
