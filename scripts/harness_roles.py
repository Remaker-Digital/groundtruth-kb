"""Single source of truth for GT-KB harness role assignment.

IP-8 of bridge/gtkb-single-harness-bridge-dispatcher-001-013.md (Codex GO at
-014) migrates this module from scalar role-string semantics to role-set
semantics. The role wire form in ``harness-state/harness-registry.json`` is a
JSON list of role tokens (the wire representation of a role set); the
in-process form is ``frozenset[str]``. Legacy scalar values are accepted on
READ and upgraded to list form on first WRITE.

Authority: ADR-SINGLE-HARNESS-OPERATING-MODE-001 (Path 2 atomic migration);
``.claude/rules/operating-role.md`` § Role Set Schema (Active Authority).
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from scripts.harness_identity import (
        DEFAULT_HARNESS_IDS as _DEFAULT_HARNESS_IDS,
    )
    from scripts.harness_identity import (
        normalize_harness_id,
        normalize_harness_name,
    )
    from scripts.harness_identity import (
        resolved_harness_id as _resolved_persistent_harness_id,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from harness_identity import (  # type: ignore[no-redef]
        DEFAULT_HARNESS_IDS as _DEFAULT_HARNESS_IDS,
    )
    from harness_identity import (
        normalize_harness_id,
        normalize_harness_name,
    )
    from harness_identity import (
        resolved_harness_id as _resolved_persistent_harness_id,
    )

try:
    from scripts.harness_projection_reader import load_harness_projection
except ImportError:  # pragma: no cover - direct script execution path
    from harness_projection_reader import (  # type: ignore[no-redef]
        load_harness_projection,
    )

ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
# Compatibility/provenance value (per
# .claude/rules/acting-prime-builder.md § Compatibility/Provenance
# Classification). Accepted on READ; rejected on SET.
ROLE_ACTING_PRIME_BUILDER = "acting-prime-builder"

# READ vocabulary includes the legacy compatibility/provenance value so older
# registry projection records continue to load without error.
VALID_ROLES_FOR_READ = frozenset(
    {
        ROLE_PRIME_BUILDER,
        ROLE_LOYAL_OPPOSITION,
        ROLE_ACTING_PRIME_BUILDER,
    }
)

# WRITE vocabulary excludes the legacy compatibility/provenance value; only
# ``prime-builder`` and ``loyal-opposition`` are valid SET targets. Per
# the Acting-Prime Compatibility Contract, ``acting-prime-builder`` is
# READ-accepted but SET-rejected.
VALID_ROLES_FOR_WRITE = frozenset({ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION})

# Backward-compat: callers that previously imported ``VALID_ROLES`` get the
# READ vocabulary (the strictly-larger set). New callers should reference
# ``VALID_ROLES_FOR_READ`` or ``VALID_ROLES_FOR_WRITE`` explicitly.
VALID_ROLES = VALID_ROLES_FOR_READ

ROLE_ASSIGNMENTS_RELATIVE_PATH = Path("harness-state") / "harness-registry.json"
DEFAULT_HARNESS_IDS = _DEFAULT_HARNESS_IDS
OLLAMA_HARNESS_ID = "D"
OLLAMA_ROLE_PROMOTION_PREREQUISITE_BRIDGES = (
    "gtkb-ollama-integration-phase-2-routing",
    "gtkb-ollama-integration-phase-2-adapters",
    "gtkb-ollama-integration-phase-2-dispatch",
)
BRIDGE_VERIFIED_STATUS = "VERIFIED"
OLLAMA_PHASE2_PROJECT_ID = "PROJECT-GTKB-OLLAMA-INTEGRATION"
OLLAMA_PHASE2_AUTHORIZATION_ID = "PAUTH-PROJECT-GTKB-OLLAMA-INTEGRATION-OLLAMA-INTEGRATION-PHASE-2-PLUS-COMPLETION"
OLLAMA_PHASE2_CLOSURE_WORK_ITEMS = ("WI-4379", "WI-4380", "WI-4381", "WI-4382")
OLLAMA_PHASE2_MEMORY_MARKER = "<!-- OLLAMA-PHASE-2-CLOSURE -->"
OLLAMA_PHASE2_COMPLETION_EVIDENCE = (
    "Ollama Phase 2+ closure after VERIFIED routing, adapter, and dispatch child bridges "
    "plus successful harness D role promotion."
)
WORK_ITEM_TERMINAL_RESOLUTION_STATUSES = {
    "verified",
    "resolved",
    "retired",
    "wont_fix",
    "not_a_defect",
}
PROJECT_TERMINAL_STATUSES = {"completed", "retired", "cancelled"}


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Role-set helper API (IP-8 of gtkb-single-harness-bridge-dispatcher-001).
# ---------------------------------------------------------------------------


def _normalize_role_field(raw: Any) -> frozenset[str]:
    """Normalize a role field into a ``frozenset[str]``.

    Accepts:

    - ``None`` or empty string -> ``frozenset()``.
    - Scalar role string (legacy) -> singleton frozenset.
    - List/tuple/set/frozenset of role strings -> frozenset of valid tokens.

    Only tokens in ``VALID_ROLES_FOR_READ`` survive normalization. Unknown
    tokens are silently dropped (caller-side validation policy is to treat
    an empty result as "no recognized role").
    """
    if raw is None or raw == "":
        return frozenset()
    if isinstance(raw, str):
        normalized = raw.strip().lower()
        return frozenset({normalized}) if normalized in VALID_ROLES_FOR_READ else frozenset()
    if isinstance(raw, (list, tuple, set, frozenset)):
        tokens = (str(r).strip().lower() for r in raw if r)
        return frozenset(tok for tok in tokens if tok in VALID_ROLES_FOR_READ)
    return frozenset()


def _role_set_to_json(role_set: Iterable[str]) -> list[str]:
    """Serialize a role set into a JSON-canonical sorted list.

    The wire form always uses sorted-list order so two role records that
    represent the same role set serialize identically (stable hashing,
    drift detection).
    """
    return sorted(frozenset(role_set))


def is_prime_builder(record: dict[str, Any]) -> bool:
    """True iff this record's durable role set carries Prime-Builder authority.

    Per the Acting-Prime Compatibility Contract, ``acting-prime-builder`` in
    the role set ALSO counts as Prime-equivalent for attribution purposes
    (READ-side compatibility; SET-side is separately gated).
    """
    role_set = _normalize_role_field(record.get("role"))
    return ROLE_PRIME_BUILDER in role_set or ROLE_ACTING_PRIME_BUILDER in role_set


def is_loyal_opposition(record: dict[str, Any]) -> bool:
    """True iff this record's durable role set carries Loyal-Opposition authority."""
    return ROLE_LOYAL_OPPOSITION in _normalize_role_field(record.get("role"))


