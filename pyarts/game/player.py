'''
Player
'''
from pyarts.log import error

from .order import NoOrder

class Player(object):
    HUMAN = 'human'
    PASSIVE = 'passive'
    AI = 'ai'

    def __init__(self):
        self.teams = []
        self.orders = {}
        for i in range(16):
            self.orders[i] = NoOrder()

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
        return self.orders.get(cycle)

    def clearorder(self, cycle):
        self.orders.pop(cycle, None)

    def addorder(self, order):
        if order.cycle in self.orders:
            error('WARNING multiple orders for a single player')
        
        self.orders[order.cycle] = order
