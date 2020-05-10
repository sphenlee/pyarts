'''
Root
This is the component that instantiates the entire game
'''

import pyglet

from pyarts.container import component

# TODO
mapfile = 'maps/test/map.json'

@component
class Root(object):
    depends = ['settings', 'datasrc', 'game', 'gamestate']

    def __init__(self):
        pass

    def inject(self, **kwargs):
        self.__dict__.update(kwargs)

    def load(self, settings=None):
        if settings is None:
            settings = {
                'localpid': 0,
                'data': {
                    'core': mapfile,
                    'map': mapfile,
                    'save': mapfile
                }
            }
        self.settings.load(settings)
        
    def save(self, datasink):
        self.game.save(datasink)
        
    def update(self):
        self.gamestate.step()
