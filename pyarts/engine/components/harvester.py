'''
Harvester

A component for entities that can harvest resources
'''

from .component import Component, register

from .stats import StatusEffect
from .variables import Variable
from ..target import Target
from ..pathfinder import distance

from pyarts.log import debug, info

@register
class Harvester(Component):
    depends = ['moving', 'locator', '@map']

    def init(self):
        self.dropoff = None
        self.pickup = None

    def inject(self, **kwargs):
        self.__dict__.update(kwargs)

    def configure(self, data):
        self.capacity = data['capacity']
        self.rate = data['rate']

    def save(self):
        return {
            'carrying': self.carrying,
            'harvesting': self.harvesting
        }

    def load(self, data):
        self.carrying = data.get('carrying', 0)
        self.harvesting = data.get('harvesting', False)

    def step(self):
        if self.harvesting:
            #print(f'{self.carrying} + {self.rate} => {self.capacity}')
            self.carrying = min(self.carrying + self.rate, self.capacity)


    def findlike(self, proto, pos):
        x, y = pos
        debug('looking for ', proto, x, y)
        R = 20
        for e in self.map.entities_in_rect(x-R, y-R, x+R, y+R):
            if e.proto.name == proto.name:
                debug('found', e, e.proto)
                return e

    def finddropoff(self, pos):
        closest = None
        x, y = pos
        R = 1024 * 128
        for e in self.map.entities_in_rect(x-R, y-R, x+R, y+R):
            if e.team == self.ent.team and e.has('harveststore'):
                if closest is None or distance(pos, e.locator.pos()) < distance(pos, closest.locator.pos()):
                    closest = e

        return closest

    def gotopickup(self, proto, pos):
        self.pickup = self.findlike(proto, pos)
        if self.pickup:
            self.moving.moveto(Target(self.pickup))
            return True

    def gotodropoff(self):
        self.dropoff = self.finddropoff(self.locator.pos())
        if self.dropoff:
            self.moving.moveto(Target(self.dropoff))
            return True

    @property
    def intransit(self):
        return self.moving.intransit

    def startharvest(self):
        res = self.pickup.resource
        if res.unplace_harvester:
            self.locator.unplace()

        self.harvesting = True

    def full(self):
        return self.carrying == self.capacity

    def stopharvest(self):
        if self.pickup:
            res = self.pickup.resource
            res.deduct(self.carrying)

        if not self.locator.placed:
            self.locator.replace()
        
        self.harvesting = False

    def do_dropoff(self):
        res = self.pickup.resource
        
        info(f'droped off {self.carrying} resources')
        self.dropoff.harveststore.dropoff(res, self.carrying)
        self.carrying = 0
        self.dropoff = None
