'''
Abilities

A component for entities that can use abilities
'''

from .component import Component, register

@register
class Abilities(Component):
    name = 'abilities'
    depends = [ '@content' ]

    def inject(self, content):
        self.content = content

    def configure(self, data):
        self.abilities = []
        self.cooldowns = []

        for name in data:
            ability = self.content.getability(name)
            self.abilities.append(ability)
            self.cooldowns.append(0)
        
    def save(self):
        pass

    def load(self, data):
        pass

    def step(self):
        pass
