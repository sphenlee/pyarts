'''
Camera

How the user looks at the game world
'''

from pyglet import gl

class Camera(object):
    def __init__(self):
        self.lookx = 0.0
        self.looky = 0.0

    def unproject(self, pos):
        return (pos[0] - self.lookx, pos[1] - self.looky)

    def setup(self):
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(self.lookx, self.looky, 0)

    def move(self, dx, dy):
        self.lookx += dx
        self.looky += dy
