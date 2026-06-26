#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""PreToolUse black-box gate: block direct agent writes to dispatcher config + runtime state.

WI-4788 slice 1 (PROJECT-GTKB-DISPATCHER-RELIABILITY). Per ADR-DISPATCHER-ARCHITECTURE-001
isolation invariants 1-3, the dispatcher is a GT-KB-owned service: harnesses must not directly
mutate dispatcher config or runtime state. Those mutations must flow through the governed CLI
(``gt bridge dispatch config``, ``gt mode set-role``, ``gt harness``), which write-throughs the
projection and keeps it consistent (the WI-4820 false-green-drift class). This gate fires on the
Write/Edit tools (direct agent file authoring); the governed CLIs mutate via Python file I/O and
bypass the Write tool naturally -- the asymmetry that makes "config/state via CLI+skill only"
mechanical rather than advisory.

The implementation-source half of the black box is already covered by ``implementation_start_gate.py``
(writes to dispatcher source need a bridge-GO packet); this slice adds the config + runtime-state half.

Slice 1 is the decision module + tests. Registering this hook in ``.claude/settings.json`` and
``.codex/hooks.json`` PreToolUse arrays is a thin follow-on activation step, kept separate so the
decision logic is reviewed and tested on its own (the same split used for ``bridge-compliance-gate``).
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MUTATING_TOOLS = frozenset({"Write", "Edit", "NotebookEdit"})

# The governed CLI per protected class -- named in the block reason so the agent is
# redirected to the only sanctioned mutation path for that surface.
_GOVERNED_CLI = {
    "dispatcher_config": "gt bridge dispatch config (e.g. set-eligibility)",
    "harness_registry": "gt mode set-role / gt harness (the registry projection is generated, not hand-edited)",
    "dispatcher_runtime_state": "the dispatcher daemon / gt bridge dispatch commands (runtime state is service-owned)",
}

# Exact protected files (project-root-relative POSIX paths).
_PROTECTED_EXACT = {
    "config/dispatcher/rules.toml": "dispatcher_config",
    "harness-state/harness-registry.json": "harness_registry",
}

# Protected directory prefixes (project-root-relative POSIX, trailing slash).
_PROTECTED_PREFIXES = {
    ".gtkb-state/bridge-poller/": "dispatcher_runtime_state",
    ".gtkb-state/cross-harness-trigger/": "dispatcher_runtime_state",
    ".gtkb-state/dispatcher-daemon/": "dispatcher_runtime_state",
}


@dataclass(frozen=True)
class GateDecision:
    """Outcome of the black-box gate for a single tool call."""

    block: bool
    protected_class: str | None = None
    reason: str | None = None
    bypass_audited: bool = False


def _normalize_rel_path(target_path: str) -> str | None:
    """Return the project-root-relative POSIX path for ``target_path``, or None when it is
    empty or resolves outside the project root."""
    if not target_path or not str(target_path).strip():
        return None
    raw = Path(str(target_path))
    candidate = raw if raw.is_absolute() else PROJECT_ROOT / raw
    try:
        resolved = candidate.resolve(strict=False)
    except OSError:
        return None
    try:
        rel = resolved.relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        return None
    return rel.as_posix()


def classify_protected_path(rel_path: str | None) -> str | None:
    """Return the protected dispatcher class for a project-relative POSIX path, or None.

    Classes: ``dispatcher_config``, ``harness_registry``, ``dispatcher_runtime_state``.
    """
    if not rel_path:
        return None
    if rel_path in _PROTECTED_EXACT:
        return _PROTECTED_EXACT[rel_path]
    for prefix, cls in _PROTECTED_PREFIXES.items():
        if rel_path == prefix.rstrip("/") or rel_path.startswith(prefix):
            return cls
    return None


def gate_decision(tool_name: str, target_path: str, *, bypass: bool = False) -> GateDecision:
    """Decide whether a Write/Edit/NotebookEdit to ``target_path`` must be blocked (WI-4788).

    A mutating tool targeting a protected dispatcher config/state surface is blocked with a
    reason naming the governed CLI for that class -- unless the owner bypass is set, in which
    case it passes with an audit flag. Non-mutating tools and non-protected paths always pass.
    """
    if tool_name not in MUTATING_TOOLS:
        return GateDecision(block=False)
    rel = _normalize_rel_path(target_path)
    protected_class = classify_protected_path(rel)
    if protected_class is None:
        return GateDecision(block=False)
    if bypass:
        return GateDecision(block=False, protected_class=protected_class, bypass_audited=True)
    cli = _GOVERNED_CLI.get(protected_class, "the governed gt dispatch CLI")
    reason = (
        f"BLOCKED (GTKB-DISPATCH-BLACKBOX-GATE / WI-4788): direct {tool_name} to dispatcher "
        f"{protected_class} surface '{rel}' is not allowed. The dispatcher is a GT-KB-owned service "
        f"(ADR-DISPATCHER-ARCHITECTURE-001 invariants 1-3); mutate this surface through {cli}. "
        f"Owner override: set GTKB_DISPATCH_BLACKBOX_BYPASS=1."
    )
    return GateDecision(block=True, protected_class=protected_class, reason=reason)


def _record_gate_denial(pattern_id: str, subject: str, reason: str) -> None:
    """Append a denial/bypass record to the gate-denials JSONL (best-effort, never raises)."""
    path = Path(os.environ.get("GTKB_GATE_DENIALS_PATH", ".gtkb-state/gate-denials.jsonl"))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    record = {
        "schema_version": 1,
        "timestamp_utc": _dt.datetime.now(tz=_dt.UTC).isoformat().replace("+00:00", "Z"),
        "gate": "dispatch-blackbox-gate",
        "pattern_id": pattern_id,
        "command_hash": hashlib.sha256(subject.encode("utf-8")).hexdigest(),
        "reason": reason,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


def _read_payload() -> dict:
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return {}
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _payload_target_path(payload: dict) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        for key in ("file_path", "path", "notebook_path"):
            val = tool_input.get(key)
            if isinstance(val, str) and val:
                return val
    return ""


def main() -> int:
    """PreToolUse entry point: read the hook payload from stdin and emit allow/deny."""
    diagnostic = "--diagnostic" in sys.argv[1:]
    payload = _read_payload()
    tool_name = str(payload.get("tool_name") or "")
    target_path = _payload_target_path(payload)
    bypass = os.environ.get("GTKB_DISPATCH_BLACKBOX_BYPASS") == "1"
    decision = gate_decision(tool_name, target_path, bypass=bypass)

    if diagnostic:
        print(
            json.dumps(
                {
                    "decision": "block" if decision.block else "allow",
                    "diagnostic": True,
                    "protected_class": decision.protected_class,
                    "reason": decision.reason or "",
                    "bypass_audited": decision.bypass_audited,
                    "would_block": decision.block,
                },
                sort_keys=True,
            )
        )
        return 0

    if decision.bypass_audited:
        _record_gate_denial(
            "dispatch-blackbox-bypass",
            json.dumps(payload, sort_keys=True),
            f"OWNER BYPASS (GTKB_DISPATCH_BLACKBOX_BYPASS=1): {tool_name} to {decision.protected_class} allowed",
        )

    if decision.block:
        reason = decision.reason or "BLOCKED (GTKB-DISPATCH-BLACKBOX-GATE)"
        _record_gate_denial("dispatch-blackbox-protected-write", json.dumps(payload, sort_keys=True), reason)
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                        "additionalContext": reason,
                    }
                },
                sort_keys=True,
            )
        )
    else:
        print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
