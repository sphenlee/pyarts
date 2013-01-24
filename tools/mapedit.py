'''
Map editor
'''

import pyglet
import array
import math

import ui.radial

def dist(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx*dx + dy*dy)

class Map(object):
    def __init__(self):
        self.n = 0      # number of verts
        self.c = 1024   # capacity of vert buffer
        self.vb = pyglet.graphics.vertex_list_indexed(self.c, [0], 'v2f', 'c3B')

        self.indices = array.array('I')

    def draw(self):
        self.vb.draw(pyglet.gl.GL_TRIANGLES)

    def addvert(self, x, y):
        if self.n == self.c:
            self.c *= 2
            self.vb.resize(self.c, len(self.indices))

        self.vb.vertices[self.n*2:(self.n+1)*2] = [x, y]
        self.setcolor(self.n, 0xff, 0xff, 0xff)
        self.n += 1
        return self.n - 1

    def addface(self, a, b, c):
        self.indices.append(a)
        self.indices.append(b)
        self.indices.append(c)
        self.vb.resize(self.c, len(self.indices))
        self.vb.indices = self.indices

    def setcolor(self, i, r, g, b):
        self.vb.colors[i*3:(i+1)*3] = [r, g, b]

    def vertat(self, x, y):
        for i in xrange(self.n):
            px, py = self.vb.vertices[i*2], self.vb.vertices[i*2+1]
            if dist(x, y, px, py) < 20:
                return i

class CreateMode(object):
    def __init__(self, map):
        self.map = map
        self.tri = []
        self.hover = None

    def on_mouse_press(self, x, y, button, modifiers):
        if not (button & pyglet.window.mouse.LEFT):
            return

        i = self.map.vertat(x, y)
        if i is None:
            i = self.map.addvert(x, y)

        self.map.setcolor(i, 0xff, 0x7f, 0x00)
        self.hover = None
        self.tri.append(i)

        if len(self.tri) == 3:
            self.map.addface(*self.tri)
            for i in self.tri:
                self.map.setcolor(i, 0xff, 0xff, 0xff)
            self.tri = []

    def on_mouse_motion(self, x, y, dx, dy):
        i = self.map.vertat(x, y)
        if self.hover is not None:
            if self.hover in self.tri:
                self.map.setcolor(self.hover, 0xff, 0x7f, 0x00)
            else:
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

