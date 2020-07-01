'''
The Engine holds all of the state that is shared by all players.

This includes the EntityManager, Map and the list of teams.
'''

import random

from .event import Event

from pyarts.container import component


@component
class Engine(object):
    depends = ['datasrc', 'map', 'scripting', 'entitymanager', 'components',
               'contentmanager', 'pathfinder', 'spritemanager']

    def __init__(self):
        self.teams = {}
        self.races = {}
        self.townnames = None

        self.ontowncreated = Event(debug='ontowncreated')

    def inject(self, datasrc, map, scripting, entitymanager, contentmanager,
               pathfinder, spritemanager, components):
        self.datasrc = datasrc
        self.datasrc.onload.add(self.load)
        self.map = map
        self.scripting = scripting
        self.entities = entitymanager
        self.content = contentmanager
        self.pathfinder = pathfinder
        self.sprites = spritemanager
        self.components = components

    def load(self):
        self.races = self.datasrc.getraces()
        for name, race in list(self.races.items()):
            race['name'] = name

        for tid, t in self.datasrc.getteams().items():
            tid = int(tid)
            team = self.components.construct('team', tid)
            team.load(t)
            self.teams[tid] = team

        # self.scripting.runmain() # where should this go?

        with open(self.datasrc.getresource('res/town_names.txt')) as fp:
            self.townnames = [line.strip() for line in fp]

    def save(self, sink):
        for tid, t in self.teams.items():
            data = t.save()
            sink.addteam(tid, data)

        self.entities.save(sink)
        self.map.save(sink)

    def step(self):
        self.map.step()
        self.entities.step()

    def getteam(self, tid):
        return self.teams[tid]

    def getteams(self, tidmask):
        return [t for i, t in self.teams.items() if (i & tidmask)]

    def getrace(self, name):
        return self.races[name]

    def generate_town_name(self):
        # randomness! fixme TODO!
        return random.choice(self.townnames)
