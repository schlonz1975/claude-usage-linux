#!/bin/bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
linux_dir="$(cd -- "$script_dir/.." && pwd)"
install_root="${XDG_DATA_HOME:-$HOME/.local/share}"
app_dir="$install_root/claude-usage"
bin_dir="$HOME/.local/bin"
applications_dir="$install_root/applications"
autostart_dir="${XDG_CONFIG_HOME:-$HOME/.config}/autostart"
icons_dir="$install_root/icons/hicolor/256x256/apps"
launcher="$bin_dir/claude-usage"

case "$app_dir" in
    "$HOME"/*/claude-usage) ;;
    *) echo "Refusing unsafe installation path: $app_dir" >&2; exit 1 ;;
esac

command -v claude >/dev/null || {
    echo "Claude Code CLI was not found in PATH." >&2
    exit 1
}

mkdir -p "$app_dir/assets" "$bin_dir" "$applications_dir" "$autostart_dir" "$icons_dir"
cp -R "$linux_dir/claude_usage" "$app_dir/"
install -m 0755 "$linux_dir/claude-usage" "$app_dir/claude-usage"
install -m 0644 "$linux_dir/assets/claude-tray.png" "$app_dir/assets/claude-tray.png"
ln -sfn "$app_dir/claude-usage" "$launcher"
install -m 0644 "$linux_dir/assets/claude-usage.png" "$icons_dir/claude-usage.png"

desktop_file="$(mktemp)"
service_desktop_file="$(mktemp)"
trap 'rm -f "$desktop_file" "$service_desktop_file"' EXIT
sed "s|__EXECUTABLE__|$launcher|g" \
    "$linux_dir/packaging/claude-usage.desktop.in" > "$desktop_file"
sed "s|__EXECUTABLE__|$launcher|g" \
    "$linux_dir/packaging/claude-usage-service.desktop.in" > "$service_desktop_file"
install -m 0644 "$desktop_file" "$applications_dir/claude-usage.desktop"
install -m 0644 "$service_desktop_file" "$autostart_dir/claude-usage.desktop"

if command -v kpackagetool6 >/dev/null; then
    if kpackagetool6 --type Plasma/Applet --show com.schlonz1975.claudeusage >/dev/null 2>&1; then
        kpackagetool6 --type Plasma/Applet --upgrade "$linux_dir/plasmoid"
    else
        kpackagetool6 --type Plasma/Applet --install "$linux_dir/plasmoid"
    fi
else
    echo "Warning: kpackagetool6 was not found; the Plasma widget was not installed." >&2
fi

echo "Installed Claude Usage for Linux."
echo "The widget data service will start automatically the next time you log in."
echo "Add 'Claude Usage' to your Plasma panel through KDE's Add Widgets screen."
echo "For the portable tray fallback, run: $launcher"
