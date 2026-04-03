"""Slice 1a: S252 credential refresh utility behavioral tests.

Tests for scripts/refresh_test_credentials.py — exercises _az_get_secret,
_read_env_local, _write_env_local, _fetch_widget_key, _verify_credentials, main.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 1

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.refresh_test_credentials import (
    _az_get_secret,
    _read_env_local,
    _write_env_local,
    _fetch_widget_key,
    _verify_credentials,
    ENV_LOCAL,
)


# ── _az_get_secret ────────────────────────────────────────────────

class TestAzGetSecret:
    """Behavioral tests for Azure Key Vault secret retrieval."""

    @patch("scripts.refresh_test_credentials.subprocess.run")
    def test_success_returns_secret(self, mock_run):
        """Successful az CLI call returns trimmed secret value."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="  my-secret-value  \n",
        )

        result = _az_get_secret("kv-test", "secret-name")

        assert result == "my-secret-value"
        call_args = mock_run.call_args[0][0]
        assert "--vault-name" in call_args
        assert "kv-test" in call_args
        assert "--name" in call_args
        assert "secret-name" in call_args

    @patch("scripts.refresh_test_credentials.subprocess.run")
    def test_failure_returns_none(self, mock_run):
        """Non-zero return code -> None."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr="Vault not found",
        )

        result = _az_get_secret("kv-test", "secret-name")

        assert result is None

    @patch("scripts.refresh_test_credentials.subprocess.run",
           side_effect=FileNotFoundError("az not found"))
    def test_az_not_installed_returns_none(self, mock_run):
        """Missing Azure CLI -> None."""
        result = _az_get_secret("kv-test", "secret-name")
        assert result is None

    @patch("scripts.refresh_test_credentials.subprocess.run")
    def test_timeout_returns_none(self, mock_run):
        """CLI timeout -> None."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="az", timeout=30)

        result = _az_get_secret("kv-test", "secret-name")

        assert result is None


# ── _read_env_local / _write_env_local ────────────────────────────

class TestEnvLocalIO:
    """Behavioral tests for .env.local reading and writing."""

    def test_read_parses_key_value_pairs(self, tmp_path):
        """Reads KEY=VALUE pairs, skips comments and blanks."""
        env_file = tmp_path / ".env.local"
        env_file.write_text(
            "# Comment\n"
            "API_KEY=abc123\n"
            "\n"
            "WIDGET_KEY=wk_test\n",
            encoding="utf-8",
        )

        with patch("scripts.refresh_test_credentials.ENV_LOCAL", env_file):
            result = _read_env_local()

        assert result == {"API_KEY": "abc123", "WIDGET_KEY": "wk_test"}

    def test_read_missing_file_returns_empty(self, tmp_path):
        """Missing file -> empty dict (no error)."""
        env_file = tmp_path / ".env.local"

        with patch("scripts.refresh_test_credentials.ENV_LOCAL", env_file):
            result = _read_env_local()

        assert result == {}

    def test_write_preserves_comments(self, tmp_path):
        """Write updates values while preserving comments."""
        env_file = tmp_path / ".env.local"
        env_file.write_text(
            "# Agent Red config\n"
            "API_KEY=old_value\n"
            "OTHER=keep\n",
            encoding="utf-8",
        )

        with patch("scripts.refresh_test_credentials.ENV_LOCAL", env_file):
            _write_env_local({"API_KEY": "new_value", "NEW_KEY": "added"})

        content = env_file.read_text(encoding="utf-8")
        assert "# Agent Red config" in content
        assert "API_KEY=new_value" in content
        assert "OTHER=keep" in content
        assert "NEW_KEY=added" in content


# ── _fetch_widget_key ─────────────────────────────────────────────

class TestFetchWidgetKey:
    """Behavioral tests for widget key retrieval from tenant config API."""

    @patch("httpx.Client")
    def test_success_returns_widget_key(self, mock_client_cls):
        """200 with widget_key in config -> returns key."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "config": {"widget_key": "wk_refreshed_key"}
        }
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        result = _fetch_widget_key("https://api.example.com", "admin-key-123")

        assert result == "wk_refreshed_key"
        # Verify API key sent in header
        call_kwargs = mock_client.get.call_args
        assert "X-API-Key" in call_kwargs[1]["headers"]

    @patch("httpx.Client")
    def test_non_200_returns_none(self, mock_client_cls):
        """Non-200 status -> None."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        result = _fetch_widget_key("https://api.example.com", "bad-key")

        assert result is None


