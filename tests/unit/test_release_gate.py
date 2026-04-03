"""Slice 6: S253 release gate + canary integration behavioral tests.

Tests BOTH test_pipeline.py phase ordering AND release_pipeline.py Step 5
fail-closed widget transport proof.

Note: test_pipeline.py imports cause teardown issues with pytest + Python 3.14.
Phase constant tests use subprocess to avoid this.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 6

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def _run_python_check(code: str) -> str:
    """Run a Python snippet in a subprocess and return stdout."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=15,
        cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0, f"Check failed: {result.stderr}"
    return result.stdout.strip()


# ── Phase 19 in canonical run sets (test_pipeline.py) ─────────────

class TestPhaseOrdering:
    """Verify Phase 19 (Widget Transport) is in canonical run sets."""

    def test_phase_19_in_phase_order_all(self):
        out = _run_python_check(
            "from scripts.test_pipeline import PHASE_ORDER_ALL; "
            "print(19 in PHASE_ORDER_ALL)"
        )
        assert out == "True"

    def test_phase_19_in_live_phases(self):
        out = _run_python_check(
            "from scripts.test_pipeline import LIVE_PHASES; "
            "print(19 in LIVE_PHASES)"
        )
        assert out == "True"

    def test_phase_19_in_live_group(self):
        out = _run_python_check(
            "from scripts.test_pipeline import PHASE_GROUPS; "
            "print(19 in PHASE_GROUPS['live'])"
        )
        assert out == "True"

    def test_phase_19_in_all_group(self):
        out = _run_python_check(
            "from scripts.test_pipeline import PHASE_GROUPS; "
            "print(19 in PHASE_GROUPS['all'])"
        )
        assert out == "True"


# ── Credential gating in test_pipeline.py ─────────────────────────

class TestTestPipelineCredentialGating:
    """Verify fail-closed credential gating per SPEC-1845."""

    def test_env_vars_present_returns_none(self):
        out = _run_python_check(
            "from scripts.test_pipeline import _check_required_env_vars; "
            "r = _check_required_env_vars("
            "{'PREVIEW_WIDGET_KEY': 'wk', 'PROD_URL': 'https://x'}, "
            "['PREVIEW_WIDGET_KEY', 'PROD_URL'], 19, 'WT'); "
            "print(r is None)"
        )
        assert out == "True"

    def test_env_vars_missing_returns_warn(self):
        out = _run_python_check(
            "from scripts.test_pipeline import _check_required_env_vars; "
            "r = _check_required_env_vars("
            "{'PREVIEW_WIDGET_KEY': ''}, "
            "['PREVIEW_WIDGET_KEY', 'PROD_URL'], 19, 'WT'); "
            "print(r.status, r.extra)"
        )
        assert "WARN" in out
        assert "PREVIEW_WIDGET_KEY" in out


# ── Step 5 fail-closed in release_pipeline.py ─────────────────────

