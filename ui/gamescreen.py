'''
Game Screen renders all of the parts of the main game
UI - the map, ability buttons, status bar, towns bar and minimap
'''

from .screen import Screen

class GameScreen(Screen):
    def __init__(self, game):
        super(GameScreen, self).__init__()
        self.game = game

    def on_draw(self):
        game.render()
