'''
AbilityPanel

Renders the buttons for entity abilities
'''

from .. import cairosg as sg
from ..screen import Screen

from pyarts.container import component

MAX_ABILITIES = 6 # well the maximum we will show

EMPTY_PAINT = sg.ColourPaint(0, 0, 0, 0.8)

@component
class AbilityPanel(object):
    depends = ['imagecache', 'game']

    WIDTH = 128*2
    HEIGHT = 128*3

    def __init__(self):
        self.sg = sg.SceneGraph(self.WIDTH, self.HEIGHT).paint(0, 0, 0, 0.8)        
        self.grid = sg.Grid(3, 2)
        for i in xrange(MAX_ABILITIES):
            self.grid.append(sg.Rect().paint(EMPTY_PAINT))
        self.sg.append(self.grid)

    def inject(self, imagecache, game):
        self.imagecache = imagecache
        self.game = game

        self.game.onselectionchange.add(self.update)

    def update(self):
        ent = self.game.selection[0]

        if ent.has('abilities') and ent.ownedby(self.game.localplayer):
            ab = ent.abilities
            n = len(ab)

            for i in xrange(6):
                if i >= n:
                    self.grid.children[i] = sg.Rect().paint(EMPTY_PAINT)
                else:
                    img = self.imagecache.getimage(ab[i].ability.image)
                    c = sg.Canvas()
                    c.append(sg.Rect().paint(img))
                    if ab[i].ability.cooldown > 0:
                        percent = float(ab[i].cooldown) / ab[i].ability.cooldown
                        c.append(sg.Rect().paint(1, 0, 0, percent))
                    self.grid.children[i] = c
                    

        else:
            for i in xrange(6):
                self.grid.children[i] = sg.Rect().paint(EMPTY_PAINT)

    def draw(self):
        if self.game.selection:
            ent = self.game.selection[0]
            if ent.has('abilities') and ent.ownedby(self.game.localplayer):
                ab = ent.abilities
                
                for i in xrange(len(ab)):
                    if ab[i].ability.cooldown > 0:
                        percent = float(ab[i].cooldown) / ab[i].ability.cooldown
                        self.grid.children[i].children[1].paint(1, 0, 0, percent)

        self.sg.drawat(x=Screen.WIDTH - self.WIDTH, y=0)
