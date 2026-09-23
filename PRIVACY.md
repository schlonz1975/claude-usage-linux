# Privacy

Claude Usage for Linux is designed to run locally.

## Current status

`claude_usage/client.py` is a stub — it does not read any credentials or make
any network requests yet. See [NOTES_LIVE_DATA.md](NOTES_LIVE_DATA.md) for
what finishing it will require.

## Data it will read, once wired up

Claude Code has no free, dedicated "read my rate limits" call the way the
Codex CLI does. The finished client is expected to send a minimal real
request to Anthropic's Messages API (mirroring how Claude Code's own internal
quota check works) using a token you provide, and read the resulting
`anthropic-ratelimit-unified-*` response headers. It will not read your
prompts, chats, or project files, and it will not read Claude Code's own
`~/.claude/.credentials.json` OAuth session token directly.

## Data it stores

The application stores only:

- panel layout configuration managed by KDE Plasma;
- display preferences under `~/.config/claude-usage`;
- notification markers under `~/.local/state/claude-usage`.

It does not store prompts, chats, or account credentials.

## Network and telemetry

The application has no analytics, telemetry, or crash-reporting SDK. The
usage-page button opens claude.ai in the default browser.

## Removal

`./scripts/uninstall.sh` removes the program, widget, icon, launchers, and
autostart entry. Notification markers remain unless removed manually; they
contain only limit-window identifiers, reset timestamps, and thresholds.
