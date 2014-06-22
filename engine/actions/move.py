'''
MoveAction

Performs high level motion of an entity
'''

from .walk import WalkAction

def distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

class MoveAction(object):
    ent = None

    def __init__(self, target, range=10, follow=True):
        self.target = target
        self.range = range
        self.follow = follow

    def step(self):
        # TODO use pathfinder to plot a path and use Walk actions to follow it

        pos = self.target.getpos()
        me = self.ent.locator.pos()

        print pos, me, distance(me, pos)

        if distance(me, pos) > self.range:
            walk = WalkAction(pos)
            self.ent.actions.give(walk)
        elif self.target.ispos() or not self.follow:
            self.ent.actions.done()