def primary_role(record: dict[str, Any]) -> str:
    """Return the primary role string for a record (Prime-first ordering).

    Used by call sites that expect a scalar role string for display or
    backward-compat. When the record's role set is multi-element, Prime
    takes precedence. When the record's role set is empty, returns
    ``ROLE_LOYAL_OPPOSITION`` (the default-on-bootstrap value).

    ``acting-prime-builder`` returns ``ROLE_PRIME_BUILDER`` for primary-role
    display per the Compatibility/Provenance Classification (the harness's
    primary effective role is still Prime-equivalent for attribution).
    """
    role_set = _normalize_role_field(record.get("role"))
    if ROLE_PRIME_BUILDER in role_set or ROLE_ACTING_PRIME_BUILDER in role_set:
        return ROLE_PRIME_BUILDER
    if ROLE_LOYAL_OPPOSITION in role_set:
        return ROLE_LOYAL_OPPOSITION
    return ROLE_LOYAL_OPPOSITION


def resolved_harness_id(
    project_root: Path | None = None,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
) -> str | None:
    return _resolved_persistent_harness_id(
        project_root,
        harness_id=harness_id,
        harness_name=harness_name,
        bootstrap_missing=True,
    )


def role_assignments_path(project_root: Path, override: Path | None = None) -> Path:
    if override is not None:
        return override.expanduser().resolve()
    env_override = os.environ.get("GTKB_ROLE_ASSIGNMENTS_PATH")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return project_root.resolve() / ROLE_ASSIGNMENTS_RELATIVE_PATH


def _empty_document(project_root: Path) -> dict[str, Any]:
    _ = project_root
    return {
        "schema_version": 1,
        "source_of_truth": "GT-KB harness role assignments",
        "description": (
            "Maps durable harness installation IDs to operating roles. "
            "Harness records are projected from harness-state/harness-registry.json. "
            "Role field is a JSON list (the wire representation of a role set) "
            "drawn from {prime-builder, loyal-opposition}. Legacy scalar values "
            "are accepted on READ and upgraded to list form on first WRITE."
        ),
        "updated_at": _now_iso(),
        "harnesses": {},
    }


def _normalize_document(raw: Any, project_root: Path) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    document = _empty_document(project_root)
    document.update({key: value for key, value in raw.items() if key != "harnesses"})
    harnesses = raw.get("harnesses")
    normalized_harnesses: dict[str, dict[str, Any]] = {}
    if isinstance(harnesses, dict):
        for raw_id, raw_record in harnesses.items():
            harness_id = normalize_harness_id(str(raw_id))
            if not harness_id or not isinstance(raw_record, dict):
                continue
            role_set = _normalize_role_field(raw_record.get("role"))
            if not role_set:
                # Record has no recognized role; skip rather than infer.
                continue
            normalized_harnesses[harness_id] = dict(raw_record)
            normalized_harnesses[harness_id]["role"] = _role_set_to_json(role_set)
    if normalized_harnesses:
        document["harnesses"] = normalized_harnesses
    return document


