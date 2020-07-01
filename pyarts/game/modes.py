'''
Modes
'''

from pyarts.container import dynamic_component
from pyarts.engine.target import Target
from pyarts.log import info


class BaseMode(object):
    def inject(self):
        pass

    def setup(self, modestack, game):
        self.modestack = modestack
        self.game = game

    def enter(self):
        pass

    def exit(self):
        pass

    def mouse_move(self, x, y):
        pass


@dynamic_component
class NormalMode(BaseMode):
    '''
    The mode the game is usually in
    '''
    depends = []

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


@dynamic_component
class TargetingMode(BaseMode):
    '''
    A mode used to select a target for an ability
    '''
    depends = []

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


@dynamic_component
class BuildMode(TargetingMode):
    '''
    A mode used to place new buildings
    '''
    depends = ['spritemanager', 'datasrc', 'local', 'camera']

    def __init__(self, order, proto, **kwargs):
        super(BuildMode, self).__init__(order, allowent=False)
        self.proto = proto

    def inject(self, spritemanager, datasrc, local, camera):
        self.sm = spritemanager
        self.datasrc = datasrc
        self.local = local
        self.camera = camera

    def enter(self):
        ghost = '/' + self.datasrc.getresource(
            self.proto.data['appearance']['sprite'])

        self.r = self.proto.data['locator']['r']

        self.sprite = self.sm.new_sprite(ghost, self.r)
        self.sm.set_color(self.sprite, (0x00, 0xFF, 0x00, 0x80))
        self.sm.set_visible(self.sprite, self.local.tidmask, selected=False)

    def exit(self):
        self.sm.remove(self.sprite)

    def mouse_move(self, x, y):
        x, y = self.camera.unproject((x, y))
        self.sm.set_pos(self.sprite, x - self.r, y - self.r)
