#!/bin/sh
# Run the app from a virtualenv on the /data volume. The image ships only the web stack;
# YuE2 and PyTorch (several GB) are installed into this venv by the startup updater, so
# they survive container re-creation and image upgrades.
set -e

VENV="/data/venv-py$(python -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
if [ ! -x "$VENV/bin/python" ]; then
    echo "Creating persistent virtualenv in $VENV"
    python -m venv --system-site-packages "$VENV"
fi

exec "$VENV/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
