'''
Footprint

Component to make an entity block paths for the pathfinder.

NOTE: Assumes the entity does NOT move! (ie. buildings)
'''

from .component import Component, register

@register
class Footprint(Component):
    depends = ['locator', '@map']

    def inject(self, locator, map):
        self.locator = locator
        self.map = map

    def configure(self, data):
        self.ready = False
    
    def load(self, data):
        self.step()

    def step(self):
        if not self.ready:
            print 'footprinting', self.ent
            self.ready = self.map.footprint(self.locator)
    
    def save(self):
        return { }
