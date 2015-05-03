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

    def getorder(self, cycle):
        return self.orders[cycle & 0xFF]

    def clearorder(self, cycle):
        self.orders[cycle & 0xFF] = None

    def addorder(self, cycle, order):
        self.orders[cycle & 0xFF] = order
