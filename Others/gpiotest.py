import RPi.GPIO as GPIO
from time import sleep
from gpiozero import DistanceSensor 
pin = 11

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(pin, GPIO.OUT)

ultrasonic = DistanceSensor(echo=21, trigger=20, max_distance=1, threshold_distance=0.3)

#ultrasonic.distance
while True:
    
   #print(ultrasonic.distance)
   #sleep(0.2)
   ultrasonic.wait_for_in_range()
   print("In range")
   ultrasonic.wait_for_out_of_range()
   print("Out of range") 



#GPIO.cleanup()
