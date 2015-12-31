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

    def is_town_cost(self):
        return self.resource is not None or self.energy is not None

    def is_entity_cost(self):
        return self.mana is not None


    @staticmethod
    def from_data(data):
        return Cost(**data)

class ResourcePool(object):
    def __init__(self):
        self.resource = 0
        self.energy = 0

    def sufficient(self, cost):
        return self.resource > cost.resource and self.energy > cost.energy

    def deduct(self, cost):
        self.resource -= cost.resource
        self.energy -= cost.energy

        print 'paid %d, %d, resources now %d, %d' % (cost.resource, cost.energy,
            self.resource, self.energy)

    def add(self, kind, amt):
        if kind == 'resource':
            self.resource += amt
        elif kind == 'energy':
            self.energy += amt

    def load(self, data):
        self.resource = data.get('resource', 0)
        self.energy = data.get('energy', 0)

    def save(self):
        return {
            'resource' : self.resource,
            'energy' : self.energy
        }
