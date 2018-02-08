import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import cv2
import numpy as np
import math
import threading
from threading import Thread

class SignDetection:

    def __init__(self):
        self.image=[]
        self.red_light = False
        self.green_light = False
        self.yellow_light = False
        self.alpha = 8.0 * math.pi / 180
        self.v0 = 119.865631204
        self.ay = 332.262498472
        self.focal_length=(57*30)/4.5
        
    def detect_obj(self,classifier,image,type=""):
        self.image=image
        v=0
        gray_image = cv2.cvtColor(self.image , cv2.COLOR_BGR2GRAY)
        sign=classifier.detectMultiScale(gray_image,1.02,10)
        if type=='Traffic light':
            sign=classifier.detectMultiScale(gray_image,1.2,7)
        for (x,y,w,h) in sign:
            cv2.rectangle(self.image,(x,y),(x+w,y+h),(0,219,255),2)
            v = y + h - 5
            d=self.distance_to_camera(v, 15.5 - 10, 300)
            #d=self.distance_to_camera_temp(v)
            cv2.putText(self.image, "%s %.1fcm" %(type, d), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,219,255), 1)
            if type=='Traffic light':
                boundaries = [
                  ([17, 15, 100], [50, 50, 204]),  #red
                #	([255, 178, 189], [229, 25, 54]),      #green
                  ([100, 25, 6], [255, 178, 233]),  #green is yet to find
                  ([25, 146, 190], [62, 174, 250])] 
                roi=self.image[y+5:y + h-5, x+15:x + w-15] 
                roi = cv2.blur(roi,(5,5))
    
                for (lower, upper) in boundaries:
                    lower = np.array(lower, dtype = "uint8")
                    upper = np.array(upper, dtype = "uint8")
                    #print(lower)                   
                    mask = cv2.inRange(roi, lower, upper)
                    output = cv2.bitwise_and(roi, roi, mask = mask)
                    gray = cv2.cvtColor(output , cv2.COLOR_BGR2GRAY)        
                    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
                    
                    pos=len(gray)/3
                    if maxVal:
                        if pos > maxLoc[1]:
                            cv2.putText(self.image, 'Red', (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                            red_light = True
                            break
                        
                        # Green light  (This has problem, becuase of range)
                        elif 3*pos > maxLoc[1] > 2*pos:
                            cv2.putText(self.image, 'Green', (x+5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                            green_light = True
                            break
                        # yellow light
                        elif 2*pos > maxLoc[1] > pos:
                            cv2.putText(self.image, 'Yellow', (x+5, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                            yellow_light = True
                            break
                
    
        
    def detect(self,image):
        self.image=image
        sign={}
                     
        sign['Traffic light']= cv2.CascadeClassifier("../classifiers/trafficlight_LBP_classifier.xml")
        sign['Stop']= cv2.CascadeClassifier("../classifiers/stopsign_classifier.xml")
        sign['No Left'] = cv2.CascadeClassifier("../classifiers/noleftturn_classifier.xml")
        
        
##        self.detect_obj(stop_classifier)
        signs = [key for key in sign]
        t={}
        for type in signs:
            t[type]=Thread(target = self.detect_obj,args=(sign[type],self.image,type))
            t[type].start()
        [t[type].join() for type in signs]    
            
##        gray_image = cv2.cvtColor(image , cv2.COLOR_BGR2GRAY)
##        stop_sign = stop_classifier.detectMultiScale(gray_image,1.02,10)
##        traffic_light = light_classifier.detectMultiScale(gray_image,1.02,10)
##        no_left = noleft_classifier.detectMultiScale(gray_image,1.02,10)
##
##        for (x,y,w,h) in stop_sign:
##            cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
##            v = y + h - 5
##            d=self.distance_to_camera(v, 15.5 - 10, 100, image)
##            cv2.putText(image, "STOP %.1fcm" % d, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
##            
##        for (x,y,w,h) in traffic_light:
##            cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,255),2)
##            v = y + h - 5
##            d=self.distance_to_camera(v, 15.5 - 10, 100, image)
##            cv2.putText(image, 'Traffic Light %.1fcm' % d, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
##        
##        for (x,y,w,h) in no_left:
##             cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
##             v = y + h - 5
##             d=self.distance_to_camera(v, 15.5 - 10, 100, image)
##             cv2.putText(image, 'No-left-Turn %.1fcm' % d, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255,0), 2)
##
        
        return image
    
    def distance_to_camera(self, v, h, x_shift):
        return h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))
    
    def distance_to_camera_temp(self,v):
        return (4.5*self.focal_length)/v
  
        