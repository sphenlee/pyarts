'''
Moving

Component required for an entity to use the MoveAction.


'''

from .component import Component, register

from ..sector import Sector

from pyarts.log import warn, trace, debug

def parse_walk(value):
    parts = value.upper().split('|')
    walk = 0
    for part in parts:
        walk |= getattr(Sector, 'WALK_' + part)

    return walk

def raw_distance(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

def distance(ent, pt):
    ept = ent.locator.pos()
    #print(f'distance ept={ept}')
    return raw_distance(ent.locator.pos(), pt) # - ent.locator.r**2
    

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
    
    def load(self, data):
        self.target = data.get('target')
        self.range = data.get('range')
        self.waypoints = data.get('waypoints', [])
        #self.intransit = bool(self.waypoints)

    @property
    def intransit(self):
        return self.target is not None

    def set_incorporeal(self, val):
        '''
        Allows a unit to pass through buildings, trees etc...
        Used to allow units to "exit" a building when constructing
        '''
        if val:
            self.walk &= (0xFF ^ Sector.WALK_FOOT)
        else:
            self.walk |= Sector.WALK_FOOT

    def step(self):
        if not self.target:
            return

        if not self.waypoints:
            d = distance(self.ent, self.target.getpos())
            if d <= self.range**2:
                trace('{0} reached target {1}', self.ent, self.target)
                self.stop()
                return

            else:
                trace('{0} not at target {1} yet, d={2}', self.ent, self.target, d)
                self.findpath()

        if not self.waypoints:
            # have to check waypoints again - findpath may not be able to find one
            return

        pt = self.waypoints[-1]

        self.steering.towards(pt)

        d = distance(self.ent, pt)
        trace('{0} distance to waypoint at {1} = {2}', self.ent, pt, d)
        if d <= self.range**2:
            trace('{0} reached waypoint at {1}', self.ent, pt)
            self.waypoints.pop()


    def save(self):
        return {
            'target': self.target,
            'range': self.range,
            'waypoints' : self.waypoints,
        }


    def moveto(self, target, range=None):
        debug('moveto {0}@{1}', target, range)
        self.target = target
        self.range = range
        self.findpath()


    def findpath(self):
        start = self.locator.pos()
        goal = self.target.getpos()

        if self.range is None and self.target.isent():
            self.range = self.target.ent.locator.r + self.locator.r
        else:
            self.range = 0#self.locator.r
        
        path = self.pathfinder.findpath(start, goal, self.walk, self.range)
        if path:
            # waypoints list is backwards
            # popping off completed points from the end is cheaper
            self.waypoints[:] = list(reversed(path))

            # if len(self.waypoints) > 1:
            #     # the first point is just the centre of the current cell,
            #     # so if we have more than one point we skip this
            #     self.waypoints.pop()

            # if self.range == 0:
            #     # for an exact target we don't want the centre of the destination
            #     # cell, so replace it with the actual goal
            #     self.waypoints[0] = goal
        else:
            warn('no path to', self.target)
            self.stop()


    def stop(self):
        self.target = None
        self.range = None
        del self.waypoints[:]
        self.steering.stop()
