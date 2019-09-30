'''
The Engine holds all of the state that is shared by all players.

This includes the EntityManager, Map and the list of teams.
'''

from .team import Team
from .event import Event

from pyarts.container import component

@component
class Engine(object):
    depends = ['datasrc', 'map', 'scripting', 'entitymanager', 'contentmanager', 'pathfinder', 'spritemanager']

    def __init__(self):
        self.teams = {}
        self.races = {}

        self.ontowncreated = Event(debug='ontowncreated')

    def inject(self, datasrc, map, scripting, entitymanager, contentmanager, pathfinder, spritemanager):
        self.datasrc = datasrc
        self.datasrc.onload.add(self.load)
        self.map = map
        self.scripting = scripting
        self.entities = entitymanager
        self.content = contentmanager
        self.pathfinder = pathfinder
        self.sprites = spritemanager

    def load(self):
        self.races = self.datasrc.getraces()
        for name, race in list(self.races.items()):
            race['name'] = name

        for tid, t in self.datasrc.getteams().items():
            tid = int(tid)
            team = Team(self, tid)
            team.load(t)
            self.teams[tid] = team

        #self.scripting.runmain() # where should this go?


    def save(self, sink):
        for tid, t in self.teams.items():
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
        return [t for i, t in self.teams.items() if (i & tidmask)]

    def getrace(self, name):
        return self.races[name]