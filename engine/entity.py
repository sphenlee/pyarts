'''
Entity

Entities represent every object with behaviour in a game.
Entities have an ID (eid) which is unique, and a collection
of components.  They have no other behaviour except what is
specified by the components.
'''

class Entity(object):
    def __init__(self, eid):
        self.eid = eid
        self.components = { }

    def save(self):
        data = { }
        for name, comp in components.iteritems():
            data[name] = comp.save()
        return data

    def load(self, data):
        data = { }
        for name, comp in components.iteritems():
            data[name] = comp.save()
        return data