def load_role_assignments(project_root: Path, assignment_path: Path | None = None) -> dict[str, Any]:
    """Load harness role assignments from the registry projection (WI-3342 IP-3).

    Migrated from reading the retired standalone role mirror directly to
    reading the DB-backed registry projection
    (``harness-state/harness-registry.json``) via
    ``scripts/harness_projection_reader.load_harness_projection``. The
    ``assignment_path`` parameter is retained for signature compatibility
    (positional callers such as ``scripts/workstream_focus.py``); readers
    resolve role state from the projection. Fail-soft: a missing or malformed
    projection yields an empty document, never an exception.
    """
    _ = assignment_path  # retained for signature + writer-path compatibility
    document = _empty_document(project_root)
    projection = load_harness_projection(project_root)
    harnesses: dict[str, dict[str, Any]] = {}
    for record in projection.get("harnesses", []):
        if not isinstance(record, dict):
            continue
        if record.get("status") != "active":
            continue
        harness_id = normalize_harness_id(str(record.get("id") or ""))
        if not harness_id:
            continue
        role_set = _normalize_role_field(record.get("role"))
        if not role_set:
            continue
        normalized_record = dict(record)
        normalized_record["role"] = _role_set_to_json(role_set)
        harnesses[harness_id] = normalized_record
    document["harnesses"] = harnesses
    return document


def write_role_assignments(project_root: Path, document: dict[str, Any], assignment_path: Path | None = None) -> Path:
    path = role_assignments_path(project_root, assignment_path)
    _mirror_role_assignments_to_registry(project_root, document)
    return path


def _decode_harness_json_field(raw: Any) -> Any:
    """Decode a harnesses-table JSON-text column value (role / invocation_surfaces).

    ``KnowledgeDB.get_harness`` returns these columns as raw JSON text (or
    ``None``); decoding is required before round-tripping through
    ``insert_harness``, which JSON-encodes its inputs."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return raw


def _mirror_role_assignments_to_registry(project_root: Path, document: dict[str, Any]) -> None:
    """Write the role assignments to the DB ``harnesses`` registry table and
    regenerate the hot-path projection.

    WI-3342 IP-5: this is the AUTHORITATIVE role write. The transitional
    standalone mirror write was removed, so the DB-backed registry and its
    projection are the sole authoritative role surface.

    For each harness whose role set differs from its current DB row, an
    append-only ``insert_harness`` version carries the new role (every other
    field forwarded from the current row). A harness with no current DB row is
    skipped — first-version creation belongs to the registry seed / new-harness
    registration flow, not this update mirror.

    SessionStart-safe: this module is stdlib-only, so the ``groundtruth_kb``
    import is function-local. A missing ``groundtruth.db`` (e.g. a DB-less test
    fixture) or an unavailable ``groundtruth_kb`` package is a graceful no-op;
    any other DB error is raised, so a registry-write failure surfaces rather
    than silently losing the role write."""
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return
    try:
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.harness_projection import generate_harness_projection
    except Exception:
        return
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, dict):
        return
    try:
        db = KnowledgeDB(db_path=db_path)
        changed = False
        for harness_id, record in harnesses.items():
            if not isinstance(record, dict):
                continue
            new_role = sorted(_normalize_role_field(record.get("role")))
            current = db.get_harness(str(harness_id))
            if current is None:
                continue
            current_role = sorted(_normalize_role_field(_decode_harness_json_field(current.get("role"))))
            if current_role == new_role:
                continue
            db.insert_harness(
                id=str(harness_id),
                harness_name=str(current.get("harness_name") or harness_id),
                harness_type=str(current.get("harness_type") or harness_id),
                role=new_role,
                changed_by="harness-role-write",
                change_reason="WI-3342 harness role write",
                status=str(current.get("status") or "registered"),
                reviewer_precedence=current.get("reviewer_precedence"),
                invocation_surfaces=_decode_harness_json_field(current.get("invocation_surfaces")),
                capabilities_ref=current.get("capabilities_ref"),
            )
            changed = True
        if changed:
            generate_harness_projection(db, project_root)
    except Exception as exc:
        # WI-3342 IP-5: the DB-backed registry is the sole authoritative role
        # surface, so a registry-write failure must surface rather than
        # silently lose the role write.
        raise RuntimeError(f"harness registry role write failed: {exc}") from exc


def _ensure_record(
    document: dict[str, Any],
    harness_id: str,
    *,
    harness_name: str | None = None,
) -> dict[str, Any]:
    harnesses = document.setdefault("harnesses", {})
    record = harnesses.setdefault(harness_id, {})
    normalized_name = normalize_harness_name(harness_name)
    if normalized_name:
        record.setdefault("harness_type", normalized_name)
    if "role" not in record:
        record["role"] = _role_set_to_json({ROLE_LOYAL_OPPOSITION})
    return record


def current_prime_ids(document: dict[str, Any]) -> list[str]:
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, dict):
        return []
    return [
        str(harness_id)
        for harness_id, record in harnesses.items()
        if isinstance(record, dict) and is_prime_builder(record)
    ]


def _bridge_latest_statuses(project_root: Path, bridge_ids: Iterable[str]) -> dict[str, dict[str, str | None]]:
    wanted = {str(bridge_id) for bridge_id in bridge_ids}
    statuses: dict[str, dict[str, str | None]] = {
        bridge_id: {"status": None, "file": None} for bridge_id in sorted(wanted)
    }
    index_path = project_root / "bridge" / "INDEX.md"
    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return statuses

    current: str | None = None
    for raw_line in lines:
        line = raw_line.strip()
        if line.startswith("Document: "):
            current = line.removeprefix("Document: ").strip()
            continue
        if current not in wanted or statuses[current]["status"] is not None:
            continue
        if ":" not in line:
            continue
        status, path = line.split(":", 1)
        if path.strip().startswith("bridge/"):
            statuses[current] = {"status": status.strip(), "file": path.strip()}
    return statuses


def ollama_role_promotion_prerequisites(project_root: Path) -> dict[str, Any]:
    """Return the bridge-evidence gate for Ollama role promotion.

    Harness D may only be promoted after the routing, adapter, and dispatch
    child threads independently reach VERIFIED. This helper reads the live
    bridge index and returns a report-friendly structure without mutating
    state.
    """

    statuses = _bridge_latest_statuses(project_root, OLLAMA_ROLE_PROMOTION_PREREQUISITE_BRIDGES)
    missing = [bridge_id for bridge_id, row in statuses.items() if row.get("status") != BRIDGE_VERIFIED_STATUS]
    return {
        "all_verified": not missing,
        "required": list(OLLAMA_ROLE_PROMOTION_PREREQUISITE_BRIDGES),
        "latest": statuses,
        "missing_verified": missing,
    }


def _evaluate_ollama_dispatch_readiness(
    project_root: Path,
    *,
    require_daemon: bool,
) -> dict[str, Any]:
    try:
        from scripts.verify_ollama_dispatch import evaluate_dispatch_readiness
    except ImportError:  # pragma: no cover - direct script execution path
        from verify_ollama_dispatch import evaluate_dispatch_readiness  # type: ignore[no-redef]

    return evaluate_dispatch_readiness(
        project_root,
        recipient=OLLAMA_HARNESS_ID,
        require_daemon=require_daemon,
    )


def evaluate_ollama_role_promotion(
    project_root: Path,
    *,
    require_daemon: bool = True,
    readiness_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate whether harness D is eligible for durable role promotion.

    The gate is intentionally stricter than bridge evidence alone: VERIFIED
    child threads prove the implementation slices landed, while dispatch
    readiness proves the local harness can actually receive headless work.
    Missing readiness therefore refuses promotion before any registry write.
    """

    root = project_root.resolve()
    prerequisites = ollama_role_promotion_prerequisites(root)
    readiness = (
        readiness_result
        if readiness_result is not None
        else _evaluate_ollama_dispatch_readiness(root, require_daemon=require_daemon)
    )
    projection = load_harness_projection(root)
    ollama_record = next(
        (
            record
            for record in projection.get("harnesses", [])
            if isinstance(record, dict) and str(record.get("id") or "") == OLLAMA_HARNESS_ID
        ),
        None,
    )
    registry_ready = bool(
        ollama_record
        and ollama_record.get("harness_name") == "ollama"
        and ollama_record.get("harness_type") == "ollama"
        and ollama_record.get("status") in {"registered", "suspended", "active"}
    )
    blocking_reasons: list[str] = []
    if not prerequisites["all_verified"]:
        blocking_reasons.append("missing_verified_child_bridge")
    if not registry_ready:
        blocking_reasons.append("ollama_registry_record_not_promotable")
    if not bool(readiness.get("ready")):
        blocking_reasons.append("ollama_dispatch_not_ready")
    return {
        "ready": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
        "prerequisites": prerequisites,
        "dispatch_readiness": readiness,
        "registry_record": ollama_record,
    }


