#!/usr/bin/env bash
set -euo pipefail
REPO="git@github.com:soler2000/Motion_PI_Cam_2.git"
ROOT="/opt/motion_pi_cam_2"
cd "${ROOT}"
git init
cat > .gitignore <<'EOF'
venv/
__pycache__/
srv/
*.pyc
*.pyo
*.swp
*.swo
*.log
releases/
EOF
git add .
git commit -m "Initial commit: Motion_PI_Cam_2"
git branch -M main
git remote add origin "${REPO}"
echo "Now run: git push -u origin main"
