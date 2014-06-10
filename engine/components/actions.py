'''
Actions

Component for managing entity actions
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
        if self.queue:
            self.queue[-1].step()

    def give(self, action):
        action.ent = self.ent
        self.queue.append(action)

    def done(self):
        self.queue.pop()
