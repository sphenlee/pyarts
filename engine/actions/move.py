'''
MoveAction

Performs high level motion of an entity
'''

class MoveAction(Action):
    def __init__(self, target, range=0):
        self.target = target
        self.range = range

