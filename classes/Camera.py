import picamera
from picamera.array import PiRGBArray
import logging
import sys
from PIL import Image
import cv2
if sys.version_info >= (3, 0):
    from queue import Queue
else:
    from Queue import Queue
from threading import Thread
import io
from time import sleep
import numpy as np

PICAMERA = 0
USB = 1

class Camera():
    def __init__(self, camera_type, camera_num=0, resolution=(320, 240), framerate=20, rotation=0):
        self.ready = False
        self.camera = None
        self.camera_type = camera_type
        self.stopped = False
        self.Q = Queue(maxsize=2*framerate)
        self.t = None
        self.history = None
        self.rotation = rotation
        self.resolution = resolution
        
        self.framerate_ms = 1.0/float(framerate)

        if self.camera_type == PICAMERA:
            self.camera = picamera.PiCamera()
            if rotation:
                self.camera.rotation = rotation    
            self.camera.resolution = resolution
            self.camera.framerate = framerate
            self.camera.sharpness = 0
            self.camera.contrast = 0
            self.camera.brightness = 65
            self.camera.saturation = 0
            self.camera.ISO = 0
            self.camera.video_stabilization = True
            self.camera.exposure_compensation = 0
            self.camera.exposure_mode = 'auto'
            self.camera.meter_mode = 'average'
            self.camera.awb_mode = 'auto'
            self.camera.image_effect = 'none'
            self.camera.color_effects = None
                        
            #sleep(2)
            
            #while self.camera.analog_gain < 1 or  self.camera.digital_gain < 1:
            #    sleep(0.1)
                
            #self.camera.exposure_mode = 'off'
            
            #if self.camera.analog_gain < 1 or  self.camera.digital_gain < 1:
            #    raise RuntimeError('low gains')
            
        elif self.camera_type == USB:
            w, h = resolution
            self.camera = cv2.VideoCapture(camera_num)
            self.camera.set(3, w)
            self.camera.set(4, h)
            self.camera.set(cv2.cv.CV_CAP_PROP_FPS, framerate)
        else:
            raise EnviormentError("Invalid camera type")

        #logging.debug("CameraOne.__init__()")

    def start(self):
        if self.t:
            return

        f = None
        if self.camera_type == PICAMERA:
            f = self.update_picamera
        else:
            f = self.update_usb

        self.t = Thread(target=f, args=())
        #self.t.daemon = True
        self.t.start()

    def update_picamera(self):
        stream = PiRGBArray(self.camera)
        image = self.camera.capture_continuous(stream, format="bgr", use_video_port=True)
            
        while True:
            if self.stopped:
                return

            frame = image.next()
            frame = frame.array
            stream.truncate(0)
            
            if self.Q.full():
                self.Q.get()
                
            self.Q.put(frame)
            # logging.info("Camera(): Frame added to queue")

            self.ready = True

    def update_usb(self):
        while True:
            if self.stopped:
                return

            (grabbed, frame) = self.camera.read()

            if not grabbed:
                self.stop()
                return

            frame = cv2.flip(frame, self.rotation)
            
            if self.Q.full():
                self.Q.get()
            
            self.Q.put(frame)
            #logging.info("Camera(): Frame added to queue")
            
            self.ready = True
                
            #sleep(self.framerate_ms)
            
    def stop(self):
        self.stopped = True
        if self.camera_type == USB:
            self.camera.release()
        else:
            self.camera.close()
        self.t = None

    def more(self):
        return not self.Q.empty()

    def ready(self):
        return self.ready

    def get_frame(self, latest = False):
        #logging.info("Camera Queue: " + str(self.Q.qsize()))
        while latest:
            #logging.info("Camera Queue: " + str(self.Q.qsize()))
            if not self.Q.empty():
                self.history = self.Q.get()
            else:
                break
        else:
            if not self.Q.empty():
                self.history = self.Q.get()        
        return self.history

    def clear_queue(self):
        self.Q.clear()
