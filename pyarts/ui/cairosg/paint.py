'''
Cairo Scene Graph

Paints are used to fill nodes.
Colours and Images, and eventually gradients.
'''

import cairocffi as cairo
class Paint(object):
    pass

class ColourPaint(Paint):
    def __init__(self, r, g, b, a=1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def apply(self, ctx):
        ctx.set_source_rgba(self.r, self.g, self.b, self.a)

class ImagePaint(Paint):
    def __init__(self, fname):
        self.fname = fname
        self.patt = None

    def apply(self, ctx):
        if self.patt is None:
            img = cairo.ImageSurface.create_from_png(self.fname)
            m = cairo.Matrix()
            w = img.get_width()
            h = img.get_height()
            s = min(w, h)
            m.scale(s, s)

            self.patt = cairo.SurfacePattern(img)
            self.patt.set_matrix(m)

        ctx.set_source(self.patt)