import cv2, numpy as np, collections

class Motion:
  def __init__(self, S):
    self.bg = None
    self.conf = {"thresh": 18, "min_area": 1200}
    self.sensitivity = S.surveillance["sensitivity"]

  def detect(self, frame_gray):
    if self.bg is None:
      self.bg = frame_gray.copy().astype("float"); return False, 0.0
    cv2.accumulateWeighted(frame_gray, self.bg, 0.03)
    delta = cv2.absdiff(frame_gray, cv2.convertScaleAbs(self.bg))
    _, thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area = sum(cv2.contourArea(c) for c in cnts)
    # map sensitivity 0..100 to area threshold 3000..400
    min_area = int(3000 - (self.sensitivity/100.0)*2600)
    triggered = area > min_area
    return triggered, area
