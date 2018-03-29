import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from classes.Driver import Driver
from classes.State import ACTIONS
from classes.Dataset import Dataset
from classes.LoadCar import load_car
from classes.KBhit import KBHit
import logging
from time import sleep, time
import pickle
from keras.models import model_from_json
import os

logger = logging.getLogger("play_auto.py")

logger.debug("ACTIONS = " + str(ACTIONS))

logging.debug("Loading model")

json_file = open('../models/model001.best.h5', 'r')

loaded_model_json = json_file.read()
json_file.close()

loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("../models/weights001.best.h5")

loaded_model.compile(loss='categorical_crossentropy',
                  optimizer='adadelta',
                  metrics=['accuracy'])

logging.debug("Model loaded")

car, rps_ms, port = load_car("../config-auto.json")

driver = Driver(car, show_camera = True)

driver.action_auto(loaded_model)

driver.close()
car.close()
kb.set_normal_term()
