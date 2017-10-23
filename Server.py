import time
import threading
import io
import picamera
import tornado.web
import tornado.websocket
import logging
logging.basicConfig(level=logging.DEBUG)

import signal

from Car import Car4W
from Tyre import Tyre
#from RegisterCar import RegisterCar
from UDSensor import CollisionSensor
from RequestHandler import Action, CameraOne

signal.signal(signal.SIGINT, signal.SIG_DFL)

ultrasonic_c = CollisionSensor(echo=21, trigger=20)
ultrasonic_l = CollisionSensor(echo=6, trigger=5)
ultrasonic_r = CollisionSensor(echo=16, trigger=26)

sensors = [ultrasonic_c, ultrasonic_l, ultrasonic_r]

frontRight = Tyre(24, 25, 19, 50)
frontLeft = Tyre(11, 9, 13, 50)
backLeft = Tyre(15, 14, 12, 50)
backRight = Tyre(23, 17, 18, 50)

car = Car4W(frontRight, frontLeft, backRight, backLeft, sensors)

handlers = [
    (r"/camera_c", CameraOne),
    (r"/action", Action, {'car': car})
]

class Server():
    def __init__(self):
        # Currently starting from crontab -e
        # self.rc = RegisterCar()
        # self.rc.register_car("Mater")
        pass

    def start(self):
        global handlers
        
        application = tornado.web.Application(handlers)
        application.listen(8000)

        try:
            logging.debug("Starting Server Loop")
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            logging.debug("Exiting server loop")
            print "Exiting";

    # Destructor
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        rc.unregister_car()

try:
    logging.debug("Server.py called")
    s = Server()
    s.start()
except KeyboardInterrupt:
    print "Exiting";
