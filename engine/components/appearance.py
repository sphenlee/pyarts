'''
Appearance

Component to make a component visible on the game screen
'''

from .component import Component, register

@register
class Appearance(Component):
    name = 'appearance'
    depends = ['locator', '@renderer']

    def inject(self, locator, renderer):
        self.locator = locator

    def configure(self, data):
        img = data['sprite']
        self.sprite = renderer.new_sprite(img)

    def save(self):
        return {}

    def load(self, data):
        pass

    def step(self):
        self.sprite.setpos(self.locator.x - self.locator.r,
                           self.locator.y - self.locator.r)
