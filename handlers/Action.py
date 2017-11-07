import tornado
import logging
import threading
import picamera
from threading import Thread
from queue import Queue
import picamera
import tornado.web
import tornado.websocket
from time import sleep
import io


class Action(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.q = Queue()
        self.t = None
        self.car = kwargs.pop('car')
        super(Action, self).__init__(*args, **kwargs)

    def check_origin(self, origin):
        return True

    def _execute_actions(self):
        logging.debug("Action()._execute_action()")
        while True:
            message = self.q.get()
            if message:
                logging.debug("Message => " + message)
                message = message.split(" ")
                method_name = message[1]
                if hasattr(self.car, method_name):
                    method = getattr(self.car, method_name)
                    method()
                    self.q.task_done()
                else:
                    logging.error("Invalid method " + method_name)
            else:
                self.car.stop()

    def on_message(self, message):
        if not self.t:
            logging.debug("Thread Create for execute action")
            self.t = Thread(target=self._execute_actions)
            self.t.start()
        try:
            logging.debug("Message recevied: " + message)
            self.q.put(message)
        except tornado.websocket.WebSocketClosedError:
            pass
