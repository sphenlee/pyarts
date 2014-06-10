'''
Behaviour

Component to control what auto commands do for each kind of entity
'''

from .component import Component, register

from engine.actions import MoveAction#, AttackAction

@register
class Behaviour(Component):
    name = 'behaviour'
    depends = ['actions', '@entitymanager']

    def inject(self, actions, entitymanager):
        self.actions = actions
        self.entitymanager = entitymanager

    def save(self):
        return { }

    def load(self, data):
        self.type = data["type"]

    def autocommand(self, target):
        if target.ispos():
            return MoveAction(target)
        else:
            ent = self.entitymanager.get(target.eid)
            print ent
            return MoveAction(target)
