'''
Moving

Component required for an entity to use the MoveAction.


'''

from .component import Component, register

from ..pathfinder import distance

@register
class Moving(Component):
    depends = ['@pathfinder', 'locator', 'steering']

    def inject(self, pathfinder, locator, steering):
        self.pathfinder = pathfinder
        self.locator = locator
        self.steering = steering

    def configure(self, data):
        self.walk = 0x01 | 0x08 #data.get('walk', 1) # TODO
        self.waypoints = []
        self.intransit = False
    
    def load(self, data):
        if data:
            self.waypoints = data.get('waypoints')
            self.intransit = bool(self.waypoints)

    def step(self):
        if not self.waypoints:
            self.steering.stop()
            self.intransit = False
            return

        pt = self.waypoints[-1]

        self.steering.towards(pt)

        d = distance(pt, self.locator.pos())
        if d < 2:
            self.waypoints.pop()

    def save(self):
        return {
            'waypoints' : self.waypoints
        }

    def moveto(self, target, range=None):
        self.intransit = True

        start = self.locator.pos()
        goal = target.getpos()
        if target.isent():
            range = target.ent.locator.r

        path = self.pathfinder.findpath(start, goal, self.walk, range)
        if path is not None:
            self.waypoints[:] = path
            if range is None:
                self.waypoints[0] = goal
        else:
            print 'no path to', target
            self.stop()


    def stop(self):
        self.intransit = False

        del self.waypoints[:]
