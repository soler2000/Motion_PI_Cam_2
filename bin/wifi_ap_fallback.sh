#!/usr/bin/env bash
set -euo pipefail
TRY=${WIFI_TRY_SEC:-30}
SSID=${AP_SSID:-MotionPiCam-AP}
PSK=${AP_PSK:-changeMe123}

nmcli radio wifi on
nmcli dev wifi rescan || true

for i in $(seq 1 $TRY); do
  if nmcli -t -f ACTIVE,DEVICE con show --active | grep -q "^yes:wlan0"; then
    exit 0
  fi
  sleep 1
done

if ! nmcli con show "motion-pi-cam-2-ap" >/dev/null 2>&1; then
  nmcli con add type wifi ifname wlan0 con-name "motion-pi-cam-2-ap" autoconnect yes ssid "$SSID"
  nmcli con modify "motion-pi-cam-2-ap" 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared
  nmcli con modify "motion-pi-cam-2-ap" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "$PSK"
fi
nmcli con up "motion-pi-cam-2-ap"
