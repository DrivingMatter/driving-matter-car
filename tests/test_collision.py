import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from classes.Collision import Collision
from classes.UDSensor import CollisionSensor
import os
from time import sleep
import cv2
from PIL import Image
import numpy as np
import io
from time import time
import json
import logging

logging.basicConfig(level=logging.DEBUG)

config = json.loads(open("../config.json").read())

# Loading Sensors Settings
ss = sensor_settings = config['sensor_settings']
ultrasonic_c = CollisionSensor(
   echo=ss['ultrasonic_c']['echo'], trigger=ss['ultrasonic_c']['trigger'])
ultrasonic_l = CollisionSensor(
   echo=ss['ultrasonic_l']['echo'], trigger=ss['ultrasonic_l']['trigger'])
ultrasonic_r = CollisionSensor(
     echo=ss['ultrasonic_r']['echo'], trigger=ss['ultrasonic_r']['trigger'])
sensors = [("center", ultrasonic_c),
           ("left", ultrasonic_l), ("right", ultrasonic_r)]

c = Collision(sensors)
c.start()

#s = ultrasonic_c
#print (ss['ultrasonic_r']['echo'])
#print (ss['ultrasonic_r']['trigger'])

print ("Started...")
while True:
    print (str(c.get()) + '    ' + str(time()))
    sleep(0.01)
    #print("Collison:")
    #print (s.check_collision())

