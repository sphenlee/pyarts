'''
EntityProto
A prototype for an entity. This defines stuff about an entity that
never changes individually. EntityProtos are local to each Team
and hence can be modified by upgrades.
'''


class EntityProto(object):
    def __init__(self, epid, team):
        self.epid = epid
        self.instances = set()
        self.team = team

    def __repr__(self):
        return f'<EntityProto {self.epid} "{self.name}"" owned by {self.team}>'

    def load(self, data):
        self.name = data['name']
        self.components = data['components']
        self.rank = data.get('rank', 1000)
        self.data = data

    def save(self):
        return self.data
