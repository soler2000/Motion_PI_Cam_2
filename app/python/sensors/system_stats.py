import psutil
def cpu_temp():
    ts = psutil.sensors_temperatures()
    for k,v in ts.items():
        if v: return v[0].current
    return 0.0
def cpu_load():
    return psutil.cpu_percent()