def _ollama_role_promotion_rollback_commands(role: str) -> list[str]:
    return [
        "gt harness set-role --harness <previous-active-harness> --role <previous-role> --reason <rollback-reason>",
        f"gt harness suspend --harness {OLLAMA_HARNESS_ID} --cause non-operating-detected --reason <rollback-reason>",
        f"gt harness set-role --harness <active-counterpart> --role {role} --reason <rollback-reason>",
    ]


def _validate_role_switch_preconditions(project_root: Path, requested_role: str) -> None:
    """Run canonical role-switch validators before any Ollama activation write."""

    try:
        from groundtruth_kb.mode_switch.transaction import TransactionValidationError
        from groundtruth_kb.mode_switch.validation import (
            validate_bridge_artifact,
            validate_role_artifact,
            validate_session_state_artifact,
        )
    except Exception as exc:  # pragma: no cover - import environment guard
        raise RuntimeError(f"cannot import canonical role-switch validators: {exc}") from exc

    for validation_result in (
        validate_role_artifact(project_root),
        validate_bridge_artifact(project_root),
        validate_session_state_artifact(project_root),
    ):
        if not validation_result.is_valid:
            raise TransactionValidationError(
                f"{validation_result.axis} artifact validation failed: {'; '.join(validation_result.errors)}",
                axis=validation_result.axis,
                errors=validation_result.errors,
            )
    if requested_role not in VALID_ROLES_FOR_WRITE:
        raise TransactionValidationError(
            f"requested role {requested_role!r} not in {sorted(VALID_ROLES_FOR_WRITE)}",
            axis="role",
        )


