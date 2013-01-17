'''
Camera

How the user looks at the game world
'''

from pyglet import gl

class Camera(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h

        self.lookx = 0.0
        self.looky = 0.0

    def setup(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluOrtho2D(0, self.w, 0, self.h)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(self.lookx, self.looky, 0)
