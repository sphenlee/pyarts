'''
Container

This module does the global dependnecy injection used by the entire game.
Right now there are going to be two different DI systems - this global one
and the entity specific one. Perhaps merged the implementations later?
'''

from pyarts.log import trace, info, error


def get_deps(cls):
    deps = cls.depends
    if isinstance(deps, list):
        return deps
    else:
        return deps()


def get_inject_kwargs(comp, components):
    return {cname: components[cname] for cname in get_deps(type(comp))}


class Components(object):
    '''
    A "meta" component that lets instances be created at runtime.
    These runtime scoped components can't be listed as dependencies
    of other components as there may be zero or many of them
    '''

    depends = []

    def __init__(self):
        self.instances = None

    def inject(self):
        pass

    def construct(self, name, *args, **kwargs):
        info('constructing {0}', name)
        cls = getcomponentclass(name)
        if _scopes[name] != 'dynamic':
            error('component {} cannot be runtime constructed (scope is {})',
                  name, _scopes[name])
            raise RuntimeError('dependency injection failed')

        inst = cls(*args, **kwargs)
        kwargs = get_inject_kwargs(inst, self.instances)
        trace('injecting {0}', inst.__class__.__name__)
        inst.inject(**kwargs)
        return inst


def construct(name):
    info('constructing {0}', name)
    # find all the dependencies - transitive
    deps = set([name])
    while 1:
        newdeps = set(deps)
        for c in deps:
            cls = getcomponentclass(c)
            for d in get_deps(cls):
                newdeps.add(d)

        if newdeps == deps:
            break

        deps = newdeps

    # construct the component classes
    components = {}
    for cname in deps:
        cls = getcomponentclass(cname)
        if _scopes[cname] != 'singleton':
            error('component {} cannot be constructed at global level '
                  '(scope is {})', cname, _scopes[cname])
            raise RuntimeError('dependency injection failed')

        trace('creating {0}', cname)
        components[cname] = cls()

    # we expect that someone depends on this
    c = components['components']
    c.instances = components

    # perform the injection
    for comp in list(components.values()):
        kwargs = get_inject_kwargs(comp, components)
        trace('injecting {0}', comp.__class__.__name__)
        comp.inject(**kwargs)

    info('done')
    return components[name]


_all_components = {}
_scopes = {}  # to avoid setting attributes on the Rust implemented classes


def getcomponentclass(name):
    return _all_components[name]


def scoped_component(cls, scope):
    if hasattr(cls, 'name'):
        name = cls.name
    else:
        name = cls.__name__.lower()

    _scopes[name] = scope
    _all_components[name] = cls
    return cls


scoped_component(Components, 'singleton')


def dynamic_component(cls):
    return scoped_component(cls, 'dynamic')


def component(cls):
    return scoped_component(cls, 'singleton')
