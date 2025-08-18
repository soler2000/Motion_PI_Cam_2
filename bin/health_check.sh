#!/usr/bin/env bash
set -e
echo "Services:"
systemctl --no-pager --failed || true
echo
echo "Ports:"
ss -lntup | grep -E '(:8000|:8554|:8888|:8889)' || echo "no listeners"
echo
echo "I2C scan (bus 1):"
which i2cdetect >/dev/null 2>&1 && i2cdetect -y 1 || echo "i2c-tools not installed"
