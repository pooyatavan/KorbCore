import os, threading, sys, socket, datetime, time, random
from re import findall
from subprocess import Popen, PIPE
from string import ascii_uppercase

from modules.ConfigReader import Config

rooms = {}

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

def GetDate():
    return datetime.datetime.now().date()

def TimeDo(start):
    return round(time.perf_counter()-start, 2)

def RandomeCode(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code

def Check(ForCheck):
    if bool(Config.read()['core'][ForCheck]) == " True":
        return True
    else:
        return False