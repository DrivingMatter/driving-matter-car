# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import io
from PIL import Image
import numpy as np

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.rotation = 180
camera.resolution = (320, 240)
camera.framerate = 20
rawCapture = PiRGBArray(camera, size=(320, 240))
stream = io.BytesIO()
# allow the camera to warmup
time.sleep(0.1)

start = time.time()
print (start)
i = 0 
# capture frames from the camera
for frame in camera.capture_continuous(stream, format="jpeg", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    # show the frame
    # img = frame.array
    stream.seek(0)

    #593 - 30 sec else 524
    #img = np.asarray(Image.open(stream))
    #cv2.imshow("Frame", img)

    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    #rawCapture.truncate(0)
    #stream.seek(0)
    stream.truncate(0)


    if (time.time() - start) > 30:
        break
    
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
    	break
    i += 1
print (i)
print (time.time() - start)
