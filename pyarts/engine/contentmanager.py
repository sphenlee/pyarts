'''
ContentManager

A place to store various other game objects that need configuration data:
 * Abilities
 * Activities
 * Status Effects
 * possibly others...
'''

from .ability import Ability

from pyarts.container import component

@component
class ContentManager(object):
    depends = ['datasrc', 'scripting']

    def __init__(self):
        self.abilities = {}

    def inject(self, datasrc, scripting):
        self.datasrc = datasrc
        self.datasrc.onload.add(self.load)
        self.scripting = scripting

    def load(self):
        for name, data in self.datasrc.getcontent('abilities').iteritems():
            self.abilities[name] = Ability(data, self.scripting)

        
    def getability(self, name):
        return self.abilities[name]