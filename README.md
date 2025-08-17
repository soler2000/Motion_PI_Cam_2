# Motion_PI_Cam_2

**Dual-mode Raspberry Pi Zero 2 W camera system for iPhone/iPad.**
- **Mode 1 – Reversing:** ultra-low-latency WebRTC, ToF distance overlay, LED warning (0.1–10 Hz).
- **Mode 2 – Surveillance:** motion detection, pre-roll, recording to HLS, gallery & timeline.

> OS: Raspberry Pi OS **Bookworm** • Hardware: **Zero 2 W**, CSI camera, **VL53L1X** (0x29), **UPS HAT (C) INA219** (0x43), **WS2812 16-LED** ring on **GPIO18**.

---

## Features

- **Streaming:** `rpicam-vid` (H.264 baseline) → **MediaMTX** → WebRTC (Mode 1), HLS (Mode 2).
- **Rotation:** 0/180 (stream-copy) or 90/270 via transpose + `h264_v4l2m2m`.
- **Motion:** OpenCV frame differencing with configurable sensitivity; **pre-roll**.
- **Recording:** 5-min default segments, thumbnails, retention policy.
- **LED:** White illumination + **White↔Red** alternation 0.1–10 Hz proportional to distance.
- **UPS:** INA219 voltage/current/power/% + **safe shutdown** threshold.
- **Web UI (Flask):** Dashboard, Reversing, Surveillance, Gallery, multi-page **Settings**, dark mode.
- **Network:** Tries known Wi-Fi for 30s; **AP fallback** via NetworkManager (SSID `MotionPiCam-AP`).

---

## Architecture

- Component diagram: [`docs/architecture.puml`](docs/architecture.puml)
- Sequences: [`docs/flows.puml`](docs/flows.puml)

Render with [PlantUML](https://plantuml.com):
```bash
plantuml docs/architecture.puml
plantuml docs/flows.puml
