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
    depends = ['datasrc', 'components']

    def __init__(self):
        self.abilities = {}

    def inject(self, datasrc, components):
        self.datasrc = datasrc
        self.datasrc.onload.add(self.load)

        self.components = components

    def load(self):
        for name, data in self.datasrc.getcontent('abilities').items():
            self.abilities[name] = self.components.construct('ability', data)

    def getability(self, name):
        return self.abilities[name]
