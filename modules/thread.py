import threading

def thread(func, daemon=True):
    thread = threading.Thread(target=func)
    thread.daemon = daemon
    thread.start()
    return thread