import socket
from time import sleep
import threading

def process():
    sock = socket.socket()
    sock.bind(("0.0.0.0",4899))
    sock.listen(3)
    print ("Waiting on connection")
    conn = sock.accept()
    print ("Client connected")

    while True:
        m = conn[0].recv(4096)
        conn[0].send(m[::-1])

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

thread = threading.Thread(target=process)
thread.daemon = True
thread.start()
while True:
    exit_signal = input('Type "exit" anytime to stop server\n')
    if exit_signal == 'exit':
        break