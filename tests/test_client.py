from pathlib import Path
import unittest
import urllib.error
from unittest.mock import Mock, patch

from claude_usage.client import ClaudeClientError, read_usage


def response_headers(pairs):
    headers = Mock()
    headers.get = lambda key, default=None: pairs.get(key, default)
    return headers


class ReadUsageTests(unittest.TestCase):
    def test_missing_token_is_reported_clearly(self) -> None:
        missing = Path("/nonexistent/claude-usage/oauth_token")
        with patch.dict("os.environ", {}, clear=True), \
             patch("claude_usage.client.TOKEN_FILE", missing):
            with self.assertRaisesRegex(ClaudeClientError, "claude setup-token"):
                read_usage()

    def test_success_builds_snapshots_from_rate_limit_headers(self) -> None:
        headers = response_headers({
            "anthropic-ratelimit-unified-5h-utilization": "0.42",
            "anthropic-ratelimit-unified-5h-reset": "1500000000",
            "anthropic-ratelimit-unified-7d-utilization": "0.1",
            "anthropic-ratelimit-unified-7d-reset": "1600000000",
        })
        response = Mock()
        response.headers = headers
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)

        with patch.dict("os.environ", {"CLAUDE_USAGE_OAUTH_TOKEN": "test-token"}), \
             patch("claude_usage.client.urllib.request.urlopen", return_value=response):
            snapshots = read_usage()

        self.assertEqual(len(snapshots), 2)
        self.assertEqual(snapshots[0].window_minutes, 300)
        self.assertEqual(snapshots[0].remaining_percent, 58)
        self.assertEqual(snapshots[1].window_minutes, 10_080)
        self.assertEqual(snapshots[1].remaining_percent, 90)

    def test_401_reports_expired_sign_in(self) -> None:
        error = urllib.error.HTTPError("url", 401, "unauthorized", {}, None)
        error.headers = response_headers({})
        with patch.dict("os.environ", {"CLAUDE_USAGE_OAUTH_TOKEN": "test-token"}), \
             patch("claude_usage.client.urllib.request.urlopen", side_effect=error):
            with self.assertRaisesRegex(ClaudeClientError, "claude setup-token"):
                read_usage()

    def test_429_still_reads_rate_limit_headers(self) -> None:
        error = urllib.error.HTTPError("url", 429, "too many requests", {}, None)
        error.headers = response_headers({
            "anthropic-ratelimit-unified-5h-utilization": "0.95",
            "anthropic-ratelimit-unified-5h-reset": "1500000000",
        })
        with patch.dict("os.environ", {"CLAUDE_USAGE_OAUTH_TOKEN": "test-token"}), \
             patch("claude_usage.client.urllib.request.urlopen", side_effect=error):
            snapshots = read_usage()

        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].remaining_percent, 5)


if __name__ == "__main__":
    unittest.main()
