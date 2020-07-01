# import component classes

from .game import *
from .engine import *
from .log import *


from .container import component, construct


# register components implemented in Rust

from yarts import MapRenderer, GameUi, Root, GameLog

component(MapRenderer)
component(GameUi)
component(Root)
component(GameLog)
