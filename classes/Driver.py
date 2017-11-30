from State import ACTIONS
from datetime import datetime
from time import sleep
from PIL import Image

import cv2
import io
import numpy as np

class Driver:
	def __init__(self, car, show_camera = False):
		self.show_camera = show_camera
		self.car = car
                self.cv2_window_name = []

	def display_camera(self, datavector):
		camera_names = [key for key in datavector if key.startswith('camera')]
		for name in camera_names:
                        if name not in self.cv2_window_name:
                            self.cv2_window_name.append(name)

                        frame = datavector[name]
			img = Image.open(io.BytesIO(frame))
			cv2.imshow(name, np.asarray(img))
			cv2.waitKey(1)  # CV2 Devil - Don't dare to remove

	def action_nowait(self, action):
		if action not in ACTIONS:
			raise Exception("Unknown action")

		self.car.take_action(action)		

	def action_blocking(self, action):
		if action not in ACTIONS:
			raise Exception("Unknown action")

		state0 = self.car.get_state_vector(latest=True)

		if self.show_camera:
                    print "State 0 Showing"
                    self.display_camera(state0)
                print "Taking action"
		self.car.take_action(action)

		sleep(self.car.timeframe) # Wait for action to complete
                
		self.car.stop() # Stop the car
                
                state1 = self.car.get_state_vector(latest=True)
		if self.show_camera:
                    print "State 1 Showing"
                    self.display_camera(state1)

		return state0, action, state1 		

	def process_dataset_vector(self, state0, a, state1):
		datavector = {}	
		datavector_title = []

		for key in state0:
			name = 'state0_' + key
			datavector[name] = state0[key]
			datavector_title.append(name)

		datavector['action'] = a
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