'''
Target
'''

class Target(object):
    pos = None
    eid = None

    def __init__(self, entities, obj):
        self.entities = entities

        if isinstance(obj, tuple) and len(obj) == 2:
            self.pos = obj
        elif isinstance(obj, int):
            self.eid = obj

    def ispos(self):
        return self.pos is not None

    def isent(self):
        return self.eid is not None

    def getpos(self):
        if self.ispos():
            return self.pos
        else:
            ent = self.entities.get(self.eid)
            return ent.locator.pos()
