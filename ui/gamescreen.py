'''
Game Screen renders all of the parts of the main game
UI - the map, ability buttons, status bar, towns bar and minimap
'''

import pyglet
from pyglet import gl
from pyglet.window import key

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
        self.push_mode(NormalMode())

        self.click = None
        self.dragbox = None

    def push_mode(self, mode):
        self.modes.append(mode)

    def on_mouse_press(self, x, y, button, mod):
        self.click = (x, y)

    def on_mouse_drag(self, x, y, dx, dy, button, mod):
        self.dragbox = (x, y)

    def on_mouse_release(self, x, y, button, mod):
        add = False
        if mod & key.MOD_SHIFT:
            add = True

        if self.dragbox is None:
            self.game.selectpoint(*self.click, add=add)
        else:
            self.game.selectrect(self.click[0], self.click[1],
                self.dragbox[0], self.dragbox[1],
                add=add)

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

