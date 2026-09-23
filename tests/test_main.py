from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from claude_usage.main import main


class SetTokenTests(unittest.TestCase):
    def test_set_token_writes_file_with_owner_only_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            token_file = Path(directory) / "claude-usage" / "oauth_token"
            with patch("claude_usage.main.TOKEN_FILE", token_file), \
                 patch("claude_usage.main.getpass.getpass", return_value=" secret-token "):
                exit_code = main(["--set-token"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(token_file.read_text(encoding="utf-8"), "secret-token\n")
            self.assertEqual(token_file.stat().st_mode & 0o777, 0o600)

    def test_set_token_rejects_empty_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            token_file = Path(directory) / "claude-usage" / "oauth_token"
            with patch("claude_usage.main.TOKEN_FILE", token_file), \
                 patch("claude_usage.main.getpass.getpass", return_value="  "):
                exit_code = main(["--set-token"])

            self.assertEqual(exit_code, 1)
            self.assertFalse(token_file.exists())


if __name__ == "__main__":
    unittest.main()
