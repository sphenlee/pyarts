'''
Game Screen renders all of the parts of the main game
UI - the map, ability buttons, status bar, towns bar and minimap
'''

import pyglet
from pyglet import gl
from pyglet.window import key, mouse

from .screen import Screen
from engine.datasource import DataSource
from engine.game import Game
from .modes import *

class GameScreen(Screen):
    def pre_activate(self):
        mapfile = 'maps/test/map.json'
        self.datasrc = DataSource(mapfile, mapfile, mapfile)
        self.game = Game(self.datasrc)
        self.game.load()

        self.modes = []
        self.push_mode(NormalMode(self.game))

        self.click = None
        self.dragbox = None

        pyglet.clock.schedule(self.update, 0.1)

    def update(self, dt, *args):
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

    def on_mouse_press(self, x, y, button, mod):
        if button & mouse.RIGHT:
            add = bool(mod & key.MOD_SHIFT)
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

            if self.dragbox is not None:
                # dragged
                x1, y1 = self.click
                x2, y2 = self.dragbox
                ents = self.entities_in_rect(x1, y1, x2, y2)
            else:
                # no drag, just click
                ents = self.entities_at_point(x, y)
            
            if ents:
                self.mode.left_click_ents(ents, add)
            else:
                self.mode.left_click_pos(x, y, add)
            
            self.click = None
            self.dragbox = None

    def on_draw(self):
        self.window.clear()
        self.game.render()

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

