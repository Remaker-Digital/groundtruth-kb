# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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

# Re-export everything from the repositories package.
# SYNC NOTICE (SPEC-1627): This list MUST mirror repositories/__init__.py __all__.
# When adding a new repository class, add it to BOTH files.
from src.multi_tenant.repositories import (  # noqa: F401
    AgentSkillBindingRepository,
    AlertHistoryRepository,
    AlertRuleRepository,
    AuditLogRepository,
    ConversationRepository,
    CustomerProfileRepository,
    DocumentConflictError,
    DocumentNotFoundError,
    DomainIndexRepository,
    IncidentRepository,
    KnowledgeBaseRepository,
    MemoryVectorRepository,
    PlatformAdminRepository,
    PlatformConfigRepository,
    PlatformScopedRepository,
    PreferencesRepository,
    SLASnapshotRepository,
    TeamMemberRepository,
    TenantAgentOverlayRepository,
    TenantIsolationError,
    TenantRepository,
    TenantScopedRepository,
    UsageRepository,
    VerificationTokenRepository,
)

__all__ = [
    # Exceptions
    "TenantIsolationError",
    "DocumentNotFoundError",
    "DocumentConflictError",
    # Base classes
    "TenantScopedRepository",
    "PlatformScopedRepository",
    # Tenant-scoped repositories
    "TenantRepository",
    "ConversationRepository",
    "UsageRepository",
    "CustomerProfileRepository",
    "KnowledgeBaseRepository",
    "MemoryVectorRepository",
    "PreferencesRepository",
    "TeamMemberRepository",
    # Platform-scoped repositories
    "PlatformConfigRepository",
    "AuditLogRepository",
    "SLASnapshotRepository",
    "VerificationTokenRepository",
    "IncidentRepository",
    "AlertRuleRepository",
    "AlertHistoryRepository",
    "PlatformAdminRepository",
    "DomainIndexRepository",
    "TenantAgentOverlayRepository",
    "AgentSkillBindingRepository",
]
