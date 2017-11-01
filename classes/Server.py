import tornado.web
import tornado.websocket
import logging


class Server():
    def __init__(self, handlers, port=8000):
        self.handlers = handlers
        self.port = port
        # Currently starting from crontab -e
        # self.rc = RegisterCar()
        # self.rc.register_car("Mater")
        pass

    def start(self):
        application = tornado.web.Application(self.handlers)
        application.listen(self.port)

        try:
            logging.debug("Starting Server Loop")
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            logging.debug("Exiting server loop")
            print "Exiting"
