'''
Control

Takes the raw inputs from Rust and converts them into more specific events.
* Unprojects from screen space to game space
* Checks for clicks on entities or poisitions
'''

from pyarts.container import component


@component
class Control(object):
    depends = ['modestack', 'map', 'camera']

    def inject(self, modestack, map, camera):
        self.modestack = modestack
        self.map = map
        self.camera = camera

    def entities_at_point(self, x, y):
        ''' Ask the map for entities within 16 pixels of (x, y) '''
        return self.map.entities_in_rect(x - 16, y - 16, x + 16, y + 16)

    def entities_in_rect(self, x1, y1, x2, y2):
        ''' Ask the map for entities within a box '''
        return self.map.entities_in_rect(x1, y1, x2, y2)

    def mouse_move(self, x, y):
        self.modestack.mode.mouse_move(x, y)

    def left_click_box(self, x1, y1, x2, y2, add):
        x1, y1 = self.camera.unproject((int(x1), int(y1)))
        x2, y2 = self.camera.unproject((int(x2), int(y2)))

        ents = self.entities_in_rect(x1, y1, x2, y2)
        
        if ents:
            self.modestack.mode.left_click_ents(ents, add)

    def left_click(self, x, y, add):
        x, y = self.camera.unproject((int(x), int(y)))
        
        ents = self.entities_at_point(x, y)
        
        if ents:
            self.modestack.mode.left_click_ents(ents, add)
        else:
            self.modestack.mode.left_click_pos(x, y, add)

    def right_click(self, x, y, add):
        x, y = self.camera.unproject((int(x), int(y)))
        ents = self.entities_at_point(x, y)
        self.modestack.mode.right_click(x, y, ents, add)

    def ability_button(self, num, add):
        self.modestack.mode.ability(num, add)
