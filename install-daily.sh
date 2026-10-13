#!/bin/zsh
# Installs a macOS LaunchAgent that runs chart.py when you log in and every day
# at noon (if the Mac is asleep at noon, launchd runs it when it wakes up).
# chart.py catches up on every missed day, so days the Mac was off get filled too.
#
#   ./install-daily.sh              install (also runs it once right away)
#   ./install-daily.sh --uninstall  remove it (already-made commits stay)
#
# Log: ~/Library/Logs/chart-fill.log
set -euo pipefail

LABEL="com.krsmauro.chart-fill"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$HOME/Library/Logs/chart-fill.log"
REPO="${0:A:h}"  # zsh: absolute path of this script's folder
DOMAIN="gui/$(id -u)"

if [[ "${1:-}" == "--uninstall" ]]; then
  launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"
  echo "Removed $LABEL."
  exit 0
fi

PYTHON="$(command -v python3)" || { echo "python3 not found on PATH" >&2; exit 1; }

if [[ "$REPO" == "$HOME"/(Documents|Desktop|Downloads)* ]]; then
  echo "Warning: $REPO is in a folder macOS privacy-protects. Background jobs may be"
  echo "blocked from it (look for 'Operation not permitted' in $LOG). If that"
  echo "happens, move the repo somewhere like ~/code and run this script again."
  echo
fi

mkdir -p "${PLIST:h}" "${LOG:h}"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>$REPO/chart.py</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>PYTHONUNBUFFERED</key>
    <string>1</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>12</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>$LOG</string>
  <key>StandardErrorPath</key>
  <string>$LOG</string>
</dict>
</plist>
EOF

plutil -lint -s "$PLIST"
launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true  # reinstall cleanly if already loaded
launchctl bootstrap "$DOMAIN" "$PLIST"
echo "Installed $LABEL; it is running once now. Follow it with:"
echo "  tail -f $LOG"
