'''
Appearance

Component to make a component visible on the game screen
'''

from .component import Component, register

class Appearance(Component):
    name = 'appearance'
    depends = ['locator', '@renderer']

    def inject(self, locator, renderer):
        self.locator = locator
        self.sprite = renderer.getsprite()

    def save(self):

    def load(self, data):
        self.__dict__.update(data)

    