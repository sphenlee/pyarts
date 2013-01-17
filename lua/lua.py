'''
Lua in Python

TODO:
 * pass python dicts and lists as tables
 * return lua functions as python callables
 * auto-ref live lua objects (how??)
'''

# exports
__all__ = ['Lua', 'func', 'rawfunc', 'table']

# load the library
import ctypes
lua = ctypes.cdll.LoadLibrary('liblua5.1.so')

# declare arg and return types
lua.lua_tolstring.restype = ctypes.c_char_p
lua.lua_tonumber.restype = ctypes.c_double

lua.lua_pushnumber.argtypes = [ ctypes.c_void_p, ctypes.c_double ]
lua.lua_pushinteger.argtypes = [ ctypes.c_void_p, ctypes.c_long ]

# declare constants
LUA_MULTIRET = -1

LUA_REGISTRYINDEX = -10000
LUA_ENVIRONINDEX = -10001
LUA_GLOBALSINDEX = -10002

LUA_TNIL = 0
LUA_TBOOLEAN = 1
LUA_TLIGHTUSERDATA = 2
LUA_TNUMBER = 3
LUA_TSTRING = 4
LUA_TTABLE = 5
LUA_TFUNCTION = 6
LUA_TUSERDATA = 7
LUA_TTHREAD = 8

# utility to get a python value onto the lua stack
def luapush(L, val):
    ty = type(val)
    if val is None:
        lua.lua_pushnil(L)
    elif ty == str:
        lua.lua_pushstring(L, val)
    elif ty == int:
        lua.lua_pushinteger(L, val)
    elif ty == float:
        lua.lua_pushnumber(L, val)
    elif ty == rawfunc:
        lua.lua_pushcclosure(L, val, 0)
    elif ty == table:
        lua.lua_pushvalue(L, val.idx)

# utility to get a python value off the stack
def luaget(L, idx):
    ty = lua.lua_type(L, idx)
    if ty == LUA_TNIL:
        return None
    elif ty == LUA_TNUMBER:
        n = lua.lua_tonumber(L, idx)
        return n
    elif ty == LUA_TSTRING:
        s = lua.lua_tolstring(L, idx, None)
        return s
    elif ty == LUA_TTABLE:
        t = table(L, idx)
        return t
    elif ty == LUA_TFUNCTION:
        f = function(L, idx)
        return f

# lua state class
class State(object):
    def __init__(self):
        self.L = lua.luaL_newstate()
        lua.luaL_openlibs(self.L)

    def close(self):
        lua.lua_close(self.L)

    def dostring(self, code):
        lua.luaL_loadstring(self.L, code)
        lua.lua_pcall(self.L, 0, 0, 0)
        
    def dofile(self, fname):
        with open(fname) as fp:
            code = fp.read()
        self.dostring(code)

    def setglobal(self, name, val):
        luapush(self.L, val)
        lua.lua_setfield(self.L, LUA_GLOBALSINDEX, name)
        
    def getglobal(self, name):
        lua.lua_getfield(self.L, LUA_GLOBALSINDEX, name)
        return luaget(self.L, -1)

# python wrapper for a lua table
import collections

class table(collections.MutableMapping):
    def __init__(self, L, idx):
        super(table, self).__init__()
        self.L = L
        if idx is None:
            lua.lua_newtable()
            self.idx = lua.lua_gettop() - 1
        else:
            self.idx = idx

    def __repr__(self):
        return 'lua.table(...)'

    def __getitem__(self, key):
        luapush(self.L, key)
        lua.lua_gettable(self.L, self.idx)
        return luaget(self.L, -1)

    def __setitem__(self, key, val):
        luapush(self.L, key)
        luapush(self.L, val)
        lua.lua_settable(self.L, self.idx)

    def __delitem__(self, key):
        lua.lua_pushnil(self.L)
        lua.lua_settable(self.L, self.idx)

    def __len__(self):
        return lua.lua_objlen(self.L, self.idx)

    def __iter__(self):
        return tableiter(self.L, self.idx)

class tableiter(object):
    def __init__(self, L, idx):
        self.L = L
        self.idx = idx
        lua.lua_pushnil(self.L)

    def __repr__(self):
        return 'lua.tableiter(...)'

    def next(self):
        err = lua.lua_next(self.L, self.idx)
        if err == 0:
            raise StopIteration('StopIteration')
        key = luaget(self.L, -2)
        val = luaget(self.L, -1)
        lua.lua_settop(self.L, -2);
        return key, val

class function(object):
    def __init__(self, L, idx):
        self.L = L
        self.idx = idx

    def __repr__(self):
        return 'lua.function(...)'

    def __call__(self, *args):
        n = lua.lua_gettop(self.L)
        lua.lua_pushvalue(self.L, self.idx)
        for a in args:
            luapush(self.L, a)
        lua.lua_pcall(self.L, len(args), LUA_MULTIRET, 0)
        m = lua.lua_gettop(self.L)
        ret = [ ]
        for i in xrange(1, m - n + 1):
            ret.append(luaget(self.L, n + i))
        return tuple(ret)

# decorator for making a python function into a raw lua function
# 'raw' as in taking the Lua state, not converted args
rawfunc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)

# decorator for making a python function into a lua function,
# args are converted into python objects
def func(func):
    @rawfunc
    def wrapper(L):
        nargs = lua.lua_gettop(L)
        args = [ ]
        for i in xrange(1, nargs + 1):
            args.append(luaget(L, i))
        luapush(L, func(*args))
        return 1
    return wrapper

##########################################
# Test program

@func
def myprint(s):
    if type(s) is table:
        print 'table', s['hello']
        s['magic'] = 'more'
        
        for k, v in s:
            print 'iter: ', k, v
    else:
        print 'in python', s


L = State()
L.setglobal('x', 123)
L.setglobal('myprint', myprint)
script = '''
myprint('hello')
myprint(x)
t = {
    hello = 'world',
    world = 'magic'
}
myprint(t)
print('lua ' .. t.magic)
function InLua(x)
    print('in lua ' .. x)
    return 'foo', 42
end
'''
L.dostring(script)

t = L.getglobal('t')

fn = L.getglobal('InLua')
print fn(123)

L.dofile('test.lua')

t = table(L)
t['hello'] = 'world'


L.close()
