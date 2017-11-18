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

GPIO.setmode(GPIO.BCM)


class Car4W:
    FORWARD = 1
    FORWARD_LEFT = 2
    FORWARD_RIGHT = 3
    BACKWARD = 4
    BACKWARD_LEFT = 5
    BACKWARD_RIGHT = 6
    STOPPED = 7

    def __init__(self, tyres, sensors=[], cameras=[], timeframe=0.1):
        logging.debug("Car4W.__init__()")
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
        logging.debug("_auto_stop()")
        while True:
            if self.state in [self.FORWARD, self.FORWARD_LEFT, self.FORWARD_RIGHT]:
                collision = self.collision.get()
                logging.info("Ultrasonic Values: " + str(collision))
                if collision.get("center") and self.state == self.FORWARD:
                    logging.debug("Center collision detected, stopping.")
                    self.stop()
                if collision.get("left") and self.state == self.FORWARD_LEFT:
                    logging.debug("Left collision detected, stopping.")
                    self.stop()
                if collision.get("right") and self.state == self.FORWARD_RIGHT:
                    logging.debug("Right collision detected, stopping.")
                    self.stop()
            sleep(self.timeframe)

            # TODO: Sent the new state

    def get_state(self):
        start_time = time.time()
        #logging.debug("Collecting state")

        state = {}

        # ADDING: Car state
        state['car_state'] = self.state # Put car state eg FOWARD, RIGHT, LEFT

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

    def _get_string_for_bytes(self, name, size = 16):
        space_count = size - len(name)
        assert(space_count >= 0)
        return name + (" " * space_count)


    def _int_to_bytes(self, val, size = 4):
        return ('%%0%dx' % (size << 1) % val).decode('hex')[-size:]
        # return (val).to_bytes(size, byteorder='big')

    def forward(self):
        # None mean sensor doesn't exists, False mean no collision
        if self.collision.get().get("center") in (False, None):
            self.state = self.FORWARD
            self.frontLeft.forward()
            self.frontRight.forward()
            self.backLeft.forward()
            self.backRight.forward()
        else:
            self.stop()
            logging.debug("forward() => Center collision")

    def backward(self):
        self.state = self.BACKWARD
        self.frontLeft.backward()
        self.frontRight.backward()
        self.backLeft.backward()
        self.backRight.backward()

    def stop(self):
        self.state = self.STOPPED
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
            self.state = self.FORWARD_RIGHT
        else:
            self.stop()
            logging.debug("forwardRight() => Right collision")

    def forwardLeft(self):
        if self.collision.get().get("left") in (False, None):
            self.frontRight.forward()
            self.backRight.forward()

            self.frontLeft.stop()
            self.backLeft.stop()
            self.state = self.FORWARD_LEFT
        else:
            self.stop()
            logging.debug("forwardLeft() => Left collision")

    def backwardRight(self):
        self.state = self.BACKWARD_RIGHT
        self.frontLeft.backward()
        self.backLeft.backward()

        self.frontRight.stop()
        self.backRight.stop()

    def backwardLeft(self):
        self.state = self.BACKWARD_LEFT
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

