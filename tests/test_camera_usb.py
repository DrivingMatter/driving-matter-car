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

c = Camera(USB, camera_num=0, resolution=(
    320, 240), framerate=15, rotation=180)
c.start()

framerate = 0
start = time()
while True:

    if c.ready and c.more():
        framerate += 1
        frame = c.get_frame()
        stream = io.BytesIO()
        stream.write(frame)
        stream.seek(0)
        img = Image.open(stream)
        img = np.asarray(img)
        cv2.imshow("camera_c", img)
        stream.seek(0)
        key = cv2.waitKey(1) & 0xFF

        print ("FPS: " + str(framerate / (time() - start)))
