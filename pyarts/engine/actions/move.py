'''
MoveAction

Performs high level motion of an entity
'''

from .action import Action

class MoveAction(Action):
    def __init__(self, target, range=10, follow=False):
        self.target = target
        self.range = range
        self.follow = follow

    def start(self):
        self.ent.moving.moveto(self.target)

    def step(self):
        if not self.ent.moving.intransit:
            if self.follow:
                self.start() # start action again
            else:
                self.done()
        
    def stop(self):
        self.ent.moving.stop()
