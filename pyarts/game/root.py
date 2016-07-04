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

    def load(self, settings):
        self.settings.load(settings)

        self.gamescreen.load()
        
    def save(self, datasink):
        self.game.save(datasink)
        self.gamescreen.save(datasink)
        