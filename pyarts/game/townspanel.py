'''
TownsPanel

Shows towns and resource info
'''

from pyarts.container import component
from pyarts.log import debug, trace

@component
class TownsPanel(object):
    depends = ['engine', 'local', 'datasrc']


    def __init__(self):
        self.resources = {}

    def inject(self, engine, local, datasrc):
        self.local = local
        self.datasrc = datasrc

        engine.ontowncreated.add(self.townadded)

    def townadded(self, team, town):
        debug('added town', team, town)

        # TODO
        #if not team.controlled_by(self.local.player):
        #    print('local player doesn\'t control this town')
        #    return

        resource = '/' + self.datasrc.getresource(town.race['resource_icon'])
        energy = '/' + self.datasrc.getresource(town.race['energy_icon'])
        
        self.resources[town.resources.rpid] = {
            'resource_image': resource,
            'energy_image': energy,
            'resource_value': 0,
            'energy_value': 0,
        }

        town.resources.onchange.add(self.update_resources)
        
        # refresh the number right now
        self.update_resources(town.resources)

    def update_resources(self, resources):
        trace('update', resources)
        self.resources[resources.rpid]['resource_value'] = resources.resource
        self.resources[resources.rpid]['energy_value'] = resources.energy
