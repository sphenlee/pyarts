'''
Game Screen renders all of the parts of the main game
UI - the map, ability buttons, status bar, towns bar and minimap
'''

from .screen import Screen
from engine.datasource import DataSource
from engine.game import Game

class GameScreen(Screen):
    def on_activate(self):
        mapfile = 'maps/test/map.json'
        self.datasrc = DataSource(mapfile, mapfile, mapfile)
        self.game = Game(self.datasrc)
        self.game.load()

    def on_draw(self):
        self.window.clear()
        self.game.render()
        return True
