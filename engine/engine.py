'''
The Engine holds all of the state that is shared by all players
'''

from .map import Map
from .entitymanager import EntityManager
#from .playermanager import PlayerManager

class Engine(object):
    def __init__(self):
        self.map = Map()
        self.entities = EntityManager()
        #self.players = PlayerManager()

        self.towns = [ ]

    def render(self):
        self.map.render()
        self.entities.render()
