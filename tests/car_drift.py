from classes.LoadCar import load_car

car, rps_ms, port = load_car("config.json")

def test():
        from time import sleep

        self.forward()
        sleep(0.5)
        self.stop()

        sleep(1)

        self.backward()
        sleep(0.5)
        self.stop()

        sleep(1)

        self.forwardRight()
        sleep(0.5)
        self.stop()

        sleep(1)

        self.forwardLeft()
        sleep(0.5)
        self.stop()

        sleep(1)

        self.backwardLeft()
        sleep(1)
        self.stop()

        sleep(1)

        self.backwardRight()
        sleep(1)
        self.stop()
