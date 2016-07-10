'''
QueueAction

Drains the ability queue of an entity
'''

from .action import Action
from .ability import AbilityAction

class QueueAction(Action):
    def __init__(self):
        self.now = None

    def start(self):
        print 'starting queue drain', self.ent.queue.queue
        queue = self.ent.queue

        if not queue.queue:
            self.now = None
            self.done()
            return

        ainst, target = queue.queue.pop(0)
        self.now = ainst
        print 'starting', ainst, target
        self.ent.actions.now(AbilityAction(ainst, target))

    def step(self):
        pass

    def stop(self):
        pass
