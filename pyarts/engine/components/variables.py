'''
Variables

Variables are frequently changing numbers that describe
the capabilities of an entity. (For infrequently changing
values use Stats)
Variables can nominate stats that will be the variable's
maximum and regeneration rate (which can be negative).
'''

from .component import Component, register

class Variable(object):
    def __init__(self, name, descr, stats):
        self.name = name
        self.stats = stats
        # NOTE: max and regen are the names of stats, not the actual values!
        self.max_key = descr.get('max')
        self.regen_key = descr.get('regen')

        # start at a percentage of max by default
        self.val = self.max * int(descr.get('initial', 100)) // 100
        self.frac = 0

    def __repr__(self):
        return '<Variable %s %d + %d/1000, max=%d, regen=%d>' % (
            self.name, self.val, self.frac, self.max, self.regen)

    @property
    def max(self):
        return self.stats[self.max_key]
    
    @property
    def regen(self):
        return self.stats[self.regen_key]
    
    def step(self):
        ''' Apply regeneration '''
        if self.val < self.max:
            self.frac += self.regen
            if self.frac > 1000:
                self.val += 1
                self.frac -= 1000
            if self.val > self.max:
                self.val = self.max
        

@register
class Variables(Component):
    depends = [ 'stats' ]

    def init(self):
        self.vars = {}

    def inject(self, stats):
        self.stats = stats

    def configure(self, data):
        if data:
            for name, descr in data.items():
                self.vars[name] = Variable(name, descr, self.stats)

    def save(self):
        return dict((k, v.val) for k, v in self.vars.items())

    def load(self, data):
        if data is not None:
            for name, value in data.items():
                self.vars[name].val = value

    def step(self):
        for var in self.vars.values():
            var.step()

    def get(self, key):
        return self.vars[key]

    def __contains__(self, key):
        return key in self.vars

    def __getitem__(self, key):
        return self.vars[key].val

    def __setitem__(self, key, val):
        if 0 <= val <= self.vars[key].max:
            self.vars[key].val = val
