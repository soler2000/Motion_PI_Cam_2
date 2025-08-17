import time, threading
from rpi_ws281x import PixelStrip, Color
from .animations import alt_warn, hex_to_rgb

class LedRing:
  def __init__(self, gpio=18, count=16, brightness=128):
    self.strip = PixelStrip(count, gpio, 800000, 10, False, brightness, 0)
    self.strip.begin()
    self.master_enabled = True
    self.mode = "idle"
    self.conf = {
      "brightness": brightness, "color_white":"#FFFFFF","color_red":"#FF0000",
      "min_distance_m":0.5,"max_distance_m":5.0,"f_min_hz":0.1,"f_max_hz":10.0
    }
    self.distance_m = None
    self._stop=False
    self.t = threading.Thread(target=self._loop, daemon=True); self.t.start()

  def status(self):
    return f"{'On' if self.master_enabled else 'Off'} ({self.mode})"

  def set_config(self, conf): self.conf.update(conf)

  def _apply(self, color, brightness=None):
    if not self.master_enabled: color=(0,0,0)
    if brightness is None: brightness=self.conf["brightness"]
    self.strip.setBrightness(int(brightness))
    for i in range(self.strip.numPixels()):
      self.strip.setPixelColor(i, Color(*color))
    self.strip.show()

  def set_all(self, color, brightness=None): self._apply(color, brightness)

  def _loop(self):
    while not self._stop:
      if not self.master_enabled:
        self._apply((0,0,0))
        time.sleep(0.2); continue
      if self.mode == "reverse_warn":
        alt_warn(self.distance_m, self.conf, self.set_all)
        time.sleep(0.02)
      elif self.mode == "lit":
        self.set_all(hex_to_rgb(self.conf["color_white"]))
        time.sleep(0.1)
      else:
        self._apply((0,0,0)); time.sleep(0.2)

  def set_mode(self, m): self.mode=m

  def flash_red(self, ms=250):
    self._apply(hex_to_rgb(self.conf["color_red"]))
    time.sleep(ms/1000.0)
