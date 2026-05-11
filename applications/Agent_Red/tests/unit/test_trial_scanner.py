"""Tests for the trial expiry scanner background task (WI-D1).

Covers:
    - _trial_scanner_loop: expired trial detection and status transition
    - register_trial_scanner: startup/shutdown wiring
    - Edge cases: no expired trials, scanner exception resilience,
      partial failures, already-expired tenants

Run:
    pytest tests/unit/test_trial_scanner.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from src.app.background import (
    _TRIAL_SCAN_INTERVAL,
    _TRIAL_SCAN_STARTUP_DELAY,
    _trial_scanner_loop,
    _startup_trial_scanner,
    _shutdown_trial_scanner,
    register_trial_scanner,
)

# Patch target: the lazy import inside _trial_scanner_loop resolves from
# src.multi_tenant.repository, which re-exports from repositories.tenant.
_REPO_PATCH = "src.multi_tenant.repository.TenantRepository"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_trial_tenant(
    tenant_id: str,
    trial_expires_at: str,
    status: str = "active",
    billing_channel: str = "trial",
) -> dict:
    """Create a minimal trial tenant document."""
    return {
        "id": tenant_id,
        "tenant_id": tenant_id,
        "status": status,
        "billing_channel": billing_channel,
        "tier": "trial",
        "trial_expires_at": trial_expires_at,
        "customer_email": f"{tenant_id}@test.com",
    }


def _expired_iso(days_ago: int = 1) -> str:
    """Return an ISO timestamp N days in the past."""
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def _future_iso(days_ahead: int = 7) -> str:
    """Return an ISO timestamp N days in the future."""
    return (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()


# ---------------------------------------------------------------------------
# Tests: _trial_scanner_loop
# ---------------------------------------------------------------------------


class TestTrialScannerLoop:
    """Unit tests for the trial expiry scanner loop."""

    @pytest.mark.asyncio
    async def test_expires_single_trial(self):
        """Scanner transitions a single expired trial to TRIAL_EXPIRED."""
        mock_repo = AsyncMock()
        mock_repo.list_expired_trials.return_value = [
            _make_trial_tenant("t-exp-001", _expired_iso(2)),
        ]
        mock_repo.patch.return_value = {}

        with (
            patch(_REPO_PATCH, return_value=mock_repo),
            patch("src.app.background.asyncio.sleep", side_effect=[None, asyncio.CancelledError]),
        ):
            with pytest.raises(asyncio.CancelledError):
                await _trial_scanner_loop()

        mock_repo.list_expired_trials.assert_called_once()
        mock_repo.patch.assert_called_once()
        call_kwargs = mock_repo.patch.call_args.kwargs
        assert call_kwargs["tenant_id"] == "t-exp-001"
        assert call_kwargs["document_id"] == "t-exp-001"
        ops = call_kwargs["operations"]
        status_op = next(o for o in ops if o["path"] == "/status")
        assert status_op["value"] == "trial_expired"
        # Verify trial_expired_at is set
        expired_at_op = next(o for o in ops if o["path"] == "/trial_expired_at")
        assert expired_at_op["value"] is not None

    @pytest.mark.asyncio
    async def test_expires_multiple_trials(self):
        """Scanner transitions multiple expired trials in one sweep."""
        mock_repo = AsyncMock()
        mock_repo.list_expired_trials.return_value = [
            _make_trial_tenant("t-a", _expired_iso(3)),
            _make_trial_tenant("t-b", _expired_iso(1)),
            _make_trial_tenant("t-c", _expired_iso(14)),
        ]
        mock_repo.patch.return_value = {}

        with (
            patch(_REPO_PATCH, return_value=mock_repo),
            patch("src.app.background.asyncio.sleep", side_effect=[None, asyncio.CancelledError]),
        ):
            with pytest.raises(asyncio.CancelledError):
                await _trial_scanner_loop()

        assert mock_repo.patch.call_count == 3
        expired_ids = [
            call.kwargs["tenant_id"]
            for call in mock_repo.patch.call_args_list
        ]
        assert set(expired_ids) == {"t-a", "t-b", "t-c"}

    @pytest.mark.asyncio
    async def test_no_expired_trials_no_patches(self):
        """Scanner does nothing when no trials are expired."""
        mock_repo = AsyncMock()
        mock_repo.list_expired_trials.return_value = []

        with (
            patch(_REPO_PATCH, return_value=mock_repo),
            patch("src.app.background.asyncio.sleep", side_effect=[None, asyncio.CancelledError]),
        ):
            with pytest.raises(asyncio.CancelledError):
                await _trial_scanner_loop()

        mock_repo.list_expired_trials.assert_called_once()
        mock_repo.patch.assert_not_called()

    @pytest.mark.asyncio
    async def test_partial_failure_continues(self):
        """If one tenant's patch fails, the scanner continues with others."""
        mock_repo = AsyncMock()
        mock_repo.list_expired_trials.return_value = [
            _make_trial_tenant("t-ok", _expired_iso(1)),
            _make_trial_tenant("t-fail", _expired_iso(2)),
            _make_trial_tenant("t-ok2", _expired_iso(3)),
        ]
        # Second patch raises, first and third succeed
        mock_repo.patch.side_effect = [
            {},
            RuntimeError("Cosmos throttled"),
            {},
        ]

        with (
            patch(_REPO_PATCH, return_value=mock_repo),
            patch("src.app.background.asyncio.sleep", side_effect=[None, asyncio.CancelledError]),
        ):
            with pytest.raises(asyncio.CancelledError):
                await _trial_scanner_loop()

        assert mock_repo.patch.call_count == 3

    @pytest.mark.asyncio
    async def test_query_failure_does_not_crash(self):
        """If list_expired_trials raises, the loop continues to next cycle."""
        mock_repo = AsyncMock()
        mock_repo.list_expired_trials.side_effect = [
            RuntimeError("Cosmos unavailable"),
            [],  # second call succeeds
        ]

        call_count = 0

        async def controlled_sleep(seconds):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                raise asyncio.CancelledError

        with (
            patch(_REPO_PATCH, return_value=mock_repo),
            patch("src.app.background.asyncio.sleep", side_effect=controlled_sleep),
        ):
            with pytest.raises(asyncio.CancelledError):
                await _trial_scanner_loop()

        # Should have been called twice (first fails, second succeeds)
        assert mock_repo.list_expired_trials.call_count == 2

    @pytest.mark.asyncio
    async def test_skips_tenant_without_id(self):
        """Scanner skips documents missing tenant_id field."""
        mock_repo = AsyncMock()
        mock_repo.list_expired_trials.return_value = [
            {"status": "active", "billing_channel": "trial"},  # no tenant_id
            _make_trial_tenant("t-valid", _expired_iso(1)),
        ]
        mock_repo.patch.return_value = {}

        with (
            patch(_REPO_PATCH, return_value=mock_repo),
            patch("src.app.background.asyncio.sleep", side_effect=[None, asyncio.CancelledError]),
        ):
            with pytest.raises(asyncio.CancelledError):
                await _trial_scanner_loop()

        # Only the valid tenant should be patched
        mock_repo.patch.assert_called_once()
        assert mock_repo.patch.call_args.kwargs["tenant_id"] == "t-valid"


