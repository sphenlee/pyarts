'''
Order
'''

class Order(object):
    NONE = 0
    AUTOCOMMAND = 1
    ABILITY = 2

    def __init__(self, type, ents):
        self.type = type
        self.ents = ents

class NoOrder(Order):
    def __init__(self):
        Order.__init__(self, Order.NONE, None)

class AutoCommandOrder(Order):
    def __init__(self, ents, target, add):
        Order.__init__(self, Order.AUTOCOMMAND, ents)
        self.target = target
        self.add = add

class AbilityOrder(Order):
    def __init__(self, ents, idx):
        Order.__init__(self, Order.ABILITY, ents)
        self.idx = idx
        self.target = None # target is optional
