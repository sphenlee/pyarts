'''
DataSource
Manages loading all resources and data
'''

import json
import os.path as p

from .event import Event
from pyarts.container import component

@component
class DataSource(object):
    name = 'datasrc'
    depends = ['settings']

    def __init__(self):
        self.onload = Event(debug='datasrc.onload')
        self.onready = Event(debug='datasrc.onready')

    def inject(self, settings):
        settings.onready.add(self.load)

    def load(self, settings):
        self.save = json.load(open(settings.data_save))
        self.map = json.load(open(settings.data_map))
        self.core = json.load(open(settings.data_core))

        self.onload.emit()
        self.onready.emit()

    def getresource(self, name):
        return p.join('maps', 'test', name)

    def getentityprotos(self, tid):
        protos = self.map['entityprotos']
        protos.update(self.getteams()[str(tid)]['entityprotos'])
        return protos

    def getcontent(self, type):
        return self.map['content'][type]

    def getentity(self, eid):
        return self.save['entities'][str(eid)]

    def getteams(self):
        return self.save['teams']

    def getraces(self):
        return self.map['races']

    def getplayers(self):
        return self.save['players']

    def gettileset(self, name):
        return self.map['tileset'][name]

    def getloadedsectors(self):
        for xy in self.save['map']['loaded']:
            yield tuple(map(int, xy.split('/')))

    def getmapsector(self, x, y):
        return self.save['map']['sectors']['%d/%d' % (x, y)]

    def getmisc(self, key, *default):
        # can't use a None default here - use *args to detect no default
        # as being different to a None default
        if len(default) == 1:
            return self.save['misc'].get(key, default[0])
        else:
            return self.save['misc'][key]

