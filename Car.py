import RPi.GPIO as GPIO
import logging
GPIO.setmode(GPIO.BCM)

class Car4W:
    frontRight = None
    frontLeft = None
    backRight = None
    backLeft = None
    sensors = []
    
    def __init__(self,frontRight,frontLeft,backRight,backLeft, sensors):
        self.frontRight = frontRight
        self.frontLeft = frontLeft
        self.backRight = backRight
        self.backLeft = backLeft
        self.sensors = sensors

        self.stop()

    def forward(self):
        if self.collision()[0]:
            self.frontLeft.forward()
            self.frontRight.forward()
            self.backLeft.forward()
            self.backRight.forward()
        else:
            logging.debug("forward() => Center collision")

    def backward(self):
        self.frontLeft.backward()
        self.frontRight.backward()
        self.backLeft.backward()
        self.backRight.backward()

    def stop(self):
        self.frontLeft.stop()
        self.frontRight.stop()
        self.backLeft.stop()
        self.backRight.stop()

    def forwardRight(self):
        if self.collision()[2]:
            self.frontLeft.forward()
            self.backLeft.forward()

            self.frontRight.stop()
            self.backRight.stop()
        else:
            logging.debug("forwardRight() => Right collision")

    def forwardLeft(self):
        if self.collision()[1]:
            self.frontRight.forward()
            self.backRight.forward()

            self.frontLeft.stop()
            self.backLeft.stop()
        else:
            logging.debug("forwardLeft() => Left collision")


    def backwardRight(self):
        self.frontLeft.backward()
        self.backLeft.backward()

        self.frontRight.stop()
        self.backRight.stop()

    def backwardLeft(self):
        self.frontRight.backward()
        self.backRight.backward()

        self.frontLeft.stop()
        self.backLeft.stop()

    def collision(self):
        collisions = []
        for sensor in self.sensors:
            collisions.append(sensor.check_collision())
        return collisions

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
        
