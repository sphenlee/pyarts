'''
Stats
'''


from .component import Component, register

@register
class Stats(Component):
    name = 'stats'
    depends = []

    def save(self):
        return {}

    def load(self, data):
        pass
