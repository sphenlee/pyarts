'''
A texture based on a cairo context
'''

import pyglet
import cairo
from . import cairodl

class CairoImage(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surf)

    def get_texture(self):
        data = self.surf.get_data()
        return pyglet.image.ImageData(self.width, self.height, 'RGBA', str(data))

    def render(self, stream):
        dl = cairodl.CairoDL(self.ctx)
        dl.render(stream)
