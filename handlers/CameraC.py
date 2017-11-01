import tornado
import logging
import threading
import picamera
from threading import Thread
from Queue import Queue
import picamera
import tornado.web
import tornado.websocket
from time import sleep
import io

class CameraC(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.t = None
        self.camera = None
        logging.debug("CameraOne.__init__()")
        super(CameraOne, self).__init__(*args, **kwargs)

    def start_camera(self):
        logging.debug("CameraOne.start_camera()") 
        if self.camera:
            self.camera.stop()
        self.camera = picamera.PiCamera()
        self.camera.start_preview()
        self.camera.rotation = 180
        self.camera.resolution= (320, 240)
        self.camera.framerate = 15

    def check_origin(self, origin):
        return True
    
    def on_message(self, message):
        if message == "read_camera":
            self.start_camera();
            sleep(0.2);
            if self.t == None:
                self.t = threading.Thread(target=self.loop)
                self.t.start()
        else:
            print("Unsupported function: " + message)

    def loop(self):
        stream = io.BytesIO()
        
        for frame in self.camera.capture_continuous(stream, format="jpeg", use_video_port=True):
            stream.seek(0)

            try:
                self.write_message(stream.getvalue(), True)
            except tornado.websocket.WebSocketClosedError:
                self.camera.close()
                self.camera = None
                break
            
            stream.truncate(0)   