'''
AbilityAction

High level action for getting an entity to do an action
'''

from .action import Action
from .move import MoveAction
from ..pathfinder import distance

class AbilityAction(Action):
    def __init__(self, ainst, target=None, onstart=None):
        self.ainst = ainst
        self.ability = ainst.ability
        self.target = target
        self.onstart = onstart

    def start(self):
        self.ainst.wait = self.ability.wait

        if self.ability.onstart:
            self.ability.onstart(self.ent.eid)

    def suspend(self):
        if self.ability.onstop:
            self.ability.onstop(self.ent.eid)

    def step(self):
        if self.ainst.wait == 0:
            self.doability()
        else:
            self.ainst.wait -= 1

    def doability(self):
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
                self.ent.actions.now(mv)
                return

        print 'done ability'
        if self.onstart:
            self.onstart()

        self.ainst.startcooldown()

        self.ability.activate(self.ent, self.target)

        self.done()
