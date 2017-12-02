from classes.Driver import Driver
from classes.State import ACTIONS
from classes.LoadCar import load_car

car, rps_ms, port = load_car("../config.json")
driver = Driver(car, show_camera = True)

class CarEnvironment:
    def __init__(self, car):
        self.car = car
    
    def get_input_shape(self):
        