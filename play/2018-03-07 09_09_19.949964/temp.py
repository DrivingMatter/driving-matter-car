import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import cv2
import numpy as np
import math
import threading
from threading import Thread
import timeit


image=cv2.imread("img40.jpg",1)
gray_image = cv2.cvtColor(image , cv2.COLOR_RGB2GRAY)
cv2.imshow("img",gray_image)
cv2.waitKey(0)
classifier=cv2.CascadeClassifier("stopsign_classifier.xml")

sign=classifier.detectMultiScale(
                gray_image,
                scaleFactor=1.2,
                minNeighbors=1,
                minSize=(20,20),
                flags=cv2.CASCADE_SCALE_IMAGE
                )
        
for (x,y,w,h) in sign:
    print "in detect"
    cv2.rectangle(image,(x,y),(x+w,y+h),(255,219,0),2)

cv2.imshow("img",image)
cv2.waitKey(0)