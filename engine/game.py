'''
Game

The game represents the entire state of a game.
It holds the local player specific information as well
as the engine.
'''

from .engine import Engine
from .camera import Camera

class Game(object):
    def __init__(self, datasrc, localplayer=0):
        self.datasrc = datasrc
        self.localplayer = localplayer
        self.engine = Engine(datasrc)
        self.camera = Camera(800, 600)

    def load(self):
        self.engine.load()

        data = self.datasrc.getmisc('game.initial.state')

        look = data['camera'][self.localplayer]
        self.camera.lookx = look['x']
        self.camera.looky = look['y']

    def render(self):
        self.camera.setup()
        self.engine.render() # FIXME - engine should not have any graphics in it
