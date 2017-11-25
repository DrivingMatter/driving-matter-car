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


class Action(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.q = Queue(maxsize=2)
        self.t = None
        self.car = kwargs.pop('car')
        super(Action, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def _execute_actions(self):
        logging.debug("Action()._execute_action()")
        while True:
            message = self.q.get()

            # Wait until car is idle
            while not self.car.is_idle():
                print("Waiting...")
                sleep(0.01)

            logging.debug("Message => " + message)
            message = message.split(" ")
            method_name = message[1]
            if hasattr(self.car, method_name):
                self.car.take_action(method_name)
                self.q.task_done()

            else:
                logging.error("Invalid method " + method_name)
        
    def on_message(self, message):
        if not self.t:
            logging.debug("Thread create to handle _execute_action")
            self.t = Thread(target=self._execute_actions)
            self.t.start()
        try:
            logging.debug("Message recevied: " + message)
            self.q.put_nowait(message)
        except tornado.websocket.WebSocketClosedError:
            pass
        except Queue.Full:
            msg = str(message)
            logging.debug("Action ignored, Queue already full. #" + msg)
            self.write_message("Action ignored, Queue already full. #" + msg)
