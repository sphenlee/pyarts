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
        self.is_selected = False
        self.visible = 0

    def save(self):
        return {}

    def load(self, data):
        pass

    def step(self):
        if self.sprite is None:
            return

        if not self.locator.placed:
            self.visible = 0
        elif self.visibility == self.VISIBLE_ALWAYS:
            self.visible = ~0
        else:
            pt = self.locator.x, self.locator.y
            cell = self.map.pos_to_cell(*pt)
            sec = self.map.sector_at_cell(*cell)
            off = self.map.cell_to_offset(*cell)
            if sec:
                if self.visibility == self.VISIBLE_VISITED:
                    self.visible = sec.cellvisited_mask(off)
                else:
                    self.visible = sec.cellvisible_mask(off)
        
        self.sprite.setvisible(self.visible, self.is_selected)

        self.sprite.setpos(self.locator.x - self.locator.r,
                           self.locator.y - self.locator.r)

    def selected(self, yes):
        self.is_selected = yes

    def visible_to(self, tidmask):
        return (self.visible & tidmask) != 0

    def destroy(self):
        self.sprites.remove(self.sprite)
        self.sprite = None
