'''
Collisions
Each frame computes collisions between entities.
Performed once to save each entity doing it again.
'''

from pyarts.container import component

from .sector import distance2

@component
class Collisions(object):
    depends = ['map']

    def __init__(self):
        pass

    def inject(self, map):
        self.map = map

    def step(self):
        self.collisions = {}

        locators = list(self.map.locators)

        # TODO this is n^2 because it's easier :(
        for a in locators:
            coll = []

            ar2 = a.r * a.r
            ax, ay = a.pos()

            for b in locators:
                if a.eid == b.eid:
                    continue # skip self collision

                d = distance2(ax, ay, b.x, b.y)
                r2 = ar2 + b.r*b.r
                if d < r2:
                    #print 'entity %d has hard-collided with %d' % (a.eid, b.eid)
                    coll.append((True, b.ent))
                elif d < r2 * 5:
                    #print 'entity %d has soft-collided with %d' % (a.eid, b.eid)
                    coll.append((False, b.ent))

            self.collisions[a.eid] = coll


    def getcollisions(self, eid):
        return self.collisions.get(eid)
