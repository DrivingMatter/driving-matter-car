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

logger = logging.getLogger(__name__)
GPIO.setmode(GPIO.BCM)

class Car4W:
    def __init__(self, tyres, sensors=[], cameras=[], timeframe=0.1):
        logger.debug("Car4W.__init__()")
        
        self.action_id = 0

        self.t = None
        self.camera = None
        self.timeframe = timeframe

        if len(tyres) != 4:
            raise EnvironmentError("Car4W required four tyres")

        self.state = 0
        self.frontRight = tyres[0][1]
        self.frontLeft = tyres[1][1]
        self.backRight = tyres[2][1]
        self.backLeft = tyres[3][1]

        self.collision = Collision(sensors)
        self.collision.start()

        self.cameras = cameras
        for camera in self.cameras:
            camera[1].start()

        #Thread(target=self._auto_stop).start()

        self.stop()  # Stop the car, reset pins.

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

    def get_state_vector(self):
        start_time = time.time()

        state = {}

        # ADDING: Sensors details
        sensors = self.collision.get()
        state['sensors'] = sensors
        
        # ADDING: Camera data
        for camera in self.cameras:
            name = "camera_" + camera[0]
            frame = camera[1].get_frame()
            state[name] = frame

        #logger.debug("Received State in {} seconds".format(time.time() - start_time))
        return state # converted to pickle in State.py

    def forward(self):
        # None mean sensor doesn't exists, False mean no collision
        if self.collision.get().get("center") in (False, None):
            self.state = State.FORWARD
            self.frontLeft.forward()
            self.frontRight.forward()
            self.backLeft.forward()
            self.backRight.forward()
        else:
            self.stop()
            logger.debug("forward() => Center collision")

    def backward(self):
        self.state = State.BACKWARD
        self.frontLeft.backward()
        self.frontRight.backward()
        self.backLeft.backward()
        self.backRight.backward()

    def idle(self):
        self.state = State.IDLE
        self.stop()

    def stop(self):
        self.state = State.STOPPED
        self.frontLeft.stop()
        self.frontRight.stop()
        self.backLeft.stop()
        self.backRight.stop()

    def forwardRight(self):
        if self.collision.get().get("right") in (False, None):
            self.frontLeft.forward()
            self.backLeft.forward()

            self.frontRight.stop()
            self.backRight.stop()
            self.state = State.FORWARD_RIGHT
        else:
            self.stop()
            logger.debug("forwardRight() => Right collision")

    def forwardLeft(self):
        if self.collision.get().get("left") in (False, None):
            self.frontRight.forward()
            self.backRight.forward()

            self.frontLeft.stop()
            self.backLeft.stop()
            self.state = State.FORWARD_LEFT
        else:
            self.stop()
            logger.debug("forwardLeft() => Left collision")

    def backwardRight(self):
        self.state = State.BACKWARD_RIGHT
        self.frontLeft.backward()
        self.backLeft.backward()

        self.frontRight.stop()
        self.backRight.stop()

    def backwardLeft(self):
        self.state = State.BACKWARD_LEFT
        self.frontRight.backward()
        self.backRight.backward()

        self.frontLeft.stop()
        self.backLeft.stop()

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
        sleep(3)
        self.stop()

        sleep(1)

        self.backwardRight()
        sleep(3)
        self.stop()

    def __del__():
        GPIO.cleanup()