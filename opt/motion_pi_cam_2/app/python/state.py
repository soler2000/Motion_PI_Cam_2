import os, sqlite3, subprocess, json
from datetime import datetime
DB = os.environ.get("DB_PATH","/srv/motion_pi_cam_2/config.db")

def _conn(): 
    c=sqlite3.connect(DB, check_same_thread=False)
    c.row_factory=sqlite3.Row
    return c

class Settings:
    def __init__(self, db_path=DB):
        global DB; DB=db_path
        self.db=_conn()
    # --- mode ---
    def get_mode(self):
        r=self.db.execute("SELECT active FROM modes WHERE id=1").fetchone()
        return r["active"] if r else "reverse"
    def set_mode(self,m):
        self.db.execute("UPDATE modes SET active=? WHERE id=1",[m]); self.db.commit()
    # --- helpers ---
    def _get1(self, table):
        r=self.db.execute(f"SELECT * FROM {table} WHERE id=1").fetchone()
        return dict(r) if r else {}
    def _set1(self, table, data):
        keys=sorted(data.keys())
        sets=",".join([f"{k}=?" for k in keys])
        vals=[data[k] for k in keys]
        self.db.execute(f"UPDATE {table} SET {sets} WHERE id=1", vals); self.db.commit()
    # --- sections ---
    @property
    def reversing(self): return self._get1("reversing_settings")
    def save_reversing(self, d): self._set1("reversing_settings", d)
    @property
    def surveillance(self): return self._get1("surveillance_settings")
    def save_surveillance(self, d): self._set1("surveillance_settings", d)
    @property
    def led(self): return self._get1("led_settings")
    def save_led(self, d): self._set1("led_settings", d)
    @property
    def system(self): return self._get1("system_settings")
    def save_system(self, d): self._set1("system_settings", d)
    # --- wifi ---
    def wifi_rssi(self):
        try:
            out=subprocess.check_output("iw dev wlan0 link | grep signal || true", shell=True).decode()
            return int(out.strip().split()[-2]) if out.strip() else None
        except Exception: return None
    # --- events ---
    def add_event(self, eid, path, score):
        self.db.execute("INSERT OR REPLACE INTO events(id,ts_start,path,motion_score) VALUES(?,?,?,?)",
                        [eid, datetime.utcnow().isoformat(), path, score])
        self.db.commit()
    def end_event(self, eid):
        self.db.execute("UPDATE events SET ts_end=? WHERE id=?",
                        [datetime.utcnow().isoformat(), eid]); self.db.commit()
    def list_events(self, frm=None, to=None):
        q="SELECT * FROM events WHERE 1=1"
        p=[]
        if frm: q+=" AND ts_start>=?"; p.append(frm+"T00:00:00")
        if to:  q+=" AND ts_start<=?"; p.append(to+"T23:59:59")
        q+=" ORDER BY ts_start DESC LIMIT 200"
        return [dict(r) for r in self.db.execute(q,p).fetchall()]
