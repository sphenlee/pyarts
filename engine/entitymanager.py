'''
EntityManager

Container holding all of the entities
'''

class EntityManager(object):
    def __init__(self):
        self.entities = { } # entid -> entitiy

    def render(self):
        for ent in self.entities.itervalues():
            ent.render()
