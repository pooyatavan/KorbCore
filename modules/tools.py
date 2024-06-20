import os, threading, sys, socket
from re import findall
from subprocess import Popen, PIPE

def key():
    return str(os.urandom(12).hex)

def thread(func, daemon=True):
    thread = threading.Thread(target=func)
    thread.daemon = daemon
    thread.start()
    return thread

def restart():
    python = sys.executable
    os.execl(python, python, * sys.argv)

def network():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def IpFormatCheck(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def ping (host,ping_count):
    for ip in host:
        data = ""
        output= Popen(f"ping {ip} -n {ping_count}", stdout=PIPE, encoding="utf-8")
        for line in output.stdout:
            data = data + line
            ping_test = findall("TTL", data)
        if ping_test:
            return True
        else:
            return False