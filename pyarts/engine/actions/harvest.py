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
        self.proto = seed.proto
        self.pos = seed.locator.pos()

    def start(self):
        h = self.ent.harvester
        if h.full():
            h.gotodropoff()
            self.state = RETURNING
        else:
            self.state = INIT
    
    def interruptible(self):
        if self.state == HARVESTING: # TODO and self.resource.unplace_harvester:
            return False
        else:
            return True

    def step(self):
        #print 'harvester state is %s' % self.state
        h = self.ent.harvester

        if self.state == INIT:
            if h.gotopickup(self.proto, self.pos):
                self.state = MOVING
            else:
                self.done()

        elif self.state == MOVING:
            if not h.intransit:
                h.startharvest()
                self.state = HARVESTING

        elif self.state == HARVESTING:
            if h.full():
                h.stopharvest()
                if h.gotodropoff():
                    self.state = RETURNING
                else:
                    self.done()

        elif self.state == RETURNING:
            if not h.intransit:
                h.do_dropoff()
                self.state = INIT

    def stop(self):
        self.ent.harvester.stopharvest()
        self.ent.moving.stop()
