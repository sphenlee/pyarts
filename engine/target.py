'''
Target
'''

class Target(object):
    pos = None
    eid = None

    def __init__(self, obj):
        if isinstance(obj, tuple) and len(obj) == 2:
            self.pos = obj
        elif isinstance(obj, int):
            self.eid = obj

    def ispos(self):
        return self.pos is not None

    def isent(self):
        return self.ent is not None
