'''
Root
This is the component that instantiates the entire game
'''

from pyarts.container import component

@component
class Root(object):
    depends = ['settings', 'gamescreen', 'datasrc', 'game']

    def __init__(self):
        pass

    def inject(self, **kwargs):
        self.__dict__.update(kwargs)

    def load(self, save, map, localpid):
        self.datasrc.load(save, map, self.settings.core)
        self.game.load(localpid)
        self.gamescreen.load(localpid)
        
        