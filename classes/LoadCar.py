from classes.Car4W import Car4W
from classes.Tyre import Tyre
from classes.Camera import Camera
from classes.UDSensor import CollisionSensor
from classes.RegisterCar import RegisterCar

import json
import logging

def load_car(config_file="config.json"):
    # Loading config file
    config = json.loads(open(config_file).read())

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
        camera = Camera(c['camera_type'], c['camera_num'],
                        c['resolution'], c['framerate'], c['rotation'])
        camera.start() # Starting the camera, through exception if camera doesn't exists
        cameras.append((key, camera))        
        logging.debug(key + " camera doesn't exists, ignoring that camera")
        # Ignore is camera doesn't exist. 
        pass

    return Car4W(tyres, sensors, cameras, timeframe), rps_ms, port