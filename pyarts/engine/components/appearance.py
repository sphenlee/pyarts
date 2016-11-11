'''
Appearance

Component to make a component visible on the game screen
'''

from .component import Component, register

@register
class Appearance(Component):
    VISIBLE_ALWAYS = 'always'
    VISIBLE_VISITED = 'visited'
    VISIBLE_VIEWING = 'viewing'


    depends = ['locator', '@sprites', '@map']

    def inject(self, locator, sprites, map):
        self.locator = locator
        self.sprites = sprites
        self.map = map

    def configure(self, data):
        self.sprite = self.sprites.new_sprite(data['sprite'], self.locator.r * 2)
        self.portrait = data['portrait']
        self.visibility = data.get('visibility', self.VISIBLE_VIEWING)

    def save(self):
        return {}

    def load(self, data):
        pass

    def step(self):
        if self.sprite is None:
            return

        visible = False
        if not self.locator.placed:
            visible = False
        elif self.visibility == self.VISIBLE_ALWAYS:
            visible = True
        else:
            pt = self.locator.x, self.locator.y
            cell = self.map.pos_to_cell(*pt)
            sec = self.map.sector_at_cell(*cell)
            off = self.map.cell_to_offset(*cell)
            if sec:
                if self.visibility == self.VISIBLE_VISITED:
                    visible = sec.cellvisited(0, off)
                else:
                    visible = sec.cellvisible(0, off)
        
        self.sprite.sprite.visible = visible

        self.sprite.setpos(self.locator.x - self.locator.r,
                           self.locator.y - self.locator.r)

    def selected(self, yes):
        self.sprite.ring.visible = yes

    def destroy(self):
        self.sprites.remove(self.sprite)
        self.sprite = None
