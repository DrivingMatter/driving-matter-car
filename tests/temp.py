import RPi.GPIO as GPIO                    #Import GPIO library
import time                                #Import time library
GPIO.setmode(GPIO.BCM)                     #Set GPIO pin numbering 

TRIG = 5                                  #Associate pin 23 to TRIG
ECHO = 6                                  #Associate pin 24 to ECHO

print "Distance measurement in progress"

GPIO.setup(TRIG,GPIO.OUT)                  
GPIO.setup(ECHO,GPIO.IN)                   

while True:

  GPIO.output(TRIG, False)                 
  print "Waitng For Sensor To Settle"
  time.sleep(2)                            

  GPIO.output(TRIG, True)                  
  time.sleep(0.00001)                      
  GPIO.output(TRIG, False)                 

  while GPIO.input(ECHO)==0:               
    pulse_start = time.time()              

  while GPIO.input(ECHO)==1:               
    pulse_end = time.time()                

  pulse_duration = pulse_end - pulse_start 
  
  distance = pulse_duration * 17150 
  print distance       
  distance = round(distance, 2)            

  # if distance > 2 and distance < 400:     
  #   print "Distance:",distance - 0.5,"cm"  
  # else:
  #   print "Out Of Range"                   