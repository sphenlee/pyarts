'''
Harvest action

A complex action involving a unit cycling between a resource source and
a resource sink
'''

from .action import Action

INIT = 'init'
MOVING = 'moving'
HARVESTING = 'harvesting'
RETURNING = 'returning'

class HarvestAction(Action):
    def __init__(self, seed):
        self.seed = seed

    def start(self):
        h = self.ent.harvester
        if h.full():
            h.gotodropoff()
            self.state = RETURNING
        else:
            self.state = INIT
            
    def step(self):
        #print 'harvester state is %s' % self.state
        h = self.ent.harvester

        if self.state == INIT:
            h.gotopickup(self.seed)
            self.state = MOVING

        elif self.state == MOVING:
            if not h.intransit:
                h.startharvest()
                self.state = HARVESTING

        elif self.state == HARVESTING:
            if h.full():
                h.stopharvest()
                h.gotodropoff()
                self.state = RETURNING

        elif self.state == RETURNING:
            if not h.intransit:
                h.dropoff()
                self.state = INIT

    def stop(self):
        self.ent.harvester.stopharvest()
        self.ent.moving.stop()
