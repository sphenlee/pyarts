'''
TownsPanel

Shows towns and resource info
'''

from .. import cairosg as sg

from pyarts.container import component
from pyarts.log import debug, trace

@component
class TownsPanel(object):
    depends = ['imagecache', 'engine', 'local']


    def __init__(self):
        self.WIDTH = 200
        self.HEIGHT = 36

        self.resources = {}

        self.sg = sg.SceneGraph(self.WIDTH, self.HEIGHT).paint(0, 0, 0, 0.8)
        self.grid = sg.Grid(0, 4)
        self.sg.append(self.grid)

    def inject(self, imagecache, engine, local):
        self.imagecache = imagecache
        self.local = local

        engine.ontowncreated.add(self.townadded)


    def step(self):
        pass

    def townadded(self, team, town):
        debug('added town', team, town)

        #if not team.controlled_by(self.local.player):
        #    print('local player doesn\'t control this town')
        #    return

        resource = self.imagecache.getimage(town.race['resource_icon'])
        icon1 = sg.Rect().paint(resource)
        #icon1.scale = 1/8.0

        energy = self.imagecache.getimage(town.race['energy_icon'])
        icon2 = sg.Rect().paint(energy)
        #icon2.scale = 1/8.0

        text1 = sg.Text('').paint(1, 1, 1)
        text2 = sg.Text('').paint(1, 1, 1)

        g = self.grid
        g.rows += 1
        g.append(icon1)
        g.append(text1)
        g.append(icon2)
        g.append(text2)

        self.resources[town.resources.rpid] = (text1, text2)
        
        town.resources.onchange.add(self.update_resources)
        # refresh the number right now
        self.update_resources(town.resources)

    def update_resources(self, resources):
        trace('update', resources)
        self.resources[resources.rpid][0].text = str(resources.resource)
        self.resources[resources.rpid][1].text = str(resources.energy)
        self.sg.repaint()

    def render(self):
        return self.sg.getimage()

    def destination(self, w, h):
        return (w - self.WIDTH, 0)