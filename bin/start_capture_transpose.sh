#!/usr/bin/env bash
set -euo pipefail
RES=${STREAM_RES:-1280x720}
FPS=${STREAM_FPS:-30}
TRANSPOSE_DIR=${TRANSPOSE_DIR:-1}  # 1=cw, 2=ccw

rpicam-vid --codec h264 --inline --framerate ${FPS} \
  --width ${RES%x*} --height ${RES#*x} --timeout 0 -o - \
| ffmpeg -re -i - -vf "transpose=${TRANSPOSE_DIR}" \
  -c:v h264_v4l2m2m -b:v 2M -bufsize 2M -maxrate 2.5M -profile:v baseline \
  -f rtsp rtsp://127.0.0.1:8554/cam
