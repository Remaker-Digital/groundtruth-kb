"""Session init-binding service package.

Public surface re-exported from :mod:`groundtruth_kb.session.attestation.service`.
"""

from groundtruth_kb.session.attestation.service import (
    VALID_ROLES,
    Binding,
    RoleAttestationError,
    bind_exact_init,
    binding_for_context,
)

__all__ = [
    "VALID_ROLES",
    "Binding",
    "RoleAttestationError",
    "bind_exact_init",
    "binding_for_context",
]
