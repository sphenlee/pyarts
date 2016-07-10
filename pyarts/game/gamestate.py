'''
GameState

This holds the "run state" of the game.
 - waiting for players
 - running

'''

from pyarts.container import component

@component
class GameState(object):
    WAITING_FOR_PLAYERS = 'waiting'
    STARTING = 'starting'
    RUNNING = 'running'

    depends = ['network', 'game']

    def __init__(self):
        self.state = GameState.WAITING_FOR_PLAYERS

    def inject(self, network, game):
        self.network = network
        self.network.ongamestart.add(self.start)
        self.game = game

    def start(self):
        print 'gamestate starting!'
        self.state = GameState.RUNNING

    def step(self):
        self.network.step()
        if self.state == GameState.RUNNING:
            self.game.step()
