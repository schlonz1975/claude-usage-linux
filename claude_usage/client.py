from __future__ import annotations

import json
import os
import shutil
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .usage import LimitSnapshot, parse_limits


class ClaudeClientError(RuntimeError):
    pass


MESSAGES_URL = "https://api.anthropic.com/v1/messages?beta=true"
ANTHROPIC_VERSION = "2023-06-01"
QUOTA_CHECK_MODEL = "claude-haiku-4-5-20251001"

# Beta flags and client identification an OAuth (claude setup-token) credential
# needs to be accepted by the Messages API, mirroring Claude Code's own client.
# Sourced from the public `subtropic` Anthropic SDK OAuth shim, not reverse
# engineering: https://github.com/deksden/subtropic
OAUTH_BETAS = (
    "claude-code-20250219",
    "oauth-2025-04-20",
    "interleaved-thinking-2025-05-14",
    "fine-grained-tool-streaming-2025-05-14",
)
OAUTH_HEADERS = {
    "anthropic-dangerous-direct-browser-access": "true",
    "x-app": "cli",
    "user-agent": "claude-cli/1.0.63 (external, cli)",
    "accept": "application/json",
    "accept-language": "*",
}

TOKEN_ENV_VAR = "CLAUDE_USAGE_OAUTH_TOKEN"
TOKEN_FILE = (
    Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    / "claude-usage"
    / "oauth_token"
)

RATE_LIMIT_WINDOWS = {"5h": 300, "7d": 10_080}


def find_claude() -> Path:
    override = os.environ.get("CLAUDE_USAGE_CLI_PATH")
    if override:
        candidate = Path(override).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
        raise ClaudeClientError(f"Configured Claude Code executable is not usable: {candidate}")

    executable = shutil.which("claude")
    if executable:
        return Path(executable)
    raise ClaudeClientError("Claude Code CLI not found in PATH")


def _read_token() -> str:
    token = os.environ.get(TOKEN_ENV_VAR, "").strip()
    if token:
        return token
    try:
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        token = ""
    if not token:
        raise ClaudeClientError(
            "No Claude OAuth token configured. Run `claude setup-token`, then save "
            f"the printed token to {TOKEN_FILE} (chmod 600), or export {TOKEN_ENV_VAR}."
        )
    return token


def read_usage(timeout: float = 20.0) -> list[LimitSnapshot]:
    token = _read_token()
    payload = json.dumps(
        {
            "model": QUOTA_CHECK_MODEL,
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "quota"}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        MESSAGES_URL,
        data=payload,
        method="POST",
        headers={
            "content-type": "application/json",
            "anthropic-version": ANTHROPIC_VERSION,
            "anthropic-beta": ",".join(OAUTH_BETAS),
            "authorization": f"Bearer {token}",
            **OAUTH_HEADERS,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            headers = response.headers
    except urllib.error.HTTPError as error:
        if error.code == 401:
            raise ClaudeClientError(
                "Claude sign-in has expired or was revoked. Run `claude setup-token` "
                f"again and update {TOKEN_FILE}."
            ) from error
        # A 429 still carries the rate-limit headers we need; only bail if
        # there's genuinely nothing usable on the response.
        headers = error.headers
        if headers is None or not _has_rate_limit_headers(headers):
            raise ClaudeClientError(f"Claude usage check failed: HTTP {error.code}") from error
    except urllib.error.URLError as error:
        raise ClaudeClientError(f"Could not reach Anthropic's API: {error.reason}") from error

    windows = _windows_from_headers(headers)
    if not windows:
        raise ClaudeClientError("Claude did not return any rate-limit information")
    return parse_limits({"rateLimitsByLimitId": {"claude": {"primary": windows.get("5h"),
                                                              "secondary": windows.get("7d")}}})


def _has_rate_limit_headers(headers: Any) -> bool:
    return any(headers.get(f"anthropic-ratelimit-unified-{abbrev}-utilization") is not None
               for abbrev in RATE_LIMIT_WINDOWS)


def _windows_from_headers(headers: Any) -> dict[str, dict[str, Any]]:
    windows: dict[str, dict[str, Any]] = {}
    for abbrev, minutes in RATE_LIMIT_WINDOWS.items():
        utilization = headers.get(f"anthropic-ratelimit-unified-{abbrev}-utilization")
        reset = headers.get(f"anthropic-ratelimit-unified-{abbrev}-reset")
        if utilization is None or reset is None:
            continue
        windows[abbrev] = {
            "usedPercent": float(utilization) * 100,
            "windowDurationMins": minutes,
            "resetsAt": float(reset),
        }
    return windows
