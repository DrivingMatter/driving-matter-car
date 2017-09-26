import RPi.GPIO as GPIO
from time import sleep
import os
import sys

GPIO.setmode(GPIO.BCM)

class Tyre:
    forwardPin = None
    backwardPin = None
    pwm = None
    pwmPin = None
    
    def __init__(self, forwardPin, backwardPin, pwmPin=False, defaultPwm=50):
        GPIO.setup(forwardPin, GPIO.OUT)
        GPIO.setup(backwardPin, GPIO.OUT)
        GPIO.setup(pwmPin, GPIO.OUT)
        
        if pwmPin:
            self.pwmPin = pwmPin
            self.pwm = GPIO.PWM(pwmPin, 100)
            self.pwm.start(defaultPwm)
            print ("defaultPwn = " + str(defaultPwm))
            GPIO.output(pwmPin, GPIO.HIGH)

        self.forwardPin = forwardPin
        self.backwardPin = backwardPin

    def speed(self, percent=80):
        self.pwm.stop()
        GPIO.output(self.pwmPin, GPIO.LOW)
        
        self.pwm = GPIO.PWM(self.pwmPin, 100)
        self.pwm.start(percent)
        GPIO.output(self.pwmPin, GPIO.HIGH)

        #self.pwm.ChangeDutyCycle(percent)

    def forward(self):
        GPIO.output(self.forwardPin, GPIO.HIGH)
        GPIO.output(self.backwardPin, GPIO.LOW)

    def backward(self):
        GPIO.output(self.backwardPin, GPIO.HIGH)
        GPIO.output(self.forwardPin, GPIO.LOW)

    def stop(self):
        GPIO.output(self.forwardPin, GPIO.LOW)
        GPIO.output(self.backwardPin, GPIO.LOW)

    def test(self):
        from time import sleep

        self.forward()
        sleep(1)
        self.stop()

        self.backward()
        sleep(1)
        self.stop()

    def __del__(self):
        self.stop()
        GPIO.output(pwmPin, GPIO.LOW)
        self.pwm.stop()

class Car4W:
    frontRight = None
    frontLeft = None
    backRight = None
    backLeft = None
    
    def __init__(self,frontRight,frontLeft,backRight,backLeft):
        self.frontRight = frontRight
        self.frontLeft = frontLeft
        self.backRight = backRight
        self.backLeft = backLeft

    def forward(self):
        self.frontLeft.forward()
        self.frontRight.forward()
        self.backLeft.forward()
        self.backRight.forward()

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
        self.frontLeft.forward()
        self.backLeft.forward()

        self.frontRight.stop()
        self.backRight.stop()

    def forwardLeft(self):
        self.frontRight.forward()
        self.backRight.forward()

        self.frontLeft.stop()
        self.backLeft.stop()

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

def getch():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        fd = sys.stdin.fileno()
        import termios
        
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result

frontRight = Tyre(24, 25, 19, 100)
frontLeft = Tyre(11, 9, 13, 100)
backLeft = Tyre(15, 14, 12, 100)
backRight = Tyre(23, 17, 18, 100)

#t.forward()

#sleep(3)
#t.speed(50)
#sleep(3)
#t.speed(100)
#sleep(3)


#t.speed(50)
#t.forward()
#sleep(3)
#t.stop()

#frontRight.forward()
#frontLeft.forward()
#sleep(3)

"""
frontRight.speed(100)
frontRight.forward()
sleep(1)
frontRight.speed(75)
frontRight.forward()
sleep(1)
"""
"""
frontLeft.test()
frontRight.test()
backLeft.test()
backRight.test()
"""

car = Car4W(frontRight, frontLeft, backRight, backLeft)
car.stop()
#car.test()

try:
    while True:
        print ("Running...")
        key = ord(getch())
        print (key)
        if key == 32: #Space
            car.stop()
        if key == 91: #Special keys (arrows, f keys, ins, del, etc.)
            key = ord(getch())
            print (key)
            if key == 66: #Down arrow
                car.backward()	
            elif key == 68: #Left arrow
                car.forwardLeft()			
            elif key == 67: #Right arrow
                car.forwardRight()			
            elif key == 65: #Up arrow
                car.forward()
finally:
    car.stop()
    GPIO.cleanup() # this ensures a clean exit

#GPIO.cleanup() # this ensures a clean exit
