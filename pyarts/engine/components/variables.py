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
        # NOTE: max and regen are the names of stats, not the actual values!
        self.max = descr.get('max', 2**32)
        self.regen = descr.get('regen')

        # start at a percentage of max by default
        self.val = stats[self.max] * int(descr.get('initial', 100)) // 100
        self.frac = 0

    def step(self, stats):
        ''' Apply regeneration '''
        max_ = stats[self.max]
        if self.val < max_:
            self.frac += stats[self.regen]
            if self.frac > 1000:
                self.val += 1
                self.frac -= 1000
            if self.val > max_:
                self.val = max_
        

@register
class Variables(Component):
    depends = [ 'stats' ]

    def inject(self, stats):
        self.stats = stats

    def configure(self, data):
        self.vars = {}
        
        for name, descr in data.iteritems():
            self.vars[name] = Variable(name, descr, self.stats)

    def save(self):
        return dict((k, v.val) for k, v in self.vars.iteritems())

    def load(self, data):
        if data is not None:
            for name, value in data.iteritems():
                self.vars[name].val = value

    def step(self):
        for var in self.vars.itervalues():
            var.step(self.stats)

    def __contains__(self, key):
        return key in self.vars

    def __getitem__(self, key):
        return self.vars[key].val

    def __setitem__(self, key, val):
        if 0 < val < self.vars[key].max:
            self.vars[key].val = val

    def getmax(self, key):
        return self.stats[self.vars[key].max]
