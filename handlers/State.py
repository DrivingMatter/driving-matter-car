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
        self.car = kwargs.pop('car')
        super(State, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        print (message)
        if message == "send_state":
            self.write_message(self.car.get_state().getvalue(), True)
