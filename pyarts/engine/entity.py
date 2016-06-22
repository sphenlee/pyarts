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

    def __repr__(self):
        return '<Entity %d proto %s owned by %r>' % (self.eid, self.proto.name, self.team)

    def configure(self):
        ''' Loads shared data from the entity proto into each component '''
        # do a basic bredth first traversal of the dependencies
        # ignore cycles - not our problem!
        def configureone(name):
            comp = self.components[name]
            if comp.configured:
                return
            for dep in comp.depends:
                if dep[0] != '@':
                    configureone(dep)
            tmp = self.proto.data.get(name)
            comp.configure(tmp)

        for name in self.components.iterkeys():
            print 'configure ', name
            configureone(name)

    def save(self):
        ''' Save each component '''
        data = {
            'team' : self.team.tid,
            'proto' : self.proto.epid
        }
        for name, comp in self.components.iteritems():
            tmp = comp.save()
            if tmp is not None:
                data[name] = tmp
        return data

    def load(self, data):
        ''' Loads entity specific data into each component '''
        for name, comp in self.components.iteritems():
            tmp = data.get(name)
            comp.load(tmp)

    def step(self):
        ''' Step each component '''
        for comp in self.components.itervalues():
            comp.step()

    def has(self, comp):
        ''' Check if this entity has a certain component '''
        return comp in self.components

    @property
    def tier(self):
        '''Convenience for getting an Entity's selection tier'''
        return self.proto.rank // 100

    @property
    def rank(self):
        '''Convenience for getting an Entity's selection rank'''
        return self.proto.rank
