'''
Locator

Component to give an entity a location on the map
'''

from .component import Component, register

@register
class Locator(Component):
    name = 'locator'
    depends = ['@map']

    def inject(self, map):
        self.map = map

    def save(self):
        return {
            'x' : self.x,
            'y' : self.y,
            'r' : self.r,
            'placed' : self.placed
        }

    def load(self, data):
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.r = data.get('r', 16)
        self.placed = data.get('placed', False)
        if self.placed:
            self.map.place(self)

    def place(self, x, y):
        self.x = x
        self.y = y
        self.placed = True
        self.map.place(self)

    def unplace(self):
        self.placed = False
        self.map.unplace(self)
