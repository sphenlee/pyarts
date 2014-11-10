'''
Screen

Manages the content of the whole window
'''

class Screen(object):
    WIDTH = 1600
    HEIGHT = 900

    def __init__(self, parent=None, window=None):
        self.window = window if window is not None else parent.window

    def pre_activate(self):
        '''Hook for subclasses - to avoid needing to use super...'''

    def activate(self, *args, **kwargs):
        self.pre_activate(*args, **kwargs)
        self.window.push_handlers(self)

    def pause(self):
        self.window.pop_handlers()
