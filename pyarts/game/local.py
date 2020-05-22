
from pyarts.container import component


@component
class Local(object):
    depends = ['settings', 'game']

    def inject(self, settings, game):
        settings.onload.add(self.init_localpid)
        self.pid = None
        self.game = game


    def init_localpid(self, settings):
        self.pid = settings.localpid


    @property
    def player(self):
        '''
        Get the local player - can't call this before game is loaded!
        '''
        return self.game.players[self.pid]
