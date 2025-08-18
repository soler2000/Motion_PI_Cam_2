import subprocess, os

class VideoPipeline:
  def __init__(self, S):
    self.S=S; self.capture=None

  def _start(self, transpose=False):
    env=os.environ.copy()
    env["STREAM_RES"]=self.S.rev["resolution"]
    env["STREAM_FPS"]=str(self.S.rev["fps"])
    env["ROTATION"]=str(self.S.rev["rotation"])
    env["TRANSPOSE_DIR"]=str(self.S.rev["transpose_dir"])
    cmd=["/opt/motion_pi_cam_2/bin/start_capture_transpose.sh"] if transpose \
        else ["/opt/motion_pi_cam_2/bin/start_capture.sh"]
    self.capture = subprocess.Popen(cmd, env=env)

  def apply_mode(self):
    self.stop()
    rot = (self.S.rev["rotation"] if self.S.get_mode()=="reverse" else self.S.surveillance["rotation"])
    transpose = rot in (90,270)
    self._start(transpose=transpose)

  def stop(self):
    if self.capture and self.capture.poll() is None:
      self.capture.terminate()
      self.capture.wait(timeout=5)
    self.capture=None
