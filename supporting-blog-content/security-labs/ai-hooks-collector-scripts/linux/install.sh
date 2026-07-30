#!/bin/bash
# Installs the Cursor agent hook (Linux).
# Must run as root (e.g. via sudo or fleet policy such as Ansible/Chef).
#
# Target paths:
#   hooks.json: /etc/cursor/hooks.json
#   Script:     /usr/local/share/ai-hooks/log-tool-calls.sh
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: must run as root (use sudo)" >&2
  exit 1
fi

if [ "$(uname -s)" != "Linux" ]; then
  echo "ERROR: this installer is for Linux only (detected: $(uname -s))" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

HOOKS_SRC="$SCRIPT_DIR/hooks.json"
SCRIPT_SRC="$SCRIPT_DIR/log-tool-calls.sh"

for f in "$HOOKS_SRC" "$SCRIPT_SRC"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: missing $f" >&2
    exit 1
  fi
done

HOOKS_DST="/etc/cursor/hooks.json"
SCRIPT_DST="/usr/local/share/ai-hooks/log-tool-calls.sh"

echo "Installing Cursor agent hook (Linux)..."

mkdir -p /etc/cursor
mkdir -p /usr/local/share/ai-hooks

cp "$HOOKS_SRC" "$HOOKS_DST"
cp "$SCRIPT_SRC" "$SCRIPT_DST"

chown root:root "$HOOKS_DST"
chown root:root "$SCRIPT_DST"
chmod 644 "$HOOKS_DST"
chmod 755 "$SCRIPT_DST"

echo "Installed:"
echo "  $HOOKS_DST"
echo "  $SCRIPT_DST"
echo ""
echo "Restart Cursor to activate hooks."
