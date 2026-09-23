# Claude Usage for Linux

A native KDE Plasma panel widget and portable tray indicator for monitoring
remaining Claude usage limits on Linux. Sibling project to [Codex Usage for
Linux](../CodexUsageLinux), same design, Claude's own color theme.

> [!IMPORTANT]
> This is an unofficial community project. It is not affiliated with,
> sponsored by, or endorsed by Anthropic.

> [!WARNING]
> **Pre-alpha: live usage data is not wired up yet.** The widget, tray,
> service, and Plasma UI are complete and tested, but `claude_usage/client.py`
> is a stub that raises a clear "not implemented" error instead of returning
> real numbers. See [NOTES_LIVE_DATA.md](NOTES_LIVE_DATA.md) for exactly
> what's needed to finish it and why it was left this way.

## Features

- Shows remaining Claude usage and reset times directly in a Plasma panel.
- Shows remaining limits as two rounded rings: terracotta for the 5-hour
  session limit, peach for the weekly limit.
- Keeps the panel and tray icon free of percentage text.
- Displays each available usage window in a native Plasma popup.
- Sends one desktop warning per 20%, 10%, and 5% threshold/reset window.
- Refreshes every five minutes.
- Starts its local data service automatically at login.
- Includes a GTK/AppIndicator tray fallback for non-Plasma desktops.
- Stores no prompts, chats, API keys, or access tokens.

## How it works

```text
Anthropic Messages API (minimal quota-check request)
        │
        ▼
Local Python service
        │ D-Bus
        ▼
KDE Plasma widget
```

Once wired up, the local service will send a minimal request to Anthropic's
API and read the account's rate-limit windows off the response headers —
the same mechanism Claude Code's own CLI uses internally to check quota.
The Plasma widget only receives display-ready usage information over the
local session bus. See [NOTES_LIVE_DATA.md](NOTES_LIVE_DATA.md) for details.

## Requirements

- Linux with Python 3.10 or newer.
- The [Claude Code CLI](https://claude.com/product/claude-code), signed in
  with your Claude subscription (`claude` / `claude auth login`).
- KDE Plasma 6 for the native widget.
- Python D-Bus, PyGObject, libnotify, GTK 3, and Ayatana AppIndicator for the
  service, notifications, and portable tray fallback.

On Fedora/Nobara, the required desktop packages are commonly available as:

```bash
sudo dnf install python3-dbus python3-gobject libnotify \
  gtk3 libayatana-appindicator-gtk3 kf6-kpackage
```

## Install

```bash
cd ClaudeUsageLinux
./scripts/install.sh
```

No `sudo` is used by the installer. It installs files under `~/.local` and
creates an autostart entry under `~/.config/autostart`.

### Add the Plasma widget

1. Right-click the KDE panel and enter edit mode.
2. Select **Add Widgets**.
3. Search for **Claude Usage**.
4. Drag the widget onto the panel.

The rings show the remaining limit clockwise from the top and shrink as usage
is consumed. Click the icon to see remaining percentages and reset times.

### Portable tray fallback

Launch **Claude Usage Tray (Fallback)** from the application menu, or run:

```bash
claude-usage
```

## Diagnostics

```bash
claude-usage --check
```

Until [NOTES_LIVE_DATA.md](NOTES_LIVE_DATA.md) is resolved, this will always
report that live data isn't wired up yet — that's expected.

Run the automated test suite:

```bash
make test
```

## Uninstall

```bash
./scripts/uninstall.sh
```

Notification history remains under `~/.local/state/claude-usage` by design
and contains no account or prompt data.

## Privacy and security

The application contains no analytics, telemetry, crash reporting, or direct
credential handling. See [PRIVACY.md](PRIVACY.md) and [SECURITY.md](SECURITY.md).

## Project status

Pre-alpha. Structurally complete; live data source not yet wired up (see
above). Developed and tested on KDE Plasma 6 running on Nobara Linux. Reports
from other distributions and desktop environments are welcome.

## Credits

This project's structure is adapted from this author's own [Codex Usage for
Linux](../CodexUsageLinux) project. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

## License

MIT. See [LICENSE](LICENSE).
