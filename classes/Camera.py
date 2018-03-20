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
from time import sleep, time
import numpy as np

PICAMERA = 0
USB = 1

class Camera():
    def __init__(self, camera_type, camera_num=0, resolution=(320, 240), framerate=20, rotation=0):
        self.fps = None
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
            self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, w)
            self.camera.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, h)
            #self.camera.set(cv2.cv.CV_CAP_PROP_FPS, framerate) # doesnt works, using sleep to maintain fps
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
        self.t.daemon = True
        self.t.start()

    def update_picamera(self):
        stream = PiRGBArray(self.camera)
        image = self.camera.capture_continuous(stream, format="bgr", use_video_port=True)
            
        start = time()
        temp_fps = 0
        
        while True:
            if self.stopped:
                return

            frame = image.next()
            
            # Framerate updater
            if (time()-start) >= 1:
                self.fps = temp_fps
                temp_fps = 0
                start = time()
            temp_fps += 1
            
            
            frame = frame.array
            stream.truncate(0)
            
            if self.Q.full():
                self.Q.get()
                
            self.Q.put(frame)
            # logging.info("Camera(): Frame added to queue")

            self.ready = True

    def update_usb(self):
        start = time()
        temp_fps = 0
        while True:
            if self.stopped:
                return
            
            (grabbed, frame) = self.camera.read()
            
            # Framerate updater
            if (time()-start) >= 1:
                self.fps = temp_fps
                temp_fps = 0
                start = time()
            temp_fps += 1
            
            if not grabbed:
                self.stop()
                return

            if self.rotation != 0:
                frame = cv2.flip(frame, self.rotation)
            
            if self.Q.full():
                self.Q.get()
            
            self.Q.put(frame)
            #logging.info("Camera(): Frame added to queue")
            
            self.ready = True
            
            #sleep(0.2)
            sleep(self.framerate_ms) # webcam doesn't go over 9 fps on Raspberry Pi
            
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
        if latest and not self.Q.empty():
            size = self.Q.qsize()
            for i in range(size-2): # Keep atleast x values in queue
                self.Q.get()
            return self.Q.get()#, size
        else:
            return self.Q.get(timeout=10)#, "Wait" # OpenCV throw select timeout after 10 sec

    def clear_queue(self):
        self.Q.clear()
