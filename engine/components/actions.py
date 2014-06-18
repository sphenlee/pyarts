'''
Actions

Component for managing entity actions.
Holds a stack/queue of actions: actions can be pushed
to pause the current action and resume it later, or they can be queued
to be done after all other actions are done.
The queue can also be emptied to cancel everything.
'''

from .component import Component, register

@register
class Actions(Component):
    name = 'actions'
    depends = []

    def configure(self, data):
        self.queue = []

    def save(self):
        return { }

    def load(self, data):
        pass

    def step(self):
        ''' Step the current action '''
        if self.queue:
            self.queue[-1].step()

    def give(self, action):
        ''' Pause the current action and do this action first '''
        action.ent = self.ent
        self.queue.append(action)

    def done(self):
        ''' Current action is finished, remove it '''
        self.queue.pop()
