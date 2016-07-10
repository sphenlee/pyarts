'''
Order
'''

class Order(object):
    NONE = 'none'
    AUTOCOMMAND = 'autocommand'
    ABILITY = 'ability'

    def __init__(self, type, ents, target, add):
        self.type = type
        self.ents = ents
        self.target = target
        self.add = add
        self.cycle = None # filled in by the game

class NoOrder(Order):
    def __init__(self):
        Order.__init__(self, Order.NONE, None, None, False)

class AutoCommandOrder(Order):
    def __init__(self, ents, target, add):
        Order.__init__(self, Order.AUTOCOMMAND, ents, target, add)

class AbilityOrder(Order):
    def __init__(self, ents, idx, add):
        Order.__init__(self, Order.ABILITY, ents, None, add) # target is optional
        self.idx = idx
