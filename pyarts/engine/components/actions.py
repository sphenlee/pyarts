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
        ''' Cancel all actions and do this instead '''
        action.ent = self.ent

        if self.queue:
            self.queue[-1].suspend()
            for ac in self.queue:
                ac.stop()

        del self.queue[:]

        self.queue.append(action)
        action.start()

    def now(self, action):
        ''' Pause the current action and do this action first '''
        action.ent = self.ent
        
        if self.queue:
            self.queue[-1].suspend()
        
        self.queue.append(action)
        action.start()

    def later(self, action):
        ''' Do this action once all other actions are done '''
        action.ent = self.ent
        
        self.queue.insert(0, action)

    def done(self, action):
        ''' Action is finished, remove it '''
        if self.queue[-1] == action:
            # action is currently executing - start the next action
            self.queue.pop()
            if self.queue:
                self.queue[-1].start()
        else:
            # else just remove from queue
            self.queue.remove(action)
