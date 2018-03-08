import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from classes.Driver import Driver
from classes.State import ACTIONS
from classes.Dataset import Dataset
from classes.LoadCar import load_car
from classes.KBhit import KBHit
from classes.SignDetection import SignDetection
import logging
from time import sleep, time
logger = logging.getLogger("play_fun.py")
from scipy import misc
import cv2

logger.debug("ACTIONS = " + str(ACTIONS))

car, rps_ms, port = load_car("../config.json")
driver = Driver(car, show_camera = False)
sign_detection= SignDetection()


counter = 0 
while True:
    start_dataset = time()
    state = car.get_state_vector(latest=True, for_network=None)
    elapsed_dataset = time() - start_dataset
    
    #frame = misc.imresize(state['camera_c'], 10)
    
    start_detect = time()
    frame,detected = sign_detection.detect(state['camera_c'])
    print detected
    elapsed_detect = time() - start_detect
    
    
    cv2.imshow("camera_c", frame)
    cv2.waitKey(1)  # CV2 Devil - Don't dare to remove
        
    #print "%4d)\tTime to get dataset: %-6d" % (counter, elapsed*1000)
    #print "%4d)\tTime to get dataset: %-6d %-10s %-10s %-10s" % (counter, (time()-start)*1000, state['camera_c'][1], state['camera_l'][1], state['camera_r'][1])
    counter += 1

    wait_time = 0.2
    elapsed = elapsed_detect + start_dataset
    wait_time = wait_time if elapsed > wait_time else (wait_time - elapsed) + elapsed 
    
    print "Detection time: %03.3f  Dataset time: %03.3f  Wait time: %03.3f" % (elapsed_detect, elapsed_dataset, wait_time)
    sleep(wait_time)
