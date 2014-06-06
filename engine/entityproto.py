'''
EntityProto
A prototype for an entity. This defines stuff about an entity that
never changes individually. EntityProtos are local to each Team
and hence can be modified by upgrades.
'''

class EntityProto(object):
    def __init__(self, team):
        self.instances = set()
        self.team = team

    def load(self, data):
        self.name = data['name']
        self.sprite = data.get('sprite')
        self.components = data['components']

    