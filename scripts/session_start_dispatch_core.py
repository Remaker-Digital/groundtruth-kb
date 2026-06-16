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

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

PROJECT_ROOT = Path(r"E:\GT-KB")
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
# Parity marker for tests: Role: Prime Builder

# IP-4: canonical init-keyword recognition (receiver side).
# Per SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001: regex matches the first-line
# activator emitted by the cross-harness trigger; closed vocabulary {pb, lo}.
_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")
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
# Audit log for dispatch keyword / durable role mismatches. Shared with the
# trigger's dispatch-failures path so investigators see all dispatch-related
# failures in one location.
DISPATCH_FAILURES_PATH = PROJECT_ROOT / ".gtkb-state" / "bridge-poller" / "dispatch-failures.jsonl"


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


sys.path.insert(0, str(PROJECT_ROOT))
from scripts.harness_identity import resolved_harness_id  # noqa: E402
from scripts.harness_projection_reader import load_harness_projection  # noqa: E402


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _startup_service_timeout_seconds() -> float:
    raw = os.environ.get(STARTUP_SERVICE_TIMEOUT_ENV)
    if raw is None or not raw.strip():
        return STARTUP_SERVICE_TIMEOUT_SECONDS
    try:
        parsed = float(raw)
    except ValueError:
        return STARTUP_SERVICE_TIMEOUT_SECONDS
    return parsed if parsed > 0 else STARTUP_SERVICE_TIMEOUT_SECONDS


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


# Slice 3 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE: the ephemeral
# session-state role marker is written by the UserPromptSubmit init-keyword
# path (scripts/workstream_focus.py, Slice 2). Per
# DCL-SESSION-ROLE-RESOLUTION-001 assertion 5, SessionStart must invalidate it
# so the interactive override does not survive a SessionStart event (new
# session, compaction, resume). The constant is duplicated from
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
            "This SessionStart was launched by the cross-harness event-driven trigger",
            "(scripts/cross_harness_bridge_trigger.py) registered as PostToolUse and Stop",
            "hooks. The retired smart poller (archive/smart-poller-2026-05-09/) is no",
            "longer the active dispatch substrate.",
            "Do not relay the normal fresh-session startup disclosure.",
            "Do not treat the initial prompt as a discarded owner session-start stimulus.",
            "Treat the initial prompt as the active bridge auto-dispatch task.",
            "Read current TAFE/dispatcher bridge state and status-bearing versioned bridge files before acting; do not require or recreate `bridge/INDEX.md`.",
            "Process only entries whose live latest status is actionable for the durable role.",
            "Preserve the bridge protocol audit trail.",
        ]
    )


def _read_first_prompt_line() -> str | None:
    """Return the canonical first-line keyword passed by the trigger.

    The cross-harness trigger sets ``GTKB_BRIDGE_DISPATCH_KEYWORD`` on the
    spawned harness's env (per IP-4 companion update to
    ``scripts/cross_harness_bridge_trigger.py::_spawn_harness``). Claude Code's
    SessionStart hook stdin does not include user-prompt content, so the env
    var is the side channel for receiver-side keyword recognition.
    """
    raw = os.environ.get(_BRIDGE_DISPATCH_KEYWORD_ENV)
    if raw is None:
        return None
    return raw.strip() or None


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
    """Resolve this harness's durable role set as canonical modes.

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
    present       absent     n/a                   LEGACY_FALLBACK      warn; legacy env-var-only behavior
    present       present    yes                   DISPATCH_AUTHORIZED  bridge auto-dispatch context emitted
    present       present    no                    DISPATCH_AUTHORIZED  bridge auto-dispatch context emitted; audit log
    ============  =========  ====================  ===================  ====================================================
    """
    run_id = os.environ.get(_BRIDGE_DISPATCH_RUN_ID_ENV)
    first_line = _read_first_prompt_line() or ""
    keyword_match = _CANONICAL_KEYWORD_RE.match(first_line)

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
            "env-var without keyword; preserving legacy env-var-only dispatch behavior",
        )

    # Both present.
    assert keyword_match is not None  # narrow for type checker
    keyword_mode = keyword_match.group(1)
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


