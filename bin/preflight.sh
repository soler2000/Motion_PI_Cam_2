#!/usr/bin/env bash
set -euo pipefail
BAD=$(grep -RInE '^(<<<<<<<|=======|>>>>>>>|@@ )' app/python || true)
if [ -n "$BAD" ]; then
  echo "ERROR: Merge/diff markers found in code:"
  echo "$BAD"
  exit 1
fi
