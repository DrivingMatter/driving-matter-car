from State import ACTIONS

class Driver:
	def __init__(self, car):
		self.car = car

	def action(self, action)
		if action not in ACTIONS:
			raise Exception("Unknown action")

		state0 = self.car.get_state_vector()
			
		self.car.take_action(action)
		sleep(self.car.timeframe)
		self.car.stop() # Stop the car
		
		state1 = self.car.get_state_vector()
		
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

		return datavector, datavector_title

