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

    def getentities(self):
        return self.save['entities']

    def getteams(self):
        return self.save['teams']

    def getplayers(self):
        return self.save['players']

    def getmapsector(self, x, y):
        return self.map['map']['sectors'][x][y]

    def getmisc(self, key):
        return self.save['misc'][key]
