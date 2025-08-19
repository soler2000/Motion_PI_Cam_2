import os
from typing import Dict, Any, Tuple
try:
    from rpi_ws281x import PixelStrip, Color
except Exception:
    PixelStrip=None; Color=None
def _clamp(v,lo,hi): v=int(v); return lo if v<lo else hi if v>hi else v
def _hex_to_rgb(h:str)->Tuple[int,int,int]:
    h=(h or '').lstrip('#'); 
    return (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)) if len(h)==6 else (255,255,255)
class LedRing:
    def __init__(self, gpio=18, count=16, brightness=64):
        self.count=int(count); self.brightness=_clamp(brightness,0,255)
        self.enabled=False; self.strip=None; self.mode="idle"
        self.color_white="#FFFFFF"; self.color_red="#FF0000"
        if os.environ.get("LED_DISABLE","0") in ("1","true","TRUE"): return
        if os.geteuid()!=0 or not os.access("/dev/mem", os.W_OK): return
        if PixelStrip:
            try:
                self.strip=PixelStrip(self.count, gpio, freq_hz=800000, dma=10, invert=False, brightness=self.brightness, channel=0)
                self.strip.begin(); self.enabled=True
            except Exception:
                self.strip=None; self.enabled=False
    def _show_color(self,r,g,b):
        if not(self.strip and self.enabled): return
        c=Color(int(r),int(g),int(b))
        for i in range(self.count): self.strip.setPixelColor(i,c)
        self.strip.show()
    def off(self):
        if not(self.strip and self.enabled): return
        for i in range(self.count): self.strip.setPixelColor(i,0)
        self.strip.show()
    def set_enabled(self,on:bool):
        self.enabled=bool(on and self.strip)
        if self.enabled: self.set_mode(self.mode)
    def set_brightness(self,b:int):
        self.brightness=_clamp(b,0,255)
        if self.strip and self.enabled:
            self.strip.setBrightness(self.brightness); self.strip.show()
    def fill_rgb(self,r,g,b): self._show_color(r,g,b)
    def set_config(self,cfg:Dict[str,Any]):
        if not isinstance(cfg,dict): return
        if "master_enabled" in cfg: self.set_enabled(bool(int(cfg["master_enabled"])))
        if "brightness" in cfg: self.set_brightness(int(cfg["brightness"]))
        if "color_white" in cfg and isinstance(cfg["color_white"],str): self.color_white=cfg["color_white"]
        if "color_red"   in cfg and isinstance(cfg["color_red"],str):   self.color_red=cfg["color_red"]
    def set_mode(self,mode:str):
        self.mode=(mode or "idle")
        if not(self.strip and self.enabled): return
        if self.mode=="idle": self.off()
        elif self.mode=="white_on": self._show_color(*_hex_to_rgb(self.color_white))
        elif self.mode=="reverse_warn": self._show_color(*_hex_to_rgb(self.color_red))
        else: self.off()
