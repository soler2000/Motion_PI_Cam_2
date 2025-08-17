import threading, time

class Repeater:
    def __init__(self, interval, fn, *, daemon=True):
        self.interval = interval; self.fn = fn; self._stop=False
        self.t = threading.Thread(target=self._run, daemon=daemon)
    def start(self): self.t.start()
    def stop(self): self._stop=True
    def _run(self):
        while not self._stop:
            try: self.fn()
            except Exception: pass
            time.sleep(self.interval)
