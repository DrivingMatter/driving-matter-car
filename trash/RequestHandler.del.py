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
        global car  # TODO: Handle in better way
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
                car.stop()

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


class CameraOne(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        self.t = None
        self.camera = None
        logging.debug("CameraOne.__init__()")
        super(CameraOne, self).__init__(*args, **kwargs)

    def start_camera(self):
        logging.debug("CameraOne.start_camera()")
        if self.camera:
            self.camera.stop()
        self.camera = picamera.PiCamera()
        self.camera.start_preview()
        self.camera.rotation = 180
        self.camera.resolution = (320, 240)
        self.camera.framerate = 15

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        if message == "read_camera":
            self.start_camera()
            sleep(0.2)
            if self.t == None:
                self.t = threading.Thread(target=self.loop)
                self.t.start()
        else:
            print("Unsupported function: " + message)

    def loop(self):
        stream = io.BytesIO()

        for frame in self.camera.capture_continuous(stream, format="jpeg", use_video_port=True):
            stream.seek(0)

            try:
                self.write_message(stream.getvalue(), True)
            except tornado.websocket.WebSocketClosedError:
                self.camera.close()
                self.camera = None
                break

            stream.truncate(0)
