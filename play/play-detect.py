import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from classes.Driver import Driver
from classes.State import ACTIONS
#from classes.Dataset import Dataset
from classes.LoadCar import load_car
from classes.KBhit import KBHit
import logging
import cv2
from time import sleep
logger = logging.getLogger("play_fun.py")

logger.debug("ACTIONS = " + str(ACTIONS))

car, rps_ms, port = load_car("../config.json")
driver = Driver(car, show_camera = False)

def execute_action(action):
    logger.debug("Action :" + action)
    print driver
    driver.action_nowait(action)

try:
    kb = KBHit()
    while True:
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

        datavector = car.get_state_vector()
        
        driver.display_camera(datavector)
        
        sleep(0.05)
finally:
    driver.close()
    car.close()
 #   dataset.close()
    kb.set_normal_term()
