'''
Player
'''

from .order import NoOrder

class Player(object):
    HUMAN = 'human'
    PASSIVE = 'passive'
    AI = 'ai'

    def __init__(self):
        self.teams = []
        noorder = NoOrder()
        self.orders = [noorder] * 256

    def save(self):
        return {
            "teams" : self.teams,
            "type" : self.type
        }

    def load(self, data):
        self.teams = data["teams"]
        self.type = data["type"]
        self.tidmask = 0

        for t in self.teams:
            self.tidmask |= (1 << t)

    def getorder(self, cycle):
        return self.orders[cycle & 0xFF]

    def clearorder(self, cycle):
        self.orders[cycle & 0xFF] = None

    def addorder(self, order):
        #if self.orders[order.cycle & 0xFF] is not None:
        #    print 'WARNING multiple orders for a single player'
        #else:
        self.orders[order.cycle & 0xFF] = order
