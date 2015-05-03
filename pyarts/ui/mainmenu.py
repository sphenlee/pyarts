'''
Main Menu
'''

import pyglet
from pyglet.window import key

from .screen import Screen
from ..engine.datasource import DataSource
from ..engine.datasink import DataSink

from pyarts.container import construct

mapfile = 'maps/test/map.json'
savefile = 'maps/test/map_save.json'

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
            self.gs = construct('gamescreen')
            self.gs.load(mapfile, mapfile, mapfile, localpid=0)
            self.gs.activate(parent=self)

        elif symbol == key.F5:
            print '*********** saving game'
            sink = DataSink(savefile)
            self.gs.save(sink)
            sink.commit()
            self.gs.pause()

            print '************* loading new game'
            self.gs = construct('gamescreen')
            self.gs.load(savefile, mapfile, mapfile, localpid=0)
            self.gs.activate(parent=self)

        elif symbol == key.Q:
            pyglet.app.exit()
