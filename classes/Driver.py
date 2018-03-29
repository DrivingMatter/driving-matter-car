from SignDetection import SignDetection
from State import ACTIONS, COLLISIONS
from datetime import datetime
from time import sleep
from PIL import Image
from scipy import misc
import logging
import time
logger = logging.getLogger(__name__)
from skimage import color
import cv2
import io
import numpy as np
import time
from multiprocessing import Process, Pipe
from skimage import exposure

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

class Driver:
    def __init__(self, car, show_camera = False):
        self.show_camera = show_camera
        self.car = car
        self.sign_detection = None
        self.display_process = None
        self.parent_pipe, self.child_pipe = None, None
        

    def __histogram_equalize(img):
        img_cdf, bin_centers = exposure.cumulative_distribution(img)
        return np.interp(img, bin_centers, img_cdf)

    def detect_sign(self, datavector):
        s1 = time.time()
        
        if self.sign_detection is None:
            self.sign_detection = SignDetection()

        name = 'camera_c'
        frame = datavector[name]
        width, height, channel = frame.shape
        #frame=cv2.resize(frame,(int(width),int(height/2)),interpolation=cv2.INTER_AREA)
        frame = sign_detection.detect(frame)
        #frame=cv2.resize(frame,(int(width),int(height*2)),interpolation=cv2.INTER_AREA)
        print "{}".format(time.time()-s1)
        
        cv2.imshow(name, frame)
        cv2.waitKey(1)  # CV2 Devil - Don't dare to remove
    
    def display_camera(self, datavector):
        if self.display_process is None:
            self.parent_pipe, self.child_pipe = Pipe()
            self.display_process = Process(target=self._display, args=(self.child_pipe,))
            self.display_process.daemon = True
            self.display_process.start()
        self.parent_pipe.send(datavector)
    
    def _display(self, conn):
        while True:
            datavector = conn.recv()
            camera_names = [key for key in datavector if key.startswith('camera')]
            for name in camera_names:

                frame = datavector[name]
                
                cv2.imshow(name, frame)
                cv2.waitKey(1)  # CV2 Devil - Don't dare to remove
        
    def action_auto(self, model):
        logger.debug("Driver::action_auto()")
        while True:
            logger.debug("Collecting dataset" + str(time.time()))
            state = self.car.get_state_vector(latest=True)
            print ("Got state " + str(time.time()))

            #collisions = state['sensors']

            if self.show_camera:
                self.display_camera(state)

            actions = {}              
            for name in ['camera_c']:#, 'camera_l', 'camera_r']:
                frame = state[name]
                frame = color.rgb2gray(frame)
                frame = misc.imresize(frame, 20) # Input image is 160x120
                frame = self.__histogram_equalize(frame)
                frame = frame.astype('float32')
                #frame /= 255 # Not need because we are using histogram equalization
                frame = frame.reshape(1, 1, frame.shape[0], frame.shape[1]) # CNN
 
                action = model.predict(frame) # we get a integer
                action = np.argmax(action, axis=1)[0]
                action = ACTIONS[action]    # convert integer to function name eg forward, forwardLeft...
                actions[name] = action
            
            logger.debug("Predicted Action: " + actions)
            
            logger.debug("Taking action " + str(time.time()))
            self.car.take_action(actions['camera_c'])
            sleep(self.car.timeframe) # Wait for action to complete            
            self.car.stop()
            logger.debug("Car Stopped " + str(time.time()))            
            print ("="*80)
            

    def action_nowait(self, action):
        if action not in ACTIONS:
            raise Exception("Unknown action")

        self.car.take_action(action)        

    def action_blocking(self, action):
        if action not in ACTIONS:
            raise Exception("Unknown action")

        state0 = self.car.get_state_vector(latest=True)

        #if self.show_camera:
        #    logger.debug("State 0 Showing")
        #    self.display_camera(state0)

        logger.debug("Taking action")
        self.car.take_action(action)

        sleep(self.car.timeframe) # Wait for action to complete
                
        self.car.stop() # Stop the car
        #sleep(1)
        state1 = self.car.get_state_vector(latest=True)
        if self.show_camera:
            logger.debug("State 1 Showing")
            self.display_camera(state1)

        return state0, action, state1      

    def process_dataset_vector(self, state0, a, state1):
        datavector = {} 
        datavector_title = []

        for key in state0:
            name = 'state0_' + key
            datavector[name] = state0[key]
            datavector_title.append(name)

        datavector['action'] = ACTIONS.index(a)
        datavector_title.append('action')

        #for key in state1:
        #    name = 'state1_' + key
        #    datavector[name] = state1[key]
        #    datavector_title.append(name)

        datavector['time'] = str(datetime.now())
        datavector_title.append("time")
        return datavector, datavector_title

    def close(self):
        cv2.destroyAllWindows()
