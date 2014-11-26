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

from .entityproto import EntityProto
from .town import Town
from .event import Event

class Team(object):
    def __init__(self, eng, tid):
        self.eng = eng
        self.tid = tid
        self.entityprotos = {}
        self.towns = {}

        self.ontowncreated = Event()
        
    def __repr__(self):
        return '<Team %d>' % self.tid

    def load(self, data):
        epdatas = self.eng.datasrc.getentityprotos(self.tid)

        for epid, epdata in epdatas.iteritems():
            ep = EntityProto(epid, self)
            ep.load(epdata)
            self.entityprotos[epid] = ep

        for twid, twdata in data.get('towns', {}).iteritems():
            twid = int(twid)
            town = Town(twid, self)
            town.load(twdata)
            self.towns[twid] = town

            self.ontowncreated.emit(town)

        print self.towns

    def save(self):
        protos = {}
        for id_, ep in self.entityprotos.iteritems():
            protos[id_] = ep.save()

        towns = {}
        for twid, tw in self.towns.iteritems():
            towns[twid] = tw.save()

        return {
            'entityprotos' : protos,
            'towns' : towns
        }

    def getproto(self, name):
        return self.entityprotos[name]

    def gettown(self, twid):
        print self, repr(self.towns)
        return self.towns[twid]

    def gettownat(self, pos):
        for town in self.towns.itervalues():
            if town.contains(pos):
                return town

    def createtown(self, founder):
        twid = max(self.towns.keys()) + 1
        town = Town(twid, self)
        town.addentity(founder)
        self.towns[twid] = town
        self.ontowncreated.emit(town)
