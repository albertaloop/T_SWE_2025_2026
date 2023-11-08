""" 
    Message server (loopback)
    Will send recived message back to sender
    Closes connections if empty object recieved
"""

import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-priviledged ports are > 1023)

with socket.socket(
    socket.AF_INET, socket.SOCK_STREAM
) as s:  # With will automatically close the socket when we are done
    # Bind the created socket to the host IP and port
    s.bind((HOST, PORT))  # Host can be an IP address or a hostname

    # Enable accepting connections
    s.listen()  # Has an optional "backlog" parameter (the length of the buffer)

    # Accept an incoming connection (will block on until connection)
    conn, addr = s.accept()  # "conn" is the socket object of the client

    with conn:  # As above, with closes the connection when we exit the statement
        print(f"Connected by {addr}")  # Successful connection

        while True:
            # Recieve a MAXIMUM of 1024 bytes
            data = conn.recv(1024)  # Blocks until data is recieved
            if not data:  # If empty bytes object, signal client closed the connection
                break  # Exit the loop and close both sockets
            conn.sendall(data)  # Sends the recived data back to the client