class TestReleasePipelineStep5:
    """Verify Step 5 fail-closed widget transport proof.

    release_pipeline.py imports cause Python 3.14 teardown issues,
    so these tests use subprocess isolation.
    """

    def test_step5_dry_run_returns_fail(self):
        """Dry run returns FAIL (absence of proof is failure)."""
        code = (
            "import argparse\n"
            "from scripts.release_pipeline import step_5_verify_both\n"
            "args = argparse.Namespace(version='v1.98.76', dry_run=True, env='staging')\n"
            "r = step_5_verify_both(args)\n"
            "print(r.status)\n"
            "print(r.detail)\n"
        )
        out = _run_python_check(code)
        lines = out.splitlines()
        # Filter out log lines — status is the first non-log line
        status_line = [l for l in lines if l in ("PASS", "FAIL", "WARN")][-1]
        assert status_line == "FAIL"
        # Detail line should mention dry run
        assert any("dry run" in l.lower() for l in lines)

    def test_step5_missing_widget_key_is_failure(self):
        """Missing widget_key produces a gate failure, not a skip."""
        code = (
            "import argparse, sys\n"
            "from unittest.mock import patch, MagicMock\n"
            "from pathlib import Path\n"
            "# Ensure upgrade_verification is importable\n"
            "sys.path.insert(0, str(Path('scripts')))\n"
            "import upgrade_verification\n"
            "# Override ENVIRONMENTS to have no widget_key\n"
            "upgrade_verification.ENVIRONMENTS = {\n"
            "    'staging': {'fqdn': 'staging.example.com', 'base_url': 'https://staging.example.com', 'api_key': 'k'},\n"
            "    'production': {'fqdn': 'prod.example.com', 'base_url': 'https://prod.example.com', 'api_key': 'k'},\n"
            "}\n"
            "def mock_api(url, headers=None, **kw):\n"
            "    if '/api/health' in url: return {'status': 'healthy'}\n"
            "    return {'system_health': {'version': {'product': '1.98.76'}}}\n"
            "upgrade_verification.api_call = mock_api\n"
            "from scripts.release_pipeline import step_5_verify_both\n"
            "args = argparse.Namespace(version='v1.98.76', dry_run=False, env='staging')\n"
            "r = step_5_verify_both(args)\n"
            "print(r.status)\n"
            "print(r.detail)\n"
        )
        out = _run_python_check(code)
        lines = out.splitlines()
        assert any(l == "FAIL" for l in lines)
        assert any("widget key" in l.lower() and "cannot verify transport" in l.lower() for l in lines)

    def test_step5_incomplete_sse_is_failure(self):
        """SSE stream with token but no done event -> FAIL (incomplete proof)."""
        code = (
            "import argparse, sys, io\n"
            "from unittest.mock import patch, MagicMock\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path('scripts')))\n"
            "import upgrade_verification\n"
            "upgrade_verification.ENVIRONMENTS = {\n"
            "    'staging': {'fqdn': 'stg.example.com', 'base_url': 'https://stg.example.com',\n"
            "                'api_key': 'k', 'widget_key': 'wk_test'},\n"
            "    'production': {'fqdn': 'prod.example.com', 'base_url': 'https://prod.example.com',\n"
            "                   'api_key': 'k', 'widget_key': 'wk_test'},\n"
            "}\n"
            "def mock_api(url, headers=None, **kw):\n"
            "    if '/api/health' in url: return {'status': 'healthy'}\n"
            "    return {'system_health': {'version': {'product': '1.98.76'}}}\n"
            "upgrade_verification.api_call = mock_api\n"
            "\n"
            "# Mock urlopen to simulate incomplete SSE (token only, no done)\n"
            "class FakeResp:\n"
            "    status = 200\n"
            "    def read(self): return b'x' * 2000\n"
            "    def __enter__(self): return self\n"
            "    def __exit__(self, *a): pass\n"
            "\n"
            "class FakeSSEResp:\n"
            "    status = 200\n"
            "    def __init__(self):\n"
            "        # Only token events, NO done event\n"
            "        self._lines = [b'event: token\\n', b'data: hello\\n', b'\\n']\n"
            "    def __iter__(self): return iter(self._lines)\n"
            "    def __enter__(self): return self\n"
            "    def __exit__(self, *a): pass\n"
            "\n"
            "class FakeConvResp:\n"
            "    status = 200\n"
            "    def read(self): return b'{\"conversation_id\": \"conv-1\"}'\n"
            "    def __enter__(self): return self\n"
            "    def __exit__(self, *a): pass\n"
            "\n"
            "class FakeMsgResp:\n"
            "    status = 200\n"
            "    def read(self): return b'{\"ok\": true}'\n"
            "    def __enter__(self): return self\n"
            "    def __exit__(self, *a): pass\n"
            "\n"
            "call_count = [0]\n"
            "def fake_urlopen(req, timeout=None):\n"
            "    url = req if isinstance(req, str) else req.full_url\n"
            "    if '/widget.js' in url: return FakeResp()\n"
            "    if '/api/chat/conversations' in url: return FakeConvResp()\n"
            "    if '/api/chat/message' in url: return FakeMsgResp()\n"
            "    if '/api/chat/stream/' in url: return FakeSSEResp()\n"
            "    return FakeResp()\n"
            "\n"
            "from scripts.release_pipeline import step_5_verify_both\n"
            "args = argparse.Namespace(version='v1.98.76', dry_run=False, env='staging')\n"
            "with patch('urllib.request.urlopen', fake_urlopen):\n"
            "    r = step_5_verify_both(args)\n"
            "print(r.status)\n"
            "print(r.detail)\n"
        )
        out = _run_python_check(code)
        lines = out.splitlines()
        assert any(l == "FAIL" for l in lines), f"Expected FAIL, got: {lines}"
        assert any("sse stream incomplete" in l.lower() or "done=false" in l.lower() for l in lines), (
            f"Expected SSE incomplete error, got: {lines}"
        )


# ── SMTP canary env wiring ────────────────────────────────────────

class TestCanarySMTPEnvWiring:
    """Verify canary SMTP env vars are read at runtime."""

    def test_canary_skips_when_smtp_unconfigured(self):
        from src.jobs.run_widget_canary import send_alert
        with patch.dict(os.environ, {}, clear=True):
            send_alert("Test", "Body")  # Should not raise

    def test_canary_uses_smtp_port_from_env(self):
        from src.jobs.run_widget_canary import send_alert
        with patch.dict(os.environ, {
            "SMTP_HOST": "mail.test.com",
            "SMTP_PORT": "465",
            "SMTP_USER": "user",
            "SMTP_PASSWORD": "pass",
            "CANARY_ALERT_EMAIL": "ops@test.com",
        }):
            with patch("smtplib.SMTP_SSL") as mock_smtp:
                mock_conn = MagicMock()
                mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_conn)
                mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
                send_alert("Test", "Body")
                mock_smtp.assert_called_once_with("mail.test.com", 465)