def _startup_relay_cache_names(role_mode: str | None = None) -> tuple[str, str]:
    if role_mode in _MODE_TO_ROLE_PROFILE:
        return (
            f"last-user-visible-startup-{role_mode}.md",
            f"last-user-visible-startup-{role_mode}.meta.json",
        )
    return ("last-user-visible-startup.md", "last-user-visible-startup.meta.json")


def _startup_body_role_mode(body: str) -> str | None:
    if "Role being assumed: Loyal Opposition" in body:
        return "lo"
    if "Role being assumed: Prime Builder" in body:
        return "pb"
    return None


def _render_role_startup_report(role_profile: str) -> str | None:
    try:
        from scripts import session_self_initialization as startup  # noqa: PLC0415

        model = startup.build_startup_model(
            PROJECT_ROOT,
            role_profile=role_profile,
            harness_name=HARNESS_NAME,
            harness_id=_persistent_harness_id(),
            fast_hook=True,
        )
        return startup.render_report(
            model,
            startup._markdown_url_link(startup.GRAFANA_DASHBOARD_URL),
            PROJECT_ROOT,
        )
    except Exception:
        return None


def _write_startup_relay_cache(additional_context: str, *, role_mode: str | None = None) -> None:
    """Write the harness-scoped startup-disclosure relay cache and metadata.

    Extracts the owner-visible startup message from a validated NORMAL_STARTUP
    SessionStart payload and writes it to a harness-scoped cache file plus a
    metadata sidecar (harness, timestamp, byte length, sha256). Called only on
    the validated normal-startup path, so bridge auto-dispatch payloads never
    populate the interactive startup-disclosure relay cache. Fails soft.
    """
    marker = "## User-Visible Startup Message"
    if marker in additional_context:
        body = additional_context.split(marker, 1)[1].strip()
    else:
        body = additional_context.strip()
    if not body:
        return
    encoded = body.encode("utf-8")
    effective_role_mode = role_mode or _startup_body_role_mode(body)
    meta = {
        "harness_name": HARNESS_NAME,
        "harness_id": _persistent_harness_id(),
        "role_mode": effective_role_mode,
        "role_profile": _MODE_TO_ROLE_PROFILE.get(effective_role_mode or ""),
        "generated_at": _now_iso(),
        "byte_length": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }
    cache_name, meta_name = _startup_relay_cache_names(role_mode)
    try:
        (OUT_DIR / cache_name).write_text(body, encoding="utf-8", newline="\n")
        (OUT_DIR / meta_name).write_text(json.dumps(meta, ensure_ascii=True, indent=2), encoding="utf-8", newline="\n")
    except OSError:
        pass


