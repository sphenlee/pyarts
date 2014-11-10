'''
DataSink
'''

import json
import os.path as p

class DataSink(object):
    def __init__(self, filename):
        self.filename = filename
        self.dirname = p.dirname(filename)
        self.save = {}

    def addentityproto(self, tid, proto):
        protos = self.save.setdefault('entityprotos', {}).setdefault(tid, {})
        protos[proto.name] = proto

    def addentity(self, eid, ent):
        self.save.setdefault('entities', {})[eid] = ent

    def addteam(self, team):
        self.save.setdefault('teams', []).append(team)

    def addplayer(self, player):
        self.save.setdefault('players', []).append(player)

    def addmapsector(self, x, y, sec):
        self.save.setdefault('map', {}).setdefault('sectors', {})['%d/%d' % (x, y)] = sec

    def setloadedsectors(self, loaded):
        self.save.setdefault('map', {})['loaded'] = ['%d/%d' % (x, y) for x, y in loaded]

    def setmisc(self, key, val):
        self.save.setdefault('misc', {})[key] = val

    def addresource(self, fname, data):
        with open(p.join(self.dirname, fname), 'w') as fp:
            fp.write(data)

    def commit(self):
        with open(self.filename, 'w') as fp:
            json.dump(self.save, fp)

