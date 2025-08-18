--- a/app/python/sensors/tof_vl53l1x.py
+++ b/app/python/sensors/tof_vl53l1x.py
@@ -1,8 +1,48 @@
-import board, busio, adafruit_vl53l1x, os
+import time
+import board, busio, adafruit_vl53l1x
+
 class ToFSensor:
-    def __init__(self, addr=0x29, busnum=1):
-        self.i2c = busio.I2C(getattr(board, f"SCL{busnum-1}"), getattr(board, f"SDA{busnum-1}"))
-        self.vl = adafruit_vl53l1x.VL53L1X(self.i2c, address=addr)
-        self.vl.start_ranging()
+    def __init__(self, addr=0x29, retries=3):
+        """
+        VL53L1X ToF sensor on default Raspberry Pi I²C bus.
+        Uses Blinka's board.SCL / board.SDA (i2c-1 on Pi).
+        Retries init a few times and fails soft if not present.
+        """
+        self.vl = None
+        # Create I2C using default pins (no getattr!)
+        self.i2c = busio.I2C(board.SCL, board.SDA)
+
+        # Wait briefly for bus to become lockable (after boot)
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
+        # Try init a few times; do not crash app if missing
+        for _ in range(max(1, retries)):
+            try:
+                self.vl = adafruit_vl53l1x.VL53L1X(self.i2c, address=addr)
+                # sensible defaults
+                self.vl.distance_mode = 2    # long
+                self.vl.timing_budget = 50   # ms
+                self.vl.start_ranging()
+                break
+            except Exception:
+                time.sleep(0.2)
 
     def distance_m(self):
-        return self.vl.distance / 1000.0
+        if not self.vl:
+            return None
+        try:
+            d_mm = self.vl.distance
+            return (d_mm / 1000.0) if d_mm is not None else None
+        except Exception:
+            return None