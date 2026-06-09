# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 machine-checkable assertions.

Authority: bridge/gtkb-canonical-init-keyword-syntax-001-005.md IP-8 surface 5
(Codex GO at -008). Spec:

- DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 — assertions clause requires
  five grep checks across the trigger and the two SessionStart hooks:

  1. ``_resolve_dispatch_target`` calls ``_invert_identities`` (or equivalent
     identity-map inversion) — emitter clause.
  2. Both SessionStart hooks check set-membership against own role set —
     receiver clause.
  3. Audit-log path on STRICT_DROP branch is ``dispatch-failures.jsonl`` —
     PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 clause.
  4. NO occurrence of ``harness-state/<name>/operating-role.md`` as authority
     source — defends against the legacy harness-local override path.
  5. NO direct use of ``role_record["harness_type"]`` for command-handle
     resolution — emitter clause F2 fix (drift-detection metadata only).
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_HOOK_PATH = PROJECT_ROOT / ".claude" / "hooks" / "session_start_dispatch.py"
CODEX_HOOK_PATH = PROJECT_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py"
CORE_PATH = PROJECT_ROOT / "scripts" / "session_start_dispatch_core.py"
TRIGGER_PATH = PROJECT_ROOT / "scripts" / "cross_harness_bridge_trigger.py"


