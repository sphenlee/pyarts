'''
MapRevealer

Component to tie together the sight stat to the locator's sight property
'''

from .component import Component, register

@register
class MapRevealer(Component):
    depends = ['locator', 'stats']

    def inject(self, locator, stats):
        self.locator = locator
        self.stats = stats

    def configure(self, data):
        self.locator.sight = self.stats['sight']
    
    def load(self, data):
        self.step()

    def step(self):
        self.locator.sight = self.stats['sight']

    def save(self):
        return { }
