from State import State, ACTIONS
from Collision import Collision
from classes.Camera import Camera, PICAMERA, USB

import RPi.GPIO as GPIO
import logging
from time import sleep
from threading import Thread
import json
import picamera
import io
import pickle
import time
import cv2
import base64
import cStringIO
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Car4W:
    def __init__(self, tyres, sensors=[], cameras=[], timeframe=0.1, car_speed=50):
        logger.debug("Car4W.__init__()")

        self.action_id = 0

        self.t = None
        self.camera = None
        self.timeframe = timeframe
        self.car_speed = car_speed

        if len(tyres) != 4:
            raise EnvironmentError("Car4W required four tyres")

        self.state = 0
        self.frontRight = tyres[0][1]
        self.frontLeft = tyres[1][1]
        self.backRight = tyres[2][1]
        self.backLeft = tyres[3][1]

        self.stop()  # Stop the car, reset pins.

        self.collision = Collision(sensors)
        self.collision.start()

        logger.debug("Waiting to collision sensor to get ready")
        while not self.collision.ready:
            sleep(0.5)
        logger.info("Collision sensors are ready.")

        logger.debug("Waiting to camera to get ready")
        self.cameras = cameras
        for camera in self.cameras:
            camera[1].start()
            
        for camera in self.cameras:
            while not camera[1].ready:
                sleep(0.5)
            logger.debug(camera[0] + " is ready.")
        logger.info("Cameras are ready.")
        
        #Thread(target=self._auto_stop).start()

    # def _auto_stop(self):
    #     # Using take_action because we want to update action_id
    #     logger.debug("_auto_stop()")
    #     while True:
    #         if self.state in [State.FORWARD, State.FORWARD_LEFT, State.FORWARD_RIGHT]:
    #             collision = self.collision.get()
    #             #logger.info("Ultrasonic Values: " + str(collision))
    #             if collision.get("center") and self.state == State.FORWARD:
    #                 logger.debug("Center collision detected, stopping.")
    #                 self.take_action("stop")
    #             elif collision.get("left") and self.state == State.FORWARD_LEFT:
    #                 logger.debug("Left collision detected, stopping.")
    #                 self.take_action("stop")
    #             elif collision.get("right") and self.state == State.FORWARD_RIGHT:
    #                 logger.debug("Right collision detected, stopping.")
    #                 self.take_action("stop")
    #             else:
    #                 self.take_action("idle")
    #         else:
    #            self.take_action("idle")
    #         print "auto_stop"
    #         sleep(self.timeframe)

    def speed(self, speedup=1.5):
        percent = self.car_speed * speedup
        
        if percent > 100:
            percent = 100
        
        self.frontRight.speed(percent)
        self.frontLeft.speed(percent)
        self.backRight.speed(percent)
        self.backLeft.speed(percent)

    def set_timeframe(self, timeframe):
        self.timeframe = timeframe

    def is_idle(self):
        return self.state in (State.IDLE, State.STOPPED)

    def take_action(self, method_name):
        logger.debug("Taking action, " + method_name)
        #self.action_id += 1 # This function is called from Websocket
        method = getattr(self, method_name)
        method()

    def get_state(self):
        return self.state

    def get_state_vector(self, latest=False, for_network=False): # for_network convert numpy to list because it is faster for pickle
        start_time = time.time()

        state = {}
        
        # ADDING: Sensors details
        sensors = self.collision.get(latest)
        state['sensors'] = sensors
        
        # ADDING: Camera data
        for camera in self.cameras:
            name = camera[0]
            frame = camera[1].get_frame(latest)

            if for_network == True:
                stream = cStringIO.StringIO()
                frame = frame[:,:,::-1]
                #frame = np.roll(frame, 1, axis=-1) # BGR to RGB
                frame = Image.fromarray(frame, 'RGB')
                frame.save(stream, format="JPEG")
                frame = base64.b64encode(stream.getvalue()).decode("utf-8")

            state[name] = frame

        #logger.debug("Received State in {} seconds".format(time.time() - start_time))
        return state # converted to pickle in State.py

    def forward(self):
        self.speed(1)
        self.state = State.FORWARD
        self.frontLeft.forward()
        self.frontRight.forward()
        self.backLeft.forward()
        self.backRight.forward()

    def backward(self):
        self.speed(1)
        self.state = State.BACKWARD
        self.frontLeft.backward()
        self.frontRight.backward()
        self.backLeft.backward()
        self.backRight.backward()

    def idle(self):
        self.state = State.IDLE
        self.stop()

    def stop(self):
        self.speed(1)
        self.state = State.STOPPED
        self.frontLeft.stop()
        self.frontRight.stop()
        self.backLeft.stop()
        self.backRight.stop()

    def forwardRight(self):
        self.speed(1.5)
        self.frontLeft.forward()
        self.backLeft.forward()

        self.frontRight.backward()
        self.backRight.backward()
        self.state = State.FORWARD_RIGHT

    def forwardLeft(self):
        self.speed(1.5)
        self.frontRight.forward()
        self.backRight.forward()

        self.frontLeft.backward()
        self.backLeft.backward()
        self.state = State.FORWARD_LEFT

    def backwardRight(self):
        self.speed(1.5)
        self.state = State.BACKWARD_RIGHT
        self.frontLeft.backward()
        self.backLeft.backward()

        self.frontRight.forward()
        self.backRight.forward()

    def backwardLeft(self):
        self.speed(1.5)
        self.state = State.BACKWARD_LEFT
        self.frontRight.backward()
        self.backRight.backward()

        self.frontLeft.forward()
        self.backLeft.forward()

    def close(self):
        self.stop()
        self.collision.stop()
        for camera in self.cameras:
            camera[1].stop()

    def test(self):
        from time import sleep

        self.forward()
        sleep(0.5)
        self.stop()

        sleep(1)

        self.backward()
        sleep(0.5)
        self.stop()

        sleep(1)

        self.forwardRight()
        sleep(0.5)
        self.stop()

        sleep(1)

        self.forwardLeft()
        sleep(0.5)
        self.stop()

        sleep(1)

        self.backwardLeft()
        sleep(1)
        self.stop()

        sleep(1)

        self.backwardRight()
        sleep(1)
        self.stop()

    def __del__(self):
        GPIO.cleanup()

