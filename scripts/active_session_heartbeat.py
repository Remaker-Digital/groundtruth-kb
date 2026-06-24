#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Active-session heartbeat for cross-harness trigger suppression.

Per ``bridge/gtkb-cross-harness-trigger-active-session-suppression-001-005.md``
GO at ``-006``:

This script writes/refreshes/deletes a per-role lock file that the
cross-harness trigger uses to detect an active counterpart foreground
session. When a counterpart session holds an active lock, the trigger
suppresses dispatch to that role to prevent duplicate auto-dispatched
parallel-revision work.

Lock file: ``<state-dir>/active-{role}-session.lock`` containing JSON with
``opened_at``/``last_refreshed`` plus role-authority metadata. The metadata
separates the foreground harness identity, an owner-declared interactive role
when one is known, and the durable registry role used for headless dispatch
routing/default fallback.

The script is REGISTERED as a hook in ``.claude/settings.json`` and
``.codex/hooks.json`` with three modes:

- ``--mode session-start``: create or overwrite the lock file.
- ``--mode tool-use``: refresh ``last_refreshed``; create defensively if
  the lock is absent (e.g., SessionStart failed to fire).
- ``--mode session-stop``: delete the lock file (idempotent).

``--state-dir`` is REQUIRED; the hook command MUST pass the same path the
trigger uses (``.gtkb-state/bridge-poller``). Making it required at
argparse time forces the path coupling to be explicit at config time
rather than hidden in script defaults — eliminates the silent failure
mode where heartbeat writes one path and the trigger reads another.

Fire-and-forget: catches all exceptions and exits 0. Errors are written
to stderr but never block the hook chain.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import tempfile
import time
from pathlib import Path

LOCK_FILENAME_TEMPLATE = "active-{role}-session.lock"
REPLACE_RETRY_DELAYS_SECONDS = (0.05, 0.1, 0.2)
ROLE_PRIME = "prime-builder"
ROLE_LO = "loyal-opposition"
_ROLE_ALIASES = {
    "pb": ROLE_PRIME,
    "prime-builder": ROLE_PRIME,
    "lo": ROLE_LO,
    "loyal-opposition": ROLE_LO,
}


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _lock_path(state_dir: Path, role: str) -> Path:
    return state_dir / LOCK_FILENAME_TEMPLATE.format(role=role)


