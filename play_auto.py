from classes.Driver import Driver
from classes.State import ACTIONS
from classes.Dataset import Dataset
from classes.LoadCar import load_car
from classes.KBhit import KBHit
import logging
from time import sleep
import pickle
logger = logging.getLogger("play_auto.py")

print "ACTIONS = " + str(ACTIONS)

car, rps_ms, port = load_car("config.json")
driver = Driver(car, show_camera = True)
dataset = Dataset()

try:
    model_file = open('models/model.dat', 'rb')
    model = pickle.load(model_file)
    model_file.close()
    driver.action_auto(model)
finally:
    driver.close()
    car.close()
    dataset.close()
    kb.set_normal_term()