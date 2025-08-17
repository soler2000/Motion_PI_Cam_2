import board, busio, adafruit_ina219, time, math
class UpsMonitor:
    def __init__(self, addr=0x43, busnum=1):
        self.i2c = busio.I2C(getattr(board, f"SCL{busnum-1}"), getattr(board, f"SDA{busnum-1}"))
        self.ina = adafruit_ina219.INA219(self.i2c, addr)
        self._soc = 75.0
        self._last = time.time()
    def snapshot(self):
        v = self.ina.bus_voltage
        i = self.ina.current/1000.0  # A
        p = v*i
        # crude % estimate based on voltage (tunable)
        pct = max(0,min(100, (v-3.2)/(4.2-3.2)*100))
        return {"voltage":v, "current":i, "power":p, "percent":pct}
