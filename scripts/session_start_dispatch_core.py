"""Shared SessionStart hook dispatch core (harness-neutral).

Single definition of the SessionStart dispatch logic shared by both harness
wrappers (`.claude/hooks/session_start_dispatch.py` and
`.codex/gtkb-hooks/session_start_dispatch.py`). Each wrapper imports this
module, sets its own `HARNESS_NAME` and `OUT_DIR`, and rebinds these functions
onto its own namespace so module-level names resolve against the wrapper. The
logic emits a properly-shaped SessionStart `hookSpecificOutput` envelope,
validates the canonical startup-service freshness contract, and falls back to a
degraded-banner context when the canonical service fails or times out.

Slice D of GTKB-STARTUP-REFRACTOR-001 (WI-4272;
bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-004.md, GO)
extracted this core from the two previously byte-identical wrappers. The drift
gate for the shared primitives lives in
`scripts/check_codex_hook_parity.py::_resolution_table_parity_errors`, which
asserts the primitives here (single source) plus per-wrapper delegation. This is
a behavior-preserving refactor.

IP-4 (bridge/gtkb-canonical-init-keyword-syntax-001-005.md, Codex GO at -008):
canonical init-keyword recognition via `StartupDecision` enum +
``_bridge_dispatch_keyword_check`` per SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 +
DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001. The receiver reads its own durable
role via the registry projection (``harness-state/harness-registry.json``) and
audits set-membership against the keyword mode. Mismatch -> prompt keyword
authorized with an audit log entry to
``.gtkb-state/bridge-poller/dispatch-failures.jsonl``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from uuid import UUID

PROJECT_ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(PROJECT_ROOT))
from scripts._session_init_keyword import (  # noqa: E402
    CANONICAL_INIT_KEYWORD_REGEX,
    match_canonical_init_keyword,
)
from scripts.harness_identity import resolved_harness_id  # noqa: E402
from scripts.harness_projection_reader import load_harness_projection  # noqa: E402
from scripts.windows_subprocess import no_window_subprocess_kwargs, prefer_pythonw_executable  # noqa: E402

# Per-harness configuration. The thin wrappers
# (.claude/hooks/session_start_dispatch.py, .codex/gtkb-hooks/session_start_dispatch.py)
# override HARNESS_NAME and OUT_DIR in their own module namespace and rebind
# these functions onto it. The ``None`` placeholders make a wrapper that forgets
# to override fail fast rather than silently inherit another harness's identity.
HARNESS_NAME = None
OUT_DIR = None
STARTUP_SERVICE = PROJECT_ROOT / "scripts" / "session_self_initialization.py"
STARTUP_FRESHNESS_CONTRACT_VERSION = "gtkb-startup-freshness-v1"
STARTUP_SERVICE_TIMEOUT_ENV = "GTKB_STARTUP_SERVICE_TIMEOUT_SECONDS"
STARTUP_SERVICE_TIMEOUT_SECONDS = 150.0
STARTUP_SERVICE_TIMEOUT_BY_HARNESS = {
    # Claude Code's registered SessionStart hook budget is 60 seconds. Cap the
    # inner startup-service wait so this dispatcher can still emit a fail-soft
    # SessionStart envelope instead of being killed by the outer hook runtime.
    "claude": 55.0,
}
# Deadline guard for live hook budget
# Parity marker for tests: Role: Prime Builder

# IP-4: canonical init-keyword recognition (receiver side).
# Per SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 v3: the shared parser accepts
# ``::init (gtkb|application)`` with optional role mode ``pb|lo``.
_CANONICAL_KEYWORD_RE = CANONICAL_INIT_KEYWORD_REGEX
_BRIDGE_DISPATCH_RUN_ID_ENV = "GTKB_BRIDGE_POLLER_RUN_ID"
_BRIDGE_DISPATCH_KEYWORD_ENV = "GTKB_BRIDGE_DISPATCH_KEYWORD"
_LABEL_TO_CANONICAL_MODE = {
    "prime-builder": "pb",
    "acting-prime-builder": "pb",
    "loyal-opposition": "lo",
}
_MODE_TO_ROLE_PROFILE = {
    "pb": "prime-builder",
    "lo": "loyal-opposition",
}
# Audit log for dispatch keyword / dispatcher role-set mismatches. Shared with the
# trigger's dispatch-failures path so investigators see all dispatch-related
# failures in one location.
DISPATCH_FAILURES_PATH = PROJECT_ROOT / ".gtkb-state" / "bridge-poller" / "dispatch-failures.jsonl"
_SESSION_ENVELOPE_ACTIVITY_ENV = "GTKB_SESSION_ENVELOPE_ACTIVITY"
_DISPATCH_ACTIVITY_ENV = "GTKB_DISPATCH_ACTIVITY"
_SESSION_ENVELOPE_ROLE_ENV = "GTKB_SESSION_ENVELOPE_ROLE"
_NATIVE_PACKET_HOOK_HARNESSES = frozenset({"claude", "codex"})
_CANONICAL_PACKET_ACTIVITIES = frozenset({"ops", "deliberation", "build", "test", "spec", "project"})
_WORKER_ROLES = frozenset({"prime-builder", "loyal-opposition"})
_DISPATCH_ACTIVITY_BY_ROLE_MODE = {
    "pb": "build",
    "lo": "test",
}


class StartupDecision(Enum):
    """IP-4 receiver-side decision enum (per bridge -005 IP-4 enum cleanup).

    Five mutually-exclusive paths cover every combination of run-id env-var,
    canonical-keyword env-var, and own-role-set membership. No two paths
    share return semantics.
    """

    NORMAL_STARTUP = "normal_startup"
    DISPATCH_AUTHORIZED = "dispatch_authorized"
    SPOOF_FALLBACK = "spoof_fallback"
    LEGACY_FALLBACK = "legacy_fallback"
    STRICT_DROP = "strict_drop"


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _monotonic_seconds() -> float:
    return time.monotonic()


def _startup_service_timeout_seconds() -> float:
    raw = os.environ.get(STARTUP_SERVICE_TIMEOUT_ENV)
    if raw is None or not raw.strip():
        return STARTUP_SERVICE_TIMEOUT_SECONDS
    try:
        parsed = float(raw)
    except ValueError:
        return STARTUP_SERVICE_TIMEOUT_SECONDS
    return parsed if parsed > 0 else STARTUP_SERVICE_TIMEOUT_SECONDS


def _startup_service_timeout_seconds_for_harness() -> float:
    configured_timeout = _startup_service_timeout_seconds()
    harness_timeout = STARTUP_SERVICE_TIMEOUT_BY_HARNESS.get(str(HARNESS_NAME or "").strip().lower())
    if harness_timeout is None:
        return configured_timeout
    return min(configured_timeout, harness_timeout)


def _parse_iso8601(value: str | None) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _is_ordered(earlier: str | None, later: str | None) -> bool:
    earlier_dt = _parse_iso8601(earlier)
    later_dt = _parse_iso8601(later)
    if earlier_dt is None or later_dt is None:
        return False
    return earlier_dt <= later_dt


def _purge_previous_diagnostics(*paths: Path) -> None:
    for path in paths:
        try:
            path.unlink()
        except FileNotFoundError:
            continue
        except OSError:
            pass


# Slice 3/WI-4540 split: the legacy single-file session role marker is written
# by the UserPromptSubmit init-keyword path and may be invalidated at
# SessionStart. The transcript-defined interactive role itself persists across
# compaction/resume in the per-session marker/envelope surfaces; only the legacy
# shared cache file is deleted here. The constant is duplicated from
# scripts.workstream_focus._SESSION_ROLE_MARKER_NAME rather than imported, to
# keep the SessionStart hot path stdlib-light; the parity test asserts the two
# paths stay equal.
_SESSION_ROLE_MARKER_NAME = "active-session-role.json"


def _session_role_marker_path(project_root: Path = PROJECT_ROOT) -> Path:
    return project_root / ".claude" / "session" / _SESSION_ROLE_MARKER_NAME


def _invalidate_session_role_marker(project_root: Path = PROJECT_ROOT) -> None:
    """Delete any pre-existing LEGACY single-file session-state role marker
    before SessionStart renders. Fail-soft: a missing marker or an OSError must
    not abort startup.

    WI-4540 note: this continues to unconditionally delete the legacy shared
    single-file marker (``active-session-role.json``). The per-session markers
    (``role-*.json``) — the WI-4540 authority that must survive compaction/resume
    for the current context — are NOT touched here; they are handled by the
    context-id-scoped/freshness sweep in ``_sweep_stale_per_session_role_markers``.
    """
    try:
        _session_role_marker_path(project_root).unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


# WI-4540 (bridge -004): generous freshness window so a contiguous interactive
# context (which can span many hours) keeps its per-session marker alive across
# every SessionStart it triggers (compaction/resume), honoring the
# DELIB-20263212 context-lifetime invariant, while genuinely abandoned markers
# from prior sessions are reclaimed. A transcript-mtime signal is a documented
# follow-on hardening.
_PER_SESSION_ROLE_MARKER_STALE_SECONDS = 24 * 3600


def _per_session_marker_is_fresh(body: dict, reference: datetime, stale_seconds: int) -> bool:
    """Return True when a per-session marker body's ``written_at`` is within the
    freshness window (i.e., a concurrent live session that must be retained)."""
    written_at = body.get("written_at")
    if not isinstance(written_at, str):
        return False
    try:
        parsed = datetime.fromisoformat(written_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return (reference - parsed).total_seconds() <= stale_seconds


def _sweep_stale_per_session_role_markers(
    project_root: Path = PROJECT_ROOT,
    *,
    current_session_id: str | None = None,
    now: datetime | None = None,
    stale_seconds: int = _PER_SESSION_ROLE_MARKER_STALE_SECONDS,
) -> None:
    """Sweep stale WI-4540 per-session role markers at SessionStart; fail-soft.

    Unlike the legacy single-file invalidation, per-session markers
    (``.claude/session/role-*.json``) are NOT deleted unconditionally — that
    would reintroduce the cross-session clobber (WI-4463) the per-session keying
    exists to fix. A marker is RETAINED when it belongs to ``current_session_id``
    OR is younger than ``stale_seconds`` (a concurrent live session), and
    DELETED otherwise. Every step is fail-soft so a SessionStart never aborts.
    """
    try:
        from scripts.gtkb_session_id import PER_SESSION_ROLE_MARKER_GLOB, session_marker_dir
    except ImportError:  # pragma: no cover - direct script execution path
        from gtkb_session_id import PER_SESSION_ROLE_MARKER_GLOB, session_marker_dir  # type: ignore[no-redef]

    session_dir = session_marker_dir(project_root)
    try:
        entries = list(session_dir.glob(PER_SESSION_ROLE_MARKER_GLOB))
    except OSError:
        return
    reference = now or datetime.now(UTC)
    for entry in entries:
        try:
            body = json.loads(entry.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            body = None
        marker_session_id = body.get("session_id") if isinstance(body, dict) else None
        if current_session_id is not None and marker_session_id == current_session_id:
            continue  # the current context's marker — always retained
        if isinstance(body, dict) and _per_session_marker_is_fresh(body, reference, stale_seconds):
            continue  # a concurrent live session's marker — retained
        try:
            entry.unlink()
        except OSError:
            pass


def _persistent_harness_id() -> str:
    harness_id = resolved_harness_id(PROJECT_ROOT, harness_name=HARNESS_NAME)
    if not harness_id:
        raise RuntimeError(f"Could not resolve persistent harness identity for {HARNESS_NAME}")
    return harness_id


def _fallback_context(reason: str) -> str:
    dashboard = "file:///E:/GT-KB/docs/gtkb-dashboard/index.html"
    return "\n".join(
        [
            "# GroundTruth-KB Startup Service Degraded",
            "",
            f"Generated: {_now_iso()}",
            "",
            "The SessionStart hook could not retrieve the programmatic startup payload.",
            f"Reason: {reason}",
            "",
            f"Dashboard: [GroundTruth-KB Project Dashboard]({dashboard})",
            "",
            "Use filesystem reads and the dashboard as the live authority before acting.",
        ]
    )


def _session_start_payload(context: str) -> dict[str, dict[str, str]]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }


def _dispatch_role_mode_from_keyword() -> str | None:
    keyword_match = match_canonical_init_keyword(_read_first_prompt_line() or "")
    return keyword_match.role_mode if keyword_match is not None else None


def _session_envelope_role(role_mode: str | None) -> str:
    raw_role = (os.environ.get(_SESSION_ENVELOPE_ROLE_ENV) or "").strip().lower()
    if raw_role in _WORKER_ROLES:
        return raw_role
    if raw_role in _MODE_TO_ROLE_PROFILE:
        return _MODE_TO_ROLE_PROFILE[raw_role]
    if role_mode in _MODE_TO_ROLE_PROFILE:
        return _MODE_TO_ROLE_PROFILE[role_mode]
    return "prime-builder"


def _session_envelope_activity(role_mode: str | None) -> str | None:
    raw_activity = (
        (os.environ.get(_SESSION_ENVELOPE_ACTIVITY_ENV) or os.environ.get(_DISPATCH_ACTIVITY_ENV) or "").strip().lower()
    )
    if raw_activity in _CANONICAL_PACKET_ACTIVITIES:
        return raw_activity
    if os.environ.get(_BRIDGE_DISPATCH_RUN_ID_ENV):
        return _DISPATCH_ACTIVITY_BY_ROLE_MODE.get(role_mode or "")
    return None


def _compose_session_envelope_packet(
    *,
    packet_kind: str,
    role: str,
    activity: str | None = None,
) -> dict[str, object]:
    from groundtruth_kb.session.packet import compose_packet

    return compose_packet(
        project_root=PROJECT_ROOT,
        packet_kind=packet_kind,
        role=role,
        activity=activity,
    )


def _packet_pointer(packet: dict[str, object]) -> str:
    cache = packet.get("cache")
    if isinstance(cache, dict) and cache.get("cache_path"):
        return str(cache["cache_path"])
    pointers = packet.get("source_pointers")
    if isinstance(pointers, list) and pointers:
        first = pointers[0]
        if isinstance(first, dict) and first.get("path"):
            return str(first["path"])
    return "unavailable"


def _packet_receipt_line(label: str, packet: dict[str, object]) -> str:
    budget = packet.get("budget") if isinstance(packet.get("budget"), dict) else {}
    cache = packet.get("cache") if isinstance(packet.get("cache"), dict) else {}
    status = str(packet.get("status") or "unknown")
    parts = [
        f"- {label}: status={status}",
        f"estimated_tokens={budget.get('estimated_tokens', 'unknown')}",
        f"cap={budget.get('cap_estimated_tokens', 'unknown')}",
        f"pointer={_packet_pointer(packet)}",
        f"cache={cache.get('status', 'unavailable')}",
    ]
    diagnostic = packet.get("diagnostic") if isinstance(packet.get("diagnostic"), dict) else {}
    if diagnostic.get("pointer_only") is True:
        parts.append("pointer_only=true")
    return "; ".join(parts)


def _envelope_packet_receipt(role_mode: str | None = None, activity: str | None = None) -> str:
    role = _session_envelope_role(role_mode)
    selected_activity = activity or _session_envelope_activity(role_mode)
    harness_name = str(HARNESS_NAME or "").strip().lower()
    hook_disposition = (
        "full_sessionstart_packet_injection"
        if harness_name in _NATIVE_PACKET_HOOK_HARNESSES
        else "fallback_receipt_pointer"
    )
    lines = [
        "# GroundTruth-KB Envelope Packet Receipt",
        "",
        "- packet_injection_order: before_activity_specialization",
        f"- hook_disposition: {hook_disposition}",
        f"- role_bootstrap: {role}",
        "- live_state_policy: stable bootstrap packet; live bridge, claim, git, and MemBase state still require fresh canonical reads",
    ]
    if hook_disposition == "fallback_receipt_pointer":
        lines.append("- fallback_is_parity: false")

    try:
        session_packet = _compose_session_envelope_packet(packet_kind="session-envelope", role=role)
        lines.append(_packet_receipt_line("session_packet", session_packet))
    except Exception as exc:  # noqa: BLE001 - SessionStart must remain fail-soft.
        lines.append(f"- session_packet: status=unavailable; reason={type(exc).__name__}")

    if selected_activity:
        try:
            activity_packet = _compose_session_envelope_packet(
                packet_kind="activity-packet",
                activity=selected_activity,
                role=role,
            )
            lines.append(f"- activity: {selected_activity}")
            lines.append(_packet_receipt_line("activity_packet", activity_packet))
        except Exception as exc:  # noqa: BLE001 - SessionStart must remain fail-soft.
            lines.append(
                f"- activity_packet: status=unavailable; activity={selected_activity}; reason={type(exc).__name__}"
            )
    else:
        lines.append("- activity_packet: status=not_requested; pointer=none")
    return "\n".join(lines)


def _with_envelope_packet_receipt(
    context: str,
    *,
    role_mode: str | None = None,
    activity: str | None = None,
) -> str:
    receipt = _envelope_packet_receipt(role_mode=role_mode, activity=activity)
    return f"{receipt}\n\n{context}" if receipt else context


def _bridge_auto_dispatch_context() -> str | None:
    run_id = os.environ.get(_BRIDGE_DISPATCH_RUN_ID_ENV)
    if not run_id:
        return None
    return "\n".join(
        [
            "# GroundTruth-KB Bridge Auto-Dispatch Session",
            "",
            f"Dispatch id: {run_id}",
            "",
            "This SessionStart was launched by the dispatcher daemon",
            "(scripts/dispatcher_runtime.py) registered as PostToolUse and Stop",
            "hooks. The retired smart poller (archive/smart-poller-2026-05-09/) is no",
            "longer the active dispatch substrate.",
            "Do not relay the normal fresh-session startup disclosure.",
            "Do not treat the initial prompt as a discarded owner session-start stimulus.",
            "Treat the initial prompt as the active bridge auto-dispatch task.",
            "Read current TAFE/dispatcher bridge state and status-bearing numbered bridge files before acting; do not require or recreate retired aggregate queue state.",
            "Process only entries whose live latest status is actionable for the dispatcher-routing role.",
            "Preserve the bridge protocol audit trail.",
        ]
    )


def _read_first_prompt_line() -> str | None:
    """Return the canonical first-line keyword passed by the trigger.

    The dispatcher runtime sets ``GTKB_BRIDGE_DISPATCH_KEYWORD`` on the
    spawned harness's env (per IP-4 companion update to
    ``scripts/dispatcher_runtime.py::_spawn_harness``). Claude Code's
    SessionStart hook stdin does not include user-prompt content, so the env
    var is the side channel for receiver-side keyword recognition.
    """
    raw = os.environ.get(_BRIDGE_DISPATCH_KEYWORD_ENV)
    if raw is None:
        return None
    return raw or None


def _read_session_start_payload() -> dict[str, object]:
    """Read the SessionStart payload once, returning an empty mapping on failure."""
    try:
        stream = sys.stdin
        if stream is None or stream.isatty():
            return {}
        raw = stream.read()
    except (OSError, ValueError):
        return {}
    if not raw or not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _session_start_source(payload: dict[str, object]) -> str | None:
    source = payload.get("source")
    return source.strip() if isinstance(source, str) and source.strip() else None


def _session_start_context_id(payload: dict[str, object]) -> str | None:
    """Return a canonical SessionStart UUID suitable for a content-free guard."""
    raw_session_id = payload.get("session_id")
    if not isinstance(raw_session_id, str) or not raw_session_id.strip():
        return None
    try:
        return str(UUID(raw_session_id.strip()))
    except (AttributeError, ValueError):
        return None


def _read_session_start_source() -> str | None:
    """Return the SessionStart hook input ``source`` field, or None.

    WI-5083: Claude Code's SessionStart hook delivers a JSON payload on stdin
    whose ``source`` field distinguishes a genuinely-fresh start (``startup``)
    from a mid-session continuation (``resume`` / ``compact``) or context clear
    (``clear``). The startup service consumes this (via ``--session-start-source``)
    to avoid re-arming the startup-input gate on a mid-session boundary.

    Fail-soft in every branch: a read/parse problem, a tty stdin (manual/test
    invocation), or a payload without a string ``source`` all yield ``None``,
    which the startup service treats as a genuinely-fresh start -- preserving
    pre-WI-5083 behavior. Only the NORMAL_STARTUP / SPOOF_FALLBACK path reads
    this; the auto-dispatch path returns earlier and never calls it.
    """
    return _session_start_source(_read_session_start_payload())


def _role_modes_from_field(raw_role: object) -> frozenset[str]:
    if isinstance(raw_role, str):
        labels = [raw_role]
    elif isinstance(raw_role, (list, tuple, set, frozenset)):
        labels = [str(value) for value in raw_role]
    else:
        labels = []
    modes = {
        _LABEL_TO_CANONICAL_MODE[label.strip().lower()]
        for label in labels
        if label and label.strip().lower() in _LABEL_TO_CANONICAL_MODE
    }
    return frozenset(modes)


def _resolve_own_role_set(project_root: Path = PROJECT_ROOT) -> frozenset[str]:
    """Resolve this harness's dispatcher role set as canonical modes.

    Authority (per DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 receiver clause;
    WI-3342 IP-4): migrated from the two-step
    ``harness-state/harness-identities.json`` -> ``harness_id`` ->
    retired role-mirror ``role_label`` chain to a single
    lookup against the DB-backed registry projection
    (``harness-state/harness-registry.json``). The projection unifies identity
    and role in one record, so this resolves ``HARNESS_NAME`` to its registry
    record and reads ``id`` + ``role`` from that one row, then converts the
    role field to canonical modes via ``_LABEL_TO_CANONICAL_MODE``.

    The role field is the role-set wire form (a list of role tokens); a legacy
    scalar is also accepted. ``_role_modes_from_field`` handles both.

    Raises:
        ValueError: on unknown role label, missing registry record for this
            harness, or a record with no ``id``/``role``. Callers should treat
            these as "fail-closed treat-as-misdirected" cases. The raised
            ValueError preserves the pre-migration fail-closed contract.
    """
    projection = load_harness_projection(project_root)
    own_record = None
    for record in projection.get("harnesses", []):
        if isinstance(record, dict) and record.get("harness_name") == HARNESS_NAME:
            own_record = record
            break
    if own_record is None:
        raise ValueError(f"harness-registry.json missing entry for harness {HARNESS_NAME!r}")
    if "id" not in own_record:
        raise ValueError(f"harness-registry.json entry for {HARNESS_NAME!r} missing 'id'")
    if "role" not in own_record:
        raise ValueError(f"harness-registry.json entry for {HARNESS_NAME!r} missing 'role'")
    role_set = _role_modes_from_field(own_record["role"])
    if not role_set:
        raise ValueError(f"unknown role field: {own_record['role']!r}")
    return role_set


def _audit_log_misdirected_dispatch(
    run_id: str | None,
    observed_mode: str,
    role_set: frozenset[str],
    *,
    project_root: Path = PROJECT_ROOT,
    failures_path: Path | None = None,
) -> None:
    """Append a JSONL audit record for a dispatch role mismatch.

    Historical helper name retained for parity callers. Per the prompt-role
    authority correction, this audit record is diagnostic only; it must not
    block the explicit dispatch keyword.
    """
    target = failures_path or DISPATCH_FAILURES_PATH
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        own_harness_id: str | None
        # WI-3342 IP-4: own harness id resolves from the registry projection
        # (harness-state/harness-registry.json), migrated from the legacy
        # harness-state/harness-identities.json. Fail-soft: any read/parse
        # problem yields None, preserving the pre-migration contract.
        try:
            own_harness_id = None
            for record in load_harness_projection(project_root).get("harnesses", []):
                if isinstance(record, dict) and record.get("harness_name") == HARNESS_NAME:
                    own_harness_id = record.get("id")
                    break
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            own_harness_id = None
        record = {
            "ts": _now_iso(),
            "kind": "dispatch_role_mismatch_authorized",
            "run_id": run_id,
            "expected_role_set": sorted(role_set),
            "observed_keyword_mode": observed_mode,
            "own_harness_id": own_harness_id,
            "own_harness_name": HARNESS_NAME,
        }
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        # Fire-and-forget contract: audit-log failures must not block dispatch.
        pass


def _bridge_dispatch_keyword_check(
    *,
    project_root: Path = PROJECT_ROOT,
    failures_path: Path | None = None,
) -> tuple[StartupDecision, str]:
    """Decide how SessionStart should treat the incoming session.

    Returns ``(decision, reason)``. The decision drives the emitted
    SessionStart context.

    Behavior table (per bridge -005 IP-4, revised by the prompt-role
    authority emergency fix):

    ============  =========  ====================  ===================  ====================================================
    env-var       keyword    mode-in-role-set      Decision             Effect
    ============  =========  ====================  ===================  ====================================================
    absent        absent     n/a                   NORMAL_STARTUP       normal fresh-session
    absent        present    n/a                   SPOOF_FALLBACK       warn; normal startup; do NOT bypass
    present       absent     n/a                   LEGACY_FALLBACK      warn; normal startup; do NOT bypass
    present       present    yes                   DISPATCH_AUTHORIZED  bridge auto-dispatch context emitted
    present       present    no                    DISPATCH_AUTHORIZED  bridge auto-dispatch context emitted; audit log
    present       subject    n/a                   DISPATCH_AUTHORIZED  subject-only keyword; resolver fallback
    ============  =========  ====================  ===================  ====================================================
    """
    run_id = os.environ.get(_BRIDGE_DISPATCH_RUN_ID_ENV)
    first_line = _read_first_prompt_line() or ""
    keyword_match = match_canonical_init_keyword(first_line)

    if not run_id and not keyword_match:
        return (StartupDecision.NORMAL_STARTUP, "no markers; standard fresh-session")
    if keyword_match and not run_id:
        return (
            StartupDecision.SPOOF_FALLBACK,
            "keyword without env-var; falling through to normal startup",
        )
    if run_id and not keyword_match:
        return (
            StartupDecision.LEGACY_FALLBACK,
            "env-var without keyword; falling through to normal startup",
        )

    # Both present.
    assert keyword_match is not None  # narrow for type checker
    keyword_mode = keyword_match.role_mode
    if keyword_mode is None:
        return (
            StartupDecision.DISPATCH_AUTHORIZED,
            f"subject-only canonical dispatch keyword {keyword_match.subject!r}; resolver fallback",
        )
    try:
        own_role_set = _resolve_own_role_set(project_root=project_root)
    except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        _audit_log_misdirected_dispatch(
            run_id,
            keyword_mode,
            frozenset(),
            project_root=project_root,
            failures_path=failures_path,
        )
        return (
            StartupDecision.DISPATCH_AUTHORIZED,
            f"could not resolve own role set: {exc}; prompt keyword authorized with audit",
        )
    if keyword_mode in own_role_set:
        return (StartupDecision.DISPATCH_AUTHORIZED, "canonical dispatch authorized")
    _audit_log_misdirected_dispatch(
        run_id,
        keyword_mode,
        own_role_set,
        project_root=project_root,
        failures_path=failures_path,
    )
    return (
        StartupDecision.DISPATCH_AUTHORIZED,
        f"keyword mode {keyword_mode!r} not in role set {sorted(own_role_set)!r}; prompt keyword authorized with audit",
    )


def _dump_payload(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=True)


def _valid_session_start_payload(text: str, request_started_at: str) -> bool:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return False
    hook_output = payload.get("hookSpecificOutput")
    if not (
        isinstance(hook_output, dict)
        and hook_output.get("hookEventName") == "SessionStart"
        and isinstance(hook_output.get("additionalContext"), str)
        and "Programmatic Startup Payload" in hook_output["additionalContext"]
    ):
        return False
    startup_freshness = hook_output.get("startupFreshness")
    if not isinstance(startup_freshness, dict):
        return False
    validation = startup_freshness.get("validation")
    return (
        startup_freshness.get("contract_version") == STARTUP_FRESHNESS_CONTRACT_VERSION
        and startup_freshness.get("request_started_at") == request_started_at
        and startup_freshness.get("report_origin") == "in_memory_model_render"
        and isinstance(validation, dict)
        and validation.get("startup_payload_fresh") is True
        and validation.get("status") in {"fresh", "fresh_with_gaps"}
        and _is_ordered(request_started_at, startup_freshness.get("generated_at"))
        and _is_ordered(startup_freshness.get("generated_at"), startup_freshness.get("payload_emitted_at"))
    )


def _startup_body_role_mode(body: str) -> str | None:
    if "Role being assumed: Loyal Opposition" in body:
        return "lo"
    if "Role being assumed: Prime Builder" in body:
        return "pb"
    return None


def _render_role_startup_report(role_profile: str) -> str | None:
    try:
        from scripts import session_self_initialization as startup  # noqa: PLC0415

        role_mode = (
            "pb" if role_profile == "prime-builder" else "lo" if role_profile == "loyal-opposition" else role_profile
        )
        model = startup.build_startup_model(
            PROJECT_ROOT,
            role_profile=role_profile,
            harness_name=HARNESS_NAME,
            harness_id=_persistent_harness_id(),
            role_profile_explicit=False,
            interactive_role_source=(
                f"startup disclosure rendered for role mode {role_mode}; authoritative only when selected "
                "by the owner transcript/init-keyword path"
            ),
            fast_hook=True,
        )
        return startup.render_report(
            model,
            startup._markdown_url_link(startup.GRAFANA_DASHBOARD_URL),
            PROJECT_ROOT,
        )
    except Exception:
        return None


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stdout_path = OUT_DIR / "last-session-start.json"
    stderr_path = OUT_DIR / "last-session-start.err"
    request_started_at = _now_iso()
    _purge_previous_diagnostics(stdout_path, stderr_path)
    # Invalidate only the legacy shared session-role marker before the dispatch
    # fork and before role rendering. Per-session markers and the session
    # envelope carry the transcript-defined interactive role across contiguous
    # SessionStart-like boundaries; the sweep below handles stale per-session
    # cleanup without clobbering the current context.
    _invalidate_session_role_marker()
    # WI-4540: sweep stale per-session role markers (role-*.json) without
    # touching the current context's marker. current_session_id is resolved
    # best-effort from the marker-continuity env order; when unavailable the
    # sweep falls back to freshness-only retention (never deletes a fresh
    # marker). Fail-soft: a sweep error must not abort SessionStart.
    try:
        try:
            from scripts.gtkb_session_id import MARKER_CONTINUITY_ORDER, resolve_session_id
        except ImportError:  # pragma: no cover - direct script execution path
            from gtkb_session_id import MARKER_CONTINUITY_ORDER, resolve_session_id  # type: ignore[no-redef]

        _swept_current_id = resolve_session_id(order=MARKER_CONTINUITY_ORDER) or None
        _sweep_stale_per_session_role_markers(current_session_id=_swept_current_id)
    except Exception:  # noqa: BLE001 - lifecycle hook must fail soft.
        pass
    # IP-4: receiver-side StartupDecision dispatch per bridge -005.
    decision, _reason = _bridge_dispatch_keyword_check()
    if decision == StartupDecision.DISPATCH_AUTHORIZED:
        # Canonical dispatch requires both the dispatcher run-id env var and
        # the canonical init keyword side channel. Env-var-only legacy markers
        # fall through to normal startup so inherited test/worker state cannot
        # turn an interactive restart into a bridge worker.
        auto_dispatch_context = _bridge_auto_dispatch_context()
        if auto_dispatch_context is not None:
            payload = _session_start_payload(
                _with_envelope_packet_receipt(
                    auto_dispatch_context,
                    role_mode=_dispatch_role_mode_from_keyword(),
                )
            )
            serialized = _dump_payload(payload)
            stdout_path.write_text(serialized, encoding="utf-8")
            stderr_path.write_text("", encoding="utf-8")
            print(serialized)
            return 0
    # SPOOF_FALLBACK, LEGACY_FALLBACK, and NORMAL_STARTUP all fall through to
    # the canonical startup-service path. SPOOF_FALLBACK explicitly refuses to
    # bypass normal startup on a keyword alone; LEGACY_FALLBACK now refuses to
    # bypass on an inherited run-id alone.
    command = [
        prefer_pythonw_executable(sys.executable),
        str(STARTUP_SERVICE),
        "--project-root",
        str(PROJECT_ROOT),
        "--emit-startup-service-payload",
        "--fast-hook",
        "--harness-name",
        HARNESS_NAME,
        "--harness-id",
        _persistent_harness_id(),
    ]
    # WI-5083 / WI-5118: read the SessionStart payload once. The source keeps a
    # continuation from re-arming the gate; a validated UUID lets a completed
    # AUQ clear only that same session's pending gate without storing owner text.
    session_start_payload = _read_session_start_payload()
    # WI-5083: thread the SessionStart 'source' so the startup service can skip
    # re-arming the startup-input gate on a mid-session continuation. Read only
    # on this normal-startup path (the auto-dispatch path returned above) and
    # passed as a CLI arg. Absent source => arg omitted => treated as fresh.
    session_start_source = _session_start_source(session_start_payload)
    if session_start_source:
        command += ["--session-start-source", session_start_source]
    try:
        env = dict(os.environ)
        env["GTKB_STARTUP_REQUESTED_AT"] = request_started_at
        # A missing or malformed context must not inherit a prior session's
        # guard id. The startup service then retains its ordinary fresh-start
        # fallback instead of allowing cross-session acknowledgement.
        env.pop("GTKB_STARTUP_GUARD_ID", None)
        session_start_context_id = _session_start_context_id(session_start_payload)
        if session_start_context_id:
            env["GTKB_STARTUP_GUARD_ID"] = session_start_context_id
        process = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=_startup_service_timeout_seconds_for_harness(),
            check=False,
            env=env,
            **no_window_subprocess_kwargs(),
        )
        stdout_path.write_text(process.stdout, encoding="utf-8")
        stderr_path.write_text(process.stderr, encoding="utf-8")
        if process.returncode == 0 and _valid_session_start_payload(process.stdout, request_started_at):
            payload = json.loads(process.stdout)
            hook_output = payload["hookSpecificOutput"]
            startup_context = hook_output["additionalContext"]
            # WI-7318: the SessionStart path no longer writes a startup-disclosure
            # relay cache. The UserPromptSubmit init-keyword relay renders the
            # disclosure for its own turn, so there is nothing to persist here.
            print(
                _dump_payload(
                    _session_start_payload(
                        _with_envelope_packet_receipt(
                            startup_context,
                            role_mode=_dispatch_role_mode_from_keyword(),
                        )
                    )
                )
            )
            return 0
        reason = f"startup service returned exit {process.returncode}"
        if process.stderr.strip():
            reason = f"{reason}: {process.stderr.strip()[:400]}"
        elif process.returncode == 0:
            reason = "startup service freshness contract validation failed"
        print(
            _dump_payload(
                _session_start_payload(
                    _with_envelope_packet_receipt(
                        _fallback_context(reason),
                        role_mode=_dispatch_role_mode_from_keyword(),
                    )
                )
            )
        )
    except Exception as exc:  # noqa: BLE001 - lifecycle hook must fail soft.
        try:
            stderr_path.write_text(str(exc), encoding="utf-8")
        except OSError:
            pass
        print(
            _dump_payload(
                _session_start_payload(
                    _with_envelope_packet_receipt(
                        _fallback_context(str(exc)),
                        role_mode=_dispatch_role_mode_from_keyword(),
                    )
                )
            )
        )
    return 0
