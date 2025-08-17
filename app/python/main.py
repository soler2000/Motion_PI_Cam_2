from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO
import os, threading, time

from state import Settings
from util.log import get_logger
from util.scheduler import Repeater
from sensors.tof_vl53l1x import ToFSensor
from sensors.ups_ina219 import UpsMonitor
from sensors.system_stats import cpu_temp, cpu_load
from video.pipeline import VideoPipeline
from video.recorder import Recorder
from video.overlay_bus import OverlayBus
from led.led_ctrl import LedRing

LOG = get_logger("app")
app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

MEDIA_ROOT = os.environ.get("MEDIA_DIR","/srv/motion_pi_cam_2/media")
DB_PATH = os.environ.get("DB_PATH","/srv/motion_pi_cam_2/config.db")

S = Settings(DB_PATH)
OB = OverlayBus()
tof = ToFSensor(addr=int(os.environ.get("VL53L1X_ADDR","0x29"),0))
ups = UpsMonitor(addr=int(os.environ.get("INA219_ADDR","0x43"),0))
led = LedRing(gpio=int(os.environ.get("LED_GPIO","18")), count=int(os.environ.get("LED_COUNT","16")),
              brightness=int(os.environ.get("LED_BRIGHTNESS","128")))

# add helpers for Settings
Settings.rev = property(lambda self: self.reversing)
Settings.surv = property(lambda self: self.surveillance)
Settings.surveillance_root = MEDIA_ROOT

vp = VideoPipeline(S)
rec = Recorder(S)

def _apply_led_mode():
    if S.get_mode()=="reverse":
        led.set_config({
            "brightness": S.led["brightness"],
            "color_white": S.led["color_white"],
            "color_red": S.led["color_red"],
            "min_distance_m": S.reversing["min_distance_m"],
            "max_distance_m": S.reversing["max_distance_m"],
            "f_min_hz": S.reversing["f_min_hz"],
            "f_max_hz": S.reversing["f_max_hz"]
        })
        led.set_mode("reverse_warn" if S.led["master_enabled"] else "idle")
    else:
        led.set_config({"brightness": S.led["brightness"], "color_white": S.led["color_white"]})
        led.set_mode("lit" if S.surveillance["light_during_record"] else "idle")

def _stats_tick():
    d = tof.distance_m()
    led.distance_m = d
    snap = ups.snapshot()
    data = {
        "distance_m": round(d,1) if d is not None else None,
        "battery": snap,
        "cpu_temp": cpu_temp(),
        "cpu_load": cpu_load(),
        "wifi": S.wifi_rssi(),
        "led": led.status()
    }
    OB.update(**data)
    socketio.emit("stats", data)

def _safety_shutdown_tick():
    v = ups.snapshot()["voltage"]
    if v <= S.system["shutdown_voltage"]:
        os.system("systemctl poweroff")

def _recorder_tick():
    if S.get_mode()=="surveillance":
        rec.tick()

# start video
vp.apply_mode()
_apply_led_mode()

Repeater(2, _stats_tick).start()
Repeater(2, _safety_shutdown_tick).start()
Repeater(1, _recorder_tick).start()

@app.route("/")
def root(): return render_template("dashboard.html", mode=S.get_mode())

@app.route("/dashboard")
def dashboard(): return render_template("dashboard.html", mode=S.get_mode())

@app.route("/reverse")
def reverse(): return render_template("reverse.html")

@app.route("/surveillance")
def surveillance(): return render_template("surveillance.html")

@app.route("/gallery")
def gallery(): return render_template("gallery.html")

@app.route("/media/<path:subp>")
def media(subp):
    return send_from_directory(MEDIA_ROOT, subp)

# --- Settings pages
@app.route("/settings/reversing")
def settings_rev(): return render_template("settings_reversing.html", s=S.reversing)
@app.route("/settings/surveillance")
def settings_surv(): return render_template("settings_surveillance.html", s=S.surveillance)
@app.route("/settings/led")
def settings_led(): return render_template("settings_led.html", s=S.led)
@app.route("/settings/wifi")
def settings_wifi():
    ap = {"ssid": os.environ.get("AP_SSID","MotionPiCam-AP"),
          "psk": os.environ.get("AP_PSK","changeMe123"),
          "wifi_try": os.environ.get("WIFI_TRY_SEC","30")}
    return render_template("settings_wifi.html", ap=ap)
@app.route("/settings/system")
def settings_sys(): return render_template("settings_system.html", s=S.system)

# --- APIs
@app.route("/api/mode", methods=["GET","POST"])
def api_mode():
    if request.method=="POST":
        m=request.json.get("mode","reverse")
        S.set_mode(m); vp.apply_mode(); _apply_led_mode()
        return "",204
    return jsonify({"mode": S.get_mode()})

@app.route("/api/record/start", methods=["POST"])
def api_record_start():
    S.set_mode("surveillance"); vp.apply_mode()
    rec.manual_start()
    _apply_led_mode()
    return "",204

@app.route("/api/record/stop", methods=["POST"])
def api_record_stop():
    rec.manual_stop()
    led.set_mode("idle")
    return "",204

@app.route("/api/events")
def api_events():
    frm=request.args.get("from"); to=request.args.get("to")
    return jsonify(S.list_events(frm,to))

@app.route("/api/cleanup", methods=["POST"])
def api_cleanup():
    # Simple retention cleanup
    import glob, os, time
    days=int(S.surveillance["retention_days"])
    cutoff=time.time()-days*86400
    for root,dirs,files in os.walk(MEDIA_ROOT):
        if root.endswith("events"): continue
        for f in files:
            p=os.path.join(root,f)
            if os.stat(p).st_mtime<cutoff:
                try: os.remove(p)
                except: pass
    return "",204

# Save settings endpoints
@app.route("/api/settings/reversing", methods=["POST"])
def api_save_rev():
    S.save_reversing(request.json); vp.apply_mode(); _apply_led_mode(); return "",204

@app.route("/api/settings/surveillance", methods=["POST"])
def api_save_surv():
    S.save_surveillance(request.json); vp.apply_mode(); return "",204

@app.route("/api/settings/led", methods=["POST"])
def api_save_led():
    S.save_led(request.json); _apply_led_mode(); return "",204

@app.route("/api/settings/system", methods=["POST"])
def api_save_sys():
    S.save_system(request.json); return "",204

# Wi-Fi scan/connect (nmcli)
@app.route("/api/wifi/scan")
def api_wifi_scan():
    import subprocess, json
    out=subprocess.check_output("nmcli -t -f SSID,SIGNAL dev wifi list", shell=True).decode().strip().splitlines()
    nets=[]
    for l in out:
        if not l: continue
        ssid, signal = l.split(":")[0], l.split(":")[-1]
        if ssid: nets.append({"ssid": ssid, "signal": int(signal) if signal.isdigit() else -100})
    return jsonify(nets)

@app.route("/api/wifi/connect", methods=["POST"])
def api_wifi_connect():
    import subprocess
    d=request.json; ssid=d["ssid"]; psk=d.get("psk","")
    subprocess.call(f"nmcli dev wifi connect '{ssid}' password '{psk}' ifname wlan0", shell=True)
    return "",204

@app.route("/api/wifi/ap", methods=["POST"])
def api_wifi_ap():
    import subprocess, os
    d=request.json
    os.environ["AP_SSID"]=d.get("ssid","MotionPiCam-AP")
    os.environ["AP_PSK"]=d.get("psk","changeMe123")
    os.environ["WIFI_TRY_SEC"]=str(d.get("wifi_try",30))
    return "",204

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000)
