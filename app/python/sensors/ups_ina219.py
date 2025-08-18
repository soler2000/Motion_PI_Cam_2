--- a/app/python/sensors/ups_ina219.py
+++ b/app/python/sensors/ups_ina219.py
@@ -1,10 +1,53 @@
-import board, busio
-from adafruit_ina219 import INA219
+import time
+import board, busio
+from adafruit_ina219 import INA219
 
 class UpsMonitor:
-    def __init__(self, addr=0x43):
-        self.i2c = busio.I2C(getattr(board.SCL), getattr(board.SDA))
-        self.ina = INA219(self.i2c, address=addr)
+    def __init__(self, addr=0x43, shunt_ohms=0.1, retries=3):
+        """
+        INA219 power monitor (Waveshare UPS HAT (C) @ 0x43).
+        Uses default Raspberry Pi I²C bus via board.SCL/board.SDA.
+        Retries and fails soft if sensor not present.
+        """
+        self.v = self.i = self.p = 0.0
+        self.percent = 0
+        self.ina = None
+
+        # Use the default I²C on Pi (i2c-1). No getattr!
+        self.i2c = busio.I2C(board.SCL, board.SDA)
+
+        # Let the bus come up cleanly
+        t0 = time.time()
+        while True:
+            try:
+                if self.i2c.try_lock():
+                    self.i2c.unlock()
+                    break
+            except Exception:
+                pass
+            if time.time() - t0 > 2.0:
+                break
+            time.sleep(0.02)
+
+        # Attempt init a few times
+        for _ in range(max(1, retries)):
+            try:
+                self.ina = INA219(self.i2c, address=addr, shunt_ohms=shunt_ohms)
+                break
+            except Exception:
+                time.sleep(0.2)
 
     def snapshot(self):
-        return {
-            "voltage": float(self.ina.bus_voltage),
-            "current": float(self.ina.current)/1000.0,
-            "power": float(self.ina.power)/1000.0
-        }
+        """
+        Return a dict with voltage (V), current (A), power (W), percent (%).
+        Safe to call when sensor missing; returns zeros.
+        """
+        if not self.ina:
+            return {"voltage": 0.0, "current": 0.0, "power": 0.0, "percent": 0}
+        try:
+            v = float(getattr(self.ina, "bus_voltage", 0.0))
+            i = float(getattr(self.ina, "current", 0.0) / 1000.0)  # mA -> A
+            p = float(getattr(self.ina, "power", 0.0) / 1000.0)    # mW -> W
+            # crude % from voltage (you can refine later)
+            pct = int(max(0, min(100, round((v - 3.2) / (4.2 - 3.2) * 100))))
+            self.v, self.i, self.p, self.percent = v, i, p, pct
+            return {"voltage": v, "current": i, "power": p, "percent": pct}
+        except Exception:
+            return {"voltage": 0.0, "current": 0.0, "power": 0.0, "percent": 0}