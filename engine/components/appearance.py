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

        img = self.ent.proto.sprite
        self.sprite = renderer.new_sprite(img)
        

    def save(self):
        return {}

    def load(self, data):
        self.sprite.setpos(self.locator.x - self.locator.r,
                           self.locator.y - self.locator.r)