# ── _verify_credentials ──────────────────────────────────────────

class TestVerifyCredentials:
    """Behavioral tests for credential verification probe."""

    @patch("httpx.Client")
    def test_valid_credentials_returns_no_problems(self, mock_client_cls):
        """200 for both endpoints -> empty problems dict."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        result = _verify_credentials("https://api.example.com", "good-key", "good-widget")

        assert result == {}

    @patch("httpx.Client")
    def test_stale_widget_key_flagged(self, mock_client_cls):
        """401 for widget key -> problems dict with WIDGET_KEY entry."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        result = _verify_credentials("https://api.example.com", "", "stale-widget")

        assert "WIDGET_KEY" in result

    @patch("httpx.Client")
    def test_stale_api_key_flagged(self, mock_client_cls):
        """401 for API key -> problems dict with API_KEY entry."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_client.get.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        result = _verify_credentials("https://api.example.com", "stale-key", "")

        assert "API_KEY" in result
        assert "401" in result["API_KEY"]


# ── main() orchestration ─────────────────────────────────────────

class TestMainOrchestration:
    """Behavioral tests for the main() refresh workflow."""

    @patch("scripts.refresh_test_credentials._verify_credentials", return_value={})
    @patch("scripts.refresh_test_credentials._fetch_widget_key", return_value="wk_new")
    @patch("scripts.refresh_test_credentials._write_env_local")
    @patch("scripts.refresh_test_credentials._read_env_local", return_value={
        "STAGING_URL": "https://staging.example.com",
        "SUPERADMIN_PREVIEW_API_KEY": "old-key",
    })
    @patch("scripts.refresh_test_credentials._az_get_secret", return_value="new-api-key")
    def test_main_refresh_writes_both_keys(
        self, mock_az, mock_read, mock_write, mock_fetch, mock_verify,
    ):
        """main() refreshes API key from KV + widget key from API, writes both."""
        from scripts.refresh_test_credentials import main
        import sys

        test_args = ["prog", "--env", "staging"]
        with patch.object(sys, "argv", test_args):
            main()

        # _az_get_secret called for API key
        mock_az.assert_called_once()
        # _write_env_local called to persist the new API key
        assert mock_write.call_count >= 1
        # _fetch_widget_key called with base URL and new API key
        mock_fetch.assert_called_once_with("https://staging.example.com", "new-api-key")

    @patch("scripts.refresh_test_credentials._az_get_secret", return_value=None)
    @patch("scripts.refresh_test_credentials._read_env_local", return_value={})
    def test_main_exits_on_kv_failure(self, mock_read, mock_az):
        """main() exits with code 1 when Key Vault retrieval fails."""
        from scripts.refresh_test_credentials import main
        import sys

        test_args = ["prog", "--env", "staging"]
        with patch.object(sys, "argv", test_args), pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    @patch("scripts.refresh_test_credentials._verify_credentials", return_value={})
    @patch("scripts.refresh_test_credentials._read_env_local", return_value={
        "STAGING_URL": "https://staging.example.com",
        "SUPERADMIN_PREVIEW_API_KEY": "existing-key",
        "PREVIEW_WIDGET_KEY": "existing-wk",
    })
    def test_main_verify_only_checks_existing(self, mock_read, mock_verify):
        """main() --verify only probes existing credentials, no writes."""
        from scripts.refresh_test_credentials import main
        import sys

        test_args = ["prog", "--verify"]
        with patch.object(sys, "argv", test_args), pytest.raises(SystemExit) as exc_info:
            main()

        # Exit 0 = valid credentials
        assert exc_info.value.code == 0
        mock_verify.assert_called_once_with(
            "https://staging.example.com", "existing-key", "existing-wk",
        )

    @patch("scripts.refresh_test_credentials._read_env_local", return_value={})
    @patch("scripts.refresh_test_credentials._az_get_secret", return_value="new-key")
    @patch("scripts.refresh_test_credentials._write_env_local")
    def test_main_dry_run_does_not_write(self, mock_write, mock_az, mock_read):
        """main() --dry-run shows what would change without writing."""
        from scripts.refresh_test_credentials import main
        import sys

        test_args = ["prog", "--dry-run"]
        with patch.object(sys, "argv", test_args):
            main()

        # Dry run should NOT call _write_env_local
        mock_write.assert_not_called()
