""" 
    Message client (loopback)
    Sends messages to the loopback address
"""

import socket

HOST = "192.168.1.8"    # IP to connect to
PORT = 65432            # Port to connect to

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
