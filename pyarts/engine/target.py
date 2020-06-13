'''
Target
'''

class Target(object):
    pos = None
    ent = None

    def __init__(self, obj):
        if isinstance(obj, tuple) and len(obj) == 2:
            if isinstance(obj[0], float) or isinstance(obj[1], float):
                raise TypeError('positions should be integers!')

            self.pos = obj
        elif isinstance(obj, int):
            raise TypeError('Target can\'t take EIDs now')
        else:
            self.ent = obj

    def __repr__(self):
        if self.ispos():
            return f'<Target {self.pos[0]},{self.pos[1]}>'
        else:
            return f'<Target {self.ent!r}>'

    def ispos(self):
        return self.pos is not None

    def isent(self):
        return self.ent is not None

    def getpos(self):
        if self.ispos():
            return self.pos
        else:
            return self.ent.locator.pos()
