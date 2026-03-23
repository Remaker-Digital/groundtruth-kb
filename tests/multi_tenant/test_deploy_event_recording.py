"""Tests for deploy.py deployment event recording.

Verifies that the record_deployment_event() function in scripts/deploy.py
correctly POSTs audit events to the API, and gracefully handles failures.

Total: 8 tests

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts/ to path so we can import deploy module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))

import deploy  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _silence_log(monkeypatch):
    """Suppress deploy.log() print output during tests."""
    monkeypatch.setattr(deploy, "log", lambda msg: None)


# ---------------------------------------------------------------------------
# record_deployment_event()
# ---------------------------------------------------------------------------


class TestRecordDeploymentEvent:

    @patch.dict("os.environ", {"SPA_PLATFORM_ADMIN_KEY": "test-key-123"})
    @patch("deploy.urllib.request.urlopen")
    def test_posts_correct_payload(self, mock_urlopen):
        """Successful recording sends correct JSON payload."""
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        deploy.record_deployment_event(
            fqdn="example.com",
            environment="staging",
            version="v1.99.0",
            image="acr.io/api-gateway:v1.99.0",
            success=True,
            duration_s=45.2,
        )

        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "https://example.com/api/superadmin/deployments/record"
        assert req.get_header("X-api-key") == "test-key-123"
        assert req.get_header("Content-type") == "application/json"

        body = json.loads(req.data.decode("utf-8"))
        assert body["event_type"] == "model.deployed"
        assert body["environment"] == "staging"
        assert body["version"] == "v1.99.0"
        assert body["image"] == "acr.io/api-gateway:v1.99.0"
        assert body["status"] == "succeeded"
        assert body["duration_s"] == 45.2
        assert body["verification_pass"] == 1
        assert body["verification_fail"] == 0
        assert body["dry_run"] is False

    @patch.dict("os.environ", {"SPA_PLATFORM_ADMIN_KEY": "test-key-123"})
    @patch("deploy.urllib.request.urlopen")
    def test_failed_deploy_records_failed_status(self, mock_urlopen):
        """Failed deployment records status='failed'."""
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        deploy.record_deployment_event(
            fqdn="example.com",
            environment="production",
            version="v1.99.0",
            image="acr.io/api-gateway:v1.99.0",
            success=False,
            duration_s=120.0,
        )

        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        assert body["status"] == "failed"
        assert body["verification_pass"] == 0
        assert body["verification_fail"] == 1

    @patch.dict("os.environ", {}, clear=True)
    @patch("deploy.urllib.request.urlopen")
    def test_skips_when_no_api_key(self, mock_urlopen):
        """No SPA_PLATFORM_ADMIN_KEY → skips recording, no HTTP call."""
        deploy.record_deployment_event(
            fqdn="example.com",
            environment="staging",
            version="v1.99.0",
            image="acr.io/api-gateway:v1.99.0",
            success=True,
            duration_s=10.0,
        )

        mock_urlopen.assert_not_called()

    @patch.dict("os.environ", {"SPA_PLATFORM_ADMIN_KEY": "test-key-123"})
    @patch("deploy.urllib.request.urlopen", side_effect=Exception("Connection refused"))
    def test_network_error_is_nonfatal(self, mock_urlopen):
        """Network error during recording does not raise."""
        # Should not raise — just logs a warning
        deploy.record_deployment_event(
            fqdn="example.com",
            environment="staging",
            version="v1.99.0",
            image="acr.io/api-gateway:v1.99.0",
            success=True,
            duration_s=10.0,
        )

    @patch.dict("os.environ", {"SPA_PLATFORM_ADMIN_KEY": "test-key-123"})
    @patch("deploy.urllib.request.urlopen")
    def test_url_uses_https(self, mock_urlopen):
        """Recording URL always uses HTTPS."""
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        deploy.record_deployment_event(
            fqdn="my-app.azurecontainerapps.io",
            environment="production",
            version="v1.99.0",
            image="acr.io/api-gateway:v1.99.0",
            success=True,
            duration_s=30.0,
        )

        req = mock_urlopen.call_args[0][0]
        assert req.full_url.startswith("https://")

    @patch.dict("os.environ", {"SPA_PLATFORM_ADMIN_KEY": "test-key-123"})
    @patch("deploy.urllib.request.urlopen")
    def test_duration_is_rounded(self, mock_urlopen):
        """Duration is rounded to 1 decimal place."""
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        deploy.record_deployment_event(
            fqdn="example.com",
            environment="staging",
            version="v1.99.0",
            image="acr.io/api-gateway:v1.99.0",
            success=True,
            duration_s=45.6789,
        )

        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        assert body["duration_s"] == 45.7

    @patch.dict("os.environ", {"SPA_PLATFORM_ADMIN_KEY": "test-key-123"})
    @patch("deploy.urllib.request.urlopen")
    def test_event_type_is_always_model_deployed(self, mock_urlopen):
        """deploy.py always records model.deployed (not model.rolled_back)."""
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        deploy.record_deployment_event(
            fqdn="example.com",
            environment="production",
            version="v1.99.0",
            image="acr.io/api-gateway:v1.99.0",
            success=False,  # even on failure, it's a deploy attempt
            duration_s=10.0,
        )

        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        assert body["event_type"] == "model.deployed"

    @patch.dict("os.environ", {"SPA_PLATFORM_ADMIN_KEY": "key"})
    @patch("deploy.urllib.request.urlopen")
    def test_timeout_is_set(self, mock_urlopen):
        """Recording request uses a timeout to avoid blocking."""
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        deploy.record_deployment_event(
            fqdn="example.com",
            environment="staging",
            version="v1.0.0",
            image="img",
            success=True,
            duration_s=1.0,
        )

        _, kwargs = mock_urlopen.call_args
        assert kwargs.get("timeout") == 10
