# Security policy

## Supported versions

Security fixes are applied to the latest version on the default branch while
the project is in alpha.

## Reporting a vulnerability

Please do not open a public issue for a vulnerability involving credential
exposure, command execution, or local privilege boundaries. Use GitHub's
private vulnerability reporting feature for this repository instead.

Include the affected version, Linux distribution, desktop environment,
reproduction steps, and expected impact. Do not include access tokens,
`~/.claude/.credentials.json`, prompts, or other private account data.

## Security model

- The widget receives display-ready data over the user's local session D-Bus.
- Installation is limited to user-owned paths and does not require root.
- No network listener is opened by this application.
- The only outbound network call is a minimal usage-check request to
  `api.anthropic.com` (see [NOTES_LIVE_DATA.md](NOTES_LIVE_DATA.md)).
- The OAuth token used for that request is one you generate and save
  yourself (`claude setup-token` / `claude-usage --set-token`), stored at
  `~/.config/claude-usage/oauth_token` with `0600` permissions. The
  application never reads Claude Code's own `~/.claude/.credentials.json`.
