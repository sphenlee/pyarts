'''
Locator

Component to give an entity a location on the map
'''

from .component import Component, register

@register('locator')
class Locator(Component):
    def __init__(self, ent):
        super(Locator, self).__init__(ent)
        self.x = 0
        self.y = 0
        self.placed = False

    def save(self):
        return self.__dict__

    def load(self, data):
        self.__dict__.update(data)

    def place(self, x, y):
        self.x = x
        self.y = y
        self.placed = True

    def unplace(self):
        self.placed = False
