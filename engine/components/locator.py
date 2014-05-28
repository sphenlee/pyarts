'''
Locator

Component to give an entity a location on the map
'''

from .component import Component, register

@register
class Locator(Component):
    def save(self):
        return {
            'x' : self.x,
            'y' : self.y,
            'placed' : self.placed
        }

    def load(self, data):
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.placed = data.placed('placed', False)

    def place(self, x, y):
        self.x = x
        self.y = y
        self.placed = True

    def unplace(self):
        self.placed = False
