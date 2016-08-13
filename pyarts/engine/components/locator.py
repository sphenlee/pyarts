'''
Locator

Component to give an entity a location on the map
'''

from .component import Component, register

@register
class Locator(Component):
    depends = ['@map']

    def inject(self, map):
        self.map = map

    def configure(self, data):
        self.r = data.get('r', 16)
        self.sight = data.get('sight', self.r + 16) # guess?
        self.x = 0
        self.y = 0
        self.placed = False

    def save(self):
        return {
            'x' : self.x,
            'y' : self.y,
            'placed' : self.placed
        }

    def load(self, data):
        if data:
            self.x = data.get('x', 0)
            self.y = data.get('y', 0)
            self.placed = data.get('placed', True)
            if self.placed:
                self.map.place(self)

    def place(self, x, y):
        ''' Put the entity onto the map '''
        self.placed = True
        self.x = x
        self.y = y
        self.map.place(self)

    def move(self, x, y):
        ''' Move the entity - an instant jump to the new location '''
        self.x = x
        self.y = y
        self.map.move(self)
        
    def unplace(self):
        ''' Remove entity from the map (eg. picked up by a transport unit) '''
        self.placed = False
        self.map.unplace(self)

    def replace(self):
        ''' Replace entity back on the map where it was unplaced from '''
        self.place(self.x, self.y)

    def pos(self):
        ''' Get the entity position as a tuple '''
        return self.x, self.y
