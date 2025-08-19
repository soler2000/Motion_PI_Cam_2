import time
from ina219 import INA219
class UpsMonitor:
    def __init__(self, addr=0x43, shunt_ohms=0.1, retries=3, busnum=1):
        self.ina=None
        for _ in range(max(1,retries)):
            try:
                self.ina=INA219(shunt_ohms=shunt_ohms, address=addr, busnum=busnum)
                self.ina.configure(); break
            except Exception: time.sleep(0.2)
    def snapshot(self):
        if not self.ina: return {"voltage":0.0,"current":0.0,"power":0.0,"percent":0}
        try:
            v=float(self.ina.voltage())
            i=float(self.ina.current())/1000.0  # mA->A
            p=float(self.ina.power())/1000.0    # mW->W
            pct=int(max(0,min(100, round((v-3.2)/(4.2-3.2)*100))))
            return {"voltage":v,"current":i,"power":p,"percent":pct}
        except Exception:
            return {"voltage":0.0,"current":0.0,"power":0.0,"percent":0}
