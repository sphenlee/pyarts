'''
Event
'''
from pyarts.log import debug, error

class Event(object):
    def __init__(self, debug=None):
        self.listeners = []
        self.debug = debug

    def add(self, func):
        self.listeners.append(func)

    def remove(self, func):
        try:
            idx = self.listeners.index(func)
            del self.listeners[idx]
        except ValueError:
            # methods may not compare equal even though they are the same...
            error('event remove of {0} from {1} failed', func, self)

    def emit(self, *args, **kwargs):
        for func in self.listeners:
            if self.debug:
                debug('emitting {0} to {1}(*{2}, **{3})', self.debug, func, args, kwargs)
            func(*args, **kwargs)
