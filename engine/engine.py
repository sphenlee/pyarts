'''
The Engine holds all of the state that is shared by all players
'''

from .map import Map
from .entitymanager import EntityManager
from .renderer import Renderer
from .team import Team

class Engine(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc
        self.teams = []
        self.map = Map(self)
        self.entities = EntityManager(self)

        self.renderer = Renderer(self.datasrc)

        self.towns = [ ]

    def load(self):
        for t in self.datasrc.getteams():
            team = Team(self)
            team.load(t)
            self.teams.append(team)

        self.entities.load()

    def save(self, sink):
        for t in self.teams:
            data = t.save()
            sink.addteam(data)

        self.entities.save(sink)

    def step(self):
        self.map.step()
        self.entities.step()

    def render(self):
        self.map.draw()
        self.renderer.draw()

    def getteam(self, tid):
        return self.teams[tid]
    