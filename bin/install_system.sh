#!/usr/bin/env bash
set -euo pipefail

# Clean older installs (picam names) to avoid overwrite warnings
sudo systemctl disable --now picam.service picam-ap.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/picam.service /etc/systemd/system/picam-ap.service
sudo rm -rf /opt/picam
sudo mv /srv/picam /srv/motion_pi_cam_2 2>/dev/null || true

# Core apt packages
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip sqlite3 git curl jq \
  $(cat /opt/motion_pi_cam_2/requirements-apt.txt)

# Enable camera + I2C
sudo raspi-config nonint do_i2c 0 || true
sudo raspi-config nonint do_camera 0 || true
sudo sed -i '/^dtparam=i2c_arm/s/.*/dtparam=i2c_arm=on/' /boot/firmware/config.txt || true

# Python venv
python3 -m venv /opt/motion_pi_cam_2/venv
/opt/motion_pi_cam_2/venv/bin/pip install --upgrade pip wheel
/opt/motion_pi_cam_2/venv/bin/pip install -r /opt/motion_pi_cam_2/requirements-py.txt

# MediaMTX (ARMv7 for Zero 2 W) - idempotent
if ! command -v mediamtx >/dev/null 2>&1; then
  TMP=$(mktemp -d)
  curl -fsSL https://github.com/bluenviron/mediamtx/releases/latest/download/mediamtx_linux_armv7.tar.gz -o "$TMP/mtx.tar.gz"
  tar -xzf "$TMP/mtx.tar.gz" -C "$TMP" mediamtx
  sudo install -m 755 "$TMP/mediamtx" /usr/local/bin/mediamtx
  rm -rf "$TMP"
fi
sudo install -m 644 /opt/motion_pi_cam_2/app/services/mediamtx.yml /etc/mediamtx.yml

# MediaMTX unit (idempotent)
sudo tee /etc/systemd/system/mediamtx.service >/dev/null <<'EOF'
[Unit]
Description=MediaMTX (WebRTC/HLS broker)
After=network-online.target
Wants=network-online.target
[Service]
ExecStart=/usr/local/bin/mediamtx /etc/mediamtx.yml
Restart=on-failure
RestartSec=2
[Install]
WantedBy=multi-user.target
EOF
# Media storage
sudo mkdir -p /srv/motion_pi_cam_2/{media,thumbs,tmp,logs}
sudo chown -R pi:pi /srv/motion_pi_cam_2

# DB init
sqlite3 /srv/motion_pi_cam_2/config.db < /opt/motion_pi_cam_2/app/migrations/001_init.sql
for f in /opt/motion_pi_cam_2/app/migrations/00*_*.sql; do sqlite3 /srv/motion_pi_cam_2/config.db < "$f"; done

# Services
sudo cp /opt/motion_pi_cam_2/app/services/motion_pi_cam_2.service /etc/systemd/system/
sudo cp /opt/motion_pi_cam_2/app/services/mediamtx.yml /etc/mediamtx.yml
sudo systemctl daemon-reload
sudo systemctl enable mediamtx.service motion_pi_cam_2.service

# AP fallback (NetworkManager-based)
sudo bash -c 'cat > /etc/systemd/system/motion_pi_cam_2-ap.service <<EOF
[Unit]
Description=Motion_PI_Cam_2 Wi-Fi AP fallback
After=NetworkManager.service
[Service]
Type=oneshot
ExecStart=/opt/motion_pi_cam_2/bin/wifi_ap_fallback.sh
[Install]
WantedBy=multi-user.target
EOF'
sudo systemctl enable motion_pi_cam_2-ap.service

# Start services now
sudo systemctl start mediamtx.service motion_pi_cam_2.service
echo "Install complete."
