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


class State(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.stopped = False
        self.t = None
        self.car = kwargs.pop('car')
        super(State, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        if message == "send_state":
            self.write_message(self.car.get_state(), True)
            logging.debug("Sent send_state")
        elif message == "read_state":
            if self.t == None:
                self.t = threading.Thread(target=self.loop)
                self.t.start()
        elif message == "stop_read_state":
            self.stopped = True

    def loop(self):
        while True:
            if self.stopped:
                self.t = None
                self.stopped = False
                return
            self.write_message(self.car.get_state(), True)