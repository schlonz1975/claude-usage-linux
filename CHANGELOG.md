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
- Live usage data via a minimal Messages API request authenticated with a
  `claude setup-token` OAuth token, plus `claude-usage --set-token` to save
  it. See [NOTES_LIVE_DATA.md](NOTES_LIVE_DATA.md) for how it works.
