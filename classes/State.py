from enum import Enum

ACTIONS = ('stop', 'forward', 'forwardRight', 'forwardLeft', 'backward', 'backRight', 'backwardLeft')

class State (Enum):
    IDLE            = 0
    FORWARD         = 1
    FORWARD_LEFT    = 2
    FORWARD_RIGHT   = 3
    BACKWARD        = 4
    BACKWARD_LEFT   = 5
    BACKWARD_RIGHT  = 6
    STOPPED         = 7