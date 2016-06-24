'''
Settings
Global info needed to launch a game
'''

from pyarts.container import component

@component
class Settings(object):
    depends = []

    def __init__(self):
        self.core = 'maps/test/map.json'

    def inject(self):
        pass