def _restore_ollama_harness_record(
    db: Any,
    project_root: Path,
    prior_record: dict[str, Any],
    *,
    changed_by: str,
    change_reason: str,
    generate_harness_projection: Any,
) -> None:
    prior_role = _decode_harness_json_field(prior_record.get("role"))
    retained_role = prior_role if isinstance(prior_role, list) else []
    db.insert_harness(
        id=OLLAMA_HARNESS_ID,
        harness_name=str(prior_record.get("harness_name") or "ollama"),
        harness_type=str(prior_record.get("harness_type") or "ollama"),
        role=retained_role,
        changed_by=changed_by,
        change_reason=f"{change_reason} [restore after failed promotion]",
        status=str(prior_record.get("status") or "registered"),
        reviewer_precedence=prior_record.get("reviewer_precedence"),
        invocation_surfaces=_decode_harness_json_field(prior_record.get("invocation_surfaces")),
        capabilities_ref=prior_record.get("capabilities_ref"),
    )
    generate_harness_projection(db, project_root)


def apply_ollama_role_promotion(
    project_root: Path,
    role: str = ROLE_LOYAL_OPPOSITION,
    *,
    dry_run: bool = True,
    require_daemon: bool = True,
    readiness_result: dict[str, Any] | None = None,
    changed_by: str = "codex-prime-builder",
    change_reason: str = "WI-4382 governed Ollama role promotion",
) -> dict[str, Any]:
    """Promote harness D only after child bridge and readiness gates pass.

    ``dry_run=True`` is report-friendly and mutation-free. ``dry_run=False``
    activates harness D when needed, then delegates the role assignment to the
    canonical mode-switch transaction so durable role authority remains the
    DB-backed harness registry and generated projection.
    """

    requested_role = _set_role_validate(role)
    evaluation = evaluate_ollama_role_promotion(
        project_root,
        require_daemon=require_daemon,
        readiness_result=readiness_result,
    )
    result: dict[str, Any] = {
        "applied": False,
        "would_apply": bool(evaluation["ready"]),
        "dry_run": dry_run,
        "requested_role": requested_role,
        "evaluation": evaluation,
        "rollback_commands": _ollama_role_promotion_rollback_commands(requested_role),
    }
    if not evaluation["ready"]:
        result["reason"] = "promotion gates failed"
        return result
    if dry_run:
        result["reason"] = "dry run"
        return result

    try:
        from groundtruth_kb import harness_ops
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.harness_projection import generate_harness_projection
        from groundtruth_kb.mode_switch.invariants import verify_active_role_partition
        from groundtruth_kb.mode_switch.transaction import apply_role_switch
    except Exception as exc:  # pragma: no cover - import environment guard
        raise RuntimeError(f"cannot import canonical harness promotion writers: {exc}") from exc

    root = project_root.resolve()
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    current = db.get_harness(OLLAMA_HARNESS_ID)
    if current is None:
        result["reason"] = "unknown Ollama harness"
        result["would_apply"] = False
        return result

    prior_status = str(current.get("status") or "")
    _validate_role_switch_preconditions(root, requested_role)
    activation_applied = False
    try:
        if prior_status != "active":
            harness_ops.transition_harness(
                db,
                OLLAMA_HARNESS_ID,
                "active",
                changed_by=changed_by,
                change_reason=f"{change_reason} [activate harness D]",
            )
            activation_applied = True
            generate_harness_projection(db, root)

        transaction = apply_role_switch(
            root,
            OLLAMA_HARNESS_ID,
            requested_role,
            change_reason=f"{change_reason} [assign {requested_role}]",
        )
        partition = verify_active_role_partition(root)
    except Exception:
        if activation_applied:
            _restore_ollama_harness_record(
                db,
                root,
                current,
                changed_by=changed_by,
                change_reason=change_reason,
                generate_harness_projection=generate_harness_projection,
            )
        raise
    result.update(
        {
            "applied": True,
            "would_apply": False,
            "reason": "applied",
            "previous_status": prior_status,
            "transaction": {
                "harness_id": transaction.harness_id,
                "previous_role_set": list(transaction.previous_role_set),
                "new_role_set": list(transaction.new_role_set),
                "derived_topology": transaction.derived_topology,
                "audit_record_path": str(transaction.audit_record_path),
            },
            "partition": {
                "prime_builder_id": partition.prime_builder_id,
                "loyal_opposition_id": partition.loyal_opposition_id,
                "active_harness_ids": list(partition.active_harness_ids),
            },
        }
    )
    return result


def _work_item_row_closed(row: dict[str, Any] | None) -> bool:
    if row is None:
        return False
    resolution_status = str(row.get("resolution_status") or "").strip().lower()
    stage = str(row.get("stage") or "").strip().lower()
    return resolution_status in WORK_ITEM_TERMINAL_RESOLUTION_STATUSES and stage == "resolved"


