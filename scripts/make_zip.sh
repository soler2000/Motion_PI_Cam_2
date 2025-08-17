#!/usr/bin/env bash
set -euo pipefail
APP_NAME="Motion_PI_Cam_2"
ZIP_NAME="${APP_NAME}_rpz2w_bookworm.zip"
ROOT_DIR="/opt/motion_pi_cam_2"

cd "${ROOT_DIR}"
find app -name "__pycache__" -type d -prune -exec rm -rf {} +
rm -rf venv 2>/dev/null || true

zip -r "/tmp/${ZIP_NAME}" . -x "venv/*" -x "*.pyc" -x ".git/*" -x ".DS_Store"
mkdir -p "$HOME/releases" && cp -f "/tmp/${ZIP_NAME}" "$HOME/releases/${ZIP_NAME}"
echo "Created: $HOME/releases/${ZIP_NAME}"
