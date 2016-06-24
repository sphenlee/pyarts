'''
Screen

Manages the content of the whole window
'''

class Screen(object):
    #WIDTH = 1600
    #HEIGHT = 900
    WIDTH = 800
    HEIGHT = 600

    def __init__(self):
        pass

    def pre_activate(self):
        '''Hook for subclasses - to avoid needing to use super...'''

    def activate(self, window=None, parent=None, *args, **kwargs):
        self.window = window if window is not None else parent.window
        self.pre_activate(*args, **kwargs)
        self.window.push_handlers(self)

    def pause(self):
        self.window.pop_handlers()
