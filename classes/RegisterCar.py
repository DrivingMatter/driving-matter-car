import logging
import socket
import sys
from time import sleep
from zeroconf import ServiceInfo, Zeroconf

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class RegisterCar():
    def __init__(self):
        logging.info("RegisterCar.__init__()")
        self.zeroconf = None
        self.info = None

    def register_car(self, name, port=8000):
        logging.info("RegisterCar.register_car()")

        my_ip_address = None
        while not my_ip_address:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                my_ip_address = s.getsockname()[0]
                s.close()
            except Exception:
                sleep(1)
                my_ip_address = None

        if len(my_ip_address) > 0:
            logging.info("Service IP: " + my_ip_address)
            my_ip_address = socket.inet_aton(my_ip_address)

            desc = {'name': name}
            self.info = ServiceInfo("_http._tcp.local.",
                                    name + " DrivingMatter._http._tcp.local.",
                                    my_ip_address, port, 0, 0, desc)

            self.zeroconf = Zeroconf()
            logging.info("Registration of a service, press Ctrl-C to exit...")
            self.zeroconf.register_service(self.info)

            return True
        else:
            logging.error(
                "No network interface available, please connect to any network")
            #raise Exception("No network interface")
            return False

    def unregister_car(self):
        if self.zeroconf:
            self.zeroconf.unregister_service(self.info)
            self.zeroconf.close()
            logging.info("Service unregistered successfully")
        else:
            logging.error("No Zeroconf established yet")


logging.info("Current enviorment: " + __name__)
if __name__ == "__main__":
        # When this script is executed directly. This is executed when bootup is called
    rc = RegisterCar()
    try:
        rc.register_car("Mater")
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        rc.unregister_car()
