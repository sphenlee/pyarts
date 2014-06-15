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

    def configure(self, data):
        self.r = data.get('r', 16)

    def save(self):
        return {
            'x' : self.x,
            'y' : self.y,
            'placed' : self.placed
        }

    def load(self, data):
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.placed = data.get('placed', False)
        if self.placed:
            self.map.place(self)

    def place(self, x, y):
        ''' Put the entity onto the map '''
        self.x = x
        self.y = y
        self.placed = True
        self.map.place(self)

    def move(self, x, y):
        ''' Move the entity - an instant jump to the new location '''
        self.x = x
        self.y = y

    def unplace(self):
        ''' Remove entity from the map (eg. picked up by a transport unit) '''
        self.placed = False
        self.map.unplace(self)

    def pos(self):
        ''' Get the entity position as a tuple '''
        return self.x, self.y
