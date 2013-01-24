'''
A radial menu
'''

import ui.cairotex
import ui.cairodl

import pyglet
from pyglet import gl

import math

class Radial(object):
    width  = 128
    height = 128

    def __init__(self, opts):
        self.texs = []
        self.labels = []
        self.funcs = []

        self.pies = len(opts) - 1
        for i, opt in enumerate(opts):
            tex = self.renderpie(i, opt[1])
            self.texs.append(tex)

            label = pyglet.text.Label(
                text=opt[0],
                font_size=16,
                anchor_x='center',
                anchor_y='top')
            self.labels.append(label)

            if len(opt) == 3: # FIXME
                self.funcs.append(opt[2])
            else:
                self.funcs.append(lambda: None)

    def renderpie(self, i, cdl):
        img = ui.cairotex.CairoImage(self.width, self.height)

        self.offs = -2 * math.pi / (self.pies * 2)

        if i == 0:
            img.ctx.set_source_rgb(1, 1, 1)
            img.ctx.arc(self.width/2, self.height/2,
                self.width/5 - 1,
                0, 2 * math.pi)
            img.ctx.set_source_rgba(0, 0, 0, 1)
            img.ctx.stroke_preserve()
            img.ctx.set_source_rgba(1, 1, 1, 1)
            img.ctx.fill()

            img.ctx.translate(
                self.width/2,
                self.height/2
            )
            if cdl:
                img.render(open(cdl))
        else:
            phi = 2 * math.pi / self.pies

            img.ctx.arc(self.width/2, self.height/2,
                self.width/5 + 1,
                (i - 1) * phi + self.offs,
                 i      * phi + self.offs)
            img.ctx.arc_negative(self.width/2, self.height/2,
                self.width/2 - 1,
                 i      * phi + self.offs,
                (i - 1) * phi + self.offs)
            img.ctx.close_path()
            img.ctx.set_source_rgba(0, 0, 0, 1)
            img.ctx.stroke_preserve()
            img.ctx.set_source_rgba(1, 1, 1, 1)
            img.ctx.fill()

            phi2 = (i - 0.5) * phi + self.offs
            img.ctx.translate(
                self.width/2  + self.width/3  * math.cos(phi2),
                self.height/2 + self.height/3 * math.sin(phi2)
            )
            if cdl:
                img.render(open(cdl))

        return img.get_texture()

    window = None

    @property
    def active(self):
        return self.window is not None

    def activate(self, window, x, y):
        self.x = x
        self.y = y
        self.pie = 0
        if self.window:
            raise RuntimeError('Activated the same radial twice!')
        self.window = window
        self.window.push_handlers(self)

    def draw(self):
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        for i, tex in enumerate(self.texs):
            if i == self.pie:
                label = self.labels[i]
                label.x = self.x
                label.y = self.y - self.height/2
                gl.glColor4f(1, 1, 1, 0.7)
                label.draw()

                gl.glColor4f(1, 1, 0, 0.7)
            else:
                gl.glColor4f(1, 1, 1, 0.7)
            tex.blit(self.x - self.width/2, self.y - self.height/2)

    def on_mouse_drag(self, x, y, mdx, mdy, button, modifiers):
        dx = x - self.x
        dy = y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < self.width/5:
            self.pie = 0
        else:
            phi = math.atan2(dy, dx) - self.offs
            pie = phi / (2.0 * math.pi) * self.pies
            if pie < 0:
                self.pie = self.pies + int(pie)
            else:
                self.pie = int(pie) + 1
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        window = self.window
        self.window = None
        window.pop_handlers()
        self.funcs[self.pie]()

if __name__ == '__main__':
    window = pyglet.window.Window(fullscreen=True)

    r = Radial([
        ('Attack',  'res/ui/arrow-attack.cdl'),
        ('Move',    'res/ui/arrow-move.cdl'),
        ('Guard',   'res/ui/arrow-guard.cdl'),
        ('Attack',  'res/ui/arrow-attack.cdl'),
        ('Attack',  'res/ui/arrow-attack.cdl'),
        ('Attack',  'res/ui/arrow-attack.cdl'),
        #('Attack',  'res/ui/arrow-attack.cdl'),
        #('Attack',  'res/ui/arrow-attack.cdl'),
        #('Attack',  'res/ui/arrow-attack.cdl'),
    ])

    @window.event
    def on_draw():
        window.clear()
        if r.active:
            r.draw()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        r.activate(window, x, y)

    pyglet.app.run()
