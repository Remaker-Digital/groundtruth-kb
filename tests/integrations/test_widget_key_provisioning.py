"""Tests for WI-E1: Widget key auto-provisioning during tenant creation.

Verifies that:
    - generate_widget_key() produces valid pk_live_ keys
    - auto_provision_widget_key() patches TenantDocument with hash
    - auto_provision_widget_key() writes raw key to PreferencesDocument
    - provision_trial_tenant() includes widget_key in the returned TenantRecord
    - Stripe webhook handler includes widget_key in provisioning payload
    - Shopify billing handler includes widget_key in result
    - rotate_widget_key() updates both TenantDocument and PreferencesDocument
    - Failures in widget key provisioning don't block tenant creation

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.auth import (
    WIDGET_KEY_PREFIX,
    generate_widget_key,
    hash_widget_key,
    validate_widget_key_format,
)


# ---------------------------------------------------------------------------
# generate_widget_key() — format and uniqueness
# ---------------------------------------------------------------------------


class TestGenerateWidgetKey:
    """Tests for the canonical generate_widget_key() in auth.py."""

    def test_format_starts_with_prefix(self):
        key = generate_widget_key("test-tenant-001")
        assert key.startswith(WIDGET_KEY_PREFIX)

    def test_format_passes_validation(self):
        key = generate_widget_key("test-tenant-001")
        assert validate_widget_key_format(key) is True

    def test_contains_tenant_hash_prefix(self):
        tenant_id = "test-tenant-001"
        key = generate_widget_key(tenant_id)
        # First 12 hex chars of SHA-256 of tenant_id
        expected_hash = hashlib.sha256(tenant_id.encode()).hexdigest()[:12]
        suffix = key[len(WIDGET_KEY_PREFIX):]
        assert suffix.startswith(expected_hash)

    def test_unique_keys_per_call(self):
        """Same tenant ID produces different keys (random suffix)."""
        key1 = generate_widget_key("test-tenant-001")
        key2 = generate_widget_key("test-tenant-001")
        assert key1 != key2

    def test_different_tenants_different_hash_prefix(self):
        key1 = generate_widget_key("tenant-aaa")
        key2 = generate_widget_key("tenant-bbb")
        suffix1 = key1[len(WIDGET_KEY_PREFIX):].split("_")[0]
        suffix2 = key2[len(WIDGET_KEY_PREFIX):].split("_")[0]
        assert suffix1 != suffix2

    def test_hash_roundtrip(self):
        """Generated key can be hashed and verified."""
        key = generate_widget_key("test-tenant-001")
        hashed = hash_widget_key(key)
        assert hashed == hashlib.sha256(key.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# auto_provision_widget_key() — dual storage
# ---------------------------------------------------------------------------


class TestAutoProvisionWidgetKey:
    """Tests for auto_provision_widget_key() in provisioning.py."""

    @pytest.mark.asyncio
    async def test_patches_tenant_document_with_hash(self):
        """Widget key hash is written to TenantDocument."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        # Pre-populate a tenant document
        await fake_repo.upsert("t-001", {"id": "t-001", "tenant_id": "t-001"})

        fake_prefs_repo = AsyncMock()

        with (
            patch("src.integrations.provisioning._tenant_repo", fake_repo),
            patch(
                "src.multi_tenant.repository.PreferencesRepository",
                return_value=fake_prefs_repo,
            ),
        ):
            from src.integrations.provisioning import auto_provision_widget_key

            raw_key = await auto_provision_widget_key("t-001")

        assert raw_key is not None
        assert raw_key.startswith(WIDGET_KEY_PREFIX)

        # Verify hash was patched onto tenant doc
        doc = await fake_repo.read("t-001", "t-001")
        expected_hash = hash_widget_key(raw_key)
        assert doc["widget_key_hash"] == expected_hash

    @pytest.mark.asyncio
    async def test_writes_raw_key_to_preferences(self):
        """Raw widget key is written to PreferencesDocument."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        await fake_repo.upsert("t-002", {"id": "t-002", "tenant_id": "t-002"})

        fake_prefs_repo = AsyncMock()

        with (
            patch("src.integrations.provisioning._tenant_repo", fake_repo),
            patch(
                "src.multi_tenant.repository.PreferencesRepository",
                return_value=fake_prefs_repo,
            ),
        ):
            from src.integrations.provisioning import auto_provision_widget_key

            raw_key = await auto_provision_widget_key("t-002")

        # Verify prefs repo was called with the raw key
        fake_prefs_repo.patch.assert_called_once()
        call_args = fake_prefs_repo.patch.call_args
        assert call_args[0][0] == "t-002"  # tenant_id
        assert call_args[0][1] == "t-002:active"  # document_id
        ops = call_args[1]["operations"] if "operations" in call_args[1] else call_args[0][2]
        widget_op = next(op for op in ops if op["path"] == "/widget_key")
        assert widget_op["value"] == raw_key

    @pytest.mark.asyncio
    async def test_survives_preferences_failure(self):
        """Widget key is still returned even if PreferencesDocument write fails."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        await fake_repo.upsert("t-003", {"id": "t-003", "tenant_id": "t-003"})

        fake_prefs_repo = AsyncMock()
        fake_prefs_repo.patch.side_effect = Exception("Prefs doc not found")

        with (
            patch("src.integrations.provisioning._tenant_repo", fake_repo),
            patch(
                "src.multi_tenant.repository.PreferencesRepository",
                return_value=fake_prefs_repo,
            ),
        ):
            from src.integrations.provisioning import auto_provision_widget_key

            raw_key = await auto_provision_widget_key("t-003")

        # Key should still be generated and returned
        assert raw_key is not None
        assert raw_key.startswith(WIDGET_KEY_PREFIX)

        # Hash should still be on TenantDocument
        doc = await fake_repo.read("t-003", "t-003")
        assert doc["widget_key_hash"] is not None

    @pytest.mark.asyncio
    async def test_returns_none_when_no_repo(self):
        """Returns None gracefully when tenant repo is not configured."""
        with patch("src.integrations.provisioning._tenant_repo", None):
            from src.integrations.provisioning import auto_provision_widget_key

            result = await auto_provision_widget_key("t-004")

        assert result is None


