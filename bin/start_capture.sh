#!/usr/bin/env bash
set -euo pipefail
RES=${STREAM_RES:-1280x720}
FPS=${STREAM_FPS:-30}
ROT=${ROTATION:-0}

rpicam-vid --codec h264 --level 4 --profile baseline --inline \
  --framerate ${FPS} --width ${RES%x*} --height ${RES#*x} \
  --rotation ${ROT} --timeout 0 -o - \
| ffmpeg -re -i - -c copy -f rtsp rtsp://127.0.0.1:8554/cam
