import tornado
import logging
import threading
import picamera
from threading import Thread
from Queue import Queue
import picamera
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
from time import sleep
import io

class State(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.stopped = False
        self.t = None
        self.car = kwargs.pop('car')

        self.inf_loop = PeriodicCallback(self.loop, callback_time=50)
        super(State, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        if message == "send_state":
            state = self.car.get_state()
            self.write_message(state, True)
            logging.debug("Sent send_state")
        elif message == "read_state":
            if not self.inf_loop.is_running():
                self.inf_loop.start()
        elif message == "stop_read_state":
            self.inf_loop.stop()

    def loop(self):
        state = self.car.get_state()
        print ("Sending data")
        self.write_message(state, True)