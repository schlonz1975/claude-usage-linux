# Claude Usage for Linux

A native KDE Plasma panel widget and portable tray indicator for monitoring
remaining Claude usage limits on Linux. Sibling project to [Codex Usage for
Linux](https://github.com/schlonz1975/codex-usage-linux), same design,
Claude's own color theme.

> [!IMPORTANT]
> This is an unofficial community project. It is not affiliated with,
> sponsored by, or endorsed by Anthropic.

> [!NOTE]
> Live usage data relies on an undocumented Anthropic mechanism (the same
> one Claude Code's own CLI uses internally to check quota), not an official
> "read my rate limits" API. It could break on Anthropic's end without
> notice. See [NOTES_LIVE_DATA.md](NOTES_LIVE_DATA.md) for how it works and
> where the details came from.

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
- Stores no prompts, chats, or API keys — only the OAuth token you provide
  for usage checks (see [Authentication](#authentication)).

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

The local service sends a minimal (`max_tokens: 1`) request to Anthropic's
API and reads the account's rate-limit windows off the response headers —
the same mechanism Claude Code's own CLI uses internally to check quota.
The Plasma widget only receives display-ready usage information over the
local session bus. See [NOTES_LIVE_DATA.md](NOTES_LIVE_DATA.md) for details.

## Requirements

- Linux with Python 3.10 or newer.
- The [Claude Code CLI](https://claude.com/product/claude-code), signed in
  with your Claude subscription, to generate a usage-check token (see below).
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

### Authentication

Usage checks need a `claude setup-token` OAuth token — the same one Claude
Code's own docs recommend for CI and scripts where interactive browser login
isn't available:

```bash
claude setup-token   # opens a browser to approve, then prints a token
claude-usage --set-token   # paste it when prompted; saved 0600
```

The token is saved to `~/.config/claude-usage/oauth_token` and never leaves
your machine except in requests to `api.anthropic.com`. If the widget
reports an expired or revoked token, rerun both commands.

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

Verify the token and usage connection:

```bash
claude-usage --check
```

Run the automated test suite:

```bash
make test
```

## Uninstall

```bash
./scripts/uninstall.sh
```

Notification history remains under `~/.local/state/claude-usage`, and the
saved OAuth token remains under `~/.config/claude-usage`, by design. Remove
either manually if you want them gone.

## Privacy and security

The application contains no analytics, telemetry, or crash reporting. See
[PRIVACY.md](PRIVACY.md) and [SECURITY.md](SECURITY.md) for exactly what it
reads, stores, and sends.

## Project status

Alpha. Developed and tested on KDE Plasma 6 running on Nobara Linux. Reports
from other distributions and desktop environments are welcome.

## Credits

This project's structure is adapted from this author's own [Codex Usage for
Linux](https://github.com/schlonz1975/codex-usage-linux) project. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for details.

## License

MIT. See [LICENSE](LICENSE).
