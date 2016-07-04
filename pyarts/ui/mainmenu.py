'''
Main Menu
'''

import pyglet
from pyglet.window import key

from .screen import Screen
from ..engine.datasource import DataSource
from ..engine.datasink import DataSink
from pyarts.game.settings import Settings

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
            self.root = construct('root')
            self.root.load({
                'localpid': Settings.localpid,
                'data': {
                    'core': mapfile,
                    'map': mapfile,
                    'save': mapfile
                }
            })
            self.root.gamescreen.activate(parent=self)

        elif symbol == key.F5:
            print '*********** saving game'
            sink = DataSink(savefile)
            self.root.save(sink)
            sink.commit()
            self.root.gamescreen.pause()

            print '************* loading new game'
            self.root = construct('root')
            self.root.load(savefile, mapfile)
            self.root.gamescreen.activate(parent=self)

        elif symbol == key.Q:
            pyglet.app.exit()
