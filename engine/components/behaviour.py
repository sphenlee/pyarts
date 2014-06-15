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
        self.entities = entitymanager

    def configure(self, data):
        pass

    def save(self):
        return {
            'type' : self.type
        }

    def load(self, data):
        self.type = data['type']

    def autocommand(self, target):
        '''
        Decide based on the target and this entity
        what the appropriate action is
        '''
        if target.ispos():
            # move to the target position
            return MoveAction(target)
        else:
            # TODO - check if the entity is friend or enemy (Follow, Attack,
            # or all of the other possible actions)
            ent = self.entities.get(target.eid)
            return MoveAction(target)