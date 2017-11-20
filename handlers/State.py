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
import pickle
from time import time
import logging

class State(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.stopped = False
        self.t = None
        self.car = kwargs.pop('car')
        self.rps_ms = kwargs.pop('rps_ms') # Request Per Seconds Milliseconds

        self.timer = [0, 0]
        self.timer_index = 0
        self.start_time = time()

        self.total_requests = 0

        self.inf_loop = PeriodicCallback(self.loop, callback_time=self.rps_ms) # 50 ms = 15 Request Per Seconds; 65 ms = 15 Request Per Seconds 

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
                self.start_time = time()
                self.inf_loop.start()
        elif message == "stop_read_state":
            self.inf_loop.stop()

    def loop(self):
        self.timer[self.timer_index] += 1

        self.total_requests += 1

        elapsed = time() - self.start_time

        if elapsed > 1:
            self.start_time = time()
            self.timer_index = 1
            self.timer[0] = (self.timer[0] + self.timer[1]) / 2  
            self.timer[1] = 0

        print ("RPS: " + str(self.timer[0]))

        state = self.car.get_state()
        
        state = pickle.dumps(state)
        self.write_message(state, True)

        print ("Total requests: " + str(self.total_requests) + "\t\t" + str(int(time())))

