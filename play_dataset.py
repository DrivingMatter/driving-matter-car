from classes.Driver import Driver
from classes.State import ACTIONS
from classes.Dataset import Dataset
from classes.LoadCar import load_car
from classes.KBhit import KBHit
import logging
from time import sleep
logger = logging.getLogger("play_dataset.py")

print "ACTIONS = " + str(ACTIONS)

car, rps_ms, port = load_car("config.json")
driver = Driver(car, show_camera = True)
dataset = Dataset()

def execute_action(action):
	logger.debug("Action :" + action)
	state0, action, state1 = driver.action_blocking(action)
	logger.debug("Action executed")
	datavector, datavector_title = driver.process_dataset_vector(state0, action, state1)
	dataset.save_data(datavector, datavector_title)
	logger.debug("dataset saved")

try:
    kb = KBHit()
    while True:
        if kb.kbhit():
            c = kb.carkey()
            if c == 0: # Up
                execute_action("forward")
            elif c == 1: # Right
		execute_action("forwardRight")
            elif c == 2: # Down
		execute_action("backward")
            elif c == 3: # Left
		execute_action("forwardLeft")
            elif c == 4: # Space
		execute_action("stop")
	sleep(0.05)
finally:
    driver.close()
    car.close()
    dataset.close()
    kb.set_normal_term()