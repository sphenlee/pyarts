'''
AbilityAction

High level action for getting an entity to do an action
'''

from .action import Action
from .move import MoveAction
from ..components.moving import distance

def distance_to_target(ent, target):
    '''
    Distance from an entity to a target taking into account the radii of each
    '''
    d = distance(ent, target.getpos())
    if target.isent():
        d -= target.ent.locator.r**2
        print(f'adjusted2 d {d}')

    return d


class AbilityAction(Action):
    def __init__(self, ainst, target=None):
        self.ainst = ainst
        self.ability = ainst.ability
        self.target = target

    def start(self):
        if self.target:
            dist = distance_to_target(self.ent, self.target)

            print(f'moving into position: ent={self.ent!r} target={self.target!r} dist={dist!r} range={self.ability.range!r}')

            mindist = 0 if self.ability.range is None else self.ability.range
            if dist > mindist:
                mv = MoveAction(self.target, range=self.ability.range, follow=False)
                self.ent.actions.now(mv)
                return

        self.ainst.startwait()

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
        print('entity %d doing action %s at %s' % (
            self.ent.eid,
            self.ability.name,
            self.target))

        self.ability.deduct_cost(self.ent)

        self.ainst.startcooldown()

        self.ability.activate(self.ent, self.target)

        self.done()
