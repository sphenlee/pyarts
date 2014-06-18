'''
ContentManager

A place to store various other game objects that need configuration data:
 * Abilities
 * Activities
 * Status Effects
 * possibly others...
'''

from .ability import Ability

class ContentManager(object):
    def __init__(self):
        self.abilities = {}
        self.activities = {}
        self.statuseffects = {}

    def load(self, datasrc):
        for name, data in datasrc.getcontent('abilities').iteritems():
            self.abilities[name] = Ability(data)

        
    def getability(self, name):
        return self.abilities[name]