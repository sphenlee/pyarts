'''
Modes
'''

from target import Target

class NormalMode(object):
    '''
    The mode the game is usually in
    '''

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

        self.game.autocommand(target, add)

    def ability(self, idx):
        self.game.ability(idx)

    def draw(self):
        ''' Nothing special to draw '''
        pass

class TargetingMode(object):
    '''
    A mode used to select a target for an ability
    '''

    def __init__(self, game, order, allowpos=True, allowent=True):
        self.game = game
        self.order = order
        self.allowent = allowent
        self.allowpos = allowpos

    def left_click_pos(self, x, y, add):
        ''' Select a position target '''
        if self.allowpos:
            self.order.target = Target(self.game.engine.entities, (x, y))
            self.game.order(self.order)
        self.game.pop_mode()

    def left_click_ents(self, ents, add):
        ''' Select an entity target '''
        if self.allowent:
            self.order.target = Target(self.game.engine.entities, next(iter(ents)))
            self.game.order(self.order)
        self.game.pop_mode()

    def right_click(self, x, y, ents, add):
        ''' RIght click cancels the targeting '''
        self.game.pop_mode()

    def ability(self, idx):
        ''' Ability button also cancels targeting '''
        self.game.pop_mode()

    def draw(self):
        ''' Nothing special to draw (yet) '''
        pass
