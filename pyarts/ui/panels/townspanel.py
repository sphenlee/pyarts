'''
TownsPanel

Shows towns and resource info
'''
import pyglet

from ..screen import Screen
from .. import cairosg as sg

from pyarts.container import component

@component
class TownsPanel(object):
    depends = ['imagecache', 'engine']


    def __init__(self):
        self.WIDTH = Screen.WIDTH // 4
        self.HEIGHT = 36

        self.towns = []

        self.sg = sg.SceneGraph(self.WIDTH, self.HEIGHT).paint(0, 0, 0, 0.8)
        self.grid = sg.Grid(0, 4)
        self.sg.append(self.grid)

    def inject(self, imagecache, engine):
        self.imagecache = imagecache
        engine.ontowncreated.add(self.townadded)

    def townadded(self, team, town):
        print 'added town', team, town

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

        self.towns.append((text1, text2, icon1, icon2))

        self.update_resources(town)

    def update_resources(self, town):
        self.towns[0][0].text = str(town.resources.resource)
        self.towns[0][1].text = str(town.resources.energy)

    def draw(self):
        img = self.sg.getimage()
        s = pyglet.sprite.Sprite(img, x=Screen.WIDTH - self.WIDTH, y=Screen.HEIGHT - self.HEIGHT)
        s.draw()
