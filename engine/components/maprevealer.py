'''
MapRevealer

Component to reveal areas on the map
'''

from .component import Component, register

@register
class MapRevealer(Component):
    def save(self):
        return { }

    def load(self, data):
        pass
