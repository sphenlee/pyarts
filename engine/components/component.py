'''
Component

Base class for all component classes
'''

class Component(object):
    def __init__(self, ent):
        self.ent = ent
        self.ent.components[self.name] = self
        setattr(self.ent, self.name, self)


all_components = { }

def register(name):
    def decorator(cls):
        all_components[name] = cls
        cls.name = name
        return cls
    return decorator
