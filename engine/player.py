'''
Player
'''

from .order import NoOrder

class Player(object):
    def __init__(self):
        self.teams = []
        noorder = NoOrder()
        self.orders = [noorder] * 256

    def save(self):
        return {
            "teams" : self.teams
        }

    def load(self, data):
        self.teams = data["teams"]

    def getorder(self, cycle):
        return self.orders[cycle & 0xFF]

    def addorder(self, cycle, order):
        self.orders[cycle & 0xFF] = order
