#!/bin/bash
# Installs the Cursor agent hook (macOS).
# Must run as root (e.g. via sudo or Jamf policy).
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: must run as root (use sudo)" >&2
  exit 1
fi

SCRIPT_DIR="$(dirname "$0")"

HOOKS_SRC="$SCRIPT_DIR/hooks.json"
SCRIPT_SRC="$SCRIPT_DIR/log-tool-calls.sh"
HOOKS_DST="/Library/Application Support/Cursor/hooks.json"
SCRIPT_DST="/usr/local/share/ai-hooks/log-tool-calls.sh"

for f in "$HOOKS_SRC" "$SCRIPT_SRC"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: missing $f" >&2
    exit 1
  fi
done

echo "Installing Cursor agent hook..."

mkdir -p /usr/local/share/ai-hooks
mkdir -p "/Library/Application Support/Cursor"

cp "$HOOKS_SRC" "$HOOKS_DST"
cp "$SCRIPT_SRC" "$SCRIPT_DST"

chown root:wheel "$HOOKS_DST"
chown root:wheel "$SCRIPT_DST"
chmod 644 "$HOOKS_DST"
chmod 755 "$SCRIPT_DST"

echo "Installed:"
echo "  $HOOKS_DST"
echo "  $SCRIPT_DST"
echo ""
echo "Restart Cursor to activate hooks."
