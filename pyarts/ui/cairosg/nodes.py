'''
Cairo Scene Graph

Nodes are the actual bits that get rendered
'''

import cairocffi as cairo

from .paint import ColourPaint

class Node(object):
    def __init__(self):
        pass

    def layout(self, w, h):
        self.w = w
        self.h = h

    def hittest(self, x, y):
        return self

    def render(self, ctx, w, h):
        pass


class Canvas(Node):
    def __init__(self):
        super(Canvas, self).__init__()
        self.children = []

    def append(self, node):
        self.children.append(node)
        node.parent = self

    def layout(self, w, h):
        super(Canvas, self).layout(w, h)
        for c in self.children:
            c.layout(w, h)

    def hittest(self, x, y):
        if self.children:
            return self.children[-1].hittest(x, y)
        
    def render(self, ctx):
        with ctx:
            ctx.rectangle(0, 0, self.w, self.h)
            ctx.clip()

            for c in self.children:
                c.render(ctx)

class Grid(Canvas):
    def __init__(self, rows, cols):
        super(Grid, self).__init__()
        self.rows = rows
        self.cols = cols

    def layout(self, w, h):
        self.ew = w / self.cols
        self.eh = h / self.rows
        for c in self.children:
            c.layout(self.ew, self.eh)

    def hittest(self, x, y):
        r = int(x / self.ew)
        c = int(x / self.eh)
        try:
            return self.children[r * self.cols + c]
        except IndexError:
            return self

    def render(self, ctx):
        for idx, child in enumerate(self.children):
            y, x = divmod(idx, self.cols)

            with ctx:
                ctx.translate(x * self.ew, y * self.eh)
                ctx.rectangle(0, 0, self.ew, self.eh)
                ctx.clip()
                child.render(ctx)


class FlexBox(Canvas):
    def __init__(self, flex):
        super(FlexBox, self).__init__()
        total = sum(flex)
        self.flex = [float(f) / total for f in flex]

    def distribute(self, d):
        return [d * f for f in self.flex]

    def hittest(self, x, y):
        j, i = self.major_minor(x, y)
        for offs, child in zip(self.mj, self.children):
            j -= offs
            if j <= 0:
                return child
        else:
            return self

    def layout(self, w, h):
        j, i = self.major_minor(w, h)
        self.mi = i
        self.mj = self.distribute(j)

        for offs, child in zip(self.mj, self.children):
            child.layout(*self.major_minor(offs, self.mi))

    def render(self, ctx):
        with ctx:
            for offs, child in zip(self.mj, self.children):
                with ctx:
                    x, y = self.major_minor(offs, self.mi)
                    ctx.rectangle(0, 0, x, y)
                    ctx.clip()
                    child.render(ctx)
                ctx.translate(*self.major_minor(offs, 0))

class HBox(FlexBox):
    def major_minor(self, w, h):
        return w, h


class VBox(FlexBox):
    def major_minor(self, w, h):
        return h, w


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
    def __init__(self, text, size=None, origin=None):
        super(Text, self).__init__()
        self.text = text
        self.origin = origin if origin else (0, 0)
        self.size = size if size else 16

    def render(self, ctx):
        self.apply_paint(ctx)
        ctx.new_path()
        ctx.move_to(self.origin[0], self.h - self.origin[1])
        ctx.set_font_size(self.size)
        ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
        ctx.show_text(self.text)


class Rect(Paintable):
    def __init__(self, x=None, y=None, w=None, h=None):
        super(Rect, self).__init__()
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.myw = w if w is not None else 0
        self.myh = h if h is not None else 0

    def render(self, ctx):
        ew = self.myw if self.myw > 0 else self.myw + self.w - self.x
        eh = self.myh if self.myh > 0 else self.myh + self.h - self.y

        with ctx:
            ctx.translate(self.x, self.y)
            s = min(ew, eh)
            ctx.scale(s, s)
            self.apply_paint(ctx)
            ctx.rectangle(0, 0, 1, 1)
            ctx.fill()