'''
Settings
Global info needed to launch a game
'''

from pyarts.container import component

@component
class Settings(object):
    depends = []

    localpid = 0
    core = 'maps/test/map.json'

    def inject(self):
        pass