def _write_role_scoped_startup_relay_caches(additional_context: str) -> None:
    marker = "## User-Visible Startup Message"
    body = (
        additional_context.split(marker, 1)[1].strip() if marker in additional_context else additional_context.strip()
    )
    primary_mode = _startup_body_role_mode(body)
    if primary_mode:
        _write_startup_relay_cache(body, role_mode=primary_mode)
    # Per ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 2 and
    # DCL-SESSION-ROLE-RESOLUTION-001: both the -pb and -lo startup-disclosure
    # caches are generated unconditionally, regardless of this harness's durable
    # role set, so the UserPromptSubmit init-keyword matcher's keyword-keyed
    # cache lookup succeeds for either role when the owner declares a
    # session-stated role via ``::init gtkb (pb|lo)``. The durable role set is
    # NOT consulted here; durable role remains the authority for headless
    # dispatch routing only.
    for mode in sorted(_MODE_TO_ROLE_PROFILE):
        if mode == primary_mode:
            continue
        report = _render_role_startup_report(_MODE_TO_ROLE_PROFILE[mode])
        if report:
            _write_startup_relay_cache(report, role_mode=mode)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stdout_path = OUT_DIR / "last-session-start.json"
    stderr_path = OUT_DIR / "last-session-start.err"
    request_started_at = _now_iso()
    _purge_previous_diagnostics(stdout_path, stderr_path)
    # Slice 3 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE: invalidate any
    # pre-existing session-state role marker before the dispatch fork and before
    # any role rendering, so the ephemeral interactive override does not survive
    # this SessionStart event (DCL-SESSION-ROLE-RESOLUTION-001 assertion 5). This
    # runs on every SessionStart path (normal or bridge auto-dispatch)
    # and does not disturb the mode-switch-drain -> dispatch ordering below.
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
    # Slice 1 of gtkb-operating-mode-transaction-001: drain any pending
    # mode-switch transactions BEFORE role resolution, so a next-session-
    # effective mode/role switch takes effect for the dispatch decision
    # below. Fail-soft per design: failures are logged but do not abort
    # SessionStart.
    try:
        from pathlib import Path as _Path

        from groundtruth_kb.mode_switch.pending import apply_pending as _apply_pending

        _apply_pending(_Path(__file__).resolve().parents[2])
    except Exception:  # noqa: BLE001 - fail-soft per spec acceptance criterion #6
        pass
    # IP-4: receiver-side StartupDecision dispatch per bridge -005.
    decision, _reason = _bridge_dispatch_keyword_check()
    if decision in (StartupDecision.DISPATCH_AUTHORIZED, StartupDecision.LEGACY_FALLBACK):
        # Canonical dispatch or env-var-only legacy dispatch: emit the
        # bridge auto-dispatch context (today's behavior).
        auto_dispatch_context = _bridge_auto_dispatch_context()
        if auto_dispatch_context is not None:
            payload = _session_start_payload(auto_dispatch_context)
            serialized = _dump_payload(payload)
            stdout_path.write_text(serialized, encoding="utf-8")
            stderr_path.write_text("", encoding="utf-8")
            print(serialized)
            return 0
    # SPOOF_FALLBACK and NORMAL_STARTUP both fall through to the canonical
    # startup-service path. SPOOF_FALLBACK explicitly refuses to bypass
    # normal startup on a keyword alone — defense against owner-typed or
    # otherwise unverified keyword strings.
    command = [
        sys.executable,
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
    try:
        env = dict(os.environ)
        env["GTKB_STARTUP_REQUESTED_AT"] = request_started_at
        process = subprocess.run(
            command,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=_startup_service_timeout_seconds(),
            check=False,
            env=env,
        )
        stdout_path.write_text(process.stdout, encoding="utf-8")
        stderr_path.write_text(process.stderr, encoding="utf-8")
        if process.returncode == 0 and _valid_session_start_payload(process.stdout, request_started_at):
            payload = json.loads(process.stdout)
            hook_output = payload["hookSpecificOutput"]
            startup_context = hook_output["additionalContext"]
            # WI-4361: prefer hookSpecificOutput.startupDisclosure for relay-cache
            # writing when the startup service emits a new-shape payload (compact
            # additionalContext + complete startupDisclosure). Legacy payloads
            # without startupDisclosure fall back to the marker-split path inside
            # _write_startup_relay_cache, which finds the embedded
            # "## User-Visible Startup Message" body in additionalContext.
            startup_disclosure = hook_output.get("startupDisclosure")
            if isinstance(startup_disclosure, str) and startup_disclosure.strip():
                relay_body = startup_disclosure
            else:
                relay_body = startup_context
            _write_startup_relay_cache(relay_body)
            _write_role_scoped_startup_relay_caches(relay_body)
            print(_dump_payload(_session_start_payload(startup_context)))
            return 0
        reason = f"startup service returned exit {process.returncode}"
        if process.stderr.strip():
            reason = f"{reason}: {process.stderr.strip()[:400]}"
        elif process.returncode == 0:
            reason = "startup service freshness contract validation failed"
        print(_dump_payload(_session_start_payload(_fallback_context(reason))))
    except Exception as exc:  # noqa: BLE001 - lifecycle hook must fail soft.
        try:
            stderr_path.write_text(str(exc), encoding="utf-8")
        except OSError:
            pass
        print(_dump_payload(_session_start_payload(_fallback_context(str(exc)))))
    return 0