def _ollama_harness_promoted(project_root: Path, requested_role: str) -> bool:
    projection = load_harness_projection(project_root)
    for record in projection.get("harnesses", []):
        if not isinstance(record, dict):
            continue
        if str(record.get("id") or "") != OLLAMA_HARNESS_ID:
            continue
        return record.get("status") == "active" and requested_role in _normalize_role_field(record.get("role"))
    return False


def _phase2_memory_path(project_root: Path) -> Path:
    return project_root / "memory" / "MEMORY.md"


def _phase2_memory_needs_update(project_root: Path) -> bool:
    path = _phase2_memory_path(project_root)
    try:
        return OLLAMA_PHASE2_MEMORY_MARKER not in path.read_text(encoding="utf-8")
    except OSError:
        return True


def _append_ollama_phase2_memory_closure(project_root: Path, *, evidence: str, changed_at: str) -> bool:
    path = _phase2_memory_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        text = "# Agent Red Memory\n\n## Current Status\n\n"
    if OLLAMA_PHASE2_MEMORY_MARKER in text:
        return False

    day = changed_at.split("T", 1)[0]
    entry = (
        f"- **{day} (PROJECT-GTKB-OLLAMA-INTEGRATION Phase 2+ guarded closure):** "
        f"{OLLAMA_PHASE2_MEMORY_MARKER} Phase 2+ successor work items "
        "WI-4379, WI-4380, WI-4381, and WI-4382 resolved after the routing, "
        "adapter, dispatch, and harness D role-promotion gates passed. "
        f"Evidence: {evidence}\n"
    )
    marker = "## Current Status"
    if marker in text:
        before, after = text.split(marker, 1)
        after = after.lstrip("\n")
        text = f"{before}{marker}\n\n{entry}{after}"
    else:
        suffix = "" if text.endswith("\n") else "\n"
        text = f"{text}{suffix}\n## Current Status\n\n{entry}"
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def _project_completion_ready(db: Any, project_id: str) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    project = db.get_project(project_id)
    if project is None:
        return False, ["project_missing"]
    if str(project.get("status") or "").strip().lower() in PROJECT_TERMINAL_STATUSES:
        return False, ["project_already_terminal"]

    active_authorizations = db.list_project_authorizations(project_id, status="active")
    if active_authorizations:
        reasons.append("active_project_authorizations_remain")

    linked_work_items = db.list_project_work_items(project_id)
    if not linked_work_items:
        reasons.append("no_linked_project_work_items")
    elif any(not _work_item_row_closed(row) for row in linked_work_items):
        reasons.append("linked_work_items_not_terminal")

    return not reasons, reasons


def _complete_ollama_phase2_project_if_ready(
    db: Any,
    project_root: Path,
    *,
    changed_by: str,
    change_reason: str,
    changed_at: str,
) -> bool:
    ready, _reasons = _project_completion_ready(db, OLLAMA_PHASE2_PROJECT_ID)
    if not ready:
        return False
    try:
        from groundtruth_kb.project.lifecycle import ProjectLifecycleService
    except Exception as exc:  # pragma: no cover - import environment guard
        raise RuntimeError(f"cannot import project lifecycle service: {exc}") from exc

    _ = project_root
    service = ProjectLifecycleService(db)
    service.update_project(
        OLLAMA_PHASE2_PROJECT_ID,
        changed_by=changed_by,
        change_reason=change_reason,
        status="completed",
        completed_at=changed_at,
    )
    return True


