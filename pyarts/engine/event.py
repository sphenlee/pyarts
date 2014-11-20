'''
Event
'''

class Event(object):
    def __init__(self):
        self.listeners = []

    def add(self, func):
        self.listeners.append(func)

    def remove(self, func):
        try:
            idx = self.listeners.index(func)
            del self.listeners[idx]
        except ValueError:
            # methods may not compare equal even though they are the same...
            print 'remove failed...'

    def emit(self, *args, **kwargs):
        for func in self.listeners:
            func(*args, **kwargs)
