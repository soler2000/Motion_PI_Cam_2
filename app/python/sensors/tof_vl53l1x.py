import board, busio, adafruit_vl53l1x, os
class ToFSensor:
    def __init__(self, addr=0x29, busnum=1):
        self.i2c = busio.I2C(getattr(board.SCL), getattr(board.SDA))
        self.vl = adafruit_vl53l1x.VL53L1X(self.i2c, address=addr)
        self.vl.distance_mode = 2  # long
        self.vl.timing_budget = 50
        self.vl.start_ranging()
    def distance_m(self):
        d_mm = self.vl.distance
        return (d_mm/1000.0) if d_mm is not None else None
