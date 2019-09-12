'''
Cairo display lists

A compact vector image format designed to work with cairo
and based somewhat on PostScript
'''

import cairo

class CairoDLError(Exception):
    pass

class CairoDL(object):
    def __init__(self, ctx):
        self.ctx = ctx

    def render(self, stream):
        for line in stream:
            toks = line.split()
            if not toks:
                continue
            try:
                func = getattr(self, 'do_' + toks[0])
            except AttributeError:
                raise CairoDLError('Unknown operator ' + toks[0])

            func(*toks[1:])

    def do_rgb(self, r, g, b):
        self.ctx.set_source_rgb(float(r), float(g), float(b))

    def do_t(self, x, y):
        self.ctx.translate(float(x), float(y))

    def do_s(self, sx, sy):
        self.ctx.scale(float(sx), float(sy))

    def do_m(self, x, y):
        self.ctx.rel_move_to(float(x), float(y))

    def do_M(self, x, y):
        self.ctx.move_to(float(x), float(y))

    def do_l(self, x, y):
        self.ctx.rel_line_to(float(x), float(y))

    def do_L(self, x, y):
        self.ctx.line_to(float(x), float(y))

    def do_c(self, *args):
        assert len(args) == 6
        self.ctx.rel_curve_to(*list(map(float, args)))

    def do_C(self, *args):
        assert len(args) == 6
        self.ctx.curve_to(*list(map(float, args)))

    def do_z(self):
        self.ctx.close_path()

    def do_f(self):
        self.ctx.fill()

    def do_k(self):
        self.ctx.stroke()
