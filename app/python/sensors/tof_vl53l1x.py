import time, board, busio, adafruit_vl53l1x
class ToFSensor:
    def __init__(self, addr=0x29, retries=3):
        self.vl=None
        self.i2c=busio.I2C(board.SCL, board.SDA)
        t0=time.time()
        while time.time()-t0<2:
            try:
                if self.i2c.try_lock():
                    self.i2c.unlock(); break
            except Exception: pass
            time.sleep(0.02)
        for _ in range(max(1,retries)):
            try:
                self.vl=adafruit_vl53l1x.VL53L1X(self.i2c, address=addr)
                self.vl.distance_mode=2; self.vl.timing_budget=50; self.vl.start_ranging()
                break
            except Exception: time.sleep(0.2)
    def distance_m(self):
        if not self.vl: return None
        try:
            d=self.vl.distance
            return (d/1000.0) if d is not None else None
        except Exception: return None
