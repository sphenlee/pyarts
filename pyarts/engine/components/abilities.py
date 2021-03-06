'''
Abilities

A component for entities that can use abilities
'''

from .component import Component, register
from ..actions import AbilityAction

from pyarts.log import warn

class AbilityInstance(object):
    '''
    An ability with the per ent cooldown timer,
    and wait time for activities
    '''
    def __init__(self, ability, ent):
        self.ability = ability
        self.ent = ent
        self.cooldown = 0
        self.wait = 0

    def step(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def startcooldown(self):
        self.cooldown = self.ability.cooldown

    def startwait(self):
        self.wait = self.ability.wait


@register
class Abilities(Component):
    depends = [ '@content', 'actions' ]

    def inject(self, content, actions):
        self.content = content
        self.actions = actions

    def configure(self, data):
        self.abilities = []

        for name in data:
            ability = self.content.getability(name)
            ainst = AbilityInstance(ability, self.ent)
            self.abilities.append(ainst)
        
    def save(self):
        pass

    def load(self, data):
        pass

    def step(self):
        for ainst in self.abilities:
            ainst.step()


    def activate(self, idx, target, add):
        ainst = self[idx]

        if ainst.cooldown > 0:
            warn('not ready - ability activate checked it')
            return False # not ready

        if not ainst.ability.check_cost(self.ent):
            warn('cannot pay cost - ability activate checked it')
            return False

        if ainst.ability.queue:
            assert self.ent.has('queue'), 'entity needs a queue for this ability'
            self.ent.queue.add(ainst, target)
            ainst.ability.deduct_cost(self.ent)
            return True
        else:
            if ainst.wait > 0:
                warn('already doing this - ability activate checked it')
                return False # not ready    

            action = AbilityAction(ainst, target)
            if add:
                self.actions.now(action)
            else:
                self.actions.give(action)
            return True

    def __len__(self):
        return len(self.abilities)

    def __getitem__(self, idx):
        return self.abilities[idx]