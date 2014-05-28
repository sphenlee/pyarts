'''
Map editor
'''

import pyglet
from pyglet import gl
import array
import struct
import sys
import sqlite3
import os
import cStringIO

import ui.radial
import buffile

def dist2(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return dx*dx + dy*dy

class Mesh(object):
    def __init__(self, fp=None):
        self.n = 0  # number of verts
        self.c = 8  # capacity of vert buffer
        self.vb = pyglet.graphics.vertex_list_indexed(self.c, [0], 'v2f', 'c3B')

        self.indices = array.array('I')

        if fp is not None:
            self.loadfrom(fp)

    def saveto(self, fp):
        fp.write(struct.pack('II', self.n, len(self.indices)))

        verts = array.array('f', self.vb.vertices)[0:self.n*2]
        fp.write(verts.tostring())
        fp.write(self.indices.tostring())

    def loadfrom(self, fp):
        self.n, i = struct.unpack('II', fp.read(8))

        while self.c < self.n:
            self.c *= 2

        verts = array.array('f')
        verts.fromstring(fp.read(self.n * 2 * verts.itemsize))

        self.indices.fromstring(fp.read(i * self.indices.itemsize))

        self.vb.resize(self.c, i)
        self.vb.vertices[0:self.n*2] = verts
        self.vb.colors[0:self.n*3] = [0xFF] * (self.n*3)
        self.vb.indices = self.indices

    def draw(self, wire=True):
        if wire:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        self.vb.draw(gl.GL_TRIANGLES)
        if wire:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

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

    def movevert(self, n, x, y):
        self.vb.vertices[n*2:(n+1)*2] = [x, y]

    def setcolor(self, i, r, g, b):
        self.vb.colors[i*3:(i+1)*3] = [r, g, b]

    def vertat(self, x, y):
        for i in xrange(self.n):
            px, py = self.vb.vertices[i*2], self.vb.vertices[i*2+1]
            if dist2(x, y, px, py) < 400:
                return i

class Mode(object):
    def __init__(self, main):
        self.main = main
        self.hover = None
        self.tri = () # FIXME
        self.wire = True
        self.mesh = main.map.look.mesh

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.main.cam.unxform(x, y)

        i = self.mesh.vertat(x, y)
        if self.hover is not None:
            if self.hover in self.tri:
                self.mesh.setcolor(self.hover, 0xff, 0x7f, 0x00)
            else:
                self.mesh.setcolor(self.hover, 0xff, 0xff, 0xff)

        self.hover = i
        if self.hover is not None:
            self.mesh.setcolor(self.hover, 0xff, 0xff, 0x00)

    def draw(self):
        self.main.map.draw(wire=self.wire)

class CreateMode(Mode):
    def __init__(self, main):
        super(CreateMode, self).__init__(main)
        self.tri = []

    def on_mouse_press(self, x, y, button, modifiers):
        if not (button & pyglet.window.mouse.LEFT):
            return

        x, y = self.main.cam.unxform(x, y)

        i = self.mesh.vertat(x, y)
        if i is None:
            i = self.mesh.addvert(x, y)

        self.mesh.setcolor(i, 0xff, 0x7f, 0x00)
        #self.hover = None # FIXME?
        self.tri.append(i)

        if len(self.tri) == 3:
            self.mesh.addface(*self.tri)
            for i in self.tri:
                self.mesh.setcolor(i, 0xff, 0xff, 0xff)
            self.tri = []

class EditMode(Mode):
    def __init__(self, main):
        super(EditMode, self).__init__(main)
        self.cur = None

    def on_mouse_press(self, x, y, b, m):
        if not (b & pyglet.window.mouse.LEFT):
            return

        x, y = self.main.cam.unxform(x, y)

        self.cur = self.mesh.vertat(x, y)
        if self.cur is not None:
            self.mesh.setcolor(self.cur, 0x00, 0xff, 0x00)

    def on_mouse_release(self, x, y, b, m):
        if not (b & pyglet.window.mouse.LEFT):
            return

        if self.cur is not None:
            self.mesh.setcolor(self.cur, 0xff, 0xff, 0xff)
            self.cur = None

    def on_mouse_drag(self, x, y, dx, dy, b, m):
        if self.cur is None:
            return

        x, y = self.main.cam.unxform(x, y)

        self.mesh.movevert(self.cur, x, y)

class Camera(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.x = 0
        self.y = 0
        self.dx = 0
        self.dy = 0
        self.s = 1.0

    def on_mouse_motion(self, x, y, dx, dy):
        if x < 10:
            self.dx = 1
        elif x > self.w - 10:
            self.dx = -1
        else:
            self.dx = 0
        if y < 10:
            self.dy = 1
        elif y > self.h - 10:
            self.dy = -1
        else:
            self.dy = 0

    def unxform(self, x, y):
        return (x - self.x) / self.s, (y - self.y) / self.s

    def on_mouse_scroll(self, x, y, sx, sy):
        x, y = self.unxform(x, y)
        s = self.s
        if sy > 0:
            self.s *= 1.1
        else:
            self.s /= 1.1
        print x, y, self.s, s, self.s/s
        print (1 - s/self.s) * x
        print (1 - s/self.s) * y
        print '...'
        self.x += (1 - self.s/s) * x
        self.y += (1 - self.s/s) * y

    def update(self, dt):
        self.x += self.dx * dt * 10
        self.y += self.dy * dt * 10

    def setup(self):
        gl.glLoadIdentity()
        gl.glTranslatef(self.x, self.y, 0)
        gl.glScalef(self.s, self.s, 0)

class Node(object):
    def __init__(self):
        pass

    def draw(self, wire):
        gl.glColor3f(1, 1, 1)
        if self.terrain is not None:
            self.terrain.blit(0, 0)
        self.mesh.draw(wire)

class Map(object):
    def __init__(self, fname):
        self.nodes = {}
        self.look = None

        if os.path.exists(fname):
            self.loadfrom(fname)
        else:
            self.new(fname)

    def loadfrom(self, fname):
        self.con = sqlite3.connect(fname)

        for row in self.con.execute('select * from map'):
            self.nodes[row[0]] = self.loadone(*row)

        self.look = self.nodes[0]

    def loadone(self, nid, terrain, ground, walk, sail, fly):
        node = Node()
        node.nid = nid
        if terrain is not None:
            node.terrain = pyglet.image.load(".png", file=buffile.Buffile(terrain))
        else:
            node.terrain = None
        node.mesh = Mesh(buffile.Buffile(ground))
        return node

    def new(self, fname):
        self.con = sqlite3.connect(fname)

        self.con.executescript(open('tools/map.sql').read())
        self.con.commit()

        self.terrain = None

    def save(self):
        for nid, node in self.nodes.iteritems():
            buf = cStringIO.StringIO()
            node.mesh.saveto(buf)
            self.con.execute('update map set ground = ? where nid = ?',
                (buffer(buf.getvalue()), nid))

    def draw(self, wire):
        for node in self.nodes.itervalues():
            node.draw(wire)

class Main(object):
    def __init__(self, fname):
        self.map = Map(fname)
        self.mode = CreateMode(self)
        self.menu = ui.radial.Radial([
            ('Save', 'res/ui/mapedit-save.cdl', self.on_save),
            ('Option2', None),
            ('Wireframe', 'res/ui/mapedit-wireframe.cdl', self.on_wireframe),
            ('Center View', 'res/ui/mapedit-center.cdl', self.on_centerview)
        ])
        self.cam = Camera(1280, 1024)

    def on_save(self):
        self.map.save()

    def on_wireframe(self):
        self.mode.wire = not self.mode.wire

    def on_centerview(self):
        self.cam.x = 0
        self.cam.y = 0
        self.cam.s = 1.0

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            if type(self.mode) is CreateMode:
                self.mode = EditMode(self)
            else:
                self.mode = CreateMode(self)

            self.window.pop_handlers()
            self.window.push_handlers(self.mode)

    def on_mouse_press(self, x, y, b, m):
        if b & pyglet.window.mouse.RIGHT:
            self.menu.activate(self.window, x, y)

    def on_draw(self):
        self.window.clear()
        self.cam.setup()
        self.mode.draw()
        if self.menu.active:
            self.menu.draw()

    def update(self, dt):
        self.cam.update(dt * 60)

    def main(self):
        self.window = pyglet.window.Window(fullscreen=True)
        self.window.push_handlers(self)
        self.window.push_handlers(self.cam)
        self.window.push_handlers(self.mode)

        pyglet.clock.schedule_interval(self.update, 1/60.0)

        with self.map.con:
            pyglet.app.run()

if __name__ == '__main__':
    m = Main(fname=sys.argv[1])
    m.main()

