'''
Game

The game represents the entire state of a game.
It holds the local player specific information as well
as the engine.
'''

from .engine import Engine
from .camera import Camera

class Game(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc
        self.engine = Engine(datasrc)
        self.camera = Camera(800, 600)

    def render(self):
        self.camera.setup()
        self.engine.render()
