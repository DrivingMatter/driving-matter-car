import time
import threading
import io
import picamera
import tornado.web
import tornado.websocket
import logging
import signal
import sys
import json
import os
import pkgutil
import socket

from classes.Server import Server
from classes.Car4W import Car4W
from classes.Tyre import Tyre
from classes.Camera import Camera
from classes.UDSensor import CollisionSensor
from classes.RegisterCar import RegisterCar

from handlers import Action, State

# Work only on python 2 because using pickle and bytes difference in between python versions.
assert(sys.version_info.major == 2)

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

signal.signal(signal.SIGINT, signal.SIG_DFL)

# Loading config file
config = json.loads(open("config.json").read())

rps_ms = config['rps_ms']
car_speed = config['car_speed']
timeframe = config['timeframe']
port = config['port']

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

# Loading camera settings and camera
camera_settings = config['camera_settings']

cameras = []
if camera_settings:
    for key in camera_settings:
        c = camera_settings[key]
        try:
          camera = Camera(c['camera_type'], c['camera_num'],
                          c['resolution'], c['framerate'], c['rotation'])
          camera.start() # Starting the camera, through exception if camera doesn't exists
          cameras.append((key, camera))        
        except Exception:
          logging.debug(key + " camera doesn't exists, ignoring that camera")
          # Ignore is camera doesn't exist. 
          pass

car = Car4W(tyres, sensors, cameras, timeframe)

h = [
    (r"/action", Action.Action, {'car': car}),
    (r"/state", State.State, {'car': car, 'rps_ms': rps_ms}) # rps_ms: Request Per Seconds Millisecond
]

if __name__ == "__main__":
    try:
        logging.debug("main.py called")
        rc = RegisterCar()
        rc.register_car(socket.gethostname())
        s = Server(h, port=port)
        s.start()
    except KeyboardInterrupt:
        rc.unregister_car()
        print "Exiting"
