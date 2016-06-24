'''
Order
'''

class Order(object):
    NONE = 'none'
    AUTOCOMMAND = 'autocommand'
    ABILITY = 'ability'

    def __init__(self, type, ents, target):
        self.type = type
        self.ents = ents
        self.target = target
        self.cycle = None # filled in by the game

class NoOrder(Order):
    def __init__(self):
        Order.__init__(self, Order.NONE, None, None)

class AutoCommandOrder(Order):
    def __init__(self, ents, target, add):
        Order.__init__(self, Order.AUTOCOMMAND, ents, target)
        self.add = add

class AbilityOrder(Order):
    def __init__(self, ents, idx):
        Order.__init__(self, Order.ABILITY, ents, None) # target is optional
        self.idx = idx
