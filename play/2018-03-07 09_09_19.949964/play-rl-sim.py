# Fix play_auto collision fix

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import cv2

#from classes.Driver import Driver
from classes.State import ACTIONS, ACTIONS_REVERSE
#from classes.Dataset import Dataset
#from classes.LoadCar import load_car
#from classes.KBhit import KBHit
from classes.SignDetection import SignDetection

from scipy import misc
from PIL import Image
import logging
from time import sleep
import random
import numpy as np
from collections import deque
from Queue import LifoQueue
import pickle
import io
import keras
from keras.layers import Dense, Dropout, Flatten, Activation
from keras.layers import Conv2D, MaxPooling2D
from keras.models import Sequential
from keras.layers import ZeroPadding2D, GlobalAveragePooling2D, BatchNormalization,GlobalMaxPooling2D
from keras.optimizers import RMSprop
from skimage import color
import h5py
#from keras.models import Sequential
#from keras.layers import Dense
#from keras.optimizers import RMSprop

from tempfile import TemporaryFile
outfile = TemporaryFile()


import pandas as pd
import numpy as np
np.random.seed(2)
from scipy import misc
import sys
import os
import cv2
from sklearn.metrics import confusion_matrix

import keras
from keras.models import Sequential
from keras.optimizers import RMSprop
from keras.layers import Dense, Dropout, Flatten, Activation
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
##K.set_image_dim_ordering('th')

from keras.utils import to_categorical

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.neural_network import MLPClassifier

import matplotlib
import matplotlib.pyplot as plt

from skimage import exposure
import numpy as np

import random
resized_img = 10
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("play-rl-sim.py")
logger.debug("ACTIONS = " + str(ACTIONS))
sign_detection= SignDetection()
class CarEnv:
    def __init__(self, car):
        self.actions = ('forward', 'stop' )#, 'forwardLeft') #, 'backward')
        self.car = car
        self.cameras_size = 3 * 32 * 24
        self.sensors_size = 3
        self.state_size = self.cameras_size + self.sensors_size # 3 cameras + 3 sensors
        self.taken_actions = LifoQueue()
        
        self.reward_sensor  = -10
        self.reward_step    = 0.3
        self.reward_goal    = 100

        df = pd.read_csv("dataset.csv", usecols=[1, 2])
        df = np.array(df)

        self.X = []
        self.y = []

        for data in df:
            target = data[1]
            images = self.read_img(data[0])

            self.X.append(images)
            self.y.append(target)

        self.dataset_count = len(self.X)

        self.dataset_index = 0

    def read_img(self, url):
        image   = cv2.imread(url)
        return image

    def reset(self):
        print self.taken_actions.empty()
        while not self.taken_actions.empty():
            action = ACTIONS.index(ACTIONS_REVERSE[ACTIONS[self.taken_actions.get()]]) # Get index of reverse action
            print action
            self.take_step(action)
        logger.debug("Env reset done")

    def _process_image(self, frame):
        #frame = io.BytesIO(image_bytes)
        #frame = Image.open(frame).convert(mode='L')
        #frame = np.asarray(frame)
        frame = color.rgb2gray(frame)
        frame = misc.imresize(frame, 10) # TODO: convert to grayscale
        frame = frame.astype('float32')
        frame /= 255
        
        return frame

    def get_dataset_index(self, move = 0):
        if self.dataset_index >= self.dataset_count-1:
            self.dataset_index = 0;
        old_index = self.dataset_index
        self.dataset_index += move
        return old_index

    def get_state(self, latest=True):
        i = self.get_dataset_index()

        image = self.X[i]

        image1,detected =sign_detection.detect(image)
        cv2.imshow("camera_c", image1)
        cv2.waitKey(1)

        print detected

        detected_list = np.array([float(detected[item]) for item in detected])

        print detected_list

        camera_c_frame = np.array(self._process_image(image))
        camera_c_frame = camera_c_frame.reshape(1, camera_c_frame.shape[0], camera_c_frame.shape[1])
        state = camera_c_frame
        
        return state,detected
 
    def take_step(self, action):
        self.car.take_action(ACTIONS[action])
        sleep(self.car.timeframe)
        self.car.stop()

    def step(self, action):
        # self.take_step(action)
        self.taken_actions.put(action)

        if action == 1:
            self.get_dataset_index(0) # next frame
        else:
            self.get_dataset_index(1) # next frame

        state, detected = self.get_state()
        reward = 0
        
##        print sensors
##        for sensor in sensors:
##            if sensors[sensor]:
##                reward += self.reward_sensor
        stop = [key for key in detected if key.startswith('Stop')]
        #print detected[key]
        #print stop
        if detected[stop[0]]:
            if action==0:
                reward -=2
            else:
                reward += 0.01
        elif action==0:
            reward += 0.5
