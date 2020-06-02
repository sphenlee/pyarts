'''
Settings
Global info needed to launch a game
'''

from pyarts.engine.event import Event

from pyarts.container import component

# TODO
import os
mapfile = os.path.join(os.getcwd(), 'maps/test/map.json')

@component
class Settings(object):
    depends = []

    def __init__(self):
        self.onload = Event(debug='settings.onload')
        self.onready = Event(debug='settings.onready')

    def inject(self):
        pass

    def load(self, settings=None):
        # TODO
        default_settings = {
            'localpid': 0,
            'core': mapfile,
            'map': mapfile,
            'save': mapfile
        }

        default_settings.update(settings)
        settings = default_settings

        self.localpid = settings['localpid']
        self.server = settings.get('server', False)
        self.join = settings.get('join', None)
        self.data_core = settings['core']
        self.data_map = settings['map']
        self.data_save = settings['save']

        self.width = int(settings.get('width', 800))
        self.height = int(settings.get('height', 600))

        self.onload.emit(self)
        self.onready.emit(self)
