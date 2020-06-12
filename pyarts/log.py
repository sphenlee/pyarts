from yarts import emit_log

import inspect

def log(level, msg, *args, __up=1, **kwargs):
    frm = inspect.stack()[__up]
    mod = inspect.getmodule(frm[0])
    target = mod.__name__.replace('.', '::')

    formatted = msg.format(*args, **kwargs)

    emit_log(target=target, level=level, msg=formatted)

def trace(msg, *args, **kwargs):
    log('TRACE', msg, *args, __up=2, **kwargs)

def debug(msg, *args, **kwargs):
    log('DEBUG', msg, *args, __up=2, **kwargs)

def info(msg, *args, **kwargs):
    log('INFO', msg, *args, __up=2, **kwargs)

def warn(msg, *args, **kwargs):
    log('WARN', msg, *args, __up=2, **kwargs)

def error(msg, *args, **kwargs):
    log('ERROR', msg, *args, __up=2, **kwargs)
