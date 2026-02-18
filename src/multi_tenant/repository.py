"""
Tenant-scoped data access layer — backward-compatible re-export barrel.

All repository classes now live in ``src.multi_tenant.repositories.*``.
This file re-exports every public name so that existing imports like:

    from src.multi_tenant.repository import TenantRepository

continue to work without modification.

For new code, prefer importing from the package directly:

    from src.multi_tenant.repositories import TenantRepository
    from src.multi_tenant.repositories.base import DocumentNotFoundError

Architecture reference: Decision #1 (TenantScopedRepository)
R2 refactoring — session 34.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

# Re-export everything from the repositories package
from src.multi_tenant.repositories import (  # noqa: F401
    AuditLogRepository,
    ConversationRepository,
    CustomerProfileRepository,
    DocumentConflictError,
    DocumentNotFoundError,
    KnowledgeBaseRepository,
    MemoryVectorRepository,
    PlatformConfigRepository,
    PlatformScopedRepository,
    PreferencesRepository,
    SLASnapshotRepository,
    TeamMemberRepository,
    TenantIsolationError,
    TenantRepository,
    TenantScopedRepository,
    UsageRepository,
    VerificationTokenRepository,
)

__all__ = [
    "TenantIsolationError",
    "DocumentNotFoundError",
    "DocumentConflictError",
    "TenantScopedRepository",
    "PlatformScopedRepository",
    "TenantRepository",
    "ConversationRepository",
    "UsageRepository",
    "CustomerProfileRepository",
    "KnowledgeBaseRepository",
    "MemoryVectorRepository",
    "PreferencesRepository",
    "TeamMemberRepository",
    "PlatformConfigRepository",
    "AuditLogRepository",
    "SLASnapshotRepository",
    "VerificationTokenRepository",
]
