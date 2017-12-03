# Fix play_auto collision fix

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from classes.Driver import Driver
from classes.State import ACTIONS, ACTIONS_REVERSE
from classes.Dataset import Dataset
from classes.LoadCar import load_car
from classes.KBhit import KBHit

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
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import RMSprop

#from keras.models import Sequential
#from keras.layers import Dense
#from keras.optimizers import RMSprop

logger = logging.getLogger("play_rl.py")
logger.debug("ACTIONS = " + str(ACTIONS))

class CarEnv:
    def __init__(self, car):
        self.actions = ('forward', 'forwardRight', 'forwardLeft') #, 'backward')
        self.car = car
        self.cameras_size = 3 * 32 * 24
        self.sensors_size = 3
        self.state_size = self.cameras_size + self.sensors_size # 3 cameras + 3 sensors
        self.taken_actions = LifoQueue()
        
        self.reward_sensor  = -10
        self.reward_step    = 1
        self.reward_goal    = 100

    def reset(self):
        print self.taken_actions.empty()
        while not self.taken_actions.empty():
            action = ACTIONS.index(ACTIONS_REVERSE[ACTIONS[self.taken_actions.get()]]) # Get index of reverse action
            print action
            self.take_step(action)
        logger.debug("Env reset done")

    def _process_image(self, image_bytes):
        frame = io.BytesIO(image_bytes)
        frame = Image.open(frame).convert(mode='L')
        frame = np.asarray(frame)
        frame = misc.imresize(frame, 10)
        frame = frame.astype('float32')
        frame /= 255
        return frame

    def get_state(self, latest=True):
        state = self.car.get_state_vector(latest)

        sensors = state['sensors']
        sensors_list = np.array([float(sensors[sensor]) for sensor in sensors])

        cl = self._process_image(state['camera_l'])
        cc = self._process_image(state['camera_c'])
        cr = self._process_image(state['camera_r'])
        
        cameras = np.array([cl, cc, cr])
        cameras = cameras.reshape(-1)

        state = np.append(cameras, sensors_list)

        
        return state, sensors

    def take_step(self, action):
        self.car.take_action(ACTIONS[action])
        sleep(self.car.timeframe)
        self.car.stop()

    def step(self, action):
        self.take_step(action)
        self.taken_actions.put(action)

        state, sensors = self.get_state()

        reward = self.reward_step
        print sensors
        for sensor in sensors:
            if sensors[sensor]:
                reward += self.reward_sensor

        done = None # To be implement using OpenCV

        info = None

        return state, reward, done, info

EPISODES = 5000

class DQNAgent:
    def __init__(self, state_size, action_size, batch_size):
        self.batch_size = batch_size
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=100000)
        self.gamma = 0.9    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.e_decay = .99
        self.e_min = 0.05
        self.learning_rate = 0.01
        self.model = self._build_model()

    def _build_model(self):
        #model = MLPClassifier(hidden_layer_sizes=(16), verbose=True, batch_size=self.batch_size, max_iter=1)
        model = Sequential()
        model.add(Dense(16, activation='relu', input_shape=(self.state_size,)))
        model.add(Dropout(0.2))
        model.add(Dense(self.action_size, activation='linear'))
        model.summary()
        model.compile(loss='mse', optimizer=RMSprop(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):

        if np.random.rand() <= self.epsilon:
            logger.debug("Taking random")
            return random.randrange(self.action_size)
        logger.debug("Predicting...")    
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self):
        logger.debug("replay()")
        batch_size = min(self.batch_size, len(self.memory))
        minibatch = random.sample(self.memory, batch_size)
        X = np.zeros((batch_size, self.state_size))
        Y = np.zeros((batch_size, self.action_size))
        for i in range(batch_size):
            state, action, reward, next_state, done = minibatch[i]
            target = self.model.predict(state)[0]
            if done:
                target[action] = reward
            else:
                target[action] = reward + self.gamma * np.amax(self.model.predict(next_state)[0])
            X[i], Y[i] = state, target
        logger.debug("Fitting Data")
        self.model.fit(X, Y, batch_size=batch_size, epochs=1, verbose=1)

        if self.epsilon > self.e_min:
            self.epsilon *= self.e_decay

    def load(self, name):
        self.model.load_weights(name)
        #input_file = open(name, 'rb')
        #self.model = pickle.load(input_file)
        #input_file.close()

    def save(self, name):
        self.model.save_weights(name)
        #output_file = open(name, 'wb')
        #pickle.dump(self.model, output_file)
        #output_file.close()

if __name__ == "__main__":
    logger.debug("Loading car")
    car, rps_ms, port = load_car("../config.json")
    env = CarEnv(car)
    logger.debug("CarEnv setup done")

    action_size = len(env.actions) 

    state_size = env.state_size
    action_size = len(env.actions)
    
    agent = DQNAgent(state_size, action_size, 32)
    logger.debug("DQNAgent setup done")

    # agent.load("../save/rl-model.dat")

    for e in range(EPISODES):
        #env.reset()
        state, sensors = env.get_state()

        state = np.reshape(state, [1, -1])

        for time in range(10):

            action = agent.act(state)

            next_state, reward, done, _ = env.step(action)
            print reward 

            #reward = reward if not done else -10
            
            next_state = np.reshape(next_state, [1, -1])
            
            agent.remember(state, action, reward, next_state, done)

            state = next_state

            if done or time == 9:
                print("episode: {}/{}, score: {}, e: {:.2}"
                        .format(e, EPISODES, time, agent.epsilon))
                break
        env.reset()
        agent.replay()
        # if e % 10 == 0:
            # agent.save("../save/rl-model.dat")