def evaluate_ollama_phase2_closure(
    project_root: Path,
    *,
    role: str = ROLE_LOYAL_OPPOSITION,
) -> dict[str, Any]:
    """Evaluate whether Ollama Phase 2+ closure may mutate project artifacts.

    Closure is intentionally downstream of role promotion: if harness D is not
    active with the requested operating role, this helper refuses work-item,
    project-authorization, project, and memory updates.
    """

    requested_role = _set_role_validate(role)
    root = project_root.resolve()
    prerequisites = ollama_role_promotion_prerequisites(root)
    promoted = _ollama_harness_promoted(root, requested_role)
    memory_update_needed = _phase2_memory_needs_update(root)
    db_path = root / "groundtruth.db"
    blocking_reasons: list[str] = []
    if not prerequisites["all_verified"]:
        blocking_reasons.append("missing_verified_child_bridge")
    if not promoted:
        blocking_reasons.append("ollama_role_not_promoted")
    if not db_path.is_file():
        blocking_reasons.append("groundtruth_db_missing")
        return {
            "ready": False,
            "blocking_reasons": blocking_reasons,
            "requested_role": requested_role,
            "prerequisites": prerequisites,
            "ollama_promoted": promoted,
            "project": None,
            "authorization": None,
            "work_items": {},
            "missing_work_items": list(OLLAMA_PHASE2_CLOSURE_WORK_ITEMS),
            "work_items_requiring_update": [],
            "memory_update_needed": memory_update_needed,
            "project_completion_ready": False,
            "project_completion_deferred_reasons": ["groundtruth_db_missing"],
        }

    try:
        from groundtruth_kb.db import KnowledgeDB
    except Exception as exc:  # pragma: no cover - import environment guard
        blocking_reasons.append("knowledge_db_unavailable")
        return {
            "ready": False,
            "blocking_reasons": blocking_reasons,
            "requested_role": requested_role,
            "prerequisites": prerequisites,
            "ollama_promoted": promoted,
            "project": None,
            "authorization": None,
            "work_items": {},
            "missing_work_items": list(OLLAMA_PHASE2_CLOSURE_WORK_ITEMS),
            "work_items_requiring_update": [],
            "memory_update_needed": memory_update_needed,
            "project_completion_ready": False,
            "project_completion_deferred_reasons": [f"knowledge_db_unavailable: {exc}"],
        }

    db = KnowledgeDB(db_path=db_path)
    project = db.get_project(OLLAMA_PHASE2_PROJECT_ID)
    authorization = db.get_project_authorization(OLLAMA_PHASE2_AUTHORIZATION_ID)
    work_items = {item_id: db.get_work_item(item_id) for item_id in OLLAMA_PHASE2_CLOSURE_WORK_ITEMS}
    missing_work_items = [item_id for item_id, row in work_items.items() if row is None]
    work_items_requiring_update = [
        item_id for item_id, row in work_items.items() if row is not None and not _work_item_row_closed(row)
    ]
    if project is None:
        blocking_reasons.append("phase2_project_missing")
    if authorization is None:
        blocking_reasons.append("phase2_authorization_missing")
    if missing_work_items:
        blocking_reasons.append("phase2_work_items_missing")

    project_completion_ready, project_completion_deferred_reasons = _project_completion_ready(
        db,
        OLLAMA_PHASE2_PROJECT_ID,
    )
    return {
        "ready": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
        "requested_role": requested_role,
        "prerequisites": prerequisites,
        "ollama_promoted": promoted,
        "project": project,
        "authorization": authorization,
        "work_items": work_items,
        "missing_work_items": missing_work_items,
        "work_items_requiring_update": work_items_requiring_update,
        "memory_update_needed": memory_update_needed,
        "project_completion_ready": project_completion_ready,
        "project_completion_deferred_reasons": project_completion_deferred_reasons,
    }


def apply_ollama_phase2_closure(
    project_root: Path,
    *,
    role: str = ROLE_LOYAL_OPPOSITION,
    dry_run: bool = True,
    changed_by: str = "codex-prime-builder",
    change_reason: str = "WI-4382 governed Ollama Phase 2+ closure",
) -> dict[str, Any]:
    """Resolve Ollama Phase 2+ lifecycle artifacts after role promotion."""

    root = project_root.resolve()
    evaluation = evaluate_ollama_phase2_closure(root, role=role)
    result: dict[str, Any] = {
        "applied": False,
        "would_apply": bool(evaluation["ready"]),
        "dry_run": dry_run,
        "evaluation": evaluation,
        "resolved_work_items": [],
        "authorization_completed": False,
        "project_completed": False,
        "memory_updated": False,
        "evidence": OLLAMA_PHASE2_COMPLETION_EVIDENCE,
    }
    if not evaluation["ready"]:
        result["reason"] = "closure gates failed"
        return result
    if dry_run:
        result["reason"] = "dry run"
        return result

    try:
        from groundtruth_kb.db import KnowledgeDB
    except Exception as exc:  # pragma: no cover - import environment guard
        raise RuntimeError(f"cannot import KnowledgeDB: {exc}") from exc

    db = KnowledgeDB(db_path=root / "groundtruth.db")
    changed_at = _now_iso()
    for item_id in evaluation["work_items_requiring_update"]:
        current = db.get_work_item(item_id)
        if current is None:
            continue
        fields: dict[str, Any] = {
            "stage": "resolved",
            "status_detail": "Resolved by guarded Ollama Phase 2+ closure.",
            "completion_evidence": OLLAMA_PHASE2_COMPLETION_EVIDENCE,
        }
        if str(current.get("resolution_status") or "").strip().lower() not in WORK_ITEM_TERMINAL_RESOLUTION_STATUSES:
            fields["resolution_status"] = "resolved"
        db.update_work_item(
            item_id,
            changed_by,
            change_reason,
            owner_approved=True,
            **fields,
        )
        result["resolved_work_items"].append(item_id)

    authorization = db.get_project_authorization(OLLAMA_PHASE2_AUTHORIZATION_ID)
    if authorization is not None and authorization.get("status") == "active":
        db.update_project_authorization(
            OLLAMA_PHASE2_AUTHORIZATION_ID,
            changed_by,
            change_reason,
            status="completed",
        )
        result["authorization_completed"] = True

    result["project_completed"] = _complete_ollama_phase2_project_if_ready(
        db,
        root,
        changed_by=changed_by,
        change_reason=change_reason,
        changed_at=changed_at,
    )
    result["memory_updated"] = _append_ollama_phase2_memory_closure(
        root,
        evidence=OLLAMA_PHASE2_COMPLETION_EVIDENCE,
        changed_at=changed_at,
    )
    result.update({"applied": True, "would_apply": False, "reason": "applied"})
    return result


