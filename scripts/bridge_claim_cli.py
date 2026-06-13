#!/usr/bin/env python3
"""Bridge work-intent claim CLI.

Implements IP-0 of bridge/gtkb-work-intent-registry-prime-write-integration-011
(GO at -012). Provides claim/release/status subcommands wrapping the
``bridge_work_intent_registry`` primitive. This is the canonical interactive
pre-drafting boundary for bridge thread coordination per the
"Mandatory Pre-Drafting Claim Step" rule (to be added to
.claude/rules/file-bridge-protocol.md in IP-0b).

Usage:
    python scripts/bridge_claim_cli.py claim <slug>
    python scripts/bridge_claim_cli.py extend <slug>
    python scripts/bridge_claim_cli.py release <slug>
    python scripts/bridge_claim_cli.py status <slug>

Optional flags:
    --session-id <id>     Override harness session env vars
    --ttl-seconds <int>   Override GTKB_WORK_INTENT_TTL_SECONDS env var
                          (default 600 seconds = 10 minutes per IP-0 spec)
    --project-root <path> Override default project root (test affordance;
                          not user-facing surface)

Exit codes:
    0 - claim/release/status successful
    2 - claim refused (held by another session); stdout includes holder JSON
    3 - invalid slug or other error

Env vars:
    GTKB_BRIDGE_POLLER_RUN_ID   headless bridge dispatch run/session id
    CLAUDE_CODE_SESSION_ID       live Claude Code session_id source
    CLAUDE_SESSION_ID            legacy Claude session_id fallback
    GTKB_INHERITED_SESSION_ID    trigger-dispatched session_id source
    CODEX_SESSION_ID             Codex session_id source
    CODEX_THREAD_ID              Codex thread-id fallback
    ANTIGRAVITY_SESSION_ID       Antigravity session_id source
    GTKB_WORK_INTENT_TTL_SECONDS override default 600-second claim TTL

Implements: WI-3414 (per bridge/gtkb-work-intent-registry-prime-write-integration-012 GO).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure script-side import works regardless of how this is invoked.
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from bridge_work_intent_registry import (  # noqa: E402  (path-fix import)
    WorkIntentRegistryError,
    acquire,
    claim_status,
    current_holder,
    extend,
    release,
)
from gtkb_session_id import BRIDGE_WORK_INTENT_ORDER, resolve_session_id  # noqa: E402  (path-fix import)

DEFAULT_TTL_SECONDS = 600
# Session-id env-var membership + bridge live-harness-first order are owned by
# scripts/gtkb_session_id.py (WI-4270 shared resolver unification). SESSION_ENV_VARS
# is retained as the public name for the error message and the precedence-contract
# test; it aliases the canonical BRIDGE_WORK_INTENT_ORDER.
SESSION_ENV_VARS = BRIDGE_WORK_INTENT_ORDER
TTL_ENV_VAR = "GTKB_WORK_INTENT_TTL_SECONDS"


def _resolve_session_id(arg_value: str | None) -> str:
    """Return the session_id from --session-id or known harness env vars.

    Delegates resolution to the shared resolver (arg-first, then the bridge
    work-intent env order) and preserves the CLI's raise-on-empty contract.
    """
    resolved = resolve_session_id(arg_value, order=SESSION_ENV_VARS)
    if resolved:
        return resolved
    env_names = ", ".join(SESSION_ENV_VARS)
    raise SystemExit(f"session_id required: pass --session-id or set one of: {env_names}")


def _resolve_ttl(arg_value: int | None) -> int:
    if arg_value is not None:
        return arg_value
    env_value = os.environ.get(TTL_ENV_VAR)
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass  # fall through to default
    return DEFAULT_TTL_SECONDS


def _resolve_project_root(arg_value: Path | None) -> Path | None:
    """Return Path for --project-root, or None to use the registry default.

    Test affordance: tests can pass an isolated tmp_path so claims don't
    pollute the real .gtkb-state/work-intent/ directory.
    """
    return arg_value.resolve() if arg_value else None


def _print_holder_or_default(holder: dict[str, str] | None, *, none_repr: str = "{}") -> None:
    """Emit the holder record as JSON to stdout, or ``none_repr`` if absent."""
    if holder:
        print(json.dumps(holder, indent=2, sort_keys=True))
    else:
        print(none_repr)


def cmd_claim(args: argparse.Namespace) -> int:
    session_id = _resolve_session_id(args.session_id)
    ttl = _resolve_ttl(args.ttl_seconds)
    project_root = _resolve_project_root(args.project_root)
    try:
        acquired = acquire(args.slug, session_id, ttl_seconds=ttl, project_root=project_root)
    except WorkIntentRegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    holder = current_holder(args.slug, project_root=project_root)
    _print_holder_or_default(holder)
    return 0 if acquired else 2


def cmd_release(args: argparse.Namespace) -> int:
    session_id = _resolve_session_id(args.session_id)
    project_root = _resolve_project_root(args.project_root)
    try:
        release(args.slug, session_id, project_root=project_root)
    except WorkIntentRegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    return 0


def cmd_extend(args: argparse.Namespace) -> int:
    session_id = _resolve_session_id(args.session_id)
    project_root = _resolve_project_root(args.project_root)
    try:
        holder = extend(args.slug, session_id, project_root=project_root)
    except WorkIntentRegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    _print_holder_or_default(holder)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    project_root = _resolve_project_root(args.project_root)
    try:
        holder = claim_status(args.slug, project_root=project_root)
    except WorkIntentRegistryError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    _print_holder_or_default(holder, none_repr="null")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=("Bridge work-intent claim CLI per gtkb-work-intent-registry-prime-write-integration.")
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_claim = sub.add_parser(
        "claim",
        help="Acquire or renew a work-intent claim for a slug.",
        description=(
            "Acquire or renew a work-intent claim. Returns 0 on success, "
            "2 if held by another session, 3 on invalid input."
        ),
    )
    p_claim.add_argument("slug", help="Bridge thread slug (kebab-case).")
    p_claim.add_argument("--session-id", help="Override harness session env vars.")
    p_claim.add_argument(
        "--ttl-seconds",
        type=int,
        help=(f"Override GTKB_WORK_INTENT_TTL_SECONDS env var (default {DEFAULT_TTL_SECONDS} seconds)."),
    )
    p_claim.add_argument(
        "--project-root",
        type=Path,
        help="Override default project root (test affordance).",
    )
    p_claim.set_defaults(func=cmd_claim)

    p_extend = sub.add_parser(
        "extend",
        help="Extend a GO-implementation work-intent claim.",
        description=(
            "Extend a held GO-implementation claim by the fixed self-service "
            "increment, up to the configured total-hold cap."
        ),
    )
    p_extend.add_argument("slug", help="Bridge thread slug (kebab-case).")
    p_extend.add_argument("--session-id", help="Override harness session env vars.")
    p_extend.add_argument(
        "--project-root",
        type=Path,
        help="Override default project root (test affordance).",
    )
    p_extend.set_defaults(func=cmd_extend)

    p_release = sub.add_parser(
        "release",
        help="Release a work-intent claim for a slug.",
        description=(
            "Release a work-intent claim held by the current session. "
            "Idempotent: succeeds even when the slug is not held."
        ),
    )
    p_release.add_argument("slug", help="Bridge thread slug (kebab-case).")
    p_release.add_argument("--session-id", help="Override harness session env vars.")
    p_release.add_argument(
        "--project-root",
        type=Path,
        help="Override default project root (test affordance).",
    )
    p_release.set_defaults(func=cmd_release)

    p_status = sub.add_parser(
        "status",
        help="Show current holder for a slug.",
        description=(
            "Print the current holder record as JSON, or 'null' if the slug is unheld. Does not modify state."
        ),
    )
    p_status.add_argument("slug", help="Bridge thread slug (kebab-case).")
    p_status.add_argument(
        "--project-root",
        type=Path,
        help="Override default project root (test affordance).",
    )
    p_status.set_defaults(func=cmd_status)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
