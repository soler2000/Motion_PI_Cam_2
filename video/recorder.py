import os, subprocess, time, threading, uuid, json, shutil
from datetime import datetime
from .motion import Motion

class Recorder:
  def __init__(self, S):
    self.S=S
    self.proc=None
    self.event_id=None
    self.event_path=None
    self.motion_active=False
    self.last_trigger=None
    self.lock=threading.Lock()

  def _spawn_hls_writer(self, outdir):
    cmd=["/opt/motion_pi_cam_2/bin/start_record_hls.sh", outdir]
    return subprocess.Popen(cmd)

  def _thumb(self, outdir):
    inpl=os.path.join(outdir,"index.m3u8")
    out=os.path.join(outdir,"thumb.jpg")
    subprocess.call(["ffmpeg","-y","-i",inpl,"-frames:v","1","-q:v","4",out])

  def start_event(self, score=0.0):
    with self.lock:
      if self.event_id: return
      eid=datetime.utcnow().strftime("%Y%m%d_%H%M%S_")+uuid.uuid4().hex[:6]
      path=f"events/{datetime.utcnow().strftime('%Y-%m-%d')}/{eid}"
      full=os.path.join(self.S.surveillance_root, path)
      os.makedirs(full, exist_ok=True)
      self.proc=self._spawn_hls_writer(full)
      self.event_id=eid; self.event_path=path
      self.S.add_event(eid, path, score)

  def stop_event(self):
    with self.lock:
      if not self.event_id: return
      if self.proc: self.proc.terminate(); self.proc.wait(timeout=5)
      full=os.path.join(self.S.surveillance_root, self.event_path)
      self._thumb(full)
      self.S.end_event(self.event_id)
      self.proc=None; self.event_id=None; self.event_path=None

  def manual_start(self):
    self.start_event(score=0.0)

  def manual_stop(self):
    self.stop_event()

  def on_motion(self, score):
    self.last_trigger=time.time()
    if not self.event_id:
      self.start_event(score)

  def tick(self):
    # extend recording len after last motion
    if self.event_id and self.last_trigger:
      keep = int(self.S.surveillance["clip_len_sec"])
      if time.time() - self.last_trigger > keep:
        self.stop_event()

  @property
  def active_event_path(self):
    return self.event_path