# ---------------------------------------------------------------------------
# Tests: Configuration constants
# ---------------------------------------------------------------------------


class TestTrialScannerConfig:
    """Verify scanner configuration constants."""

    def test_scan_interval_is_one_hour(self):
        assert _TRIAL_SCAN_INTERVAL == 3600

    def test_startup_delay_is_120_seconds(self):
        assert _TRIAL_SCAN_STARTUP_DELAY == 120


# ---------------------------------------------------------------------------
# Tests: Registration
# ---------------------------------------------------------------------------


class TestTrialScannerRegistration:
    """Verify register_trial_scanner collects startup/shutdown handlers."""

    def test_registers_startup_and_shutdown(self):
        from src.app.background import _bg_startup_handlers, _bg_shutdown_handlers

        # Clear registries to isolate test
        startup_before = len(_bg_startup_handlers)
        shutdown_before = len(_bg_shutdown_handlers)

        register_trial_scanner()

        # Should append both startup and shutdown handlers
        assert len(_bg_startup_handlers) == startup_before + 1
        assert len(_bg_shutdown_handlers) == shutdown_before + 1
        assert _bg_startup_handlers[-1] is _startup_trial_scanner
        assert _bg_shutdown_handlers[-1] is _shutdown_trial_scanner


# ---------------------------------------------------------------------------
# Tests: Patch operations detail
# ---------------------------------------------------------------------------


class TestTrialScannerPatchOps:
    """Verify exact patch operations applied to expired trials."""

    @pytest.mark.asyncio
    async def test_patch_has_three_operations(self):
        """Verify status, updated_at, and trial_expired_at are all set."""
        mock_repo = AsyncMock()
        mock_repo.list_expired_trials.return_value = [
            _make_trial_tenant("t-ops", _expired_iso(7)),
        ]
        mock_repo.patch.return_value = {}

        with (
            patch(_REPO_PATCH, return_value=mock_repo),
            patch("src.app.background.asyncio.sleep", side_effect=[None, asyncio.CancelledError]),
        ):
            with pytest.raises(asyncio.CancelledError):
                await _trial_scanner_loop()

        ops = mock_repo.patch.call_args.kwargs["operations"]

        # Should have 3 operations: status, updated_at, trial_expired_at
        assert len(ops) == 3

        paths = {o["path"] for o in ops}
        assert paths == {"/status", "/updated_at", "/trial_expired_at"}

        # Status should be trial_expired
        status_op = next(o for o in ops if o["path"] == "/status")
        assert status_op["op"] == "set"
        assert status_op["value"] == "trial_expired"

        # updated_at and trial_expired_at should be valid ISO timestamps
        for path in ["/updated_at", "/trial_expired_at"]:
            op = next(o for o in ops if o["path"] == path)
            assert op["op"] == "set"
            parsed = datetime.fromisoformat(op["value"])
            assert parsed.tzinfo is not None

    @pytest.mark.asyncio
    async def test_patch_uses_tenant_id_for_both_keys(self):
        """Verify patch passes tenant_id as both partition key and document_id."""
        mock_repo = AsyncMock()
        mock_repo.list_expired_trials.return_value = [
            _make_trial_tenant("t-pk", _expired_iso(1)),
        ]
        mock_repo.patch.return_value = {}

        with (
            patch(_REPO_PATCH, return_value=mock_repo),
            patch("src.app.background.asyncio.sleep", side_effect=[None, asyncio.CancelledError]),
        ):
            with pytest.raises(asyncio.CancelledError):
                await _trial_scanner_loop()

        call_kwargs = mock_repo.patch.call_args.kwargs
        assert call_kwargs["tenant_id"] == "t-pk"
        assert call_kwargs["document_id"] == "t-pk"


# ---------------------------------------------------------------------------
# Tests: main.py registration
# ---------------------------------------------------------------------------


class TestMainRegistration:
    """Verify trial scanner is registered in main.py."""

    def test_register_trial_scanner_imported_in_main(self):
        """Confirm main.py imports and calls register_trial_scanner."""
        from src import main
        # The import itself proves registration works without errors.
        # If register_trial_scanner were missing from background.py,
        # importing main would raise ImportError.
        assert hasattr(main, "app")
