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

c = Camera(PICAMERA, camera_num=0, resolution=(
    320, 240), framerate=10, rotation=180)
c.start()

framerate = [0, 0]
start = time()
while True:

    if c.ready and c.more():
        framerate[1] += 1
        
        frame = c.get_frame()
        if frame is not None:
            cv2.imshow("camera_c", frame)
            #stream.seek(0)
            key = cv2.waitKey(1) & 0xFF

        if time() - start > 1:
            framerate = [sum(framerate)/2, 0]
            start = time()

        print ("FPS: " + str(framerate[0]))
