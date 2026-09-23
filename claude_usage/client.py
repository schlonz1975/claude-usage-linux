from __future__ import annotations

import os
import shutil
from pathlib import Path

from .usage import LimitSnapshot


class ClaudeClientError(RuntimeError):
    pass


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


def read_usage(timeout: float = 20.0) -> list[LimitSnapshot]:
    """Fetch current Claude usage windows.

    Not wired up yet. Unlike the Codex CLI, Claude Code has no standalone
    "read my rate limits" RPC — the numbers only exist as
    `anthropic-ratelimit-unified-*` headers on real Messages API responses.
    See NOTES_LIVE_DATA.md in the project root for what was found, what's
    still missing, and why this was left as a stub rather than finished
    with reverse-engineered OAuth internals.
    """
    find_claude()
    raise ClaudeClientError(
        "Live Claude usage data is not wired up yet — see NOTES_LIVE_DATA.md "
        "for what's needed to finish this."
    )
