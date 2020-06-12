'''
Modes
'''

from pyarts.engine.target import Target

from pyarts.log import info


class BaseMode(object):
    def setup(self, modestack, game):
        self.modestack = modestack
        self.game = game

    def enter(self):
        pass

    def exit(self):
        pass


class NormalMode(BaseMode):
    '''
    The mode the game is usually in
    '''
    name = 'normal'

    def __init__(self):
        pass

    def left_click_pos(self, x, y, add):
        ''' Do nothing for a left click in empty space '''
        pass

    def left_click_ents(self, ents, add):
        ''' Left click selects a single entity '''
        self.game.select(ents, add)

    def right_click(self, x, y, ents, add):
        ''' Right click issues an auto command '''
        self.game.autocommand(x, y, ents, add)

    def ability(self, idx, add):
        self.game.ability(idx, add)


class TargetingMode(BaseMode):
    '''
    A mode used to select a target for an ability
    '''
    name = 'targeting'

    def __init__(self, order, allowpos=True, allowent=True):
        self.order = order
        self.allowent = allowent
        self.allowpos = allowpos

    def enter(self):
        info('entered targeting mode')

    def exit(self):
        info('exited targeting mode')

    def left_click_pos(self, x, y, add):
        ''' Select a position target '''
        if self.allowpos:
            self.order.target = Target((x, y))
            self.game.order(self.order)
        self.modestack.pop_mode()

    def left_click_ents(self, ents, add):
        ''' Select an entity target '''
        if self.allowent:
            self.order.target = Target(next(iter(ents)))
            self.game.order(self.order)
        self.modestack.pop_mode()

    def right_click(self, x, y, ents, add):
        ''' RIght click cancels the targeting '''
        self.modestack.pop_mode()

    def ability(self, idx, add):
        ''' Ability button also cancels targeting '''
        self.modestack.pop_mode()


class BuildMode(TargetingMode):
    '''
    A mode used to place new buildings
    '''
    name = 'building'

    def __init__(self, order, ghost=None, **kwargs):
        super(BuildMode, self).__init__(order, **kwargs)

        # todo - use sprite manager to get the ghost sprite

