'''
AbilityAction

High level action for getting an entity to do an action
'''

class AbilityAction(object):
    ent = None

    def __init__(self, ability, target=None):
        self.ability = ability
        self.target = target

    def step(self):
        print 'entity %d doing action %s at %s' % (
            self.ent.eid,
            self.ability.name,
            self.target)

        self.ent.actions.done()
