"""Tests for Admin API Key Management API (WI #159).

Covers:
    - Key generation format and uniqueness
    - Key rotation (old invalidated, new returned)
    - Key revocation
    - Metadata retrieval
    - Conflict on duplicate generation
    - Audit logging
    - Service injection

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.admin_apikey_api import (
    API_KEY_ALPHABET,
    API_KEY_PREFIX,
    API_KEY_RANDOM_LENGTH,
    ApiKeyGeneratedResponse,
    ApiKeyMetadataResponse,
    ApiKeyRevokedResponse,
    configure_apikey_services,
    generate_api_key,
    router,
)
from src.multi_tenant.auth import hash_api_key


# ---------------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------------


class TestGenerateApiKey:
    """Test API key generation format and properties."""

    def test_key_starts_with_prefix(self):
        key = generate_api_key("tenant-abc123")
        assert key.startswith(API_KEY_PREFIX)

    def test_key_includes_tenant_prefix(self):
        key = generate_api_key("tenant-abc123")
        # After "ar_live_", the next 6 chars should be the tenant prefix
        after_prefix = key[len(API_KEY_PREFIX):]
        assert after_prefix.startswith("tenant")

    def test_key_has_correct_format(self):
        key = generate_api_key("tenant-abc123")
        # Format: ar_live_{tenant_prefix}_{random}
        parts = key.split("_")
        assert parts[0] == "ar"
        assert parts[1] == "live"
        # tenant prefix + random part separated by underscore
        assert len(parts) >= 4

    def test_key_random_part_length(self):
        key = generate_api_key("tenant-abc123")
        # Extract random part (after last underscore following tenant prefix)
        random_part = key.split("_")[-1]
        assert len(random_part) == API_KEY_RANDOM_LENGTH

    def test_key_random_part_uses_valid_alphabet(self):
        key = generate_api_key("tenant-abc123")
        random_part = key.split("_")[-1]
        for char in random_part:
            assert char in API_KEY_ALPHABET

    def test_keys_are_unique(self):
        keys = {generate_api_key("tenant-abc123") for _ in range(100)}
        assert len(keys) == 100

    def test_short_tenant_id(self):
        key = generate_api_key("abc")
        assert key.startswith(f"{API_KEY_PREFIX}abc_")

    def test_hash_api_key_deterministic(self):
        key = "ar_live_tenant_AbCdEfGhIjKlMnOpQrStUvWxYz012345"
        hash1 = hash_api_key(key)
        hash2 = hash_api_key(key)
        assert hash1 == hash2

    def test_hash_api_key_is_sha256(self):
        key = "test-key"
        expected = hashlib.sha256(key.encode("utf-8")).hexdigest()
        assert hash_api_key(key) == expected


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class TestModels:
    """Test Pydantic response models."""

    def test_metadata_response_no_key(self):
        resp = ApiKeyMetadataResponse(has_key=False)
        assert resp.has_key is False
        assert resp.key_prefix is None
        assert resp.created_at is None

    def test_metadata_response_with_key(self):
        resp = ApiKeyMetadataResponse(
            has_key=True,
            key_prefix="ar_live_ten",
            created_at="2026-02-05T00:00:00+00:00",
            last_rotated_at="2026-02-05T12:00:00+00:00",
        )
        assert resp.has_key is True
        assert resp.key_prefix == "ar_live_ten"
        assert resp.last_rotated_at is not None

    def test_generated_response(self):
        resp = ApiKeyGeneratedResponse(
            api_key="ar_live_tenant_AbCdEf",
            key_prefix="ar_live_tena",
            created_at="2026-02-05T00:00:00+00:00",
        )
        assert resp.api_key.startswith("ar_live_")
        assert "Save this" in resp.message

    def test_revoked_response(self):
        resp = ApiKeyRevokedResponse(revoked_at="2026-02-05T00:00:00+00:00")
        assert resp.revoked is True

    def test_camel_case_serialization(self):
        resp = ApiKeyMetadataResponse(
            has_key=True,
            key_prefix="ar_live_ten",
            created_at="2026-02-05T00:00:00+00:00",
            last_rotated_at="2026-02-05T12:00:00+00:00",
        )
        data = resp.model_dump(by_alias=True)
        assert "hasKey" in data
        assert "keyPrefix" in data
        assert "createdAt" in data
        assert "lastRotatedAt" in data


# ---------------------------------------------------------------------------
# Endpoint logic (unit tests with mocked repos)
# ---------------------------------------------------------------------------


class TestGetMetadata:
    """Test GET /api/admin/api-keys."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Wire up mock repos."""
        self.tenant_repo = AsyncMock()
        self.audit_repo = AsyncMock()
        configure_apikey_services(self.tenant_repo, self.audit_repo)
        yield
        configure_apikey_services(None, None)

    @pytest.fixture
    def ctx(self):
        return MagicMock(tenant_id="t-001", tier="professional")

    @pytest.mark.asyncio
    async def test_no_key_set(self, ctx):
        from src.multi_tenant.admin_apikey_api import get_api_key_metadata

        self.tenant_repo.read.return_value = {"tenant_id": "t-001"}
        result = await get_api_key_metadata(ctx=ctx)
        assert result.has_key is False
        assert result.key_prefix is None

    @pytest.mark.asyncio
    async def test_key_exists(self, ctx):
        from src.multi_tenant.admin_apikey_api import get_api_key_metadata

        self.tenant_repo.read.return_value = {
            "tenant_id": "t-001",
            "api_key_hash": "abc123",
            "api_key_prefix": "ar_live_t001",
            "api_key_created_at": "2026-02-05T00:00:00+00:00",
        }
        result = await get_api_key_metadata(ctx=ctx)
        assert result.has_key is True
        assert result.key_prefix == "ar_live_t001"
        assert result.created_at is not None

    @pytest.mark.asyncio
    async def test_tenant_not_found(self, ctx):
        from src.multi_tenant.admin_apikey_api import get_api_key_metadata

        self.tenant_repo.read.return_value = None
        with pytest.raises(Exception) as exc_info:
            await get_api_key_metadata(ctx=ctx)
        assert exc_info.value.status_code == 404


