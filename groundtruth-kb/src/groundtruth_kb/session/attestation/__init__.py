"""Session role-attestation service package (Slice 1).

Public surface re-exported from :mod:`groundtruth_kb.session.attestation.service`.
"""

from groundtruth_kb.session.attestation.service import (
    VALID_ROLES,
    Attestation,
    Binding,
    RoleAttestationError,
    attest_role_change,
    bind_exact_init,
    binding_for_context,
    resolve_effective_role,
    resolve_effective_role_for_context,
)

__all__ = [
    "Attestation",
    "Binding",
    "RoleAttestationError",
    "VALID_ROLES",
    "attest_role_change",
    "bind_exact_init",
    "binding_for_context",
    "resolve_effective_role",
    "resolve_effective_role_for_context",
]
