# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- KDE Plasma 6 panel widget with a Claude-themed two-ring layout.
- Detailed usage popup with progress bars and reset countdowns.
- Local D-Bus service, five-minute refresh, manual refresh, and usage-page action.
- Threshold notifications at 20%, 10%, and 5% remaining.
- Portable GTK/AppIndicator tray fallback.
- User-level installation, autostart, uninstallation, and automated tests.

### Known limitations

- Live usage data is not wired up yet: `claude_usage/client.py` is a stub.
  See [NOTES_LIVE_DATA.md](NOTES_LIVE_DATA.md).
