'''
Component

Base class for all component classes.

Methods are in lifecycle order.
'''

class Component(object):
    name = 'noname' # overriden by register function

    def __init__(self, ent):
        self.ent = ent
        self.ent.components[self.name] = self
        setattr(self.ent, self.name, self)
        self.configured = False

    def __hash__(self):
        return hash((self.ent.eid, self.name))

    def __eq__(self, rhs):
        return self.ent.eid == rhs.ent.eid and self.name == rhs.name

    def inject(self, **comps):
        ''' Called with keyword args for each dependency declared '''
        # if there are no dependencies you can leave unimplemented (hence this assert)
        assert len(comps) == 0

    def configure(self, data):
        '''
        Load data from the entity's proto - shared by all
        entities of this type
        '''
        raise NotImplementedError

    def load(self):
        '''
        Load entity specific data
        '''
        raise NotImplementedError

    def step(self):
        ''' Step the component - called one each turn '''
        pass

    def save(self):
        '''
        Save the component's state - the data returned here will
        be passed to the load method when the game is loaded
        '''
        raise NotImplementedError


_all_components = { }

def register(cls):
    cls.name = cls.__name__.lower()
    _all_components[cls.name] = cls
    return cls

def getcomponentclass(name):
    return _all_components[name]
