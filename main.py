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

from classes.Server import Server
from classes.Car4W import Car4W
from classes.Tyre import Tyre
from classes.Camera import Camera
from classes.UDSensor import CollisionSensor
from handlers import Action, CameraC, State

signal.signal(signal.SIGINT, signal.SIG_DFL)
logging.basicConfig(level=logging.DEBUG)

# Loading config file
config = json.loads(open("config.json").read())

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
cs = camera_settings = config['camera_settings']

cameras = []
if camera_settings:
    csc = camera_settings_c = camera_settings.get('camera_c')
    if camera_settings_c:
        camera_c = Camera(csc['camera_type'], csc['camera_num'],
                          csc['resolution'], csc['framerate'], csc['rotation'])
        camera_c.start() # Starting the camera
        cameras.append(("center", camera_c))



car = Car4W(tyres, sensors, camera_settings, timeframe)

h = [
    #(r"/camera_c", CameraC.CameraC), # State can replace this, with the new architecture....
    (r"/action", Action.Action, {'car': car}),
    (r"/state", State.State, {'car': car})
]

if __name__ == "__main__":

    try:
        logging.debug("main.py called")
        s = Server(h, port=port)
        s.start()
    except KeyboardInterrupt:
        print "Exiting"
