"""Claude Code SessionStart hook dispatcher.

Mirrors `.codex/gtkb-hooks/session_start_dispatch.py` so the Claude harness
emits a properly-shaped SessionStart `hookSpecificOutput` envelope, validates
the canonical startup-service freshness contract, and falls back to a
degraded-banner context when the canonical service fails or times out.

Authority: bridge/gtkb-claude-session-start-parity-001.md (Codex GO at -002).
Repairs the prior defect where `.claude/settings.json` invoked the canonical
service with `--emit-report --fast-hook` (flat `additionalContext` envelope,
silently dropped by Claude Code's hook ingestor).

IP-4 (bridge/gtkb-canonical-init-keyword-syntax-001-005.md, Codex GO at -008):
adds canonical init-keyword recognition via `StartupDecision` enum +
``_bridge_dispatch_keyword_check`` per
SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 +
DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001. The receiver reads its own durable
role via the two-step authority chain
(``harness-state/harness-identities.json`` then
``harness-state/role-assignments.json``) and applies set-membership against
the keyword mode. Mismatch → silent drop with audit log entry to
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
OUT_DIR = PROJECT_ROOT / ".claude" / "hooks"
STARTUP_SERVICE = PROJECT_ROOT / "scripts" / "session_self_initialization.py"
STARTUP_FRESHNESS_CONTRACT_VERSION = "gtkb-startup-freshness-v1"
HARNESS_NAME = "claude"
STARTUP_SERVICE_TIMEOUT_SECONDS = 50.0
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
# Audit log for misdirected dispatch silent-drops. Shared with the trigger's
# dispatch-failures path so investigators see all dispatch-related failures
# in one location.
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
            "Read `bridge/INDEX.md` directly before acting.",
            "Process only entries whose live latest status is actionable for the durable role.",
            "Preserve the bridge protocol audit trail.",
        ]
    )


def _strict_drop_context(reason: str) -> str:
    """Emit a clean-exit SessionStart context for misdirected dispatch.

    Per IP-4 of bridge/gtkb-canonical-init-keyword-syntax-001-005.md
    (Codex GO at -008) and DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001
    "Mismatch behavior" clause: the session is NOT to treat the prompt as a
    task; it exits cleanly per the harness's normal "no work to process"
    path. The returned context tells the receiving model to ignore the
    prompt without relaying any startup disclosure or dispatch payload.
    """
    return "\n".join(
        [
            "# GroundTruth-KB Bridge Auto-Dispatch — Misdirected (Silent Drop)",
            "",
            f"Reason: {reason}",
            "",
            "A cross-harness bridge dispatch arrived with a canonical init-keyword "
            "mode that does NOT match this harness's durable operating role "
            "(per DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 receiver-side "
            "set-membership clause).",
            "Do not relay the normal fresh-session startup disclosure.",
            "Do not treat the initial prompt as an actionable task.",
            "Exit this session cleanly without further bridge work.",
            "An audit-log entry has been written to "
            "`.gtkb-state/bridge-poller/dispatch-failures.jsonl` so the durable "
            "role-map drift is investigable.",
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
    ``harness-state/role-assignments.json`` -> ``role_label`` chain to a single
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
        raise ValueError(
            f"harness-registry.json missing entry for harness {HARNESS_NAME!r}"
        )
    if "id" not in own_record:
        raise ValueError(
            f"harness-registry.json entry for {HARNESS_NAME!r} missing 'id'"
        )
    if "role" not in own_record:
        raise ValueError(
            f"harness-registry.json entry for {HARNESS_NAME!r} missing 'role'"
        )
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
    """Append a JSONL audit record for a silently-dropped misdirected dispatch.

    Per PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2: audit-log on
    misdirected dispatch makes silent-drop visible to investigators, addressing
    the S321 incident class where dispatch failures ran undetected for hours.
    Fire-and-forget: audit-log write failures do not block the silent drop.
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
            "kind": "misdirected_dispatch_strict_drop",
            "run_id": run_id,
            "expected_role_set": sorted(role_set),
            "observed_keyword_mode": observed_mode,
            "own_harness_id": own_harness_id,
            "own_harness_name": HARNESS_NAME,
        }
        with target.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        # Fire-and-forget contract: audit-log failures must not block the drop.
        pass


def _bridge_dispatch_keyword_check(
    *,
    project_root: Path = PROJECT_ROOT,
    failures_path: Path | None = None,
) -> tuple[StartupDecision, str]:
    """Decide how SessionStart should treat the incoming session.

    Returns ``(decision, reason)``. The decision drives the emitted
    SessionStart context.

    Behavior table (per bridge -005 IP-4):

    ============  =========  ====================  ===================  ====================================================
    env-var       keyword    mode-in-role-set      Decision             Effect
    ============  =========  ====================  ===================  ====================================================
    absent        absent     n/a                   NORMAL_STARTUP       normal fresh-session
    absent        present    n/a                   SPOOF_FALLBACK       warn; normal startup; do NOT bypass
    present       absent     n/a                   LEGACY_FALLBACK      warn; legacy env-var-only behavior
    present       present    yes                   DISPATCH_AUTHORIZED  bridge auto-dispatch context emitted
    present       present    no                    STRICT_DROP          silent drop; audit log; clean exit
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
        # Fail-closed: if our own durable role is unreadable, treat the
        # dispatch as misdirected (cannot prove keyword matches our role).
        _audit_log_misdirected_dispatch(
            run_id,
            keyword_mode,
            frozenset(),
            project_root=project_root,
            failures_path=failures_path,
        )
        return (
            StartupDecision.STRICT_DROP,
            f"could not resolve own role set: {exc}; treating as misdirected",
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
        StartupDecision.STRICT_DROP,
        f"keyword mode {keyword_mode!r} not in role set {sorted(own_role_set)!r}; silent drop",
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


def _write_startup_relay_cache(additional_context: str) -> None:
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
    meta = {
        "harness_name": HARNESS_NAME,
        "harness_id": _persistent_harness_id(),
        "generated_at": _now_iso(),
        "byte_length": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }
    try:
        (OUT_DIR / "last-user-visible-startup.md").write_text(body, encoding="utf-8", newline="\n")
        (OUT_DIR / "last-user-visible-startup.meta.json").write_text(
            json.dumps(meta, ensure_ascii=True, indent=2), encoding="utf-8", newline="\n"
        )
    except OSError:
        pass


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stdout_path = OUT_DIR / "last-session-start.json"
    stderr_path = OUT_DIR / "last-session-start.err"
    request_started_at = _now_iso()
    _purge_previous_diagnostics(stdout_path, stderr_path)
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
    if decision == StartupDecision.STRICT_DROP:
        # Misdirected dispatch: emit silent-drop context. Audit log already
        # written by _bridge_dispatch_keyword_check.
        payload = _session_start_payload(_strict_drop_context(_reason))
        serialized = _dump_payload(payload)
        stdout_path.write_text(serialized, encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
        print(serialized)
        return 0
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
            timeout=STARTUP_SERVICE_TIMEOUT_SECONDS,
            check=False,
            env=env,
        )
        stdout_path.write_text(process.stdout, encoding="utf-8")
        stderr_path.write_text(process.stderr, encoding="utf-8")
        if process.returncode == 0 and _valid_session_start_payload(process.stdout, request_started_at):
            payload = json.loads(process.stdout)
            startup_context = payload["hookSpecificOutput"]["additionalContext"]
            _write_startup_relay_cache(startup_context)
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


if __name__ == "__main__":
    raise SystemExit(main())
