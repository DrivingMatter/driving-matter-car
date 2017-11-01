import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
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

config = json.loads(open("../config.json").read())

ultrasonic_c = CollisionSensor(echo=config['ultrasonic_c']['echo'], trigger=config['ultrasonic_c']['trigger'])
ultrasonic_l = CollisionSensor(echo=config['ultrasonic_l']['echo'], trigger=config['ultrasonic_l']['trigger'])
ultrasonic_r = CollisionSensor(echo=config['ultrasonic_r']['echo'], trigger=config['ultrasonic_r']['trigger'])

sensors = [("center", ultrasonic_c), ("left", ultrasonic_l), ("right", ultrasonic_r)]

c = Collision(sensors)
c.start()

while True:
    if c.ready and c.more():    
        print (c.get())
    sleep(0.1)
