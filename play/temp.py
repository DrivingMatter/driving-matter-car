from time import sleep
from threading import Thread


def t():
  while True:
    print ("Running")
    sleep(3000)

th = Thread(target=t)
th.name = "Python t1"
th.daemon = True
th.start()
sleep(1000000)
