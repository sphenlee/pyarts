'''
QueueAction

Drains the ability queue of an entity
'''

from .action import Action
from .ability import AbilityAction

class QueueAction(Action):
    def __init__(self):
        pass

    def start(self):
        print 'starting queue drain', self.ent.queue.queue
        queue = self.ent.queue

        if not queue.queue:
            self.done()
            return

        ability, target = queue.queue.pop(0)
        print 'starting', ability, target
        self.ent.actions.now(AbilityAction(ability, target))

    def step(self):
        pass

    def stop(self):
        pass
