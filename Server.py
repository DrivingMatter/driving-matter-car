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

import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
from time import sleep
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from Car import Car4W
from Tyre import Tyre

frontRight = Tyre(24, 25, 19, 1)
frontLeft = Tyre(11, 9, 13, 1)
backLeft = Tyre(15, 14, 12, 1)
backRight = Tyre(23, 17, 18, 1)

car = Car4W(frontRight, frontLeft, backRight, backLeft)
car.stop()

class ActionAndSensor(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True
    
    def on_message(self, message):
        try:
            pass
            self.write_message("Yahoo");
            methodName = message
            if isinstance(methodName, car):
                method = getattr(car, methodName)
                method()
                print ("INFO: Calling " + methodName)
            else:
                print ("ERR: Invalid method " + methodName)
        except tornado.websocket.WebSocketClosedError:
            self.camera_loop.stop()

class CameraOne(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True
    
    def on_message(self, message):
        global camera

        if message == "close_camera":
            camera.stop();        
            print "close_camera"    
        elif message == "read_camera":
            #startCamera();
            sleep(0.2);

            t = threading.Thread(target=self.loop)
            t.start()
            #self.camera_loop = PeriodicCallback(self.loop, 10)
            #self.camera_loop.start()
        else:
            print("Unsupported function: " + message)

    def loop(self):
        global camera
        stream = io.BytesIO()

        for frame in camera.capture_continuous(stream, format="jpeg", use_video_port=True):
            stream.seek(0)

            try:
                #TODO: remove base64 from here
                self.write_message(base64.b64encode(stream.getvalue()))
                #self.write_message(stream.getvalue(), True)
            except tornado.websocket.WebSocketClosedError:
                self.camera_loop.stop()

            #593 - 30 sec else 524
            #img = np.asarray(Image.open(stream))
            #cv2.imshow("Frame", img)

            stream.truncate(0)

        #if args.use_usb:
        #    _, frame = camera.read()
        #    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        #    img.save(sio, "JPEG")
        #else:
        #camera.capture(sio, "jpeg", use_video_port=True)
        #try:
            #.tobytes("raw", "RGBA")
            #self.write_message(sio.getvalue())
        #    self.write_message(sio.getvalue(), True)
        #except tornado.websocket.WebSocketClosedError:
        #    self.camera_loop.stop()

        #sio.





parser = argparse.ArgumentParser(description="Starts a webserver that "
                                 "connects to a webcam.")
parser.add_argument("--port", type=int, default=8000, help="The "
                    "port on which to serve the website.")
parser.add_argument("--use-usb", action="store_true", help="Use a USB "
                    "webcam instead of the standard Pi camera.")
args = parser.parse_args()

if args.use_usb:
    import cv2
    from PIL import Image
else:
    import picamera
    
def startCamera(resolution = 'low'):
    global camera
    camera = picamera.PiCamera()
    camera.start_preview()
    camera.rotation = 180
    camera.resolution= (320, 240)
    camera.framerate = 20

startCamera()
handlers = set()

handlers = [
                (r"/CameraOne", CameraOne),
                (r"/ActionAndSensor", ActionAndSensor)
            ]

application = tornado.web.Application(handlers)
application.listen(args.port)

#webbrowser.open("http://localhost:%d/" % args.port, new=2)

try:
    tornado.ioloop.IOLoop.instance().start()
except KeyboardInterrupt:
    stopCamera();
    print "Exiting";
