'''
Abilities

A component for entities that can use abilities
'''

from .component import Component, register
from ..actions import AbilityAction

@register
class Abilities(Component):
    name = 'abilities'
    depends = [ '@content', 'actions' ]

    def inject(self, content, actions):
        self.content = content
        self.actions = actions

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
        for i in range(len(self.cooldowns)):
            if self.cooldowns[i] > 0:
                self.cooldowns[i] -= 1
        

    def activate(self, idx, target):
        if self.cooldowns[idx] > 0:
            print 'not ready'
            return False # not ready

        ability = self[idx]
        def start():
            ''' TODO - there might be a nicer way to do this '''
            self.cooldowns[idx] = ability.cooldown
        action = AbilityAction(ability, target, start)
        self.actions.give(action)
        return True

    def __getitem__(self, idx):
        return self.abilities[idx]