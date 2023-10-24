import socket

def network():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address