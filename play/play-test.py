import sys
from os import path
import logging
from time import sleep, time
logger = logging.getLogger("play_fun.py")
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from classes.Driver import Driver
from classes.State import ACTIONS
from classes.LoadCar import load_car
from classes.KBhit import KBHit
from classes.Dataset import Dataset

logger.debug("ACTIONS = " + str(ACTIONS))

car, rps_ms, port = load_car("../config.json")
driver = Driver(car, show_camera = True)

def execute_action(action):
    logger.debug("Action :" + action)
    driver.action_nowait(action)

try:
    kb = KBHit()
    while True:
        """
        if kb.kbhit():
            c = kb.carkey()
            if c == 0: # w
                execute_action("forward")
            elif c == 1: # d
                execute_action("forwardRight")
            elif c == 2: # s
                execute_action("backward")
            elif c == 3: # a
                execute_action("forwardLeft")
            elif c == 4: # [SPACE]
                execute_action("stop")
        
        """
        state = car.get_state_vector(True)
        driver.display_camera(state)
        sleep(1)
        #execute_action("stop")
finally:
    driver.close()
    car.close()
    kb.set_normal_term()