##        elif action == 1:
##            reward -= 0.1
        done = None # To be implement using OpenCV

        info = None

        return state, reward, done, info

EPISODES = 40

class DQNAgent:
    def __init__(self, state_size, action_size, batch_size):
        self.batch_size = batch_size
        self.state_size = (1,24,32)
        self.action_size = action_size
        self.memory = deque(maxlen=100000)
        self.gamma = 0.9    # discount rate
        self.epsilon = 0.8  # exploration rate
        self.e_decay = .99
        self.e_min = 0.05
        self.learning_rate = 0.01
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()

        model.add(Conv2D(32, (3, 3), input_shape=self.state_size, activation='relu',data_format='channels_first'))
        model.add(BatchNormalization())
        #model.add(Dropout(0.25))
        model.add(ZeroPadding2D())

        model.add(Conv2D(32, (3, 3), activation='relu'))
        model.add(Dropout(0.1))
        model.add(ZeroPadding2D())

        model.add(MaxPooling2D())

        model.add(Conv2D(16, (3, 3), activation='relu'))
        #model.add(Dropout(0.25))
        model.add(ZeroPadding2D())

        model.add(MaxPooling2D())

        model.add(Conv2D(16, (3, 3), activation='relu'))
        #model.add(Dropout(0.25))
        model.add(ZeroPadding2D())
        model.add(MaxPooling2D())

        model.add(Flatten())
        #model.add(GlobalAveragePooling2D())
        #model.add(GlobalMaxPooling2D())

        model.add(Dense(16, activation='relu'))
        #model.add(Dropout(0.25))

        model.add(Dense(2, activation='softmax'))

        model.compile(loss='mse',
                          optimizer='adadelta', #SGD(lr=0.05, momentum=0.9, nesterov=True),
                          metrics=['accuracy']) 
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
        
        np.savez(outfile, state, action, reward, next_state, done)
        outfile.seek(0) # Only needed here to simulate closing & reopening file
        npzfile = np.load(outfile)
        npzfile.files
##
##        print (npzfile['arr_0'])

    def act(self, state):

        if np.random.rand() <= self.epsilon:
            logger.debug("Taking random")
            return random.randrange(self.action_size)
        logger.debug("Predicting...")
        state = state.reshape(1, 1, state.shape[1], state.shape[2])
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self):
        logger.debug("replay()")
        batch_size = min(self.batch_size, len(self.memory))
        minibatch = random.sample(self.memory, batch_size)
        X = []
        Y = np.zeros((batch_size, self.action_size))
        for i in range(batch_size):
            state, action, reward, next_state, done = minibatch[i]
            re_state = state.reshape(1, 1, state.shape[1], state.shape[2])
            re_next_state = next_state.reshape(1, 1, next_state.shape[1], next_state.shape[2])
            target = self.model.predict(re_state)[0]
            if done:
                target[action] = reward
            else:
                target[action] = reward + self.gamma * np.amax(self.model.predict(re_next_state)[0])
            X.append(state)
            Y[i] = target
        logger.debug("Fitting Data")
        X = np.array(X)
        print X.shape
        #X = X.reshape(X.shape[0], 1, X.shape[1], X.shape[2])
        self.model.fit(X, Y, batch_size=8, epochs=2, verbose=1)
        if self.epsilon > self.e_min:
            self.epsilon *= self.e_decay

    def load(self, name):
        self.model.load_weights(name)
##        input_file = open(name, 'rb')
##        self.model = pickle.load(input_file)
##        input_file.close()

    def save(self, name):
        self.model.save_weights(name)
##        output_file = open(name, 'wb')
##        pickle.dump(self.model, output_file)
##        output_file.close()

if __name__ == "__main__":
    logger.debug("Loading car")
    #car, rps_ms, port = load_car("../config.json")
    env = CarEnv(None)
    logger.debug("CarEnv setup done")

    action_size = len(env.actions) 

    state_size = env.state_size
    action_size = len(env.actions)
    state, _ = env.get_state()
    
    agent = DQNAgent(len(state), action_size, 16)
    logger.debug("DQNAgent setup done")

    #agent.load("../save/rl-model.dat")

    for e in range(EPISODES):
        #env.reset()
        state, _ = env.get_state()

        for time in range(10):

            action = agent.act(state)

            next_state, reward, done, _ = env.step(action)
            print reward 

            #reward = reward if not done else -10
            
            #next_state = np.reshape(next_state, [1, -1])
            
            agent.remember(state, action, reward, next_state, done)

            state = next_state

            if done or time == 9:
                print("episode: {}/{}, score: {}, e: {:.2}"
                        .format(e, EPISODES, time, agent.epsilon))
                break
        #env.reset()
        agent.replay()
        if e % 2 == 0:
            agent.save("../../save/rl-model.dat")
        
            