import argparse
import base64
import hashlib
import os
import time
import threading
import webbrowser
import base64
#try:
#    import cStringIO as io
#except ImportError:
import io
import picamera

import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
from time import sleep
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

camera = None

from Car import Car4W
from Tyre import Tyre
from RegisterCar import RegisterCar
from UDSensor import CollisionSensor

ultrasonic_center = CollisionSensor(echo=21, trigger=20)
ultrasonic_left = CollisionSensor(echo=6, trigger=5)
ultrasonic_right = CollisionSensor(echo=16, trigger=26)

sensors = [ultrasonic_center, ultrasonic_left, ultrasonic_right]

frontRight = Tyre(24, 25, 19, 50)
frontLeft = Tyre(11, 9, 13, 50)
backLeft = Tyre(15, 14, 12, 50)
backRight = Tyre(23, 17, 18, 50)

car = Car4W(frontRight, frontLeft, backRight, backLeft, sensors)
car.stop()
#print ("Stop")
#car.test()
#print ("DoneTest")

class Server():
    def __init__():
        rc = RegisterCar()
        rc.register_car("Mater")

    # Destructor
    def __enter__(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback)
        rc.unregister_car()

class Action(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True
    
    def on_message(self, message):
        try:
            methodName = message
            print ("INFO: Calling " + methodName)
            method = getattr(car, methodName)
            if not car.collision():
                method()
            #print ("ERR: Invalid method " + methodName)
        except tornado.websocket.WebSocketClosedError:
            pass

class CameraOne(tornado.websocket.WebSocketHandler):
    t = None
    def check_origin(self, origin):
        return True
    
    def on_message(self, message):
        global camera

        if message == "read_camera":
            startCamera();
            sleep(0.2);
            if self.t == None:
                self.t = threading.Thread(target=self.loop)
                self.t.start()
        else:
            print("Unsupported function: " + message)

    def loop(self):
        global camera
        stream = io.BytesIO()
        import sys
        for frame in camera.capture_continuous(stream, format="jpeg", use_video_port=True):
            stream.seek(0)

            try:
                self.write_message(stream.getvalue(), True)
            except tornado.websocket.WebSocketClosedError:
                camera.close()
                camera = None
                break
            
            stream.truncate(0)
   
def startCamera():
    global camera
    if camera:
        camera.stop()
    camera = picamera.PiCamera()
    camera.start_preview()
    camera.rotation = 180
    camera.resolution= (320, 240)
    camera.framerate = 15

handlers = set()

handlers = [
    (r"/CameraOne", CameraOne),
    (r"/Action", Action)
]

application = tornado.web.Application(handlers)
application.listen(8000)

#webbrowser.open("http://localhost:%d/" % args.port, new=2)

try:
    tornado.ioloop.IOLoop.instance().start()
except KeyboardInterrupt:
    stopCamera();
    print "Exiting";
