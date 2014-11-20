'''
Appearance

Component to make a component visible on the game screen
'''

from .component import Component, register

@register
class Appearance(Component):
    depends = ['locator', '@sprites']

    def inject(self, locator, sprites):
        self.locator = locator
        self.sprites = sprites

    def configure(self, data):
        self.sprite = self.sprites.new_sprite(data['sprite'], self.locator.r * 2)
        self.portrait = data['portrait']

    def save(self):
        return {}

    def load(self, data):
        pass

    def step(self):
        self.sprite.setpos(self.locator.x - self.locator.r,
                           self.locator.y - self.locator.r)
