import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from classes.Car4W import Car4W
from classes.Tyre import Tyre

import os
from time import sleep
import cv2
from PIL import Image
import numpy as np
import io
from time import time
import json

config = json.loads(open("../config.json").read())

car_speed = config['car_speed']
timeframe = config['timeframe']

# Loading Tyre Settings
ts = tyre_settings = config['tyre_settings']
frontRight = Tyre(ts['front_right']['forwardPin'], ts['front_right']
                  ['backwardPin'], ts['front_right']['pwmPin'], car_speed)
frontLeft = Tyre(ts['front_left']['forwardPin'], ts['front_left']
                 ['backwardPin'], ts['front_left']['pwmPin'], car_speed)
backRight = Tyre(ts['back_right']['forwardPin'], ts['back_right']
                 ['backwardPin'], ts['back_right']['pwmPin'], car_speed)
backLeft = Tyre(ts['back_left']['forwardPin'], ts['back_left']
                ['backwardPin'], ts['back_left']['pwmPin'], car_speed)
tyres = [("fr", frontRight), ("fl", frontLeft),
         ("br", backRight), ("bl", backLeft)]

car = Car4W(tyres=tyres, timeframe=timeframe)

car.test()