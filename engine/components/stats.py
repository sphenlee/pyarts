'''
Stats
'''

from .component import Component, register

class StatusEffect(object):
    def __init__(self, name, add, mult, timeout):
        self.name = name
        self.add = add
        self.mult = mult
        self.timeout = timeout

    def save(self):
        return self.__dict__

    def apply(self, stats):
        stats[self.name] = stats[self.name] * mult + add

@register
class Stats(Component):
    name = 'stats'
    depends = []

    def configure(self, data):
        self.basestats = {}
        self.stack = []

        for name, val in data.iteritems():
            self.basestats[name] = int(val)

        self.stats = self.basestats.copy()

    def save(self):
        return {
            'effects' : [eff.__save__() for eff in self.stack]
        }

    def load(self, data):
        for effdata in data['effects']:
            eff = StatusEffect(**effdata)
            self.stack.append(eff)

        self.recalculate()

    def recalculate(self):
        self.stats = self.basestats.copy()
        for eff in self.stack:
            eff.apply(self.stats)

    def step(self):
        newstack = [] # TODO this could be smarter
        for eff in self.stack:
            eff.timeout -= 1
            if eff.timeout > 0:
                newstack.append(eff)

        if len(self.stack) != len(newstack):
            self.stack = newstack
            self.recalculate()

    def apply(self, eff):
        self.stack.append(eff)
        self.recalculate()
