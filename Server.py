import tornado.web
import tornado.websocket
import logging

class Server():
    def __init__(self, handler):
        self.handler = handler
        # Currently starting from crontab -e
        # self.rc = RegisterCar()
        # self.rc.register_car("Mater")
        pass

    def start(self):
        global handlers
        
        application = tornado.web.Application(self.handlers)
        application.listen(8000)

        try:
            logging.debug("Starting Server Loop")
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            logging.debug("Exiting server loop")
            print "Exiting";

    # Destructor
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        #self.rc.unregister_car()
        pass