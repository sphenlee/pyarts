'''
Component

Base class for all component classes
'''

class Component(object):
    def __init__(self, ent):
        self.ent = ent
        self.ent.components[self.name] = self
        setattr(self.ent, self.name, self)

    def load(self):
        raise NotImplemented()

    def save(self):
        raise NotImplemented()

    def inject(self, **comps):
        assert len(comps) == 0

all_components = { }

def register(cls):
    all_components[cls.name] = cls
    return cls
