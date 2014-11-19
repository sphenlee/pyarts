'''
Action

Abstract base class for all actions
'''

class Action(object):
    ent = None

    def start(self):
        pass

    def suspend(self):
        pass

    def stop(self):
        pass

    def step(self):
        raise NotImplementedError()
