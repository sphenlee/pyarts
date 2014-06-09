'''
Behaviour

Component to control what auto commands do for each kind of entity
'''

from .component import Component, register

from engine.actions import MoveAction#, AttackAction

@register
class Behaviour(Component):
    name = 'behaviour'
    depends = ['actions']

    def inject(self, actions):
        self.actions = actions

    def save(self):
        return { }

    def load(self, data):
        self.type = data["type"]

    def autocommand(self, target):
        if instanceof(target, tuple):
            return MoveAction(target)
