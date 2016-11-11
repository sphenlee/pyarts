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
    depends = [ 'variables', 'stats', 'moving',
        'locator', '@map', '@team']

    def init(self):
        self.effect = None
        self.target = None

    def inject(self, **kwargs):
        self.__dict__.update(kwargs)

    def configure(self, data):
        self.rate = data['rate']

        # add stats and a variable, is this naughty?
        self.stats.basestats['max_carrying'] = data['capacity']
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
        print 'looking for ', seed, proto, x, y
        R = 20
        for e in self.map.entities_in_rect(x-R, y-R, x+R, y+R):
            if e.proto.name == proto.name:
                print 'found', e, e.proto
                return e

    def finddropoff(self, pos):
        x, y = pos
        R = 1024 * 128
        for e in self.map.entities_in_rect(x-R, y-R, x+R, y+R):
            if e.has('harveststore'):
                return e

    def gotopickup(self, seed):
        pickup = self.findlike(seed)
        if pickup:
            self.target = Target(pickup)
            self.moving.moveto(self.target)
            return True

    def gotodropoff(self):
        e = self.finddropoff(self.locator.pos())
        if e is not None:
            self.target = Target(e)
            self.moving.moveto(self.target)
            return True

    @property
    def intransit(self):
        return self.moving.intransit

    def startharvest(self, res):
        if res.unplace_harvester:
            self.locator.unplace()
        self.effect = self.stats.apply(StatusEffect('carrying_regen', add=self.rate))

    @property
    def carrying(self):
        return self.variables['carrying']

    def full(self):
        v = self.variables.get('carrying')
        return v.val == v.max

    def stopharvest(self, res):
        res.deduct(self.carrying)

        if not self.locator.placed:
            self.locator.replace()
        
        if self.effect:
            self.stats.remove(self.effect)
            self.effect = None

    def dropoff(self, res):
        print 'droped off %r resources' % self.variables['carrying']
        self.target.ent.harveststore.dropoff(res, self.variables['carrying'])
        self.variables['carrying'] = 0

