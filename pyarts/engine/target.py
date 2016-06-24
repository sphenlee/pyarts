'''
Target
'''

class Target(object):
    pos = None
    ent = None

    def __init__(self, obj):
        if isinstance(obj, tuple) and len(obj) == 2:
            self.pos = obj
        elif isinstance(obj, int):
            raise TypeError('Target can\'t take EIDs now')
        else:
            self.ent = obj

    def __repr__(self):
        return '<Target %r>' % (self.pos if self.ispos() else self.ent)

    def ispos(self):
        return self.pos is not None

    def isent(self):
        return self.ent is not None

    def getpos(self):
        if self.ispos():
            return self.pos
        else:
            return self.ent.locator.pos()
