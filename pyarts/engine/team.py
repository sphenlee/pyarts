'''
Team
A team is a logical group of entities.
Teams can be controlled by 0, 1 or more players.
EntityProtos are contained in a team, which means upgrades
always apply to an entire team (but not to other teams).

When loading a map there is a global list of protos that we
load first, then merge in any team specific protos.
This means that usually every teams starts with the same
protos but as upgrades are done they can diverge.
'''

from pyarts.container import dynamic_component

from .entityproto import EntityProto
from .town import Town


@dynamic_component
class Team(object):
    depends = ['engine', 'components']

    def __init__(self, tid):
        self.tid = tid
        self.entityprotos = {}
        self.towns = {}

    def inject(self, engine, components):
        self.eng = engine
        self.components = components

    def __repr__(self):
        return '<Team %d>' % self.tid

    def __eq__(self, other):
        assert isinstance(other, Team)
        return self.tid == other.tid

    def load(self, data):
        epdatas = self.eng.datasrc.getentityprotos(self.tid)

        for epid, epdata in epdatas.items():
            ep = EntityProto(epid, self)
            ep.load(epdata)
            self.entityprotos[epid] = ep

        for twid, twdata in data.get('towns', {}).items():
            twid = int(twid)
            town = self.components.construct('town', twid, self)
            town.load(twdata)
            self.towns[twid] = town

            self.eng.ontowncreated.emit(self, town)

    def save(self):
        protos = {}
        for id_, ep in self.entityprotos.items():
            protos[id_] = ep.save()

        towns = {}
        for twid, tw in self.towns.items():
            towns[twid] = tw.save()

        return {
            'entityprotos': protos,
            'towns': towns,
        }

    def controlled_by(self, player):
        '''Check if a player controls'''
        return bool(player.tidmask & (1 << self.tid))

    def getproto(self, name):
        return self.entityprotos[name]

    def gettown(self, twid):
        return self.towns[twid]

    def gettownat(self, pos):
        for town in self.towns.values():
            if town.contains(pos):
                return town

    def create_town(self, founder, race, initial_resources={}):
        twid = max(self.towns.keys()) + 1
        town = self.components.construct('town', twid, self)
        self.towns[twid] = town
        town.load({
            'name': self.eng.generate_town_name(),
            'race': race,
            'resources': initial_resources,
            'founder': founder.eid
            })
        self.eng.ontowncreated.emit(self, town)
        town.addentity(founder)
        return town
