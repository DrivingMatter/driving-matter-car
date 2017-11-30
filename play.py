from classes.Driver import Driver
from classes.State import ACTIONS
from Dataset import Dataset
from classes.LoadCar import load_car

print "ACTIONS = " + str(ACTIONS)

car = load_car("config.json")
driver = Driver(car, show_camera = True)
dataset = Dataset()
while True:
	action = raw_input("Write your action: ")
	try:
		state0, action, state1 = driver.action_blocking(action)
		datavector, datavector_title = driver.process_data(state0, action, state1)
		dataset.save_data(datavector, datavector_title)
	except:
		logging.debug("Try again, invalid action.")
		pass

    