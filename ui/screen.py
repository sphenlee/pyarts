'''
Screen

Manages the content of the whole window
'''

class Screen(object):
    def __init__(self, parent=None, window=None):
        self.window = window if window is not None else parent.window

    def on_activate(self):
        '''Hook for subclasses - to avoid needing to use super...'''

    def activate(self):
        self.on_activate()
        self.window.push_handlers(self)
