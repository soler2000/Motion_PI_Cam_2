import time

def hex_to_rgb(h):
    h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))

def freq_from_distance(d, dmin, dmax, fmin=0.1, fmax=10.0):
    if d is None: return fmin
    d = max(dmin, min(dmax, d))
    ratio = 1.0 - (d - dmin) / max(0.001, (dmax - dmin))
    return max(fmin, min(fmax, fmin + (fmax-fmin)*ratio))

def alt_warn(distance_m, conf, set_all):
    hz = freq_from_distance(distance_m, conf["min_distance_m"], conf["max_distance_m"],
                            conf["f_min_hz"], conf["f_max_hz"])
    period = 1.0 / hz
    phase = (time.time() % period) / period
    w = hex_to_rgb(conf["color_white"]); r = hex_to_rgb(conf["color_red"])
    color = w if phase < 0.5 else r
    set_all(color, brightness=conf["brightness"])
