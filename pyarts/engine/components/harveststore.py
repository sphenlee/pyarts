'''
Harvest Store

A component for entities that can have resources dropped off
'''

from .component import Component, register

@register
class HarvestStore(Component):
    depends = [ 'town' ]

    def init(self):
        pass

    def inject(self, town):
        self.town = town

    def configure(self, data):
        pass

    def save(self):
        pass

    def load(self, data):
        pass

    
    def dropoff(self, resources):
        pass