'''
A radial menu
'''

import ui.cairotex
import ui.cairodl

import pyglet
from pyglet import gl

import math

class Radial(object):
    width  = 256
    height = 256

    def __init__(self, opts):
        self.texs = []

        self.pies = len(opts) - 1
        for i, opt in enumerate(opts):
            tex = self.renderpie(i, opt[1])
            self.texs.append(tex)

    def renderpie(self, i, cdl):
        img = ui.cairotex.CairoImage(self.width, self.height)

        self.offs = 2 * math.pi / (self.pies * 2)

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
            img.render(open(cdl))

        return img.get_texture()

    window = None

    def activate(self, window, x, y):
        self.x = x
        self.y = y
        self.pie = 0
        if self.window:
            raise RuntimeError('Activated the same radial twice!')
        self.window = window
        self.window.push_handlers(self)

    def on_draw(self):
        self.window.clear()
        for i, tex in enumerate(self.texs):
            if i == self.pie:
                gl.glColor4f(1, 1, 0, 0.9)
            else:
                gl.glColor4f(1, 1, 1, 0.9)
            tex.blit(self.x - self.width/2, self.y - self.height/2)

    def on_mouse_drag(self, x, y, mdx, mdy, button, modifiers):
        dx = x - self.x
        dy = y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 32:
            self.pie = 0
        else:
            phi = math.atan2(dy, dx) - self.offs
            pie = phi / (2.0 * math.pi) * self.pies
            if pie < 0:
                self.pie = self.pies + int(pie)
            else:
                self.pie = int(pie) + 1

    def on_mouse_release(self, x, y, button, modifiers):
        window = self.window
        self.window = None
        window.pop_handlers()

if __name__ == '__main__':
    window = pyglet.window.Window(fullscreen=True)

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    r = Radial([
        ('Attack', 'res/ui/arrow-attack.cdl'),
        ('Attack', 'res/ui/arrow-attack.cdl'),
        ('Attack', 'res/ui/arrow-attack.cdl'),
        ('Attack', 'res/ui/arrow-attack.cdl'),
        ('Attack', 'res/ui/arrow-attack.cdl'),
        ('Attack', 'res/ui/arrow-attack.cdl'),
    ])

    @window.event
    def on_draw():
        pass

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        r.activate(window, x, y)

    pyglet.app.run()
