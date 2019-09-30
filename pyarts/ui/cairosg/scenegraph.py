'''
Cairo Scene Graph

The root object - creates the cairo objects and then
renders the graph
'''

import pyglet
import cairocffi as cairo

from .nodes import Canvas, Paintable

class SceneGraph(Canvas, Paintable):
    def __init__(self, w, h):
        super(SceneGraph, self).__init__()
        self.idmap = {}
        self.nodemap = {}
        self.w = int(w)
        self.h = int(h)
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.w, self.h)
        self.ctx = cairo.Context(self.surf)
        self.ctx.scale(1, -1)
        self.ctx.translate(0, -h)
        self.dirty = True
        self.img = None

    def __getitem__(self, key):
        return self.idmap[key]

    def mark_dirty(self):
        self.dirty = True

    repaint = mark_dirty # better name

    def layout(self):
        super(SceneGraph, self).layout(self.w, self.h)    

    def hittest(self, x, y):
        node = super(SceneGraph, self).hittest(x, y)
        return self.nodemap.get(node)

    def getimage(self):
        if not self.dirty:
            return self.img

        self.layout()

        with self.ctx:
            self.ctx.set_operator(cairo.OPERATOR_SOURCE)
            self.apply_paint(self.ctx)
            self.ctx.paint()

        with self.ctx:
            self.render(self.ctx)

        data = self.surf.get_data()
        self.img = pyglet.image.ImageData(self.w, self.h, 'BGRA', bytes(data))
        self.dirty = False
        return self.img

    def drawat(self, x, y):
        img = self.getimage()
        s = pyglet.sprite.Sprite(img, x=x, y=y)
        s.draw()
