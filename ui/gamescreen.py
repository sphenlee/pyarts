'''
Game Screen renders all of the parts of the main game
UI - the map, ability buttons, status bar, towns bar and minimap
'''

import pyglet
from pyglet import gl
from pyglet.window import key, mouse

from .screen import Screen
from .infopanel import InfoPanel
from engine.datasource import DataSource
from engine.datasink import DataSink
from engine.game import Game
from .modes import *

class GameScreen(Screen):
    def pre_activate(self):
        mapfile = 'maps/test/map.json'
        savefile = 'maps/test/map_save.json'
        #savefile = mapfile
        self.datasrc = DataSource(savefile, mapfile, mapfile)
        self.game = Game(self.datasrc)
        self.game.load()

        self.modes = []
        self.push_mode(NormalMode(self.game))

        self.click = None
        self.dragbox = None
        self.dx = 0
        self.dy = 0

        self.infopanel = InfoPanel(self.game)

        pyglet.clock.schedule(self.update, 0.1)

    def update(self, dt, *args):
        self.game.camera.move(self.dx, self.dy)
        self.game.step()

    @property
    def mode(self):
        return self.modes[-1]

    def push_mode(self, mode):
        self.modes.append(mode)

    def pop_mode(self, mode):
        self.modes.pop()

    def entities_at_point(self, x, y):
        return self.game.engine.map.entities_in_rect(x - 16, y - 16, x + 16, y + 16)

    def entities_in_rect(self, x1, y1, x2, y2):
        return self.game.engine.map.entities_in_rect(x1, y1, x2, y2)

    def on_mouse_motion(self, x, y, dx, dy):
        if x < 10:
            self.dx = 5
        elif x > self.WIDTH - 10:
            self.dx = -5
        else:
            self.dx = 0
        if y < 10:
            self.dy = 5
        elif y > self.HEIGHT - 10:
            self.dy = -5
        else:
            self.dy = 0

    def on_mouse_press(self, x, y, button, mod):
        if button & mouse.RIGHT:
            add = bool(mod & key.MOD_SHIFT)
            x, y = self.game.camera.unproject((x, y))
            ents = self.entities_at_point(x, y)
            self.mode.right_click(x, y, ents, add)
        elif button & mouse.LEFT:
            self.click = (x, y)

    def on_mouse_drag(self, x, y, dx, dy, button, mod):
        if button & mouse.LEFT:
            self.dragbox = (x, y)

    def on_mouse_release(self, x, y, button, mod):
        if button & mouse.LEFT:
            add = bool(mod & key.MOD_SHIFT)
            x, y = self.game.camera.unproject((x, y))
            if self.dragbox is not None:
                # dragged
                x1, y1 = self.game.camera.unproject(self.click)
                x2, y2 = self.game.camera.unproject(self.dragbox)
                ents = self.entities_in_rect(x1, y1, x2, y2)
            else:
                # no drag, just click
                ents = self.entities_at_point(x, y)
                # one entity only for a single click
                if ents:
                    ents = set((next(iter(ents)),)) # eew...
            
            if ents:
                self.mode.left_click_ents(ents, add)
            else:
                self.mode.left_click_pos(x, y, add)
            
            self.click = None
            self.dragbox = None

    def on_key_press(self, symbol, mod):
        if symbol == key.S and mod & key.MOD_CTRL:
            mapfile = 'maps/test/map_save.json'
            sink = DataSink(mapfile)
            self.game.save(sink)
            sink.commit()
            return True


    def on_draw(self):
        self.window.clear()

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluOrtho2D(0, self.WIDTH, 0, self.HEIGHT)

        self.game.render()

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        self.infopanel.draw()

        if self.dragbox:
            gl.glDisable(gl.GL_TEXTURE_2D)
            
            gl.glColor4f(1, 1, 0, 1)
            gl.glBegin(gl.GL_LINE_STRIP)
            gl.glVertex2f(self.click[0],   self.click[1])
            gl.glVertex2f(self.click[0],   self.dragbox[1])
            gl.glVertex2f(self.dragbox[0], self.dragbox[1])
            gl.glVertex2f(self.dragbox[0], self.click[1])
            gl.glVertex2f(self.click[0],   self.click[1])
            gl.glEnd()

        return True

