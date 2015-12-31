'''
Harvester

A component for entities that can harvest resources
'''

from .component import Component, register

from .stats import StatusEffect
from .variables import Variable
from ..target import Target

@register
class Harvester(Component):
    depends = [ 'variables', 'stats', 'moving', 'locator', '@map' ]

    def init(self):
        self.effect = None

    def inject(self, variables, stats, moving, locator, map):
        self.variables = variables
        self.stats = stats
        self.moving = moving
        self.locator = locator
        self.map = map

    def configure(self, data):
        self.data = data

        # add stats and a variable, is this naughty?
        self.stats.basestats['max_carrying'] = 10
        self.stats.basestats['carrying_regen'] = 0
        self.stats.recalculate()

        self.variables.vars['carrying'] = Variable('carrying', {
            'max': 'max_carrying',
            'regen': 'carrying_regen',
            'initial': 0 # percent
            }, self.stats)

    def save(self):
        pass

    def load(self, data):
        pass

    def findlike(self, seed):
        proto = seed.proto
        x, y = seed.locator.pos()
        R = 20
        for e in self.map.entities_in_rect(x-R, y-R, x+R, y+R):
            if e.proto.name == proto.name:
                return e

    def gotopickup(self, seed):
        self.moving.moveto(Target(self.findlike(seed)))

    def gotodropoff(self):
        self.moving.moveto(Target((100, 100)))

    @property
    def intransit(self):
        return self.moving.intransit

    def startharvest(self):
        self.locator.unplace()
        self.effect = self.stats.apply(StatusEffect('carrying_regen', add=self.data['rate']))

    @property
    def carrying(self):
        return self.variables['carrying']

    def full(self):
        v = self.variables.get('carrying')
        return v.val == v.max

    def stopharvest(self):
        if not self.locator.placed:
            self.locator.replace()
        
        if self.effect:
            self.stats.remove(self.effect)
            self.effect = None

    def dropoff(self):
        print 'droped off %r resources' % self.variables['carrying']
        self.variables['carrying'] = 0
