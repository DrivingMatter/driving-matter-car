import RPi.GPIO as GPIO
import time
from time import sleep
GPIO.setmode(GPIO.BCM) 
#from gpiozero import DistanceSensor


class CollisionSensor:
    collision_thresh_hold = 20

    def __init__(self, echo, trigger, max_distance=1):
        self.echo=echo
        self.trigger=trigger
        GPIO.setup(self.trigger,GPIO.OUT)                  
        GPIO.setup(self.echo,GPIO.IN)  
    
    def get_distance(self):
        GPIO.output(self.trigger, False)                 
        # print "Waitng For Sensor To Settle"
        #time.sleep(2)                            

        GPIO.output(self.trigger, True)                  
        time.sleep(0.00001)                      
        GPIO.output(self.trigger, False)                 

        pulse_start = 0
        pulse_end = 0

        while GPIO.input(self.echo)==0:               
          pulse_start = time.time()              

        while GPIO.input(self.echo)==1:               
          pulse_end = time.time()                

        pulse_duration = pulse_end - pulse_start 
        
        distance = pulse_duration * 17150    
        distance = round(distance, 2)        
        return distance

    def check_collision(self):
        return not (self.get_distance() > self.collision_thresh_hold)        


# ultrasonicR = CollisionSensor(echo=6, trigger=5)
# # ultrasonicC = CollisionSensor(echo=21, trigger=20)
# # ultrasonicL = CollisionSensor(echo=6, trigger=5)


# while True:
#    #print(ultrasonicR.get_distance())
#    print(ultrasonicR.check_collision())
   
#    sleep(0.2)



# GPIO.cleanup()

