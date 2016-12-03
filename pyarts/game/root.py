'''
Root
This is the component that instantiates the entire game
'''

import pyglet

from pyarts.container import component

@component
class Root(object):
    depends = ['settings', 'gamescreen', 'datasrc', 'game', 'gamestate']

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
        
    def run(self, window):
        self.gamescreen.activate(window=window)

        pyglet.clock.schedule(self.update, 0.5)
        
    def update(self, dt, *args):
        self.gamescreen.update(dt)
        self.gamestate.step()
