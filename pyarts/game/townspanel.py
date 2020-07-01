'''
TownsPanel

Shows towns and resource info
'''

from pyarts.container import component
from pyarts.log import debug, trace, info


@component
class TownsPanel(object):
    depends = ['engine', 'local', 'datasrc']

    def __init__(self):
        self.resources = {}

    def inject(self, engine, local, datasrc):
        self.local = local
        self.datasrc = datasrc
        self.engine = engine

        self.datasrc.onready.add(self.ready)

    def ready(self):
        for team in self.engine.teams.values():
            for town in team.towns.values():
                self.townadded(team, town)

        self.engine.ontowncreated.add(self.townadded)

    def townadded(self, team, town):
        debug('added town {}', town)

        if not team.controlled_by(self.local.player):
            debug('local player doesn\'t control this town')
            return

        resource = '/' + self.datasrc.getresource(town.race['resource_icon'])
        energy = '/' + self.datasrc.getresource(town.race['energy_icon'])

        self.resources[town.resources.rpid] = {
            'name': town.name,
            'resource_image': resource,
            'energy_image': energy,
            'resource_value': 0,
            'energy_value': 0,
            'position': (0, 0),
        }

        town.resources.onchange.add(self.update_resources)
        town.onentityadded.add(self.update_founder)

        # refresh the number right now
        self.update_resources(town.resources)
        self.update_founder(town, town.founder)

    def update_founder(self, town, ent):
        trace('update founder {} {}', town, ent)
        founder = town.founder
        if founder is not None:
            pos = founder.locator.pos()
            trace('founder pos {}', pos)
            self.resources[town.resources.rpid]['position'] = pos

    def update_resources(self, resources):
        trace('update {}', resources)
        self.resources[resources.rpid]['resource_value'] = resources.resource
        self.resources[resources.rpid]['energy_value'] = resources.energy
