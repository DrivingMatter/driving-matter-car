from SignDetection import SignDetection
from State import ACTIONS, COLLISIONS
from datetime import datetime
from time import sleep
from PIL import Image
from scipy import misc
import logging
import time
logger = logging.getLogger(__name__)

import cv2
import io
import numpy as np

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])

class Driver:
    def __init__(self, car, show_camera = False):
        self.show_camera = show_camera
        self.car = car
        self.cv2_window_name = []
        
    def detect_sign(self, datavector):
        
        sign_detection= SignDetection()
        camera_names = [key for key in datavector if key.startswith('camera')]
        for name in camera_names:

            if name not in self.cv2_window_name:
                self.cv2_window_name.append(name)

            frame = datavector[name]
            width, height, channel = frame.shape
            frame=cv2.resize(frame,(int(width),int(height/2)),interpolation=cv2.INTER_AREA)
            frame = sign_detection.detect(frame)
            #frame=cv2.resize(frame,(int(width),int(height*2)),interpolation=cv2.INTER_AREA)
            print(time.time())
            
            cv2.imshow(name, frame)
            cv2.waitKey(1)  # CV2 Devil - Don't dare to remove
            
    def display_camera(self, datavector):
        camera_names = [key for key in datavector if key.startswith('camera')]
        for name in camera_names:

            if name not in self.cv2_window_name:
                self.cv2_window_name.append(name)

            frame = datavector[name]
            cv2.imshow(name, frame)
            cv2.waitKey(1)  # CV2 Devil - Don't dare to remove
        
    def action_auto(self, model):
        logger.debug("Driver::action_auto()")
        while True:
            state = self.car.get_state_vector(latest=True)
            logger.debug("Collected state")

            collisions = state['sensors']


            frame = np.hstack([state['camera_l'], state['camera_c'], state['camera_r']])
            print (frame.shape)

            frame = misc.imresize(frame, (32, 96))
            frame = rgb2gray(frame)
            frame = frame.astype('float32')
            frame /= 255

            print (frame.shape)
            frame = frame.reshape(1, 1, frame.shape[0], frame.shape[1])
            print (frame.shape)
            
            action = model.predict(frame) # we get a integer
            action = np.argmax(action, axis=1)[0]
            action = ACTIONS[action]    # convert integer to function name eg forward, forwardLeft...
            
            logger.debug("Predicted Action: " + action)

            #logger.debug("Collisions: " + collisions)        
            can_take_action = True    
            
            for name in collisions:
                if collisions[name] == True and COLLISIONS[action] == name:
                    can_take_action = False
                    logger.debug("Collision detected")
                    break

            logger.debug("can_take_action: " + str(can_take_action))        

            if can_take_action:
                self.car.take_action(action)
                sleep(self.car.timeframe) # Wait for action to complete
                    
            self.car.stop()

    def action_nowait(self, action):
        if action not in ACTIONS:
            raise Exception("Unknown action")

        self.car.take_action(action)        

    def action_blocking(self, action):
        if action not in ACTIONS:
            raise Exception("Unknown action")

        state0 = self.car.get_state_vector(latest=True)

        if self.show_camera:
            logger.debug("State 0 Showing")
            self.display_camera(state0)

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

        for key in state1:
            name = 'state1_' + key
            datavector[name] = state1[key]
            datavector_title.append(name)

        datavector['time'] = str(datetime.now())
        datavector_title.append("time")
        return datavector, datavector_title

    def close(self):
        for window_name in self.cv2_window_name:
            cv2.destroyWindow(window_name)