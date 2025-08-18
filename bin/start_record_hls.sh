#!/usr/bin/env bash
set -euo pipefail
OUT="$1"  # /srv/motion_pi_cam_2/media/events/<event_id>
mkdir -p "$OUT"
ffmpeg -rtsp_transport tcp -i rtsp://127.0.0.1:8554/cam \
  -c copy -flags +cgop -g 30 \
  -f hls -hls_time 1 -hls_list_size 60 -hls_flags delete_segments+append_list \
  -master_pl_name master.m3u8 -hls_segment_filename "$OUT/tmp_%05d.ts" \
  "$OUT/index.m3u8"
