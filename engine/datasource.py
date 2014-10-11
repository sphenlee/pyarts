'''
DataSource
Manages loading all resources and data
'''

import json
import os
p = os.path

class DataSource(object):
    def __init__(self, save, map, core):
        self.save = json.load(open(save))
        self.map = json.load(open(map))
        self.core = json.load(open(core))

    def getresource(self, name):
        return p.join('maps', 'test', name)

    def getentityprotos(self, tid):
        protos = self.map['entityprotos']
        protos.update(self.getteams()[tid]['entityprotos'])
        return protos

    def getcontent(self, type):
        return self.map['content'][type]

    def getentity(self, eid):
        return self.save['entities'][str(eid)]

    def getteams(self):
        return self.save['teams']

    def getplayers(self):
        return self.save['players']

    def gettileset(self):
        return self.map['map']['tileset']

    def getloadedsectors(self):
        for xy in self.map['map']['loaded']:
            yield tuple(map(int, xy.split('/')))

    def getmapsector(self, x, y):
        return self.map['map']['sectors']['%d/%d' % (x, y)]

    def getmisc(self, key, *default):
        # can't use a None default here - use *args to detect no default
        # as being different to a None default
        if len(default) == 1:
            return self.save['misc'].get(key, default[0])
        else:
            return self.save['misc'][key]

