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
import logging

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

            self.Q.put(result)
            #logging.info("Collision(): Info added to queue")

            self.ready = True

            sleep(0.5) # Required by UD Sensor Hardware

    def stop(self):
        self.stopped = True
        self.t = None

    def more(self):
        return not self.Q.empty()

    def get(self):
        # logging.info("Collision Queue: " + str(self.Q.qsize()))
        if not self.Q.empty():
            self.history = self.Q.get() # TODO: handle empty value when exceptions called
        return self.history
        
    def clear_queue(self):
        self.Q.clear()
