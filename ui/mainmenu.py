'''
Main Menu
'''

import pyglet
from pyglet.window import key

from .screen import Screen
from .gamescreen import GameScreen

class MainMenu(Screen):
    '''
    The main menu
    '''

    def pre_activate(self):
        self.label = pyglet.text.Label('Press "S" to start',
            font_size=36,
            x=100, y=100)

    def on_draw(self):
        self.window.clear()
        self.label.draw()

    def on_key_press(self, symbol, mod):
        if symbol == key.S:
            gs = GameScreen(self)
            gs.activate()
        elif symbol == key.Q:
            pyglet.app.exit()
