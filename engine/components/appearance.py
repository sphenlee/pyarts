'''
Appearance

Component to make a component visible on the game screen
'''

from .component import Component, register

@register('appearance')
class Appearance(Component):
    def __init__(self, ent):
        super(Appearance, self).__init__(ent)
        self.sprite = None

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
