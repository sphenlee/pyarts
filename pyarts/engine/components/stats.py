'''
Stats

Stats are numbers describing the capabilities of an entity.
They change infrequently, as a result of StatusEffects.
(Frequently changing values should use Variables).
'''

from .component import Component, register

class StatusEffect(object):
    def __init__(self, name, add=0, mult=1, timeout=None, seid=None):
        self.id = seid if seid is not None else id(self)
        self.name = name
        self.add = add
        self.mult = mult
        self.timeout = timeout

    def __repr__(self):
        return 'StatusEffect(%r, add=%d, mult=%d, timeout=%r, seid=%r)' % (
            self.name, self.add, self.mult, self.timeout, self.id)

    def save(self):
        return self.__dict__

    def apply(self, stats):
        ''' Apply this effect '''
        stats[self.name] = stats[self.name] * self.mult + self.add

@register
class Stats(Component):
    depends = []

    def init(self):
        self.basestats = {}
        self.stack = []

    def configure(self, data):
        ''' Load the base stats from the proto and copy it for the initial stats '''
        if data:
            for name, val in data.items():
                self.basestats[name] = int(val)

        self.stats = self.basestats.copy()

    def save(self):
        '''
        Only effects need to be saved, the basestats are saved in the proto
        and the current stats will be recalculated
        '''
        return {
            'effects' : [eff.save() for eff in self.stack]
        }

    def load(self, data):
        '''
        Load status effects and then recalculate
        '''
        for effdata in data.get('effects', []):
            eff = StatusEffect(**effdata)
            self.stack.append(eff)

        self.recalculate()

    def recalculate(self):
        '''
        Recalculate the current stats from the base stats and the effects
        '''
        self.stats = self.basestats.copy()
        for eff in self.stack:
            eff.apply(self.stats)

    def step(self):
        '''
        Apply timeouts on effects
        '''
        newstack = [] # TODO this could be smarter
        for eff in self.stack:
            if eff.timeout is None:
                newstack.append(eff)
            else:
                eff.timeout -= 1
                if eff.timeout > 0:
                    newstack.append(eff)

        if len(self.stack) != len(newstack):
            self.stack = newstack
            self.recalculate()

    def apply(self, eff):
        ''' Apply a new effect to this entity '''
        self.stack.append(eff)
        self.recalculate()
        return eff.id

    def remove(self, seid):
        self.stack = [s for s in self.stack if s.id != seid]
        self.recalculate()

    def __getitem__(self, key):
        ''' Lookup a stat by name '''
        return self.stats[key]

    def get(self, key, default=None):
        return self.stats.get(key, default)
