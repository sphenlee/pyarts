'''
The Engine holds all of the state that is shared by all players.

This includes the EntityManager, Map and the list of teams.
'''

from .map import Map
from .entitymanager import EntityManager
from .contentmanager import ContentManager
from .spritemanager import SpriteManager
from .pathfinder import Pathfinder
from .team import Team
from .scripting import Scripting

from .. import lua

class Engine(object):
    def __init__(self, datasrc):
        self.datasrc = datasrc
        self.teams = {}
        self.map = Map(self)
        self.scripting = Scripting(self)
        self.entities = EntityManager(self)
        self.content = ContentManager(self)
        self.pathfinder = Pathfinder(self.map)
        self.sprites = SpriteManager(self.datasrc)
        self.races = {}


    def load(self):
        self.scripting.setup()

        self.content.load(self.datasrc)

        self.races = self.datasrc.getraces()

        for tid, t in self.datasrc.getteams().iteritems():
            tid = int(tid)
            team = Team(self, tid)
            team.load(t)
            self.teams[tid] = team

        self.entities.load()
        self.map.load()


    def save(self, sink):
        for tid, t in self.teams.iteritems():
            data = t.save()
            sink.addteam(tid, data)

        self.entities.save(sink)
        self.map.save(sink)

    def step(self):
        self.map.step()
        self.entities.step()

    def render(self):
        self.sprites.draw()

    def getteam(self, tid):
        return self.teams[tid]

    def getteams(self, tidmask):
        return [t for i, t in self.teams.iteritems() if (i & tidmask)]

    def getrace(self, name):
        return self.races[name]