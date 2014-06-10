'''
MoveAction

Performs high level motion of an entity
'''

class MoveAction(object):
    def __init__(self, target, range=0):
        self.target = target
        self.range = range
        self.ent = None

    def step(self):
        print 'moving', self.ent, self.target
        self.ent.actions.done()
