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

    def save(self):
        data = { }
        for name, comp in self.components.iteritems():
            tmp = comp.save()
            if tmp:
                data[name] = tmp
        return data

    def load(self, data):
        for name, comp in self.components.iteritems():
            print 'loading', name, comp, data
            tmp = data.get(name)
            comp.load(tmp)
