'''
Normal Mode

The mode the game is usually in
'''

from engine.target import Target

class NormalMode(object):
    def __init__(self, game):
        self.game = game

    def left_click_pos(self, x, y, add):
        ''' Do nothing for a left click in empty space '''
        pass

    def left_click_ents(self, ents, add):
        ''' Left click selects a single entity '''
        self.game.select(ents, add)

    def right_click(self, x, y, ents, add):
        ''' Right click issues an auto command '''
        if ents:
            target = Target(self.game.engine.entities, next(iter(ents)))
        else:
            target = Target(self.game.engine.entities, (x, y))

        self.game.autocommand(target)

    def ability(self, idx):
        self.game.ability(idx)

    def draw(self):
        ''' Nothing special to draw '''
        pass
