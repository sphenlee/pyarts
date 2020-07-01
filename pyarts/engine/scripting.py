'''
Scripting

Various functions that get exposed to Lua
'''

from .. import lua

from pyarts.container import component
from pyarts.log import info

from pyarts.engine.actions import ConstructAction


@component
class Scripting(object):
    depends = ['engine', 'entitymanager', 'datasrc', 'gamelog']

    def __init__(self):
        self.__lua_methods__ = {}

        self.codecache = set()
        self.lua = lua.State()

        self.setup()

    def inject(self, engine, entitymanager, datasrc, gamelog):
        self.eng = engine
        self.entities = entitymanager
        self.datasrc = datasrc
        self.gamelog = gamelog

    def code(self, code):
        if isinstance(code, list):
            code = 'return ' + '\n'.join(code)
            return self.lua.dostring(code)
        elif isinstance(code, str):
            code = 'return ' + code
            return self.lua.dostring(code)
        elif isinstance(code, dict):
            return self.get_func(code['file'], code['function'])
        else:
            raise ValueError('lua code must be string, list or dict')

    def get_func(self, file, func):
        if file in self.codecache:
            return self.lua.getglobal(func)
        else:
            code = open(self.datasrc.getresource(file)).read()
            self.lua.dostring(code)
            self.codecache.add(file)
            return self.get_func(file, func)

    # ________________________________________________________
    # functions exported to Lua from here

    def print_(self, *args):
        ''' Simulate Lua's print which tab separates args '''
        print('\t'.join(str(a) for a in args))

    def log(self, msg, *args):
        '''
        Print a message to the console log
        '''
        info(msg, *args)

    def display(self, msg, *args):
        formatted = msg.format(*args)
        self.gamelog.log(formatted)

    def create_entity(self, tid, protoname):
        team = self.eng.getteam(tid)
        proto = team.getproto(protoname)
        ent = self.entities.create(proto)

        return ent.eid

    def place_entity(self, eid, x, y):
        info('placing %d at (%d, %d)' % (eid, x, y))
        ent = self.entities.get(eid)
        ent.locator.place(x, y)

    def place_entity_near(self, eid, me):
        info('placing %d near %d' % (eid, me))
        ent = self.entities.get(eid)
        meent = self.entities.get(me)

        x, y = meent.locator.pos()

        ent.locator.place(x + meent.locator.r, y)

    def write_variable(self, eid, var, op, val):
        info('write variable', eid, op, val)
        ent = self.entities.get(eid)
        if ent.has('variables'):
            if op == 'set':
                ent.variables[var] = int(val)
            elif op == 'add':
                ent.variables[var] += int(val)

    def construct(self, me, protoname, oncomplete=None):
        ent = self.entities.get(me)
        proto = ent.team.getproto(protoname)

        ent.actions.now(ConstructAction(proto, oncomplete))

    def create_town(self, founder, race, initial_resources={}):
        ent = self.entities.get(founder)
        town = ent.team.create_town(ent, race, initial_resources)
        self.gamelog.log(f'You have founded a new town: {town.name}')
        return town.twid

    def destroy(self, eid):
        info('destroying ', eid)
        self.entities.destroy(eid)

    # _____________________________________________________________

    def setup(self):
        self.lua.setglobal('print', self.print_)
        self.lua.setglobal('create_entity', self.create_entity)
        self.lua.setglobal('place_entity', self.place_entity)
        self.lua.setglobal('place_entity_near', self.place_entity_near)
        self.lua.setglobal('write_variable', self.write_variable)
        self.lua.setglobal('destroy', self.destroy)
        self.lua.setglobal('construct', self.construct)
        self.lua.setglobal('create_town', self.create_town)
        self.lua.setglobal('log', self.log)
        self.lua.setglobal('display', self.display)

    def runmain(self):
        main = self.datasrc.getresource('main.lua')

        with open(main) as fp:
            self.lua.dostring(fp.read())
