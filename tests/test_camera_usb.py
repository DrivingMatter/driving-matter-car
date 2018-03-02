import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from classes.Camera import Camera, PICAMERA, USB
import os
from time import sleep
import cv2
from PIL import Image
import numpy as np
import io
from time import time

c = Camera(USB, camera_num=1, resolution=(320, 240), framerate=10, rotation=-1)
print "Starting..."
c.start()
print "Started"

start = time()
while True:

    if c.ready and c.more():
        
        frame = c.get_frame()
        #if frame is not None:
        #    cv2.imshow("camera_c", frame)
        #    #stream.seek(0)
        #    key = cv2.waitKey(1) & 0xFF

        #if time() - start > 1:
        #    framerate = [sum(framerate)/2, 0]
        #    start = time()
        print ("FPS: " + str(c.fps))
