'''
Event
'''

class Event(object):
    def __init__(self):
        self.listeners = []

    def add(self, func):
        self.listeners.append(func)

    def emit(self, *args, **kwargs):
        for func in self.listeners:
            func(*args, **kwargs)
