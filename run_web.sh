#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export FLASK_HOST=${FLASK_HOST:-0.0.0.0}
export FLASK_PORT=${FLASK_PORT:-7860}
python app.py
