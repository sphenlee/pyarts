'''
Entity

Entities represent every object with behaviour in a game.
Entities have an ID (eid) which is unique, and a collection
of components.  They have no other behaviour except what is
specified by the components.
'''

from toposort import toposort_flatten

from .components import *
from pyarts.log import info, trace


def component_order(components):
    graph = {}
    for name, comp in components.items():
        graph[name] = set(d for d in comp.depends if d[0] != '@')

    trace('component graph: {}', graph)
    order = toposort_flatten(graph)
    trace('sorted order: {}', order)
    return order


class Entity(object):
    def __init__(self, eid, proto):
        self.eid = eid
        self.team = proto.team
        self.proto = proto
        self.components = {}

    def __del__(self):
        info('entity %r is being deleted' % self)

    def __repr__(self):
        return '<Entity %d "%s">' % (self.eid, self.proto.name)

    def configure(self):
        ''' Loads shared data from the entity proto into each component '''
        self.component_order = component_order(self.components)

        for name in self.component_order:
            comp = self.components[name]
            data = self.proto.data.get(name)
            comp.configure(data)

    def save(self):
        ''' Save each component '''
        data = {
            'team': self.team.tid,
            'proto': self.proto.epid
        }
        for name in self.component_order:
            comp = self.components[name]
            cdata = comp.save()
            if cdata is not None:
                data[name] = cdata
        return data

    def load(self, data):
        ''' Loads entity specific data into each component '''
        for name in self.component_order:
            comp = self.components[name]
            cdata = data.get(name, {})
            comp.load(cdata)

    def step(self):
        ''' Step each component '''
        for name in self.component_order:
            comp = self.components[name]
            comp.step()

    def destroy(self):
        '''Destroy each component *in reverse order* '''
        for name in reversed(self.component_order):
            comp = self.components[name]
            comp.destroy()

    def has(self, comp):
        ''' Check if this entity has a certain component '''
        return comp in self.components

    def ownedby(self, player):
        '''Check if a player owns this entity'''
        return bool(player.tidmask & (1 << self.team.tid))

    @property
    def tier(self):
        '''Convenience for getting an Entity's selection tier'''
        return self.proto.rank // 100

    @property
    def rank(self):
        '''Convenience for getting an Entity's selection rank'''
        return self.proto.rank
