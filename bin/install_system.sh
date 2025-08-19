#!/usr/bin/env bash
set -euo pipefail
./bin/preflight.sh

APP_DIR="/opt/motion_pi_cam_2"
DATA_DIR="/srv/motion_pi_cam_2"
VENV="$APP_DIR/venv"
SERVICE="/etc/systemd/system/motion_pi_cam_2.service"

echo "[1/6] APT prerequisites…"
sudo apt-get update
sudo apt-get install -y git python3-venv python3-dev build-essential sqlite3 jq \
  rpicam-apps ffmpeg network-manager \
  $(grep -vE '^\s*#' requirements-apt.txt | tr '\n' ' ')

echo "[2/6] Directories…"
sudo rm -rf "$APP_DIR" "$DATA_DIR" 2>/dev/null || true
sudo mkdir -p "$APP_DIR" "$DATA_DIR"/{logs,media}
sudo cp -a . "$APP_DIR"
sudo chown -R pi:pi "$APP_DIR" "$DATA_DIR"

echo "[3/6] Python venv…"
python3 -m venv --system-site-packages "$VENV"
sudo chown -R pi:pi "$VENV"
"$VENV/bin/pip" install -U pip wheel setuptools
"$VENV/bin/pip" install -r "$APP_DIR/requirements-py.txt"

echo "[4/6] DB schema…"
sqlite3 "$DATA_DIR/config.db" < "$APP_DIR/schema.sql"

echo "[5/6] systemd unit…"
sudo tee "$SERVICE" >/dev/null <<'UNIT'
[Unit]
Description=Motion_PI_Cam_2 Flask + workers
After=network-online.target
Wants=network-online.target

[Service]
User=root
WorkingDirectory=/opt/motion_pi_cam_2/app/python
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONNOUSERSITE=1
Environment=LED_DISABLE=1
ExecStart=/opt/motion_pi_cam_2/venv/bin/python -m main
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable motion_pi_cam_2.service

echo "[6/6] Enable I2C & free PWM…"
sudo sed -i '/^dtparam=i2c_arm=/d' /boot/firmware/config.txt
echo 'dtparam=i2c_arm=on' | sudo tee -a /boot/firmware/config.txt >/dev/null
sudo sed -i '/^dtparam=audio=/d' /boot/firmware/config.txt
echo 'dtparam=audio=off' | sudo tee -a /boot/firmware/config.txt >/dev/null

echo "Install complete. Reboot recommended."
