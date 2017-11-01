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

PICAMERA = 0
USB = 1


class Camera():
    def __init__(self, camera_type, camera_num=0, resolution=(320, 240), framerate=15, rotation=None):
        self.ready = False
        self.camera = None
        self.camera_type = camera_type
        self.stopped = False
        self.Q = Queue(maxsize=framerate * 2)
        self.t = None

        if self.camera_type == PICAMERA:
            self.camera = picamera.PiCamera()
            self.camera.resolution = resolution
            if rotation:
                self.camera.rotation = rotation
            self.camera.framerate = framerate
        elif self.camera_type == USB:
            w, h = resolution
            self.camera = cv2.VideoCapture(camera_num)
            camera.set(3, w)
            camera.set(4, h)
        else:
            raise EnviormentError("Invalid camera type")

        logging.debug("CameraOne.__init__()")

    def start(self):
        if self.t:
            return

        f = None
        if self.camera_type == PICAMERA:
            f = self.update_picamera
        else:
            f = self.update_usb

        self.t = Thread(target=f, args=())
        self.t.daemon = True
        self.t.start()

    def update_picamera(self):
        stream = io.BytesIO()
        for frame in self.camera.capture_continuous(stream, format="jpeg", use_video_port=True):
            if self.stopped:
                return

            stream.seek(0)

            if not self.Q.full():
                self.Q.put(stream.getvalue())

            stream.truncate(0)

    def update_usb(self):
        stream = io.BytesIO()
        while True:
            if self.stopped:
                return

            if not self.Q.full():
                (grabbed, frame) = self.camera.read()

                if not grabbed:
                    self.stop()
                    return

                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img.save(sio, "JPEG")

                stream.seek(0)
                self.Q.put(stream.getvalue())
                stream.truncate(0)

                self.ready = True

    def stop(self):
        self.stopped = True
        if self.camera_type == USB:
            self.camera.release()
            cv2.destroyAllWindows()
        else:
            self.camera.stop()
        self.t = None

    def more(self):
        return self.Q.qsize() > 0

    def ready(self):
        return self.ready

    def get_frame(self):
        return self.Q.get()

    def clear_queue(self):
        self.Q.clear()
