import socket
from time import sleep
import threading

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

print("asdasd")
sock.close()