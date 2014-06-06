'''
Team
A team is a logical group of entities.
Teams can be controlled by 0, 1 or more players.
EntityProtos are contained in a team, which means upgrades
always apply to an entire team.
'''

from .entityproto import EntityProto

class Team(object):
    def __init__(self, eng):
        self.eng = eng
        self.entityprotos = {}
        
    def load(self, data):
        self.tid = data['tid']

        epdatas = self.eng.datasrc.getentityprotos(self.tid)

        for id_, epdata in epdatas.iteritems():
            ep = EntityProto(self)
            ep.load(epdata)
            self.entityprotos[id_] = ep

    def getproto(self, name):
        return self.entityprotos[name]
