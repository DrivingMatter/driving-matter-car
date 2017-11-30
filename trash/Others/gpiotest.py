import RPi.GPIO as GPIO
from time import sleep
from gpiozero import DistanceSensor 
pin = 11

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(pin, GPIO.OUT)

ultrasonicR = DistanceSensor(echo=16, trigger=26, max_distance=1, threshold_distance=0.3)
ultrasonicC = DistanceSensor(echo=21, trigger=20, max_distance=1, threshold_distance=0.3)
ultrasonicL = DistanceSensor(echo=6, trigger=5, max_distance=1, threshold_distance=0.3)

#ultrasonic.distance
while True:
   print("="*80) 
   print("Right :", ultrasonicR.distance > 0.2)
   print("Center :", ultrasonicC.distance > 0.2)
   print("Left :", ultrasonicL.distance > 0.2)
   if 0.0 in [ultrasonicR.distance, ultrasonicC.distance, ultrasonicL.distance]:
      print("Yes")
   
   sleep(0.2)
   #ultrasonic.wait_for_in_range()
   #print("In range")
   #ultrasonic.wait_for_out_of_range()
   #print("Out of range") 



GPIO.cleanup()
