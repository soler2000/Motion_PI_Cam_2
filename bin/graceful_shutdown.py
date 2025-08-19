#!/usr/bin/env python3
import time, subprocess
from sensors.ups_ina219 import UpsMonitor

ups = UpsMonitor(addr=0x43, busnum=1)
THRESH = 3.3  # volts; override via DB in main app normally
LOW_COUNT = 0
while True:
    snap = ups.snapshot()
    if snap["voltage"] <= THRESH:
        LOW_COUNT += 1
    else:
        LOW_COUNT = 0
    if LOW_COUNT >= 5:  # ~10s debounce
        #!/Removed shutdown call while sensors configured  subprocess.call(["systemctl","poweroff"])
        break
    time.sleep(2)
