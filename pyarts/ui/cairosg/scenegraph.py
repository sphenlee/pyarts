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
        self.w = w
        self.h = h
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.ctx = cairo.Context(self.surf)
        self.ctx.scale(1, -1)
        self.ctx.translate(0, -h)

    def __getitem__(self, key):
        return self.idmap[key]

    def getimage(self):
        with self.ctx:
            self.ctx.set_operator(cairo.OPERATOR_SOURCE)
            self.apply_paint(self.ctx)
            self.ctx.paint()

        with self.ctx:
            self.render(self.ctx, self.w, self.h)

        data = self.surf.get_data()
        return pyglet.image.ImageData(self.w, self.h, 'BGRA', str(data))

    def drawat(self, x, y):
        img = self.getimage()
        s = pyglet.sprite.Sprite(img, x=x, y=y)
        s.draw()
