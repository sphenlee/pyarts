'''
UI Utils
'''

import pyglet
from pyglet import gl

class TextureGroup(pyglet.graphics.Group):
    def __init__(self, tex):
        super(TextureGroup, self).__init__()
        self.tex = tex

    def set_state(self):
        gl.glColor4f(1, 1, 1, 1)
        gl.glEnable(self.tex.target)
        gl.glBindTexture(self.tex.target, self.tex.id)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_BLEND)
        #gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

    def unset_state(self):
        gl.glDisable(self.tex.target)

class TranslateGroup(pyglet.graphics.Group):
    def __init__(self, x, y, parent=None):
        super(TranslateGroup, self).__init__(parent=parent)
        self.x = x
        self.y = y

    def set_state(self):
        gl.glPushMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glTranslatef(self.x, self.y, 0)

    def unset_state(self):
        gl.glPopMatrix()
