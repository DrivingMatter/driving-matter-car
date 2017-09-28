def getch():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        fd = sys.stdin.fileno()
        import termios
        
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result

frontRight = Tyre(24, 25, 19, 1)
frontLeft = Tyre(11, 9, 13, 1)
backLeft = Tyre(15, 14, 12, 1)
backRight = Tyre(23, 17, 18, 1)

#t.forward()

#sleep(3)
#t.speed(50)
#sleep(3)
#t.speed(100)
#sleep(3)


#t.speed(50)
#t.forward()
#sleep(3)
#t.stop()

#frontRight.forward()
#frontLeft.forward()
#sleep(3)

"""
frontRight.speed(100)
frontRight.forward()
sleep(1)
frontRight.speed(75)
frontRight.forward()
sleep(1)
"""
"""
frontLeft.test()
frontRight.test()
backLeft.test()
backRight.test()
"""

car = Car4W(frontRight, frontLeft, backRight, backLeft)
car.stop()
#car.test()
try:
    sensor_left = DistanceSensor(echo=6, trigger=5, max_distance=1, threshold_distance=0.3)
    sensor_center = DistanceSensor(echo=21, trigger=20, max_distance=1, threshold_distance=0.3)
    sensor_right = DistanceSensor(echo=16, trigger=26, max_distance=1, threshold_distance=0.3)

    def print_pressed_keys(e):
        print ("Here")
	line = ', '.join(str(code) for code in keyboard._pressed_events)
        v = str(line.strip())
        print (v == "w")
        if v == "w":
            print ("Forward")
            car.forward()
        if v == 'a':
            print ("ForwardLeft")
            car.forwardLeft()
        if v == 'd':
            print ("ForwardRight")
            car.forwardRight()
        if v == 's':
            print ("Backward")
            car.backward()
        if v == 'l':
            print ("Stop")
            car.stop()

	print(v)
	
    keyboard.hook(print_pressed_keys)
    keyboard.wait('esc')
    while True:
        sleep(0.1)
        left_distance = sensor_left.distance
        center_distance = sensor_center.distance
        right_distance = sensor_right.distance

        #print ("Distance running")
        if 0.0 in [left_distance, center_distance, right_distance]: #Special keys (arrows, f keys, ins, del, etc.)
            car.stop()
    keyboard.wait('esc')
finally:
    car.stop()
    GPIO.cleanup() # this ensures a clean exit

#GPIO.cleanup() # this ensures a clean exit

