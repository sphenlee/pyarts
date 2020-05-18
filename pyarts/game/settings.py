'''
Settings
Global info needed to launch a game
'''

from pyarts.engine.event import Event

from pyarts.container import component

# TODO
mapfile = 'maps/test/map.json'

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
        if settings is None:
            settings = {
                'localpid': 0,
                'data': {
                    'core': mapfile,
                    'map': mapfile,
                    'save': mapfile
                }
            }

        self.localpid = settings['localpid']
        self.server = settings.get('server', False)
        self.join = settings.get('join', None)
        self.data_core = settings['data']['core']
        self.data_map = settings['data']['map']
        self.data_save = settings['data']['save']

        self.onload.emit(self)
        self.onready.emit(self)
