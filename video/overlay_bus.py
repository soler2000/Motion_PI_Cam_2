# simple holder for stats used by overlay/canvas on client
class OverlayBus:
  def __init__(self): self.last={}
  def snapshot(self): return self.last
  def update(self, **kwargs): self.last.update(kwargs); return self.last
