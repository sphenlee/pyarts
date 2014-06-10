'''
DataSink
'''

import json

class DataSink(object):
    def __init__(self, filename):
        self.filename = filename
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

    def setmisc(self, key, val):
        self.save.setdefault('misc', {})[key] = val

    def commit(self):
        with open(self.filename, 'w') as fp:
            json.dump(self.save, fp)

