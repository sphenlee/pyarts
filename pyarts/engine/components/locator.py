'''
Locator

Component to give an entity a location on the map
'''

from .component import Component, register
from ..event import Event
from pyarts.log import warn

@register
class Locator(Component):
    depends = ['@map']

    def __repr__(self):
        return f'<Locator eid={self.eid} x={self.x} y={self.y} placed={self.placed} r={self.r} sight={self.sight}>'

    def init(self):
        self.onplace = Event(debug='locator.onplace')

    def inject(self, map):
        self.map = map

    def configure(self, data):
        self.r = data.get('r', 16)
        self.sight = data.get('sight', self.r + 16)  # guess?

    def save(self):
        return {
            'x': self.x,
            'y': self.y,
            'placed': self.placed
        }

    def load(self, data):
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.placed = data.get('placed', False)
        if self.placed:
            self.map.place(self)

    def place(self, x, y):
        ''' Put the entity onto the map '''
        if self.placed:
            # maybe this should be an error - for now just forward to move
            return self.move(x, y)

        self.placed = True
        self.x = x
        self.y = y
        self.map.place(self)
        self.onplace.emit(self)

    def move(self, x, y):
        ''' Move the entity - an instant jump to the new location '''
        self.x = x
        self.y = y
        if self.placed:
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

    def destroy(self):
        warn(f'locator {self} being destroyed')
        self.unplace()
