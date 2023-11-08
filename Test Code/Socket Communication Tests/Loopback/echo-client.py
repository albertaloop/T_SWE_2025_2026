""" 
    Message client (loopback)
    Sends messages to the loopback address
"""

import socket

HOST = "127.0.0.1"
PORT = 65432

# Create socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Connect socket to the server
    s.connect((HOST, PORT))

    # Send message to server
    s.sendall(b"Hello World")

    # Recieve data from server
    data = s.recv(1024)

# Socket will be closed automatically
print(f"Recieved {data!r}")
