'''
Moving

Component required for an entity to use the MoveAction.


'''

from .component import Component, register

from ..sector import Sector

def parse_walk(value):
    parts = value.toupper().split('|')
    walk = 0
    for part in parts:
        walk |= getattr(Sector, 'WALK_' + part)

    return walk

def raw_distance(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

def distance(ent, pt):
    ept = ent.locator.pos()
    print(f'distance ept={ept}')
    return raw_distance(ent.locator.pos(), pt) - ent.locator.r**2
    

@register
class Moving(Component):
    depends = ['@pathfinder', 'locator', 'steering']

    def inject(self, pathfinder, locator, steering):
        self.pathfinder = pathfinder
        self.locator = locator
        self.steering = steering

    def configure(self, data):
        if data and 'walk' in data:
            self.walk = parse_walk(data['walk'])
        else:
            self.walk = Sector.WALK_GROUND | Sector.WALK_FOOT

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

        d = distance(self.ent, pt)
        print(f'moving d={d}')
        if d <= 0:
            self.waypoints.pop()
            print(f'waypoints remaining: {self.waypoints}')

    def save(self):
        return {
            'waypoints' : self.waypoints
        }

    def moveto(self, target, range=None):
        self.intransit = True

        start = self.locator.pos()
        goal = target.getpos()
        
        path = self.pathfinder.findpath(start, goal, self.walk, range)
        if path is not None:
            self.waypoints[:] = list(path)
            if len(self.waypoints) > 1:
                # the first point is just the centre of the current cell,
                # so if we have more than one point we skip this
                self.waypoints.pop()

            if range is None:
                # for an exact target we don't want the centre of the destination
                # cell, so replace it with the actual goal
                self.waypoints[0] = goal
        else:
            print('no path to', target)
            self.stop()


    def stop(self):
        self.intransit = False

        del self.waypoints[:]
