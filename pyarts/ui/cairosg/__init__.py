'''
Cairo Scene Graph
'''

import pyglet
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

# __________________________________________________

class Node(object):
    def __init__(self):
        pass

    def render(self, ctx, w, h):
        pass


class Canvas(Node):
    def __init__(self):
        super(Canvas, self).__init__()
        self.children = []

    def append(self, node):
        self.children.append(node)
        node.parent = self
        
    def render(self, ctx, w, h):
        with ctx:
            ctx.rectangle(0, 0, w, h)
            ctx.clip()

            for c in self.children:
                c.render(ctx, w, h)

class Grid(Canvas):
    def __init__(self, rows, cols):
        super(Grid, self).__init__()
        self.rows = rows
        self.cols = cols

    def render(self, ctx, w, h):
        ew = w / self.cols
        eh = h / self.rows

        for idx, child in enumerate(self.children):
            y, x = divmod(idx, self.cols)

            with ctx:
                ctx.translate(x * ew, y * eh)
                ctx.rectangle(0, 0, ew, eh)
                ctx.clip()
                child.render(ctx, ew, eh)


class Paintable(Node):
    def __init__(self):
        super(Paintable, self).__init__()
        self._paint = None

    def paint(self, *args):
        if len(args) == 1:
            self._paint = args[0]
        else:
            self._paint = ColourPaint(*args)
        return self

    def apply_paint(self, ctx):
        if self._paint:
            self._paint.apply(ctx)


class Text(Paintable):
    def __init__(self, text, size=16, origin=(0, 0)):
        super(Text, self).__init__()
        self.text = text
        self.origin = origin
        self.size = size

    def render(self, ctx, w, h):
        self.apply_paint(ctx)
        ctx.new_path()
        ctx.move_to(self.origin[0], h - self.origin[1])
        ctx.set_font_size(self.size)
        ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
        ctx.show_text(self.text)


class Rect(Paintable):
    def __init__(self, x=None, y=None, w=None, h=None):
        super(Rect, self).__init__()
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.w = w if w is not None else 0
        self.h = h if h is not None else 0

    def render(self, ctx, w, h):
        ew = self.w if self.w > 0 else self.w + w - self.x
        eh = self.h if self.h > 0 else self.h + h - self.y

        with ctx:
            ctx.translate(self.x, self.y)
            ctx.scale(ew, eh)
            self.apply_paint(ctx)
            ctx.rectangle(0, 0, 1, 1)
            ctx.fill()

# __________________________________________________

class SceneGraph(Canvas, Paintable):
    def __init__(self, w, h):
        super(SceneGraph, self).__init__()
        self.w = w
        self.h = h
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.ctx = cairo.Context(self.surf)
        self.ctx.scale(1, -1)
        self.ctx.translate(0, -h)

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

if __name__ == '__main__':
    c = Canvas()

    r = Rect(50, 50, 300, 300)
    
    r.paint = ColourPaint(0, 0, 1)
    r.paint = ImagePaint('maps/test/res/sunlight.png')

    t1 = Text('Hello Cairo!', origin=(10, 10))
    t2 = Text('It works!')
    
    g = Grid(2, 1)
    yellow = ColourPaint(1, 1, 0)
    t1.paint = yellow
    t2.paint = yellow

    c.append(r)
    g.append(t1)
    g.append(t2)
    c.append(g)

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 1000)
    ctx = cairo.Context(surf)
    c.render(ctx, 1000, 1000)
    surf.write_to_png('image.png')