def _normalize_role(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = _ROLE_ALIASES.get(value.strip().lower())
    if normalized is None:
        raise ValueError(f"unknown role value: {value!r}")
    return normalized


def _role_authority_payload(
    harness_name: str,
    *,
    interactive_role: str | None = None,
    interactive_role_source: str | None = None,
    durable_registry_role: str | None = None,
    prior: dict | None = None,
) -> dict:
    prior = prior if isinstance(prior, dict) else {}
    resolved_interactive = _normalize_role(interactive_role) or prior.get("interactive_resolved_role")
    durable_role = _normalize_role(durable_registry_role) or prior.get("durable_registry_role")
    source = interactive_role_source or prior.get("interactive_role_source")
    if resolved_interactive and durable_role and resolved_interactive != durable_role and not source:
        raise ValueError("interactive role differs from durable registry role; --interactive-role-source is required")
    if resolved_interactive:
        authority_mode = "interactive_transcript"
    elif durable_role:
        authority_mode = "durable_registry_fallback"
    else:
        authority_mode = "unknown"
    return {
        "harness_name": harness_name,
        "interactive_resolved_role": resolved_interactive,
        "interactive_role_source": source,
        "durable_registry_role": durable_role,
        "durable_registry_authority": (
            "headless dispatch routing and interactive fallback only; non-overriding when "
            "a transcript-defined interactive role is present"
        ),
        "authority_mode": authority_mode,
    }


def _atomic_write_json(path: Path, payload: dict) -> None:
    """Write JSON atomically via tmp + rename to avoid torn writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        delays = (*REPLACE_RETRY_DELAYS_SECONDS, None)
        for delay in delays:
            try:
                os.replace(tmp_name, str(path))
                break
            except PermissionError:
                if delay is None:
                    raise
                time.sleep(delay)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _lock_payload(
    *,
    opened_at: str,
    last_refreshed: str,
    harness_name: str,
    interactive_role: str | None = None,
    interactive_role_source: str | None = None,
    durable_registry_role: str | None = None,
    prior_authority: dict | None = None,
) -> dict:
    return {
        "opened_at": opened_at,
        "last_refreshed": last_refreshed,
        "harness_name": harness_name,
        "role_authority": _role_authority_payload(
            harness_name,
            interactive_role=interactive_role,
            interactive_role_source=interactive_role_source,
            durable_registry_role=durable_registry_role,
            prior=prior_authority,
        ),
    }


def _handle_session_start(
    state_dir: Path,
    role: str,
    *,
    interactive_role: str | None = None,
    interactive_role_source: str | None = None,
    durable_registry_role: str | None = None,
) -> None:
    now = _now_iso()
    payload = _lock_payload(
        opened_at=now,
        last_refreshed=now,
        harness_name=role,
        interactive_role=interactive_role,
        interactive_role_source=interactive_role_source,
        durable_registry_role=durable_registry_role,
    )
    _atomic_write_json(_lock_path(state_dir, role), payload)


def _handle_tool_use(
    state_dir: Path,
    role: str,
    *,
    interactive_role: str | None = None,
    interactive_role_source: str | None = None,
    durable_registry_role: str | None = None,
) -> None:
    lock = _lock_path(state_dir, role)
    now = _now_iso()
    prior_authority = None
    if lock.exists():
        try:
            existing = json.loads(lock.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}
        opened_at = existing.get("opened_at", now) if isinstance(existing, dict) else now
        prior_authority = existing.get("role_authority") if isinstance(existing, dict) else None
    else:
        # Defensive: SessionStart hook may have failed; create the lock anyway.
        opened_at = now
    payload = _lock_payload(
        opened_at=opened_at,
        last_refreshed=now,
        harness_name=role,
        interactive_role=interactive_role,
        interactive_role_source=interactive_role_source,
        durable_registry_role=durable_registry_role,
        prior_authority=prior_authority,
    )
    _atomic_write_json(lock, payload)


def _handle_session_stop(state_dir: Path, role: str) -> None:
    lock = _lock_path(state_dir, role)
    try:
        lock.unlink()
    except FileNotFoundError:
        # Idempotent: already gone is fine.
        sys.stderr.write(f"active_session_heartbeat: lock {lock} already absent; idempotent stop\n")
    except OSError as exc:
        sys.stderr.write(f"active_session_heartbeat: could not delete {lock}: {exc}\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Active-session heartbeat for cross-harness trigger suppression. "
            "Writes/refreshes/deletes a per-role lock file that the trigger "
            "uses to detect an active counterpart foreground session."
        )
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["session-start", "tool-use", "session-stop"],
        help="Lifecycle mode for this hook firing.",
    )
    parser.add_argument(
        "--role",
        required=True,
        choices=["claude", "codex", "cursor"],
        help="The harness name whose lock file this heartbeat manages.",
    )
    parser.add_argument(
        "--interactive-role",
        choices=sorted(_ROLE_ALIASES),
        help="Owner-declared interactive role for this foreground session, when known.",
    )
    parser.add_argument(
        "--interactive-role-source",
        help=(
            "Source of --interactive-role, e.g. init_keyword or prompt_explicit_role_hint. "
            "Required when interactive and durable roles differ."
        ),
    )
    parser.add_argument(
        "--durable-role",
        choices=sorted(_ROLE_ALIASES),
        help="Durable registry role for this harness, used for headless dispatch/default fallback.",
    )
    parser.add_argument(
        "--state-dir",
        required=True,
        type=Path,
        help=(
            "State directory for the lock file. MUST match the --state-dir the "
            "cross-harness trigger uses (typically .gtkb-state/bridge-poller)."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        # argparse exits non-zero on missing required args; preserve that
        # behavior so misconfigured hooks surface in test output, but DO
        # NOT block running tool-use or session lifecycle for in-session
        # operators. The hook timeout of 5 seconds is the operational
        # guard.
        raise

    try:
        _role_authority_payload(
            args.role,
            interactive_role=args.interactive_role,
            interactive_role_source=args.interactive_role_source,
            durable_registry_role=args.durable_role,
        )
    except ValueError as exc:
        parser.error(str(exc))

    try:
        if args.mode == "session-start":
            _handle_session_start(
                args.state_dir,
                args.role,
                interactive_role=args.interactive_role,
                interactive_role_source=args.interactive_role_source,
                durable_registry_role=args.durable_role,
            )
        elif args.mode == "tool-use":
            _handle_tool_use(
                args.state_dir,
                args.role,
                interactive_role=args.interactive_role,
                interactive_role_source=args.interactive_role_source,
                durable_registry_role=args.durable_role,
            )
        elif args.mode == "session-stop":
            _handle_session_stop(args.state_dir, args.role)
    except Exception as exc:  # noqa: BLE001 — fire-and-forget contract
        sys.stderr.write(f"active_session_heartbeat: error during {args.mode}: {exc}\n")
    # Always exit 0 (fire-and-forget) for any code path that reaches here.
    return 0


if __name__ == "__main__":
    sys.exit(main())
