#!/usr/bin/env bash
set -euo pipefail

# Small helper to create a local venv at .venv, install project requirements, and run a Python script
# Usage: ./run_in_venv.sh path/to/script.py [args...]

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
REQ_FILE="$PROJECT_ROOT/requirements.txt"

if [ $# -lt 1 ]; then
  echo "Usage: $0 path/to/script.py [args...]"
  exit 2
fi

SCRIPT="$1"
shift || true

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
  echo "Created venv at $VENV_DIR"
fi

"$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
if [ -f "$REQ_FILE" ]; then
  echo "Installing project requirements from $REQ_FILE into venv..."
  "$VENV_DIR/bin/pip" install --no-cache-dir -r "$REQ_FILE"
else
  echo "No requirements.txt found at $REQ_FILE; skipping requirements install"
fi

echo "Running script with venv python: $VENV_DIR/bin/python $SCRIPT $@"
exec "$VENV_DIR/bin/python" "$SCRIPT" "$@"
