"""Separate publication-blocking registry conditions from audit-only ones.

``gt registry validate`` returns a single ``valid: false`` verdict that folds two
independent conditions together: *parity*, which gates bridge publication, and
*membership*, which does not. Nothing in that output distinguishes them, so an
``INVALID`` result cannot be read as "publication is blocked".

The actual publication gate is
:func:`groundtruth_kb.project.registry_control_plane._load_snapshot_unlocked`,
reached from ``mint_bridge_publication_capability``. It raises on exactly two
conditions -- a canonical-vs-packaged byte mismatch and a projection-parity
mismatch -- and never consults membership. The journal check
``_ensure_no_nonterminal_journal`` runs immediately before it inside the mint
lock and is therefore also publication-blocking.

This module supplies the missing canonical reader for the question consumers
actually ask -- *is bridge publication currently blocked?* -- and a classifier
that partitions ``validate_registry`` error codes by whether they gate
publication.

The principle is already settled for the gate itself: ``registry_currentness``
states in its own docstring that it is "audit state, not membership authority",
and the WI-5933 change removed currentness from the publication path for that
reason. This module applies the same separation to the diagnostic surface.

Authority: ``GOV-PLATFORM-SOT-REGISTRY-001``,
``GOV-SOURCE-OF-TRUTH-FRESHNESS-001``, ``GOV-FILE-BRIDGE-AUTHORITY-001``,
``GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001``. Work item ``WI-6177``; approved at
``bridge/gtkb-wi6177-registry-publication-diagnostic-classification-002.md``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from groundtruth_kb.project import registry_control_plane as _rcp

__all__ = [
    "AUDIT_ONLY_ERROR_CODES",
    "PUBLICATION_BLOCKING_ERROR_CODES",
    "ErrorClassification",
    "PublicationGateState",
    "classify_validate_errors",
    "publication_gate_state",
]

#: Error codes emitted by ``validate_registry`` that correspond to conditions the
#: bridge publication gate actually checks. ``RegistryProjectionMismatch`` and
#: ``RegistryControlPlaneError`` are the two exception type names
#: ``_load_snapshot_unlocked`` raises; ``inspect_registry`` surfaces a failed
#: snapshot load as ``error = type(exc).__name__``.
#: ``RegistryTransactionInProgress`` comes from the non-terminal journal check
#: that runs immediately before the snapshot load inside the mint lock and is
#: also the exact code returned by :func:`publication_gate_state`.
#: ``registry_not_coherent`` is the generic fallback for a coherence failure and
#: is treated as blocking because a snapshot that will not load cannot mint a
#: publication capability.
#:
#: The membership of this set is asserted against the gate source by
#: ``test_blocking_error_set_matches_gate_source``; do not edit it without
#: re-running that test.
PUBLICATION_BLOCKING_ERROR_CODES: frozenset[str] = frozenset(
    {
        "RegistryProjectionMismatch",
        "RegistryControlPlaneError",
        "RegistryTransactionInProgress",
        "registry_not_coherent",
    }
)

#: Error codes emitted by ``validate_registry`` that describe audit state the
#: publication gate never reads. An ``INVALID`` verdict consisting only of these
#: does not block bridge publication.
AUDIT_ONLY_ERROR_CODES: frozenset[str] = frozenset(
    {
        "registry_identity_failure",
        "registry_membership_incomplete",
    }
)


@dataclass(frozen=True)
class PublicationGateState:
    """Result of probing the real bridge publication gate.

    ``publication_blocking`` answers the operational question directly. It is
    ``True`` only when a condition the gate itself checks is currently failing.
    """

    publication_blocking: bool
    blocking_code: str | None = None
    blocking_reason: str | None = None
    checks: Mapping[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "publication_blocking": self.publication_blocking,
            "blocking_code": self.blocking_code,
            "blocking_reason": self.blocking_reason,
            "checks": dict(self.checks),
        }


@dataclass(frozen=True)
class ErrorClassification:
    """Partition of ``validate_registry`` error codes by publication impact."""

    publication_blocking: tuple[str, ...] = ()
    audit_only: tuple[str, ...] = ()
    unclassified: tuple[str, ...] = ()

    @property
    def blocks_publication(self) -> bool:
        """True when at least one error corresponds to a real gate condition.

        Unclassified codes are treated conservatively as blocking: an unknown
        code may be a newly added gate condition, and under-reporting a blocker
        is the more dangerous error.
        """
        return bool(self.publication_blocking or self.unclassified)

    def to_dict(self) -> dict[str, object]:
        return {
            "publication_blocking": list(self.publication_blocking),
            "audit_only": list(self.audit_only),
            "unclassified": list(self.unclassified),
            "blocks_publication": self.blocks_publication,
        }


def classify_validate_errors(errors: Iterable[str]) -> ErrorClassification:
    """Partition ``validate_registry`` error codes by publication impact.

    Pure: no filesystem, database, or network access. Order within each bucket
    follows first appearance in ``errors``; duplicates are collapsed.
    """
    blocking: list[str] = []
    audit: list[str] = []
    unknown: list[str] = []
    for raw in errors:
        code = str(raw)
        if code in PUBLICATION_BLOCKING_ERROR_CODES:
            bucket = blocking
        elif code in AUDIT_ONLY_ERROR_CODES:
            bucket = audit
        else:
            bucket = unknown
        if code not in bucket:
            bucket.append(code)
    return ErrorClassification(
        publication_blocking=tuple(blocking),
        audit_only=tuple(audit),
        unclassified=tuple(unknown),
    )


def publication_gate_state(
    *,
    project_root: Path | None = None,
    registry_path: Path | None = None,
    packaged_registry_path: Path | None = None,
    db_path: Path | None = None,
) -> PublicationGateState:
    """Probe the real bridge publication gate without side effects.

    Runs the same two checks ``mint_bridge_publication_capability`` performs
    before it does anything observable: the non-terminal journal check and the
    snapshot load (coherence plus projection parity). Neither writes, and this
    function deliberately does not acquire the registry lock -- it is a
    diagnostic read, not a publication attempt.

    Calling the gate's own functions rather than reimplementing their logic is
    intentional: it makes the probe track the gate automatically. The companion
    anti-drift test asserts the classification constants still match the gate
    source.
    """
    paths = _rcp.RegistryPaths.resolve(
        project_root=project_root,
        registry_path=registry_path,
        packaged_registry_path=packaged_registry_path,
        db_path=db_path,
    )
    checks: dict[str, str] = {}

    try:
        _rcp._ensure_no_nonterminal_journal(paths.db_path)
    except Exception as exc:  # noqa: BLE001 - probe reports typed failures
        checks["nonterminal_journal"] = "fail"
        return PublicationGateState(
            publication_blocking=True,
            blocking_code=type(exc).__name__,
            blocking_reason=str(exc),
            checks=checks,
        )
    checks["nonterminal_journal"] = "pass"

    try:
        _rcp._load_snapshot_unlocked(paths)
    except Exception as exc:  # noqa: BLE001 - probe reports typed failures
        checks["snapshot_load"] = "fail"
        return PublicationGateState(
            publication_blocking=True,
            blocking_code=type(exc).__name__,
            blocking_reason=str(exc),
            checks=checks,
        )
    checks["snapshot_load"] = "pass"

    return PublicationGateState(publication_blocking=False, checks=checks)
