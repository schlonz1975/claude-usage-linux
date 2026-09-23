# Privacy

Claude Usage for Linux is designed to run locally.

## Data it reads and sends

The application reads an OAuth token you saved yourself (via
`claude-usage --set-token`, from `claude setup-token`) and sends a minimal
(`max_tokens: 1`) request to `https://api.anthropic.com/v1/messages` — the
same mechanism Claude Code's own CLI uses internally to check quota — then
reads the remaining percentage, reset time, and window duration off the
response headers. It does not read your prompts, chats, project files, or
Claude Code's own `~/.claude/.credentials.json` OAuth session token.

## Data it stores

The application stores only:

- panel layout configuration managed by KDE Plasma;
- the OAuth token you provide, under `~/.config/claude-usage/oauth_token`
  (readable only by you);
- notification markers under `~/.local/state/claude-usage`.

It does not store prompts or chats.

## Network and telemetry

The application has no analytics, telemetry, or crash-reporting SDK. The only
network call it makes is the minimal usage-check request described above.
The usage-page button opens claude.ai in the default browser.

## Removal

`./scripts/uninstall.sh` removes the program, widget, icon, launchers, and
autostart entry. The saved OAuth token and notification markers remain
unless removed manually; delete `~/.config/claude-usage` and
`~/.local/state/claude-usage` to clear them.
