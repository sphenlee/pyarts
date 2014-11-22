'''
Behaviour

Component to control what auto commands do for each kind of entity
'''

from .component import Component, register

from ..actions import MoveAction#, AttackAction

@register
class Behaviour(Component):
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

    def autocommand(self, target, add):
        '''
        Decide based on the target and this entity
        what the appropriate action is
        '''
        if self.type == 'unit' and self.ent.has('moving'):
            if target.ispos():
                # move to the target position
                action = MoveAction(target)
            else:
                # TODO - check if the entity is friend or enemy (Follow, Attack,
                # or all of the other possible actions)
                ent = self.entities.get(target.eid)
                action = MoveAction(target)

            if add:
                self.actions.later(action)
            else:
                self.actions.give(action)
        else:
            print 'building auto command', self, target, add