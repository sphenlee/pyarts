'''
Modes
'''

from pyarts.engine.target import Target

import pyglet

class NormalMode(object):
    '''
    The mode the game is usually in
    '''

    def __init__(self, game):
        self.game = game

    def enter(self):
        self.game.onmodechange.emit('normal')

    def exit(self):
        pass

    def left_click_pos(self, x, y, add):
        ''' Do nothing for a left click in empty space '''
        pass

    def left_click_ents(self, ents, add):
        ''' Left click selects a single entity '''
        self.game.select(ents, add)

    def right_click(self, x, y, ents, add):
        ''' Right click issues an auto command '''
        if ents:
            target = Target(next(iter(ents)))
        else:
            target = Target((x, y))

        self.game.autocommand(target, add)

    def ability(self, idx, add):
        self.game.ability(idx, add)

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

    def enter(self):
        self.game.onmodechange.emit('targeting')

    def exit(self):
        pass

    def left_click_pos(self, x, y, add):
        ''' Select a position target '''
        if self.allowpos:
            self.order.target = Target((x, y))
            self.game.order(self.order)
        self.game.pop_mode()

    def left_click_ents(self, ents, add):
        ''' Select an entity target '''
        if self.allowent:
            self.order.target = Target(next(iter(ents)))
            self.game.order(self.order)
        self.game.pop_mode()

    def right_click(self, x, y, ents, add):
        ''' RIght click cancels the targeting '''
        self.game.pop_mode()

    def ability(self, idx, add):
        ''' Ability button also cancels targeting '''
        self.game.pop_mode()

    def draw(self):
        ''' Nothing special to draw (yet) '''
        pass

class BuildMode(TargetingMode):
    '''
    A mode used to place new buildings
    '''

    def __init__(self, game, order, ghost=None, **kwargs):
        super(BuildMode, self).__init__(game, order, **kwargs)

        res = game.datasrc.getresource(ghost)
        img = pyglet.image.load(res)
        self.sprite = pyglet.sprite.Sprite(img)

    def draw(self):
        self.sprite.draw()