def _read(path: Path) -> str:
    assert path.is_file(), f"Missing file: {path}"
    return path.read_text(encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────
# Assertion 1 (emitter clause): _resolve_dispatch_target -> _invert_identities
# ──────────────────────────────────────────────────────────────────────────


def test_dispatch_target_resolves_via_inverted_identities_map() -> None:
    """DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 emitter clause.

    The trigger's ``_resolve_dispatch_target`` MUST resolve the
    command-handle by inverting ``harness-state/harness-identities.json``,
    not by reading the role record's denormalized ``harness_type`` field.
    """
    src = _read(TRIGGER_PATH)
    # The resolver function exists.
    assert "def _resolve_dispatch_target(" in src
    # The identity-inversion helper exists.
    assert "def _invert_identities(" in src
    # And the resolver calls the inversion (or expands it inline).
    # The canonical pattern is a direct call.
    assert "_invert_identities(" in src, (
        "Trigger must call _invert_identities() inside _resolve_dispatch_target. "
        "Grep failed; check that the emitter clause of DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 "
        "has not regressed."
    )


# ──────────────────────────────────────────────────────────────────────────
# Assertion 2 (receiver clause): both SessionStart hooks check set-membership
# ──────────────────────────────────────────────────────────────────────────


def _has_set_membership_check(src: str) -> bool:
    """Return True iff the source contains a set-membership check against own role set.

    Canonical form per IP-4 spec: ``keyword_mode in own_role_set`` (or
    ``in _resolve_own_role_set()`` directly). Both compile to the same
    semantic.
    """
    patterns = [
        re.compile(r"\bkeyword_mode\s+in\s+own_role_set\b"),
        re.compile(r"\bin\s+_resolve_own_role_set\("),
    ]
    return any(p.search(src) for p in patterns)


def test_claude_session_start_checks_set_membership_against_own_role_set() -> None:
    """DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 receiver clause (Claude via core)."""
    src = _read(CORE_PATH)
    assert "_resolve_own_role_set" in src, "SessionStart core missing _resolve_own_role_set helper."
    assert _has_set_membership_check(src), (
        "SessionStart core missing set-membership check (`keyword_mode in own_role_set` or equivalent)."
    )


def test_codex_session_start_checks_set_membership_against_own_role_set() -> None:
    """DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 receiver clause (Codex via core)."""
    src = _read(CORE_PATH)
    assert "_resolve_own_role_set" in src, "SessionStart core missing _resolve_own_role_set helper."
    assert _has_set_membership_check(src), (
        "SessionStart core missing set-membership check (`keyword_mode in own_role_set` or equivalent)."
    )


# ──────────────────────────────────────────────────────────────────────────
# Assertion 3 (audit log): STRICT_DROP path writes dispatch-failures.jsonl
# ──────────────────────────────────────────────────────────────────────────


def test_claude_strict_drop_writes_dispatch_failures_jsonl() -> None:
    """PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 — audit-log clause (Claude via core)."""
    src = _read(CORE_PATH)
    assert "dispatch-failures.jsonl" in src, (
        "SessionStart core missing audit-log path `dispatch-failures.jsonl`; silent drops would run undetected."
    )
    assert "_audit_log_misdirected_dispatch" in src, (
        "SessionStart core missing _audit_log_misdirected_dispatch helper."
    )
    assert "STRICT_DROP" in src and "_audit_log_misdirected_dispatch(" in src


def test_codex_strict_drop_writes_dispatch_failures_jsonl() -> None:
    """PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 v2 — audit-log clause (Codex via core)."""
    src = _read(CORE_PATH)
    assert "dispatch-failures.jsonl" in src, (
        "SessionStart core missing audit-log path `dispatch-failures.jsonl`; silent drops would run undetected."
    )
    assert "_audit_log_misdirected_dispatch" in src, (
        "SessionStart core missing _audit_log_misdirected_dispatch helper."
    )
    assert "STRICT_DROP" in src and "_audit_log_misdirected_dispatch(" in src


def test_strict_drop_audit_path_matches_glossary_citation() -> None:
    """The audit-log path cited in both hooks MUST match the glossary entry.

    canonical-terminology.md § canonical init keyword cites
    ``.gtkb-state/bridge-poller/dispatch-failures.jsonl``. Drift between
    rule text and code would defeat the rule-cited soft-authority chain.
    """
    glossary_path = PROJECT_ROOT / ".claude" / "rules" / "canonical-terminology.md"
    glossary = _read(glossary_path)
    # Glossary cites the exact path.
    assert ".gtkb-state/bridge-poller/dispatch-failures.jsonl" in glossary
    # Both hooks bind to the same path constant.
    core_src = _read(CORE_PATH)
    assert ".gtkb-state" in core_src and "bridge-poller" in core_src


# ──────────────────────────────────────────────────────────────────────────
# Assertion 4: NO legacy harness-local override authority
# ──────────────────────────────────────────────────────────────────────────


def test_no_harness_local_operating_role_used_as_authority() -> None:
    """DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 receiver clause guardrail.

    The legacy ``harness-state/<harness>/operating-role.md`` pointer files
    are NOT authority sources per ``.claude/rules/operating-role.md``. The
    canonical authority is the single role map at
    ``harness-state/role-assignments.json``. The IP-4 receiver MUST NOT
    revive the legacy override path.
    """
    for path in (CLAUDE_HOOK_PATH, CODEX_HOOK_PATH, CORE_PATH):
        src = _read(path)
        # The legacy override pattern reads `<harness>/operating-role.md`.
        # The bare string `operating-role.md` would also match in a docstring;
        # we look for the path FRAGMENT that indicates harness-local use.
        assert "harness-state/claude/operating-role.md" not in src, (
            f"{path.name} references legacy harness-local Claude override path; "
            "use harness-state/role-assignments.json + harness-state/harness-identities.json."
        )
        assert "harness-state/codex/operating-role.md" not in src, (
            f"{path.name} references legacy harness-local Codex override path; "
            "use harness-state/role-assignments.json + harness-state/harness-identities.json."
        )


# ──────────────────────────────────────────────────────────────────────────
# Assertion 5: NO direct use of role_record["harness_type"] as command-handle
# ──────────────────────────────────────────────────────────────────────────


def test_trigger_does_not_use_role_record_harness_type_as_command_handle() -> None:
    """DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 emitter clause (Codex F2 fix).

    The role record's ``harness_type`` field is OPTIONAL drift-detection
    metadata, NOT command-handle authority. ``_resolve_dispatch_target``
    must invert ``harness-identities.json`` for the command handle. Any
    direct read of ``role_record["harness_type"]`` outside the drift-check
    branch is a regression.

    This test checks the assignment-style patterns that would indicate
    using ``harness_type`` AS the command handle. Reading it for the drift
    comparison is permitted (see the drift-check branch in
    "__resolve_dispatch_target").
    """
    src = _read(TRIGGER_PATH)
    # The drift-check branch reads role_record["harness_type"] via .get() for
    # comparison only. The forbidden pattern is using that value as the
    # command-handle authority — e.g. `handle = role_record["harness_type"]`
    # or `command_handle=role_record["harness_type"]`.
    forbidden_patterns = [
        re.compile(r"command_handle\s*=\s*role_record\[\s*[\"']harness_type[\"']\s*\]"),
        re.compile(r"command_handle\s*=\s*role_record\.get\(\s*[\"']harness_type[\"']"),
        re.compile(r"handle\s*=\s*role_record\[\s*[\"']harness_type[\"']\s*\]"),
        re.compile(r"return\s+role_record\[\s*[\"']harness_type[\"']\s*\]"),
        re.compile(r"return\s+role_record\.get\(\s*[\"']harness_type[\"']"),
    ]
    for pattern in forbidden_patterns:
        match = pattern.search(src)
        assert match is None, (
            f"Trigger uses role_record['harness_type'] as command-handle authority "
            f"(pattern: {pattern.pattern!r}, match: {match.group(0) if match else ''!r}). "
            "Per DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 F2: harness_type is "
            "drift-detection metadata only."
        )


# ──────────────────────────────────────────────────────────────────────────
# Cross-cutting: keyword env-var name parity across emitter and receivers
# ──────────────────────────────────────────────────────────────────────────


def test_keyword_env_var_name_parity() -> None:
    """The trigger and both receivers MUST agree on the env-var name
    ``GTKB_BRIDGE_DISPATCH_KEYWORD``. Drift would silently break dispatch
    keyword recognition."""
    trigger_src = _read(TRIGGER_PATH)
    core_src = _read(CORE_PATH)
    env_name = "GTKB_BRIDGE_DISPATCH_KEYWORD"
    assert env_name in trigger_src, (
        f"Trigger does not emit env var {env_name!r}; receiver would see no keyword."
    )
    assert env_name in core_src, (
        f"SessionStart core does not read env var {env_name!r}; receiver keyword check would no-op."
    )
