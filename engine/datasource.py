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
        return open(p.join('maps', 'test', name)).read()

    def getentityproto(self, name):
        return self.map['entityprotos'][name]
        