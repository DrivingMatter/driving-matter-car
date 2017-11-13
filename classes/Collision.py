import picamera
import logging
import sys
from PIL import Image
import cv2
if sys.version_info >= (3, 0):
    from queue import Queue
else:
    from Queue import Queue
from threading import Thread
import io
from time import sleep

class Collision:
    def __init__(self, sensors, queue_size=2):
        self.history = None
        self.ready = False
        self.sensors = sensors  # [('center', object),...]
        self.stopped = False
        self.Q = Queue(maxsize=queue_size)
        self.t = None

    def start(self):
        if self.t:
            return

        self.t = Thread(target=self.update, args=())
        #self.t.daemon = True
        self.t.start()

    def update(self):
        while True:
            if self.stopped == True:
                return

            result = {}
            for sensor in self.sensors:
                result[sensor[0]] = sensor[1].check_collision()

            if self.Q.full():
                self.Q.get()  # open up the space

            self.Q.put(result)
            self.ready = True

            sleep(0.1)

    def stop(self):
        self.stopped = True
        self.t = None

    def more(self):
        return self.Q.qsize() > 0

    def get(self):
        result = None
        try:
            result = self.Q.get(0) # TODO: handle empty value when exceptions called
            self.history = result
        except Exception:
            return self.history
        return result

    def clear_queue(self):
        self.Q.clear()
