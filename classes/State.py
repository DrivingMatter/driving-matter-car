from enum import Enum

ACTIONS = ('forward', 'stop')#'forwardLeft', 'forwardRight', 'backward', 'backwardRight', 'backwardLeft', 'stop')
ACTIONS_REVERSE = {
    'forward'       : 'backward',
    'forwardLeft'   : 'forwardRight',
    'forwardRight'  : 'forwardLeft',
    'backward'      : 'forward',
    'backwardRight' : 'backwardLeft',
    'backwardLeft'  : 'backwardRight',
    'stop'          : 'stop'
}

COLLISIONS = {
    'forward'       : 'center',
    'forwardLeft'   : 'left',
    'forwardRight'  : 'right',
}

class State (Enum):
    IDLE            = 0
    FORWARD         = 1
    FORWARD_LEFT    = 2
    FORWARD_RIGHT   = 3
    BACKWARD        = 4
    BACKWARD_LEFT   = 5
    BACKWARD_RIGHT  = 6
    STOPPED         = 7