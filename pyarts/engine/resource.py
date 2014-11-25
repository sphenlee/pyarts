'''
Resource

Hold Costs and ResourcePool
'''

class Cost(object):
    __slots__ = ['resource', 'energy', 'mana']

    def __init__(self, resource=None, energy=None, mana=None):
        self.resource = resource
        self.energy = energy
        self.mana = mana


class ResourcePool(object):
    def __init__(self):
        self.resource = 0
        self.energy = 0

    