def role_for_harness(
    project_root: Path,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
    assignment_path: Path | None = None,
    ensure_prime_on_startup: bool = True,
) -> tuple[str, dict[str, Any], Path]:
    """Resolve the primary role string for the given harness.

    Returns ``(primary_role_str, document, path)``. The primary role is
    Prime-first (Prime-equivalent for ``acting-prime-builder``). The
    full role set is available via ``_normalize_role_field(record["role"])``
    in the returned document.

    When ``ensure_prime_on_startup`` is True and no harness in the document
    currently holds Prime, the resolving harness self-corrects to Prime and
    other harnesses are demoted to LO.
    """
    resolved_id = resolved_harness_id(project_root, harness_id=harness_id, harness_name=harness_name)
    path = role_assignments_path(project_root, assignment_path)
    document = load_role_assignments(project_root, assignment_path)
    if resolved_id is None:
        return ROLE_PRIME_BUILDER, document, path

    record = _ensure_record(document, resolved_id, harness_name=harness_name)
    changed = False
    if ensure_prime_on_startup and not current_prime_ids(document):
        for other_id, other_record in document.get("harnesses", {}).items():
            if other_id != resolved_id and isinstance(other_record, dict):
                other_record["role"] = _role_set_to_json({ROLE_LOYAL_OPPOSITION})
        record["role"] = _role_set_to_json({ROLE_PRIME_BUILDER})
        record["assigned_reason"] = "startup-self-correction-no-prime-builder"
        changed = True

    role_set = _normalize_role_field(record.get("role"))
    if not role_set:
        # Defensive: record has no recognized role -> default to Prime.
        record["role"] = _role_set_to_json({ROLE_PRIME_BUILDER})
        role_set = frozenset({ROLE_PRIME_BUILDER})
        changed = True

    primary = primary_role(record)
    if changed or (ensure_prime_on_startup and not path.is_file()):
        document["updated_at"] = _now_iso()
        # WI-3342 IP-5: the transitional standalone mirror write is removed;
        # the registry projection is the authoritative role write.
        _mirror_role_assignments_to_registry(project_root, document)
    return primary, document, path


def _set_role_validate(role: str) -> str:
    """Validate a SET-target role string and return its canonical form.

    Per the Acting-Prime Compatibility Contract, ``acting-prime-builder`` is
    REJECTED on SET; only ``prime-builder`` and ``loyal-opposition`` are
    valid SET targets.
    """
    requested_role = str(role or "").strip().lower()
    if requested_role not in VALID_ROLES_FOR_WRITE:
        if requested_role == ROLE_ACTING_PRIME_BUILDER:
            raise ValueError(
                "acting-prime-builder is a READ-only compatibility/provenance value "
                "and is not a valid SET target. Use prime-builder or loyal-opposition."
            )
        raise ValueError(f"Unsupported next-session role: {role}")
    return requested_role


def set_harness_role(
    project_root: Path,
    role: str,
    *,
    harness_id: str | None = None,
    harness_name: str | None = None,
    assignment_path: Path | None = None,
) -> tuple[str, dict[str, Any], Path]:
    requested_role = _set_role_validate(role)
    try:
        from groundtruth_kb.mode_switch.invariants import RolePartitionViolation, verify_role_document_partition
    except Exception as exc:  # pragma: no cover - import environment guard
        raise RuntimeError(f"cannot import canonical role partition validator: {exc}") from exc

    resolved_id = resolved_harness_id(project_root, harness_id=harness_id, harness_name=harness_name)
    if resolved_id is None:
        raise ValueError("Cannot set harness role without a durable harness ID.")

    projection = load_harness_projection(project_root)
    projection_records = [
        record
        for record in projection.get("harnesses", [])
        if isinstance(record, dict) and normalize_harness_id(str(record.get("id") or ""))
    ]
    document = _empty_document(project_root)
    document["harnesses"] = {
        normalize_harness_id(str(record.get("id") or "")): dict(record) for record in projection_records
    }
    record = document["harnesses"].get(resolved_id)
    if not isinstance(record, dict):
        raise ValueError(f"Cannot set harness role for unknown harness {resolved_id!r}.")
    if record.get("status") == "retired":
        raise ValueError(
            f"Cannot assign {requested_role!r} to harness {resolved_id!r}; "
            "retired harnesses cannot receive role metadata updates."
        )

    record["role"] = _role_set_to_json({requested_role})
    try:
        verify_role_document_partition(document)
    except RolePartitionViolation as exc:
        raise ValueError(str(exc)) from exc

    record["assigned_at"] = _now_iso()
    record["assigned_by"] = "harness-role-command"
    document["updated_at"] = _now_iso()
    # WI-3342 IP-5: the transitional standalone mirror write is removed;
    # _mirror_role_assignments_to_registry below is the authoritative role
    # write. ``path`` is resolved (not written) to preserve the return contract.
    path = role_assignments_path(project_root, assignment_path)
    _mirror_role_assignments_to_registry(project_root, document)
    return requested_role, document, path