class TestGenerateKey:
    """Test POST /api/admin/api-keys."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.tenant_repo = AsyncMock()
        self.audit_repo = AsyncMock()
        configure_apikey_services(self.tenant_repo, self.audit_repo)
        yield
        configure_apikey_services(None, None)

    @pytest.fixture
    def ctx(self):
        return MagicMock(tenant_id="t-001", tier="professional")

    @pytest.mark.asyncio
    async def test_generate_success(self, ctx):
        from src.multi_tenant.admin_apikey_api import generate_new_api_key

        self.tenant_repo.read.return_value = {"tenant_id": "t-001"}
        result = await generate_new_api_key(ctx=ctx)
        assert result.api_key.startswith(API_KEY_PREFIX)
        assert result.key_prefix == result.api_key[:12]
        assert result.created_at is not None
        # Verify patch was called with hash
        self.tenant_repo.patch.assert_called_once()
        call_args = self.tenant_repo.patch.call_args
        ops = call_args.kwargs.get("operations", call_args[1].get("operations", []))
        hash_op = [o for o in ops if o["path"] == "/api_key_hash"]
        assert len(hash_op) == 1
        assert hash_op[0]["value"] == hash_api_key(result.api_key)

    @pytest.mark.asyncio
    async def test_generate_conflict_existing_key(self, ctx):
        from src.multi_tenant.admin_apikey_api import generate_new_api_key

        self.tenant_repo.read.return_value = {
            "tenant_id": "t-001",
            "api_key_hash": "existing-hash",
        }
        with pytest.raises(Exception) as exc_info:
            await generate_new_api_key(ctx=ctx)
        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_generate_logs_audit(self, ctx):
        from src.multi_tenant.admin_apikey_api import generate_new_api_key

        self.tenant_repo.read.return_value = {"tenant_id": "t-001"}
        await generate_new_api_key(ctx=ctx)
        self.audit_repo.log_event.assert_called_once()
        audit_call = self.audit_repo.log_event.call_args
        from src.multi_tenant.cosmos_schema import AuditEventType
        assert audit_call.kwargs["event_type"] == AuditEventType.SECURITY_EVENT
        assert "api_key_generated" in str(audit_call.kwargs["payload"])


class TestRotateKey:
    """Test POST /api/admin/api-keys/rotate."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.tenant_repo = AsyncMock()
        self.audit_repo = AsyncMock()
        configure_apikey_services(self.tenant_repo, self.audit_repo)
        yield
        configure_apikey_services(None, None)

    @pytest.fixture
    def ctx(self):
        return MagicMock(tenant_id="t-001", tier="professional")

    @pytest.mark.asyncio
    async def test_rotate_success(self, ctx):
        from src.multi_tenant.admin_apikey_api import rotate_api_key

        self.tenant_repo.read.return_value = {
            "tenant_id": "t-001",
            "api_key_hash": "old-hash",
            "api_key_prefix": "ar_live_old_",
        }
        result = await rotate_api_key(ctx=ctx)
        assert result.api_key.startswith(API_KEY_PREFIX)
        assert "rotated" in result.message.lower()
        # Patch called with both hash and rotation timestamp
        ops = self.tenant_repo.patch.call_args.kwargs.get(
            "operations",
            self.tenant_repo.patch.call_args[1].get("operations", []),
        )
        rotated_op = [o for o in ops if o["path"] == "/api_key_last_rotated_at"]
        assert len(rotated_op) == 1

    @pytest.mark.asyncio
    async def test_rotate_without_existing_key(self, ctx):
        """Rotation should work even without an existing key (acts as generate)."""
        from src.multi_tenant.admin_apikey_api import rotate_api_key

        self.tenant_repo.read.return_value = {"tenant_id": "t-001"}
        result = await rotate_api_key(ctx=ctx)
        assert result.api_key.startswith(API_KEY_PREFIX)

    @pytest.mark.asyncio
    async def test_rotate_logs_audit_with_old_prefix(self, ctx):
        from src.multi_tenant.admin_apikey_api import rotate_api_key

        self.tenant_repo.read.return_value = {
            "tenant_id": "t-001",
            "api_key_hash": "old-hash",
            "api_key_prefix": "ar_live_old_",
        }
        await rotate_api_key(ctx=ctx)
        self.audit_repo.log_event.assert_called_once()
        audit_payload = self.audit_repo.log_event.call_args.kwargs["payload"]
        assert audit_payload["action"] == "api_key_rotated"
        assert audit_payload["old_prefix"] == "ar_live_old_"

    @pytest.mark.asyncio
    async def test_rotate_generates_different_key_than_old(self, ctx):
        from src.multi_tenant.admin_apikey_api import rotate_api_key

        self.tenant_repo.read.return_value = {
            "tenant_id": "t-001",
            "api_key_hash": "old-hash",
        }
        result1 = await rotate_api_key(ctx=ctx)
        result2 = await rotate_api_key(ctx=ctx)
        assert result1.api_key != result2.api_key


