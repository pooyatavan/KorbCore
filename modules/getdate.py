import datetime, time

def GetDate():
    return datetime.datetime.now().date()

def TimeDo(start):
    return round(time.perf_counter()-start, 2)