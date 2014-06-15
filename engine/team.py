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

class Team(object):
    def __init__(self, eng):
        self.eng = eng
        self.entityprotos = {}
        
    def load(self, data):
        self.tid = data['tid']

        epdatas = self.eng.datasrc.getentityprotos(self.tid)

        for epid, epdata in epdatas.iteritems():
            ep = EntityProto(epid, self)
            ep.load(epdata)
            self.entityprotos[epid] = ep

    def save(self):
        protos = {}
        for id_, ep in self.entityprotos.iteritems():
            protos[id_] = ep.save()

        return {
            'tid' : self.tid,
            'entityprotos' : protos
        }

    def getproto(self, name):
        return self.entityprotos[name]