class TestRevokeKey:
    """Test DELETE /api/admin/api-keys."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        self.tenant_repo = AsyncMock()
        self.audit_repo = AsyncMock()
        configure_apikey_services(self.tenant_repo, self.audit_repo)
        yield
        configure_apikey_services(None, None)

    @pytest.fixture
    def ctx(self):
        return MagicMock(tenant_id="t-001", tier="professional")

    @pytest.mark.asyncio
    async def test_revoke_success(self, ctx):
        from src.multi_tenant.admin_apikey_api import revoke_api_key

        self.tenant_repo.read.return_value = {
            "tenant_id": "t-001",
            "api_key_hash": "existing-hash",
            "api_key_prefix": "ar_live_t001",
        }
        result = await revoke_api_key(ctx=ctx)
        assert result.revoked is True
        # Verify hash cleared
        ops = self.tenant_repo.patch.call_args.kwargs.get(
            "operations",
            self.tenant_repo.patch.call_args[1].get("operations", []),
        )
        hash_op = [o for o in ops if o["path"] == "/api_key_hash"]
        assert hash_op[0]["value"] is None

    @pytest.mark.asyncio
    async def test_revoke_no_key_exists(self, ctx):
        from src.multi_tenant.admin_apikey_api import revoke_api_key

        self.tenant_repo.read.return_value = {"tenant_id": "t-001"}
        with pytest.raises(Exception) as exc_info:
            await revoke_api_key(ctx=ctx)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_revoke_logs_audit(self, ctx):
        from src.multi_tenant.admin_apikey_api import revoke_api_key

        self.tenant_repo.read.return_value = {
            "tenant_id": "t-001",
            "api_key_hash": "hash",
            "api_key_prefix": "ar_live_t001",
        }
        await revoke_api_key(ctx=ctx)
        self.audit_repo.log_event.assert_called_once()
        audit_payload = self.audit_repo.log_event.call_args.kwargs["payload"]
        assert audit_payload["action"] == "api_key_revoked"
        assert audit_payload["revoked_prefix"] == "ar_live_t001"


class TestServiceNotInitialized:
    """Test 503 when services not wired."""

    @pytest.fixture(autouse=True)
    def reset_services(self):
        configure_apikey_services(None, None)
        yield
        configure_apikey_services(None, None)

    @pytest.fixture
    def ctx(self):
        return MagicMock(tenant_id="t-001", tier="professional")

    @pytest.mark.asyncio
    async def test_get_metadata_503(self, ctx):
        from src.multi_tenant.admin_apikey_api import get_api_key_metadata

        with pytest.raises(Exception) as exc_info:
            await get_api_key_metadata(ctx=ctx)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_generate_503(self, ctx):
        from src.multi_tenant.admin_apikey_api import generate_new_api_key

        with pytest.raises(Exception) as exc_info:
            await generate_new_api_key(ctx=ctx)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_rotate_503(self, ctx):
        from src.multi_tenant.admin_apikey_api import rotate_api_key

        with pytest.raises(Exception) as exc_info:
            await rotate_api_key(ctx=ctx)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_revoke_503(self, ctx):
        from src.multi_tenant.admin_apikey_api import revoke_api_key

        with pytest.raises(Exception) as exc_info:
            await revoke_api_key(ctx=ctx)
        assert exc_info.value.status_code == 503


class TestConfigureServices:
    """Test service injection."""

    def test_configure_sets_repos(self):
        repo = MagicMock()
        audit = MagicMock()
        configure_apikey_services(repo, audit)
        # Verify by checking module-level vars
        import src.multi_tenant.admin_apikey_api as mod
        assert mod._tenant_repo is repo
        assert mod._audit_repo is audit
        configure_apikey_services(None, None)

    def test_configure_with_none_audit(self):
        repo = MagicMock()
        configure_apikey_services(repo, None)
        import src.multi_tenant.admin_apikey_api as mod
        assert mod._tenant_repo is repo
        assert mod._audit_repo is None
        configure_apikey_services(None, None)


class TestConstants:
    """Test module constants."""

    def test_prefix(self):
        assert API_KEY_PREFIX == "ar_live_"

    def test_random_length(self):
        assert API_KEY_RANDOM_LENGTH == 32

    def test_alphabet_has_letters_and_digits(self):
        assert "a" in API_KEY_ALPHABET
        assert "Z" in API_KEY_ALPHABET
        assert "0" in API_KEY_ALPHABET
        assert "9" in API_KEY_ALPHABET
        # No special characters
        assert "-" not in API_KEY_ALPHABET
        assert "_" not in API_KEY_ALPHABET


# ---------------------------------------------------------------------------
# Router prefix and endpoint existence checks
# ---------------------------------------------------------------------------


class TestRouterAndEndpoints:
    """Verify router prefix and that key endpoints are registered."""

    def test_router_prefix_is_api_admin_api_keys(self):
        """Router prefix must be /api/admin/api-keys."""
        assert router.prefix == "/api/admin/api-keys"

    def test_reset_endpoint_exists(self):
        """reset_api_key_via_email (public, no auth) endpoint is registered."""
        route_paths = [r.path for r in router.routes]
        assert any("reset" in p for p in route_paths)

    def test_list_api_keys_endpoint_exists(self):
        """GET /api/admin/api-keys (list/get metadata) endpoint is registered."""
        # The root path includes the prefix: /api/admin/api-keys
        route_paths = [r.path for r in router.routes]
        assert any("api-keys" in p for p in route_paths)
