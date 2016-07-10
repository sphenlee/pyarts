'''
Queue

A component for entities that have a queue of abilities to
perform (usually buildings)
'''

from .component import Component, register
from ..actions.queue import QueueAction

@register
class Queue(Component):
    depends = [ 'actions' ]

    def inject(self, actions):
        self.actions = actions

    def configure(self, data):
        self.queue = []
        
    def save(self):
        pass

    def load(self, data):
        pass

    def step(self):
        pass

    def add(self, ability, target):
        print 'queueing', ability, target
        startqueue = len(self.queue) == 0
        
        self.queue.append((ability, target))

        if startqueue:
            self.actions.now(QueueAction())
