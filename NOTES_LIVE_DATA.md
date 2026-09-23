# Wiring up live usage data

`claude_usage/client.py` is currently a stub. This is what's been established
so far about finishing it, and why it was left unfinished.

## Why this isn't a straight port of the Codex client

Codex Usage for Linux works because the Codex CLI exposes a free, dedicated
JSON-RPC method (`account/rateLimits/read`) over `codex app-server`. It's
called by spawning the already-authenticated, officially-shipped `codex`
binary and talking a documented local protocol to it — the widget never
touches an auth token directly.

Claude Code has no equivalent. There is no standalone "tell me my rate
limits" call. The numbers only exist as response headers on real Messages API
calls, and Claude Code's own CLI (`claude -p ...`) does not surface them in
its `--output-format json` output — confirmed by testing directly: a `claude
-p` call returns token/cost usage for that call, not the account-wide
`anthropic-ratelimit-*` percentages.

## What Claude Code itself does internally

Reverse-reading strings in the installed `claude` binary
(`~/.local/share/claude/versions/<version>`, a bundled JS build) turned up
Claude Code's own internal quota-check function. In simplified form:

```js
function mR1() {
  const model = currentModel();
  const client = await getClient({ maxRetries: 0, model, source: "quota_check" });
  return client.beta.messages.create({
    model,
    max_tokens: 1,
    messages: [{ role: "user", content: "quota" }],
    metadata: /* ... */,
  }).asResponse();
}
```

It then reads rate-limit info off the response headers:

```js
function FK7(headers) {
  const out = {};
  for (const [key, abbrev] of [["five_hour","5h"], ["seven_day","7d"], ["overage","overage"]]) {
    const utilization = headers.get(`anthropic-ratelimit-unified-${abbrev}-utilization`);
    const reset = headers.get(`anthropic-ratelimit-unified-${abbrev}-reset`);
    if (utilization !== null && reset !== null) {
      out[key] = { utilization: Number(utilization), resets_at: Number(reset) };
    }
  }
  return out;
}
```

Confirmed header names seen in the binary:

- `anthropic-ratelimit-unified-status`
- `anthropic-ratelimit-unified-reset`
- `anthropic-ratelimit-unified-fallback`
- `anthropic-ratelimit-unified-representative-claim` (the limiting `rateLimitType`)
- `anthropic-ratelimit-unified-5h-utilization` / `-5h-reset`
- `anthropic-ratelimit-unified-7d-utilization` / `-7d-reset`
- `anthropic-ratelimit-unified-overage-utilization` / `-overage-reset` / `-overage-status` / `-overage-disabled-reason`
- `anthropic-ratelimit-unified-{5h,7d,overage}-surpassed-threshold`

`rateLimitType` values seen: `five_hour`, `seven_day`, `seven_day_opus`,
`seven_day_sonnet`, `overage`. Claude's own UI labels: `five_hour` → "session
limit", `seven_day` → "weekly limit", `seven_day_opus` → "Opus limit". These
map directly onto `window_label()` in `usage.py` (300 min / 10080 min
already wired to "Session limit" / "Weekly limit").

Nothing is cached to disk anywhere in `~/.claude/` — these numbers only exist
in memory during a running session, updated as a side effect of real API
calls. There is no zero-cost way to read them from outside a session.

## Where research stopped

Building a client that authenticates directly against `api.anthropic.com`
requires knowing the exact auth header shape for an OAuth-style token
(bearer scheme, and — from partial string matches — some
`anthropic-beta: oauth-...` flag appears to be required) and how the
refresh-token flow works (`https://platform.claude.com/v1/oauth/token` was
visible, along with `client_id`-related strings). Digging further into those
specific details — the OAuth client_id and refresh flow used internally by
Claude Code — was blocked by this environment's own auto-mode classifier as
"Credential Exploration," and that block was respected rather than routed
around. That's a reasonable line: reverse-engineering Anthropic's internal
auth protocol to build a standalone client against it is a different,
riskier thing than what Codex Usage does.

## The safer path not yet taken

`claude setup-token` (documented in `claude --help`) mints a long-lived
token explicitly meant for external tooling to authenticate as the
subscription user, without needing the interactive OAuth dance. That's the
sanctioned equivalent of `codex login` here, and the natural credential
source for this client — the open question is only the exact request shape
(auth header, required beta flag) needed to use that token directly against
`/v1/messages` and read the headers above. That's a small, well-scoped
follow-up, not a redesign.

## Suggested shape for the finished `read_usage()`

Whatever HTTP call ends up being made, have it build the same dict shape
`parse_limits()` in `usage.py` already accepts, so nothing else in the
codebase needs to change:

```python
{
    "rateLimitsByLimitId": {
        "claude": {
            "planType": "pro",  # or "max", "team", "enterprise", ...
            "primary": {         # five_hour
                "usedPercent": ...,     # utilization * 100
                "windowDurationMins": 300,
                "resetsAt": ...,         # unix timestamp
            },
            "secondary": {        # seven_day
                "usedPercent": ...,
                "windowDurationMins": 10_080,
                "resetsAt": ...,
            },
        },
    }
}
```

`display_snapshots()` already prefers the `"claude"` bucket and returns at
most two windows, matching the widget's two-ring layout.
