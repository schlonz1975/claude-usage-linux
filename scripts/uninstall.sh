#!/bin/bash

set -euo pipefail

install_root="${XDG_DATA_HOME:-$HOME/.local/share}"
app_dir="$install_root/claude-usage"

case "$app_dir" in
    "$HOME"/*/claude-usage) ;;
    *) echo "Refusing unsafe installation path: $app_dir" >&2; exit 1 ;;
esac

rm -f \
    "$HOME/.local/bin/claude-usage" \
    "$install_root/applications/claude-usage.desktop" \
    "${XDG_CONFIG_HOME:-$HOME/.config}/autostart/claude-usage.desktop" \
    "$install_root/icons/hicolor/256x256/apps/claude-usage.png"
rm -rf "$app_dir"

if command -v kpackagetool6 >/dev/null && \
   kpackagetool6 --type Plasma/Applet --show com.schlonz1975.claudeusage >/dev/null 2>&1; then
    kpackagetool6 --type Plasma/Applet --remove com.schlonz1975.claudeusage
fi

echo "Uninstalled Claude Usage for Linux."
echo "Notification history remains in ${XDG_STATE_HOME:-$HOME/.local/state}/claude-usage."
