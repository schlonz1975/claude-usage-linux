import unittest
from unittest.mock import patch

from claude_usage.client import ClaudeClientError, read_usage


class StubClientTests(unittest.TestCase):
    def test_read_usage_reports_not_wired_up_yet(self) -> None:
        with patch("claude_usage.client.find_claude", return_value="/bin/claude"):
            with self.assertRaisesRegex(ClaudeClientError, "not wired up yet"):
                read_usage()

    def test_missing_cli_is_reported_before_the_stub_message(self) -> None:
        with patch("claude_usage.client.shutil.which", return_value=None):
            with self.assertRaisesRegex(ClaudeClientError, "not found in PATH"):
                read_usage()
