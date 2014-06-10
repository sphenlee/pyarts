'''
Component

Base class for all component classes
'''

class Component(object):
    def __init__(self, ent):
        self.ent = ent
        self.ent.components[self.name] = self
        setattr(self.ent, self.name, self)

    def __hash__(self):
        return hash((self.ent.eid, self.name))

    def __eq__(self, rhs):
        return self.ent.eid == rhs.ent.eid and self.name == rhs.name

    def configure(self, data):
        raise NotImplemented()

    def load(self):
        raise NotImplemented()

    def save(self):
        raise NotImplemented()

    def inject(self, **comps):
        assert len(comps) == 0

    def step(self):
        pass

_all_components = { }

def register(cls):
    _all_components[cls.name] = cls
    return cls

def getcomponentclass(name):
    return _all_components[name]
