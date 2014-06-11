'''
Entity

Entities represent every object with behaviour in a game.
Entities have an ID (eid) which is unique, and a collection
of components.  They have no other behaviour except what is
specified by the components.
'''

from .components import *

class Entity(object):
    def __init__(self, eid, proto):
        self.eid = eid
        self.team = proto.team
        self.proto = proto
        self.components = { }

    def configure(self):
        for name, comp in self.components.iteritems():
            tmp = self.proto.data.get(name)
            comp.configure(tmp)

    def save(self):
        data = {
            'team' : self.team.tid,
            'proto' : self.proto.epid
        }
        for name, comp in self.components.iteritems():
            tmp = comp.save()
            if tmp:
                data[name] = tmp
        return data

    def load(self, data):
        for name, comp in self.components.iteritems():
            tmp = data.get(name)
            comp.load(tmp)

    def step(self):
        for comp in self.components.itervalues():
            comp.step()

    def has(self, comp):
        return comp in self.components