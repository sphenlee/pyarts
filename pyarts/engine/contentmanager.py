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
    depends = ['engine', 'datasrc', 'scripting']

    def __init__(self):
        self.abilities = {}

    def inject(self, engine, datasrc, scripting):
        self.eng = engine
        self.datasrc = datasrc
        self.scripting = scripting

    def load(self):
        for name, data in self.datasrc.getcontent('abilities').iteritems():
            self.abilities[name] = Ability(data, self.scripting)

        
    def getability(self, name):
        return self.abilities[name]