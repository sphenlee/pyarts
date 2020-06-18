'''
AbilityPanel

Renders the buttons for entity abilities
'''

from .. import cairosg as sg

from pyarts.container import component

MAX_ABILITIES = 6 # well the maximum we will show

EMPTY_PAINT = sg.ColourPaint(0, 0, 0, 0.8)

@component
class AbilityPanel(object):
    depends = ['imagecache', 'game', 'local']

    WIDTH = 96*3
    HEIGHT = 96*2

    def __init__(self):
        self.sg = sg.SceneGraph(self.WIDTH, self.HEIGHT).paint(0, 0, 0, 0.8)        
        self.grid = sg.Grid(2, 3)
        for i in range(MAX_ABILITIES):
            self.grid.append(sg.Rect().paint(EMPTY_PAINT))
        self.sg.append(self.grid)

    def inject(self, imagecache, game, local):
        self.imagecache = imagecache
        self.game = game
        self.local = local

        self.game.onselectionchange.add(self.update)

    def update(self):
        try:
            ent = self.game.selection[0]
        except IndexError:
            ent = None

        if ent and ent.has('abilities') and ent.ownedby(self.local.player):
            ab = ent.abilities
            n = len(ab)

            for i in range(6):
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
            for i in range(6):
                self.grid.children[i] = sg.Rect().paint(EMPTY_PAINT)

        self.sg.mark_dirty()

    def step(self):
        if self.game.selection:
            ent = self.game.selection[0]
            if ent.has('abilities') and ent.ownedby(self.local.player):
                ab = ent.abilities
                
                for i in range(len(ab)):
                    if ab[i].ability.cooldown > 0:
                        percent = float(ab[i].cooldown) / ab[i].ability.cooldown
                        self.grid.children[i].children[1].paint(1, 0, 0, percent)


    def render(self):        
        return self.sg.getimage()

    def destination(self, w, h):
        return (w - self.WIDTH, h - self.HEIGHT)