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
        #gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)

    def unset_state(self):
        gl.glDisable(self.tex.target)
