'''
WalkAction

Performs a low level, essentially straight line walk to a point.
Does low level avoidance of obstacles.
Used to MoveAction to do the actual moving
'''

from .action import Action

def distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

class WalkAction(Action):
    ent = None

    def __init__(self, pos):
        self.pos = pos

    def start(self):
        self.locator = self.ent.locator
        self.steering = self.ent.steering

    def step(self):
        self.steering.towards(self.pos)

        d = distance(self.pos, self.locator.pos())
        if d < 10:
            self.steering.stop()
            self.ent.actions.done()
