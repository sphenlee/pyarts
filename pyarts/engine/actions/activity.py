'''
ActivityAction

A custom action
'''

from .action import Action

class ActivityAction(Action):
    def __init__(self, activity):
        self.activity = activity

    def start(self):
        

    def step(self):
        if not self.ent.moving.intransit:
            if self.follow:
                self.start() # start action again
            else:
                self.done()
        
    def stop(self):
        self.ent.moving.stop()
