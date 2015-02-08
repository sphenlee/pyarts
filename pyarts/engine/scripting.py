'''
Scripting

Various functions that get exposed to Lua
'''

from .. import lua

class Scripting(object):
    def __init__(self, eng):
        self.__lua_methods__ = {}

        self.lua = lua.State()
        self.eng = eng

    def print_(self, *args):
        ''' Simulate Lua's print which tab separates args '''
        print '\t'.join(str(a) for a in args)
        
    def create_entity(self, tid, protoname):
        team = self.eng.getteam(tid)
        proto = team.getproto(protoname)
        ent = self.eng.entities.create(proto)

        return ent.eid

    def place_entity(self, eid, x, y):
        print 'placing %d at (%d, %d)' % (eid, x, y)
        ent = self.eng.entities.get(eid)
        ent.locator.place(x, y)

    def place_entity_near(self, eid, me):
        print 'placing %d near %d' % (eid, me)
        ent = self.eng.entities.get(eid)
        meent = self.eng.entities.get(me)

        x, y = meent.locator.pos()

        ent.locator.place(x + meent.locator.r, y)

    def write_variable(self, eid, var, op, val):
        print 'write variable', eid, op, val
        ent = self.eng.entities.get(eid)
        if ent.has('variables'):
            if op == 'set':
                ent.variables[var] = int(val)
            elif op == 'add':
                ent.variables[var] += int(val)

    def setup(self):
        self.lua.setglobal('print', self.print_)
        self.lua.setglobal('create_entity', self.create_entity)
        self.lua.setglobal('place_entity', self.place_entity)
        self.lua.setglobal('place_entity_near', self.place_entity_near)
        self.lua.setglobal('write_variable', self.write_variable)

    def runmain(self, datasrc):
        main = datasrc.getresource('main.lua')

        with open(main) as fp:
            self.lua.dostring(fp.read())
