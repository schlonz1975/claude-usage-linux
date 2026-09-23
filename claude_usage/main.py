from __future__ import annotations

import argparse
import getpass
import sys
import unittest
from pathlib import Path

from .client import ClaudeClientError, TOKEN_FILE, find_claude, read_usage


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Claude usage indicator for Linux")
    parser.add_argument("--check", action="store_true", help="check CLI and account connectivity")
    parser.add_argument("--self-test", action="store_true", help="run automated tests")
    parser.add_argument("--service", action="store_true", help="run the Plasma data service")
    parser.add_argument(
        "--set-token", action="store_true",
        help="save a `claude setup-token` OAuth token for live usage checks",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        tests_dir = Path(__file__).resolve().parent.parent / "tests"
        suite = unittest.defaultTestLoader.discover(str(tests_dir))
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1

    if args.set_token:
        token = getpass.getpass("Paste the token printed by `claude setup-token`: ").strip()
        if not token:
            print("No token entered.", file=sys.stderr)
            return 1
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        TOKEN_FILE.write_text(token + "\n", encoding="utf-8")
        TOKEN_FILE.chmod(0o600)
        print(f"Saved token to {TOKEN_FILE}")
        return 0

    if args.check:
        try:
            executable = find_claude()
            snapshots = read_usage()
        except ClaudeClientError as error:
            print(f"Claude Usage check failed: {error}", file=sys.stderr)
            return 1
        print(f"Claude CLI: {executable}")
        print(f"Usage connection: working ({len(snapshots)} windows available)")
        return 0

    if args.service:
        from .service import run_service

        return run_service()

    try:
        from .tray import UsageTray
    except (ImportError, ValueError) as error:
        print(f"Could not load the Linux tray libraries: {error}", file=sys.stderr)
        return 1
    UsageTray().run()
    return 0
