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

lua.luaL_ref.argtypes = [ ctypes.c_void_p, ctypes.c_int ]
lua.luaL_ref.restype = ctypes.c_int

lua.luaL_unref.argtypes = [ ctypes.c_void_p, ctypes.c_int, ctypes.c_int ]
lua.luaL_unref.restype = None

lua.lua_rawgeti.argtypes = [ ctypes.c_void_p, ctypes.c_int, ctypes.c_int ]
lua.lua_rawgeti.restype = None

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

class popper(object):
    def __init__(self, L):
        self.L = L

    def __enter__(self):
        self.top = lua.lua_gettop(self.L)

    def __exit__(self, *args):
        lua.lua_settop(self.L, self.top)

class LuaRef(object):
    def __init__(self, L, idx):
        self.L = L
        with popper(L):
            lua.lua_pushvalue(self.L, idx)
            lua.lua_getfield(self.L, LUA_REGISTRYINDEX, ".pyrefs")
            lua.lua_pushvalue(self.L, -2)
            self.ref = lua.luaL_ref(self.L, -2)
            #print '<ref %d>' % self.ref
            
    def __del__(self):
        with popper(self.L):
            #print '<unref %d>' % self.ref
            lua.lua_getfield(self.L, LUA_REGISTRYINDEX, ".pyrefs")
            lua.luaL_unref(self.L, -1, self.ref)

    def push(self):
        #print 'push <ref %d>' % self.ref
        lua.lua_getfield(self.L, LUA_REGISTRYINDEX, ".pyrefs")
        lua.lua_rawgeti(self.L, -1, self.ref)
        lua.lua_remove(self.L, -2)

class LuaError(Exception):
    pass

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
    elif ty == Table:
        val.ref.push()
    elif ty == LuaRef:
        val.push()
    else:
        raise TypeError('luapush: %r' % ty)

# utility to get a python value off the stack
def luaget(L, idx):
    ty = lua.lua_type(L, idx)
    if ty == LUA_TNIL:
        #print 'nil'
        return None
    elif ty == LUA_TNUMBER:
        #print 'num'
        n = lua.lua_tonumber(L, idx)
        return n
    elif ty == LUA_TSTRING:
        #print 'str'
        s = lua.lua_tolstring(L, idx, None)
        return s
    elif ty == LUA_TTABLE:
        #print 'tab'
        ref = LuaRef(L, idx)
        t = Table(L, ref)
        return t
    elif ty == LUA_TFUNCTION:
        #print 'fun'
        ref = LuaRef(L, idx)
        f = function(L, ref)
        return f
    else:
        raise TypeError('luaget: %r' % ty)

# lua state class
class State(object):
    def __init__(self):
        self.lua = lua # keep the DLL open as long as we have a state object around

        self.L = lua.luaL_newstate()
        #lua.luaL_openlibs(self.L)

        lua.lua_createtable(self.L, 0, 0)
        lua.lua_setfield(self.L, LUA_REGISTRYINDEX, ".pyrefs")

    def __del__(self):
        self.close()

    def close(self):
        self.lua.lua_close(self.L)

    def loadstring(self, code):
        ok = lua.luaL_loadstring(self.L, code.encode('ascii'))
        ret = luaget(self.L, -1)
        if ok == 0:
            return ret
        else:
            raise LuaError(ret)

    def dostring(self, code):
        return self.loadstring(code)()
        
    def setglobal(self, name, val):
        luapush(self.L, val)
        lua.lua_setfield(self.L, LUA_GLOBALSINDEX, name)
        
    def getglobal(self, name):
        lua.lua_getfield(self.L, LUA_GLOBALSINDEX, name)
        return luaget(self.L, -1)

# python wrapper for a lua table
import collections

class Table(collections.MutableMapping):
    def __init__(self, L, ref):
        super(Table, self).__init__()
        self.L = L
        if ref is None:
            lua.lua_newtable()
            self.ref = LuaRef(L, -1)
        else:
            self.ref = ref

    def __repr__(self):
        
        return '<lua.Table ref %d>' % self.ref.ref

    def __getitem__(self, key):
        with popper(self.L):
            self.ref.push()
            luapush(self.L, key)
            lua.lua_gettable(self.L, -2)
            return luaget(self.L, -1)

    def __setitem__(self, key, val):
        with popper(self.L):
            luapush(self.L, key)
            luapush(self.L, val)
            self.ref.push()
            lua.lua_settable(self.L, -1)

    def __delitem__(self, key):
        with popper(self.L):
            luapush(self.L, key)
            lua.lua_pushnil(self.L)
            self.ref.push()
            lua.lua_settable(self.L, -1)

    def __len__(self):
        with popper(self.L):
            self.ref.push()
            return lua.lua_objlen(self.L, -1)

    def __iter__(self):
        return TableIter(self.L, self.ref)

class TableIter(object):
    def __init__(self, L, ref):
        self.L = L
        self.ref = ref
        self.ref.push()
        lua.lua_pushnil(self.L)

    def __repr__(self):
        return '<lua.TableIter ref %d>' % self.ref.ref

    def next(self):
        err = lua.lua_next(self.L, -2)
        if err == 0:
            lua.lua_settop(self.L, -2) # pop the table
            raise StopIteration('StopIteration')
        key = luaget(self.L, -2)
        val = luaget(self.L, -1)
        lua.lua_settop(self.L, -2); # pop value
        return key, val

class function(object):
    def __init__(self, L, ref):
        self.L = L
        self.ref = ref

    def __repr__(self):
        return '<lua.function ref %d>' % self.ref.ref

    def __call__(self, *args):
        with popper(self.L):
            n = lua.lua_gettop(self.L)
            self.ref.push()
            for a in args:
                luapush(self.L, a)
            ok = lua.lua_pcall(self.L, len(args), LUA_MULTIRET, 0)
            m = lua.lua_gettop(self.L)
            if m  - n == 1:
                ret = luaget(self.L, -1)
            else:
                ret = [ ]
                for i in xrange(1, m - n + 1):
                    ret.append(luaget(self.L, n + i))
                ret = tuple(ret)
            if ok == 0:
                return ret
            else:
                raise LuaError(ret)

# decorator for making a python function into a raw lua function
# 'raw' as in taking the Lua state, not converted args
rawfunc = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)

# decorator for making a python function into a lua function,
# args are converted into python objects
def func(func):
    @rawfunc
    def wrapper(L):
        try:
            nargs = lua.lua_gettop(L)
            args = [ ]
            for i in xrange(1, nargs + 1):
                args.append(luaget(L, i))
            ret = func(*args)
            if isinstance(ret, tuple):
                for v in ret:
                    luapush(L, v)
                return len(ret)
            else:
                luapush(L, ret)
                return 1
        except:
            # no python exceptions can get into Lua
            import traceback
            traceback.print_exc()
            return 0

    return wrapper
