'''
The Engine holds all of the state that is shared by all players
'''

from .map import Map
from .entitymanager import EntityManager
#from .playermanager import PlayerManager
from .renderer import Renderer

class Engine(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc
        self.map = Map(self)
        self.entities = EntityManager(self)
        #self.players = PlayerManager(self)
        
        self.renderer = Renderer()

        self.towns = [ ]

    def render(self):
        self.map.draw()
        self.renderer.draw()
