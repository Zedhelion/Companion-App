import socket
from time import sleep
import threading
import subprocess


class MyClass(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def listen():
        print("I'm from another py file!")
        sock = socket.socket()
        sock.bind(("0.0.0.0",4899))
        sock.listen(3)
        print ("Waiting on connection")
        conn = sock.accept()
        print ("Client connected")

        while True:
            try:
                m = conn[0].recv(4096)
                conn[0].send(m[::-1])
            except KeyboardInterrupt:
                break

        sock.close()

myclass = MyClass()
myclass.start()
myclass.join()
