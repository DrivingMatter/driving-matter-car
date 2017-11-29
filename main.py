import time
import threading
import io
import picamera
import tornado.web
import tornado.websocket
import logging
import signal
import sys
import json
import os
import pkgutil
import socket

from classes.Server import Server
from classes.LoadCar import load_car

from handlers import Action, State

# Work only on python 2 because using pickle and bytes difference in between python versions.
assert(sys.version_info.major == 2)

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
signal.signal(signal.SIGINT, signal.SIG_DFL)

car = load_car("config.json")

h = [
    (r"/action", Action.Action, {'car': car}),
    (r"/state", State.State, {'car': car, 'rps_ms': rps_ms}) # rps_ms: Request Per Seconds Millisecond
]

if __name__ == "__main__":
    try:
        logging.debug("main.py called")
        rc = RegisterCar()
        rc.register_car(socket.gethostname())
        s = Server(h, port=port)
        s.start()
    except KeyboardInterrupt:
        rc.unregister_car()
        print "Exiting"
