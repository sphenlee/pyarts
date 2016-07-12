'''
Settings
Global info needed to launch a game
'''

from pyarts.engine.event import Event

from pyarts.container import component

@component
class Settings(object):
    depends = []

    localpid = 0

    def __init__(self):
        self.onload = Event()

    def inject(self):
        pass

    def load(self, settings):
        self.localpid = settings['localpid']
        self.data_core = settings['data']['core']
        self.data_map = settings['data']['map']
        self.data_save = settings['data']['save']

        self.onload.emit(self)