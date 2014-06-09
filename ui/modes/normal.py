'''
Normal Mode
'''

class NormalMode(object):
    def __init__(self, game):
        self.game = game

    def left_click_pos(self, x, y):
        pass

    def left_click_ents(self, ents, add):
        self.game.select(ents, add)

    def right_click(self, x, y, ents):
        print 'right click', x, y, ents
        if ents:
            self.game.autocommand_ent(next(iter(ents)))
        else:
            self.game.autocommand_pos(x, y)


    def draw(self):
        pass
