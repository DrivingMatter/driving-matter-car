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
logger = logging.getLogger(__name__)

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
        self.t.start()

    def update(self):
        while True:
            if self.stopped == True:
                return

            result = {}
            for sensor in self.sensors:
                result[sensor[0]] = sensor[1].check_collision()

            if self.Q.full():
                self.Q.get()
                
            self.Q.put(result)
            #logger.info("Collision(): Info added to queue")

            self.ready = True

            sleep(2) # Required by UD Sensor Hardware

    def stop(self):
        self.stopped = True
        self.t = None

    def more(self):
        return not self.Q.empty()

    def ready(self):
        return self.ready

    def get(self, latest = False):
        # logger.info("Collision Queue: " + str(self.Q.qsize()))
        while latest:
            if not self.Q.empty():
                self.history = self.Q.get()
            else:
                break
        else:
            if not self.Q.empty():
                self.history = self.Q.get()        
        return self.history
        
    def clear_queue(self):
        self.Q.clear()
