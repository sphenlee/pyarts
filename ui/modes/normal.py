'''
Normal Mode
'''

from engine.target import Target

class NormalMode(object):
    def __init__(self, game):
        self.game = game

    def left_click_pos(self, x, y, add):
        pass

    def left_click_ents(self, ents, add):
        self.game.select(ents, add)

    def right_click(self, x, y, ents, add):
        print 'right click', x, y, ents, add
        if ents:
            target = Target(self.game.engine.entities, next(iter(ents)))
        else:
            target = Target(self.game.engine.entities, (x, y))

        self.game.autocommand(target)


    def draw(self):
        pass
