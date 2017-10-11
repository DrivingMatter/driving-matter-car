import RPi.GPIO as GPIO
from time import sleep
from gpiozero import DistanceSensor 


class CollisionSensor:
    collision_thresh_hold = 0.2

    def __init__(self, echo, trigger, max_distance=1):
        self.ultrasonic = DistanceSensor(echo=echo, trigger=trigger, max_distance=max_distance)

    def check_collision(self):
        return self.ultrasonic.distance > self.collision_thresh_hold:
            
             
"""

ultrasonicR = Collision_Sensor(echo=16, trigger=26)
ultrasonicC = Collision_Sensor(echo=21, trigger=20)
ultrasonicL = Collision_Sensor(echo=6, trigger=5)

#ultrasonic.distance
while True:

   print(ultrasonicL.check_collision())
   sleep(0.2)

GPIO.cleanup()

"""
