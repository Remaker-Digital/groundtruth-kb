"""Tests for Phase 6 deferred features.

SPEC-0761 (customer admin), SPEC-0195 (CSV export), SPEC-0151 (covered by A/B),
SPEC-0245 (launcher image), SPEC-1705 (staging proxy), SPEC-0617 (admin RAG),
SPEC-0823 (RAG + memory), SPEC-0297 (backup encryption).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import time



# ---------------------------------------------------------------------------
# SPEC-0761: Customer admin provisioning
# ---------------------------------------------------------------------------

class TestCustomerAdminProvisioning:
    """SPEC-0761: Standard admin account for customer handoff."""

    def test_provision_function_exists(self):
        """provision_customer_admin function is importable."""
        from src.multi_tenant.admin_team_api import provision_customer_admin
        assert callable(provision_customer_admin)

    def test_seed_tenant_has_customer_admin(self):
        """seed_tenant.py TEAM_MEMBERS includes a customer admin."""
        import importlib
        mod = importlib.import_module("scripts.seed_tenant")
        team = getattr(mod, "TEAM_MEMBERS", [])
        roles = [m["role"] for m in team]
        assert "admin" in roles, "Must have a standard admin for customer handoff"
        assert "superadmin" in roles, "Must retain superadmin"

    def test_customer_admin_is_admin_role(self):
        """Customer admin has 'admin' role (not superadmin)."""
        import importlib
        mod = importlib.import_module("scripts.seed_tenant")
        team = getattr(mod, "TEAM_MEMBERS", [])
        admin_members = [m for m in team if m["role"] == "admin"]
        assert len(admin_members) >= 1
        assert admin_members[0]["display_name"] == "Account Administrator"


# ---------------------------------------------------------------------------
# SPEC-0195: Transcript CSV export
# ---------------------------------------------------------------------------

class TestTranscriptCSVExport:
    """SPEC-0195: Conversation transcript CSV export."""

    def test_export_endpoint_exists(self):
        """export-csv endpoint is registered on the conversation router."""
        from src.multi_tenant.admin_conversation_api import router
        paths = [r.path for r in router.routes]
        assert any("export-csv" in p for p in paths)

    def test_export_function_exists(self):
        """export_conversation_csv function is importable."""
        from src.multi_tenant.admin_conversation_api import export_conversation_csv
        assert callable(export_conversation_csv)



# ---------------------------------------------------------------------------
# SPEC-0245: Custom launcher image upload
# ---------------------------------------------------------------------------

class TestCustomLauncherImage:
    """SPEC-0245: Custom launcher image upload."""

    def test_launcher_upload_router_exists(self):
        """Launcher image upload router is importable."""
        from src.multi_tenant.launcher_image_upload import router
        paths = [r.path for r in router.routes]
        assert any("upload" in p for p in paths)

    def test_launcher_delete_endpoint_exists(self):
        """Launcher image delete endpoint exists."""
        from src.multi_tenant.launcher_image_upload import router
        methods = []
        for r in router.routes:
            methods.extend(getattr(r, "methods", []))
        assert "DELETE" in methods


# ---------------------------------------------------------------------------
# SPEC-1705: Local UI dev mode
# ---------------------------------------------------------------------------

class TestLocalUIDevMode:
    """SPEC-1705: Local UI development against staging."""

    def test_staging_env_file_exists(self):
        """Provider admin .env.staging exists with staging API URL."""
        from pathlib import Path
        env_file = Path("admin/provider/.env.staging")
        assert env_file.exists()
        content = env_file.read_text()
        assert "VITE_API_URL" in content
        assert "orangeglacier" in content  # Staging FQDN

    def test_standalone_staging_env_exists(self):
        """Standalone admin .env.staging exists."""
        from pathlib import Path
        env_file = Path("admin/standalone/.env.staging")
        assert env_file.exists()


# ---------------------------------------------------------------------------
# SPEC-0617 + SPEC-0823: RAG configuration
# ---------------------------------------------------------------------------

class TestRAGConfiguration:
    """SPEC-0617 (admin RAG) + SPEC-0823 (RAG + customer memory)."""

    def test_rag_config_service_importable(self):
        """RAGConfigService is importable."""
        from src.multi_tenant.rag_config import RAGConfigService
        svc = RAGConfigService()
        assert svc is not None

    def test_default_config_has_all_sources(self):
        """Default RAG config has all 5 knowledge source types."""
        from src.multi_tenant.rag_config import RAGConfiguration
        config = RAGConfiguration.default("test-tenant")
        assert len(config.sources) == 5
        assert "merchant_docs" in config.sources
        assert "admin_docs" in config.sources
        assert "customer_memory" in config.sources

    def test_merchant_docs_enabled_by_default(self):
        """Merchant docs source is enabled by default."""
        from src.multi_tenant.rag_config import RAGConfiguration
        config = RAGConfiguration.default("test-tenant")
        assert config.sources["merchant_docs"].enabled is True

    def test_admin_docs_disabled_by_default(self):
        """Admin docs (SPEC-0617) is opt-in, disabled by default."""
        from src.multi_tenant.rag_config import RAGConfiguration
        config = RAGConfiguration.default("test-tenant")
        assert config.sources["admin_docs"].enabled is False

    def test_customer_memory_disabled_by_default(self):
        """Customer memory (SPEC-0823) is opt-in, disabled by default."""
        from src.multi_tenant.rag_config import RAGConfiguration
        config = RAGConfiguration.default("test-tenant")
        assert config.sources["customer_memory"].enabled is False

    def test_update_source(self):
        """Can enable/configure a knowledge source."""
        from src.multi_tenant.rag_config import RAGConfigService
        svc = RAGConfigService()
        result = svc.update_source(
            "test-tenant", "admin_docs", enabled=True, max_results=10
        )
        assert result.enabled is True
        assert result.max_results == 10

    def test_get_enabled_sources(self):
        """get_enabled_sources returns only enabled sources."""
        from src.multi_tenant.rag_config import RAGConfigService
        svc = RAGConfigService()
        enabled = svc.get_enabled_sources("test-tenant")
        # Default: merchant_docs + conversation_history
        enabled_types = {s.source_type.value for s in enabled}
        assert "merchant_docs" in enabled_types
        assert "admin_docs" not in enabled_types

    def test_chunk_size_bounds(self):
        """Chunk size is clamped to valid range."""
        from src.multi_tenant.rag_config import RAGConfigService
        svc = RAGConfigService()
        result = svc.update_source("t1", "merchant_docs", chunk_size=10)
        assert result.chunk_size == 64  # Minimum
        result = svc.update_source("t1", "merchant_docs", chunk_size=99999)
        assert result.chunk_size == 2048  # Maximum


# ---------------------------------------------------------------------------
# SPEC-0297: Backup encryption
# ---------------------------------------------------------------------------

class TestBackupEncryption:
    """SPEC-0297: Backup encryption, key management, tiered storage."""

    def test_key_derivation(self):
        """Tenant backup key is derived from master key."""
        from src.multi_tenant.backup_encryption import BackupKeyManager
        mgr = BackupKeyManager(master_key=b"test-master-key-32-bytes-padding!")
        key = mgr.derive_tenant_key("tenant-001")
        assert len(key) == 32  # SHA-256

    def test_different_tenants_different_keys(self):
        """Different tenants get different backup keys."""
        from src.multi_tenant.backup_encryption import BackupKeyManager
        mgr = BackupKeyManager(master_key=b"test-master-key-32-bytes-padding!")
        k1 = mgr.derive_tenant_key("tenant-001")
        k2 = mgr.derive_tenant_key("tenant-002")
        assert k1 != k2

    def test_encrypt_decrypt_roundtrip(self):
        """Data survives encrypt → decrypt roundtrip."""
        from src.multi_tenant.backup_encryption import (
            BackupKeyManager, encrypt_backup, decrypt_backup
        )
        mgr = BackupKeyManager(master_key=b"test-master-key-32-bytes-padding!")
        key = mgr.derive_tenant_key("tenant-001")
        original = b"Hello, this is backup data for tenant-001"
        encrypted = encrypt_backup(original, key)
        decrypted = decrypt_backup(encrypted, key)
        assert decrypted == original

    def test_key_rotation(self):
        """Key rotation creates a new key, marks old as rotated."""
        from src.multi_tenant.backup_encryption import BackupKeyManager
        mgr = BackupKeyManager(master_key=b"test-master-key-32-bytes-padding!")
        old_key = mgr.derive_tenant_key("tenant-001")
        old_info = mgr.get_key_info("tenant-001")
        assert old_info.status == "active"

        new_key = mgr.rotate_key("tenant-001")
        assert new_key != old_key
        assert old_info.status == "rotated"
        new_info = mgr.get_key_info("tenant-001")
        assert new_info.status == "active"

    def test_backup_creation(self):
        """BackupService creates encrypted backups."""
        from src.multi_tenant.backup_encryption import BackupService, BackupStatus
        svc = BackupService()
        record = svc.create_backup(
            "tenant-001", b"backup data", document_count=42
        )
        assert record.status == BackupStatus.COMPLETED
        assert record.encrypted is True
        assert record.document_count == 42

    def test_backup_listing(self):
        """list_backups returns tenant-scoped results."""
        from src.multi_tenant.backup_encryption import BackupService
        svc = BackupService()
        svc.create_backup("t1", b"data1")
        svc.create_backup("t2", b"data2")
        svc.create_backup("t1", b"data3")
        assert len(svc.list_backups("t1")) == 2
        assert len(svc.list_backups("t2")) == 1

    def test_storage_tier_offloading(self):
        """Backups offload from hot → warm → cold."""
        from src.multi_tenant.backup_encryption import (
            BackupService, StorageTier, BackupStatus
        )
        svc = BackupService()
        record = svc.create_backup("t1", b"data")
        assert record.storage_tier == StorageTier.HOT

        # Force offload
        record.offload_at = time.time() - 1
        candidates = svc.get_offload_candidates()
        assert len(candidates) == 1

        svc.offload_backup(record.backup_id)
        assert record.storage_tier == StorageTier.WARM

        record.offload_at = time.time() - 1
        svc.offload_backup(record.backup_id)
        assert record.storage_tier == StorageTier.COLD
        assert record.status == BackupStatus.ARCHIVED

    def test_default_retention_periods(self):
        """Retention periods match spec requirements."""
        from src.multi_tenant.backup_encryption import DEFAULT_RETENTION, StorageTier
        assert DEFAULT_RETENTION[StorageTier.HOT] == 90
        assert DEFAULT_RETENTION[StorageTier.WARM] == 365
        assert DEFAULT_RETENTION[StorageTier.COLD] >= 2555  # 7+ years
