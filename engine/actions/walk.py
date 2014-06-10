'''
WalkAction

Performs a low level, essentially straight line walk to a point.
Does low level avoidance of obstacles.
Used to MoveAction to do the actual moving
'''

class WalkAction(object):
    ent = None

    def __init__(self, pos):
        self.pos = pos

    def step(self):
        print 'walking to ', self.pos, self.ent

        self.ent.locator.move(*self.pos)
        self.ent.actions.done()
