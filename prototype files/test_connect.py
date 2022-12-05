import socket
import sys
import tqdm
import os, fcntl
import errno
import csv
from time import sleep

def listen():
    print("im from another py file!")
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 4899
    BUFFER_SIZE = 4096
    SEPARATOR = "<SEPARATOR>"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind((SERVER_HOST, SERVER_PORT))
    fcntl.fcntl(s, fcntl.F_SETFL, os.O_NONBLOCK)

    s.listen(5)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    client_socket, address = s.accept() 
    # if below code is executed, that means the sender is connected
    print(f"[+] {address} is connected.")

    received = client_socket.recv(BUFFER_SIZE).decode()
    filename, filesize = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    filesize = int(filesize)

    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        while True:
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:    
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))

    client_socket.close()
    s.close()

listen()