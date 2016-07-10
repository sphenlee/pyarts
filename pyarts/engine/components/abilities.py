'''
Abilities

A component for entities that can use abilities
'''

from .component import Component, register
from ..actions import AbilityAction

class AbilityInstance(object):
    '''
    An ability with the per ent cooldown timer,
    and wait time for activities
    '''
    def __init__(self, ability):
        self.ability = ability
        self.cooldown = 0
        self.wait = 0

    def step(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def startcooldown(self):
        self.cooldown = self.ability.cooldown


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
            ainst = AbilityInstance(ability)
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
            print 'not ready - ability activate checked it'
            return False # not ready

        if ainst.ability.queue:
            assert self.ent.has('queue'), 'entity needs a queue for this ability'
            return self.ent.queue.add(ainst, target)
        else:
            if ainst.wait > 0:
                print 'already doing this - ability activate checked it'
                return False # not ready

            def onstart():
                ''' TODO - there might be a nicer way to do this '''
                ainst.ability.deduct_cost(self.ent)

            action = AbilityAction(ainst, target, onstart)
            if add:
                self.actions.now(action)
            else:
                self.actions.give(action)
            return True

    def __len__(self):
        return len(self.abilities)

    def __getitem__(self, idx):
        return self.abilities[idx]