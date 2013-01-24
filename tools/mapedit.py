'''
Map editor
'''

import pyglet
import array
import math

def dist(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx*dx + dy*dy)

class Map(object):
    def __init__(self):
        self.vcount = 0
        self.verts = array.array('f')
        self.colors = array.array('B')
        self.indices = array.array('I')

        self.vb = None

    def draw(self):
        if self.vb:
            self.vb.draw(pyglet.gl.GL_TRIANGLES)

    def update(self):
        if not self.vb:
            self.vb = pyglet.graphics.vertex_list_indexed(self.vcount, self.indices, 'v2f', 'c3B')
        else:
            self.vb.resize(self.vcount, len(self.indices))

        self.vb.vertices = self.verts
        self.vb.colors = self.colors
        self.vb.indices = self.indices

    def addvert(self, x, y):
        self.vcount += 1
        self.verts.append(x)
        self.verts.append(y)

        self.colors.append(0xFF)
        self.colors.append(0xFF)
        self.colors.append(0xFF)

        return self.vcount - 1

    def addface(self, a, b, c):
        self.indices.append(a)
        self.indices.append(b)
        self.indices.append(c)
        self.update()

    def setcolor(self, i, r, g, b):
        self.vb.colors[i*3:(i+1)*3] = [r, g, b]

    def vertat(self, x, y):
        for i in xrange(self.vcount):
            px, py = self.verts[i*2], self.verts[i*2+1]
            if dist(x, y, px, py) < 10:
                return i

class CreateMode(object):
    def __init__(self, map):
        self.map = map
        self.tri = []
        self.hover = None

    def on_mouse_press(self, x, y, button, modifiers):
        n = self.map.addvert(x, y)
        self.tri.append(n)
        if len(self.tri) == 3:
            self.map.addface(*self.tri)
            self.tri = []

    def on_mouse_motion(self, x, y, dx, dy):
        if self.tri:
            return

        i = self.map.vertat(x, y)
        if self.hover is not None:
            self.map.setcolor(self.hover, 0xff, 0xff, 0xff)
        self.hover = i
        if self.hover is not None:
            self.map.setcolor(self.hover, 0xff, 0xff, 0x00)

    def on_draw(self):
        self.map.draw()

class Main(object):
    def __init__(self):
        self.map = Map()
        self.mode = CreateMode(self.map)

    def main(self):
        window = pyglet.window.Window(fullscreen=False)
        window.push_handlers(self.mode)

        pyglet.app.run()

if __name__ == '__main__':
    m = Main()
    m.main()

