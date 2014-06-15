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
    def __init__(self, name, descr):
        self.name = name
        self.max = descr.get('max', 2**32)
        self.regen = descr.get('regen')

        self.val = 0 # TODO initial value of a variable somewhere?

    def step(self, stats):
        ''' Apply regeneration '''
        max_ = stats[self.max]
        if self.val < max_:
            self.val += stats[self.regen]
            if self.val > max_:
                self.val = max_
        

@register
class Variables(Component):
    name = 'variables'
    depends = [ 'stats' ]

    def inject(self, stats):
        self.stats = stats

    def configure(self, data):
        self.vars = {}
        
        for name, descr in data.iteritems():
            self.vars[name] = Variable(name, descr)

    def save(self):
        return dict((k, v.val) for k, v in self.vars.iteritems())

    def load(self, data):
        if data is not None:
            for name, value in data.iteritems():
                self.vars[name].val = value

    def step(self):
        for var in self.vars.itervalues():
            var.step(self.stats)

    def __getitem__(self, key):
        return self.vars[key].val
