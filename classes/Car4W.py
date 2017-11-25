import RPi.GPIO as GPIO
import logging
from time import sleep
from threading import Thread
import json
import picamera
import io
from Collision import Collision
from classes.Camera import Camera, PICAMERA, USB
import pickle
import time
from enum import Enum

GPIO.setmode(GPIO.BCM)

class State (Enum):
    IDLE            = 0
    FORWARD         = 1
    FORWARD_LEFT    = 2
    FORWARD_RIGHT   = 3
    BACKWARD        = 4
    BACKWARD_LEFT   = 5
    BACKWARD_RIGHT  = 6
    STOPPED         = 7

class Car4W:
    def __init__(self, tyres, sensors=[], cameras=[], timeframe=0.1):
        logging.debug("Car4W.__init__()")
        
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

        Thread(target=self._auto_stop).start()

        self.stop()  # Stop the car, reset pins.

    def _auto_stop(self):
        # Using take_action because we want to update action_id
        logging.debug("_auto_stop()")
        while True:
            if self.state in [State.FORWARD, State.FORWARD_LEFT, State.FORWARD_RIGHT]:
                collision = self.collision.get()
                logging.info("Ultrasonic Values: " + str(collision))
                if collision.get("center") and self.state == State.FORWARD:
                    logging.debug("Center collision detected, stopping.")
                    self.take_action("stop")
                if collision.get("left") and self.state == State.FORWARD_LEFT:
                    logging.debug("Left collision detected, stopping.")
                    self.take_action("stop")
                if collision.get("right") and self.state == State.FORWARD_RIGHT:
                    logging.debug("Right collision detected, stopping.")
                    self.take_action("stop")
            else:
               self.take_action("idle")
            
            sleep(self.timeframe)

    def set_timeframe(self, timeframe):
        self.timeframe = timeframe

    def is_idle(self):
        return self.state == State.IDLE

    def take_action(self, method_name):
        self.action_id += 1 # This function is called from Websocket
        method = getattr(self, method_name)
        method()

    def get_state(self):
        return self.state

    def get_state_vector(self):
        start_time = time.time()
        #logging.debug("Collecting state")

        state = {}

        # ADDING: Car state
        state['car_state'] = self.state.name # Put car state eg FOWARD, RIGHT, LEFT
        state['car_action_id'] = self.car_action_id # Put car state eg FOWARD, RIGHT, LEFT

        # ADDING: Sensors details
        sensors = self.collision.get()
        state['sensors'] = sensors
        
        # ADDING: Camera data
        for camera in self.cameras:
            name = "camera_" + camera[0]
            frame = camera[1].get_frame()
            state[name] = frame

        logging.debug("Received State in {} seconds".format(time.time() - start_time))
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
            logging.debug("forward() => Center collision")

    def backward(self):
        self.state = State.BACKWARD
        self.frontLeft.backward()
        self.frontRight.backward()
        self.backLeft.backward()
        self.backRight.backward()

    def idle(self):
        self.state = State.IDLE
        self.frontLeft.stop()
        self.frontRight.stop()
        self.backLeft.stop()
        self.backRight.stop()

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
            logging.debug("forwardRight() => Right collision")

    def forwardLeft(self):
        if self.collision.get().get("left") in (False, None):
            self.frontRight.forward()
            self.backRight.forward()

            self.frontLeft.stop()
            self.backLeft.stop()
            self.state = State.FORWARD_LEFT
        else:
            self.stop()
            logging.debug("forwardLeft() => Left collision")

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

        sleep(3)

        self.backward()
        sleep(0.5)
        self.stop()

        sleep(3)

        self.forwardRight()
        sleep(0.5)
        self.stop()

        sleep(3)

        self.forwardLeft()
        sleep(0.5)
        self.stop()

        sleep(3)

        self.backwardLeft()
        sleep(0.5)
        self.stop()

        sleep(3)

        self.backwardRight()
        sleep(0.5)
        self.stop()

    def __del__():
        GPIO.cleanup()