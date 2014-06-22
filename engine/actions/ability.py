'''
AbilityAction

High level action for getting an entity to do an action
'''

from .move import MoveAction, distance

class AbilityAction(object):
    ent = None

    def __init__(self, ability, target=None, start=None):
        self.ability = ability
        self.target = target
        self.start = start

    def step(self):
        print 'entity %d doing action %s at %s' % (
            self.ent.eid,
            self.ability.name,
            self.target)

        if self.target:
            pos = self.target.getpos()
            me = self.ent.locator.pos()

            print 'ability', pos, me, distance(me, pos)

            if distance(me, pos) > self.ability.range:
                mv = MoveAction(self.target, range=self.ability.range, follow=False)
                self.ent.actions.give(mv)
                return

        print 'done ability'
        if self.start:
            self.start()

        self.ability.activate(self.ent.eid)

        self.ent.actions.done()