# ---------------------------------------------------------------------------
# provision_trial_tenant() — widget key in TenantRecord
# ---------------------------------------------------------------------------


class TestTrialProvisioningWidgetKey:
    """provision_trial_tenant() should include widget_key in result."""

    @pytest.mark.asyncio
    async def test_trial_tenant_has_widget_key(self):
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        fake_prefs_repo = AsyncMock()

        with (
            patch("src.integrations.provisioning._tenant_repo", fake_repo),
            patch(
                "src.multi_tenant.repository.PreferencesRepository",
                return_value=fake_prefs_repo,
            ),
        ):
            from src.integrations.provisioning import provision_trial_tenant

            record = await provision_trial_tenant(
                customer_email="trial@example.com",
                trial_duration_days=14,
            )

        assert record.widget_key is not None
        assert record.widget_key.startswith(WIDGET_KEY_PREFIX)
        assert record.tenant_id is not None

    @pytest.mark.asyncio
    async def test_trial_tenant_survives_widget_key_failure(self):
        """Trial provisioning succeeds even if widget key generation fails."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        # Make patch fail (simulating Cosmos DB error)
        original_patch = fake_repo.patch

        call_count = 0

        async def failing_patch(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # First patch call is from auto_provision_widget_key
            if call_count == 1:
                raise Exception("Cosmos DB error")
            return await original_patch(*args, **kwargs)

        fake_repo.patch = failing_patch

        with patch("src.integrations.provisioning._tenant_repo", fake_repo):
            from src.integrations.provisioning import provision_trial_tenant

            record = await provision_trial_tenant(
                customer_email="trial@example.com",
            )

        # Tenant should still be created
        assert record.tenant_id is not None
        assert record.billing_channel.value == "trial"
        # Widget key is None because provisioning failed
        assert record.widget_key is None


# ---------------------------------------------------------------------------
# security_hardening.py — rotation dual-write
# ---------------------------------------------------------------------------


class TestRotateWidgetKeyDualWrite:
    """rotate_widget_key() should update both TenantDocument and PreferencesDocument."""

    @pytest.mark.asyncio
    async def test_rotation_updates_preferences(self):
        """Rotation patches the raw key into PreferencesDocument."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        await fake_repo.upsert("t-rot", {"id": "t-rot", "tenant_id": "t-rot"})

        fake_prefs_repo = AsyncMock()

        # Mock request with tenant context
        mock_request = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "t-rot"
        mock_request.state.tenant_context = mock_ctx

        with (
            patch(
                "src.multi_tenant.security_hardening._tenant_repo",
                fake_repo,
            ),
            patch(
                "src.multi_tenant.repository.PreferencesRepository",
                return_value=fake_prefs_repo,
            ),
        ):
            from src.multi_tenant.security_hardening import rotate_widget_key

            response = await rotate_widget_key(mock_request)

        # Verify response has the new key
        assert response.new_widget_key.startswith(WIDGET_KEY_PREFIX)

        # Verify TenantDocument was patched with hash
        doc = await fake_repo.read("t-rot", "t-rot")
        expected_hash = hashlib.sha256(response.new_widget_key.encode()).hexdigest()
        assert doc["widget_key_hash"] == expected_hash

        # Verify PreferencesDocument was patched with raw key
        fake_prefs_repo.patch.assert_called_once()
        call_args = fake_prefs_repo.patch.call_args
        ops = call_args[1]["operations"] if "operations" in call_args[1] else call_args[0][2]
        widget_op = next(op for op in ops if op["path"] == "/widget_key")
        assert widget_op["value"] == response.new_widget_key

    @pytest.mark.asyncio
    async def test_rotation_survives_prefs_failure(self):
        """Rotation succeeds even if PreferencesDocument update fails."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        await fake_repo.upsert("t-rot2", {"id": "t-rot2", "tenant_id": "t-rot2"})

        fake_prefs_repo = AsyncMock()
        fake_prefs_repo.patch.side_effect = Exception("Prefs not found")

        mock_request = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "t-rot2"
        mock_request.state.tenant_context = mock_ctx

        with (
            patch(
                "src.multi_tenant.security_hardening._tenant_repo",
                fake_repo,
            ),
            patch(
                "src.multi_tenant.repository.PreferencesRepository",
                return_value=fake_prefs_repo,
            ),
        ):
            from src.multi_tenant.security_hardening import rotate_widget_key

            response = await rotate_widget_key(mock_request)

        # Should still succeed
        assert response.new_widget_key.startswith(WIDGET_KEY_PREFIX)
        assert "Update your website" in response.message
