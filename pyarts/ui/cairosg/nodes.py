'''
Cairo Scene Graph

Nodes are the actual bits that get rendered
'''

import cairocffi as cairo

from .paint import ColourPaint

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


class FlexBox(Canvas):
    def __init__(self, flex):
        super(FlexBox, self).__init__()
        total = sum(flex)
        self.flex = [float(f) / total for f in flex]


    def distribute(self, d):
        return [d * f for f in self.flex]

class HBox(FlexBox):
    def render(self, ctx, w, h):
        widths = self.distribute(w)

        with ctx:
            for x, child in zip(widths, self.children):
                with ctx:
                    ctx.rectangle(0, 0, x, h)
                    ctx.clip()
                    child.render(ctx, x, h)
                ctx.translate(x, 0)


class VBox(FlexBox):
    def render(self, ctx, w, h):
        heights = self.distribute(h)

        with ctx:
            for y, child in zip(heights, self.children):
                with ctx:
                    ctx.rectangle(0, 0, w, y)
                    ctx.clip()
                    child.render(ctx, w, y)
                ctx.translate(0, y)


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
            s = min(ew, eh)
            ctx.scale(s, s)
            self.apply_paint(ctx)
            ctx.rectangle(0, 0, 1, 1)
            ctx.fill()