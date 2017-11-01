import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


class Tyre:

    def __init__(self, forwardPin, backwardPin, pwmPin=False, defaultPwm=50):
        self.forwardPin = None
        self.backwardPin = None
        self.pwm = None
        self.pwmPin = None

        GPIO.setup(forwardPin, GPIO.OUT)
        GPIO.setup(backwardPin, GPIO.OUT)
        GPIO.setup(pwmPin, GPIO.OUT)

        if pwmPin:
            self.pwmPin = pwmPin
            self.pwm = GPIO.PWM(pwmPin, 100)
            self.pwm.start(defaultPwm)
            #print ("defaultPwn = " + str(defaultPwm))
            GPIO.output(pwmPin, GPIO.HIGH)

        self.forwardPin = forwardPin
        self.backwardPin = backwardPin

    def speed(self, percent=80):
        self.pwm.stop()
        GPIO.output(self.pwmPin, GPIO.LOW)

        self.pwm = GPIO.PWM(self.pwmPin, 100)
        self.pwm.start(percent)
        GPIO.output(self.pwmPin, GPIO.HIGH)

        # self.pwm.ChangeDutyCycle(percent)

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
        GPIO.output(self.pwmPin, GPIO.LOW)
        self.pwm.stop()
