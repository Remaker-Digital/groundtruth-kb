#!/usr/bin/env python3
"""Verify Codex hook intent stays aligned with Agent Red governance hooks."""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FORMAL_APPROVAL_HOOK = ".claude/hooks/formal-artifact-approval-gate.py"
BRIDGE_COMPLIANCE_HOOK = ".claude/hooks/bridge-compliance-gate.py"
WORKSTREAM_FOCUS_HOOK = ".claude/hooks/workstream-focus.py"
SESSION_SELF_INITIALIZATION_SCRIPT = "scripts/session_self_initialization.py"
SINGLE_HARNESS_AUTOMATION_SCRIPT = "scripts/single_harness_bridge_automation.py"
HARNESS_IDENTITY_RECORD = "harness-state/harness-identities.json"
ROLE_ASSIGNMENT_RECORD = "harness-state/harness-registry.json"
CODEX_CONFIG = ".codex/config.toml"
CODEX_HOOKS = ".codex/hooks.json"
CLAUDE_SETTINGS = ".claude/settings.json"
CLAUDE_SESSION_START_DISPATCHER = ".claude/hooks/session_start_dispatch.py"
CODEX_WRAPPER_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"
CODEX_FORMAL_APPROVAL_WRAPPER = CODEX_WRAPPER_DIR / "formal-artifact-approval.cmd"
CODEX_BRIDGE_COMPLIANCE_WRAPPER = CODEX_WRAPPER_DIR / "bridge-compliance-gate.cmd"
CODEX_BRIDGE_COMPLIANCE_ADAPTER = CODEX_WRAPPER_DIR / "bridge-compliance-gate-bash-adapter.py"
CODEX_BRIDGE_COMPLIANCE_AUDIT_DISPATCHER = CODEX_WRAPPER_DIR / "bridge-compliance-audit.cmd"
CODEX_WORKSTREAM_FOCUS_WRAPPER = CODEX_WRAPPER_DIR / "workstream-focus.cmd"
CODEX_SESSION_START_WRAPPER = CODEX_WRAPPER_DIR / "session-start.cmd"
CODEX_SESSION_START_DISPATCHER = CODEX_WRAPPER_DIR / "session_start_dispatch.py"
CODEX_SESSION_STOP_DISPATCHER = CODEX_WRAPPER_DIR / "session_stop_dispatch.py"
CODEX_WRAPUP_TRIGGER_DISPATCHER = CODEX_WRAPPER_DIR / "session_wrapup_trigger_dispatch.py"

# -----------------------------------------------------------------------------
# Resolution-table parity constants (Slice 8 of
# PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE; WI-3478;
# bridge gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-003.md
# GO at -004).
#
# These literals are the resolution-table contract that
# ``_resolution_table_parity_errors`` enforces across the Claude and Codex
# SessionStart dispatchers.  Slice 1, 2, 3, 4 VERIFIED dependencies established
# the as-shipped contract; Slice 8 promotes byte-parity from convention to
# mechanical assertion.
# -----------------------------------------------------------------------------
CODEX_SESSION_START_DISPATCHER_PATH = ".codex/gtkb-hooks/session_start_dispatch.py"
# Slice D of GTKB-STARTUP-REFRACTOR-001 (WI-4272): the shared SessionStart
# dispatch primitives were extracted from the two byte-identical wrappers into
# this single core module. The resolution-table primitive assertions now check
# the core (single source); the wrappers are checked only for delegation +
# intentional-difference guards.
SESSION_START_DISPATCH_CORE_PATH = "scripts/session_start_dispatch_core.py"
SESSION_ROLE_RESOLVER_PATH = "scripts/session_role_resolution.py"
WORKSTREAM_FOCUS_PATH = "scripts/workstream_focus.py"

# Marker constant literal shared by both dispatchers and the resolver/UPS
# writer per ``DCL-SESSION-ROLE-RESOLUTION-001`` (Slice 4 VERIFIED).
_MARKER_CONSTANT_LITERAL = '_SESSION_ROLE_MARKER_NAME = "active-session-role.json"'

# As-shipped ``StartupDecision`` enum vocabulary per the IP-4 enum cleanup
# (bridge ``gtkb-canonical-init-keyword-syntax-001-005..009``).  This is the
# spec-revision equivalent of the scoping-003 line 344
# ``INTERACTIVE_OVERRIDE_AUTHORIZED`` term; the implementation never shipped a
# distinct ``INTERACTIVE_OVERRIDE_AUTHORIZED`` member.
_STARTUP_DECISION_CLASS_LITERAL = "class StartupDecision(Enum):"
_STARTUP_DECISION_MEMBER_LITERALS = (
    'NORMAL_STARTUP = "normal_startup"',
    'DISPATCH_AUTHORIZED = "dispatch_authorized"',
    'SPOOF_FALLBACK = "spoof_fallback"',
    'LEGACY_FALLBACK = "legacy_fallback"',
    'STRICT_DROP = "strict_drop"',
)

# Canonical init-keyword regex per ``SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001``.
_CANONICAL_KEYWORD_RE_LITERAL = '_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")'

# Audit-log primitives (Slice 4 VERIFIED + scoping-003 receiver behavior).
_AUDIT_LOG_KIND_LITERAL = '"misdirected_dispatch_strict_drop"'
_AUDIT_LOG_PATH_TOKEN = ".gtkb-state/bridge-poller/dispatch-failures.jsonl"

# Intentional-difference guards (assertion 8): the precise OUT_DIR assignment
# and HARNESS_NAME assignment literals are what a copy-paste-of-harness-name
# drift would change.  These literals avoid false-positive matches on
# docstring cross-references (each dispatcher's module docstring legitimately
# references the other dispatcher's path).
_CLAUDE_OUT_DIR_LITERAL = 'OUT_DIR = PROJECT_ROOT / ".claude" / "hooks"'
_CODEX_OUT_DIR_LITERAL = 'OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"'
_CLAUDE_HARNESS_NAME_LITERAL = 'HARNESS_NAME = "claude"'
_CODEX_HARNESS_NAME_LITERAL = 'HARNESS_NAME = "codex"'

# Expected ``StartupDecision`` enum members as ``{name: string_value}`` per the
# IP-4 enum cleanup (bridge ``gtkb-canonical-init-keyword-syntax-001-005..009``).
# Assertion 2 enforces this as a CLOSED set — extra members fail the check.
# Addresses verification NO-GO -006 F2 (text-presence loop weakened to closed-set
# AST comparison).
_STARTUP_DECISION_EXPECTED: dict[str, str] = {
    "NORMAL_STARTUP": "normal_startup",
    "DISPATCH_AUTHORIZED": "dispatch_authorized",
    "SPOOF_FALLBACK": "spoof_fallback",
    "LEGACY_FALLBACK": "legacy_fallback",
    "STRICT_DROP": "strict_drop",
}

# Behavior-table column headers documented in the ``_bridge_dispatch_keyword_check``
# docstring per the GO-approved Slice 8 scope.  Retained for reference only —
# the original loose-substring check was replaced with a header-row regex per
# verification NO-GO -009 F3.
_BEHAVIOR_TABLE_HEADER_TOKENS: tuple[str, ...] = (
    "env-var",
    "keyword",
    "mode-in-role-set",
    "Decision",
    "Effect",
)

# Regex matching the five-token behavior-table header row.  Retained for
# reference; the v3 anchored check (``_HEADER_ROW_RE`` + ``_SEPARATOR_ROW_RE``
# per-line check) replaced the unanchored ``.search()`` use.  See
# ``_docstring_has_anchored_header_row``.
_BEHAVIOR_TABLE_HEADER_ROW_RE = re.compile(r"env-var\s+keyword\s+mode-in-role-set\s+Decision\s+Effect")

# Line-anchored regexes used by ``_docstring_has_anchored_header_row``.
# ``_HEADER_ROW_RE`` matches a line that is exactly the five tokens in order
# separated by whitespace (no leading/trailing text on the line).
# ``_SEPARATOR_ROW_RE`` matches a separator line consisting of one or more
# ``=`` characters interleaved with whitespace (the table-rule pattern used
# by reStructuredText-style tables).  Together they anchor the header check
# to the actual table structure per verification NO-GO -011 F3.
_HEADER_ROW_RE = re.compile(r"^env-var\s+keyword\s+mode-in-role-set\s+Decision\s+Effect$")
_SEPARATOR_ROW_RE = re.compile(r"^=+(?:\s+=+)+$")

# Cache-writer parity guards (assertion 9; addresses Slice 8 NO-GO -002 F2).
# Per ``ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`` Decision 2 and Slice 1
# VERIFIED, ``_write_role_scoped_startup_relay_caches`` must iterate
# ``_MODE_TO_ROLE_PROFILE`` and skip ``primary_mode`` so both ``-pb.md`` and
# ``-lo.md`` caches are generated unconditionally regardless of the
# harness's durable role set.  ``_resolve_own_role_set`` references in the
# function body are the pre-Slice-1 defective shape that conditioned cache
# writes on the durable role set (per scoping-003 line 71).
_CACHE_WRITER_LOOP_LITERAL = "for mode in sorted(_MODE_TO_ROLE_PROFILE):"
_CACHE_WRITER_SKIP_LITERAL = "if mode == primary_mode:"
_CACHE_WRITER_FORBIDDEN_LITERAL = "_resolve_own_role_set"

# Canonical resolution-table dict content (Slice D single-source relocation).
# Under single-sourcing the old "two dispatchers must be ast-equivalent" check
# is moot (one copy); the stronger replacement asserts the core's dict content
# equals these canonical mappings, so ANY content drift in the single source
# fails the gate.
_EXPECTED_RESOLUTION_DICTS: dict[str, dict[str, str]] = {
    "_LABEL_TO_CANONICAL_MODE": {
        "prime-builder": "pb",
        "acting-prime-builder": "pb",
        "loyal-opposition": "lo",
    },
    "_MODE_TO_ROLE_PROFILE": {
        "pb": "prime-builder",
        "lo": "loyal-opposition",
    },
}

# Slice D delegation markers: each thin wrapper must import the shared core and
# rebind its functions onto the wrapper namespace.
_CORE_IMPORT_TOKEN = "import session_start_dispatch_core"
_CORE_REBIND_TOKEN = "types.FunctionType("


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _commands_for_event(hooks_document: dict[str, Any], event_name: str) -> list[str]:
    commands: list[str] = []
    for group in hooks_document.get("hooks", {}).get(event_name, []):
        for hook in group.get("hooks", []):
            command = hook.get("command")
            if isinstance(command, str):
                commands.append(command)
    return commands


def _contains_hook_path(command: str, hook_path: str) -> bool:
    normalized_command = command.replace("\\", "/").lower()
    normalized_hook_path = hook_path.replace("\\", "/").lower()
    return normalized_hook_path in normalized_command


def _contains_path(command: str, path: Path) -> bool:
    normalized_command = command.replace("\\", "/").lower()
    normalized_path = path.as_posix().lower()
    return normalized_path in normalized_command


def _contains_hook_wrapper(command: str, wrapper_path: Path) -> bool:
    """Return true for the project-intended wrapper path across runner homes."""
    normalized_command = command.replace("\\", "/").lower()
    normalized_path = wrapper_path.as_posix().lower()
    wrapper_fragment = f"gtkb-hooks/{wrapper_path.name.lower()}"
    return normalized_path in normalized_command or wrapper_fragment in normalized_command


def _uses_shell_command_substitution(command: str) -> bool:
    return "$(" in command


def _wrapper_errors(wrapper_path: Path, required_terms: list[str]) -> list[str]:
    if not wrapper_path.is_file():
        if os.environ.get("CI") == "true":
            return []
        return [f"missing Codex hook wrapper: {wrapper_path}"]
    text = wrapper_path.read_text(encoding="utf-8")
    errors: list[str] = []
    for term in required_terms:
        if term not in text:
            errors.append(f"Codex hook wrapper {wrapper_path.name} must include {term}")
    return errors


def _wrapup_trigger_errors(wrapper_path: Path) -> list[str]:
    dispatcher_path = CODEX_WRAPUP_TRIGGER_DISPATCHER
    if not dispatcher_path.is_file():
        if os.environ.get("CI") == "true":
            return []
        return [f"missing Codex wrap-up trigger dispatcher: {dispatcher_path}"]
    text = dispatcher_path.read_text(encoding="utf-8")
    errors = _wrapper_errors(
        dispatcher_path,
        [
            "session_self_initialization.py",
            "--emit-wrapup",
            "--force-wrapup",
            "--fast-hook",
            "--harness-name",
            "--harness-id",
            "harness_identity",
            "resolved_harness_id",
            "UserPromptSubmit",
            "ACCEPTED_TRIGGER_PHRASES",
            "_is_wrapup_trigger",
            "_startup_input_gate_active",
            "discard_next_user_prompt",
            "startup_response_pending",
            "wrap up this session",
            "start a new session",
            "begin fresh",
            "subprocess.run",
            'print("{}")',
            "hookSpecificOutput",
            "hookEventName",
            "additionalContext",
        ],
    )
    for term in ("last-wrapup-trigger.json", "last-wrapup-trigger.err", "last-wrapup-trigger-input.json"):
        if term not in text:
            errors.append(f"Codex wrap-up trigger dispatcher {dispatcher_path.name} must capture diagnostics")
    if "--role-profile" in text:
        errors.append("Codex wrap-up trigger dispatcher must discover the role profile instead of forcing one")
    return errors


def _start_wrapper_errors(wrapper_path: Path) -> list[str]:
    dispatcher_path = CODEX_SESSION_START_DISPATCHER
    core_path = PROJECT_ROOT / SESSION_START_DISPATCH_CORE_PATH
    if not dispatcher_path.is_file():
        if os.environ.get("CI") == "true":
            return []
        return [f"missing Codex SessionStart hook dispatcher: {dispatcher_path}"]
    if not core_path.is_file():
        if os.environ.get("CI") == "true":
            return []
        return [f"missing shared SessionStart dispatch core: {core_path}"]
    # Slice D of GTKB-STARTUP-REFRACTOR-001: the behavioral SessionStart contract
    # lives in the shared core (scripts/session_start_dispatch_core.py); the codex
    # wrapper delegates. Verify the wrapper delegates, then check the core for the
    # behavioral tokens.
    errors: list[str] = []
    wrapper_text = dispatcher_path.read_text(encoding="utf-8")
    if _CORE_IMPORT_TOKEN not in wrapper_text:
        errors.append(
            f"Codex SessionStart hook dispatcher {dispatcher_path.name} must delegate to the "
            f"shared core ({_CORE_IMPORT_TOKEN})"
        )
    text = core_path.read_text(encoding="utf-8")
    errors.extend(
        _wrapper_errors(
            core_path,
            [
                "session_self_initialization.py",
                "--emit-startup-service-payload",
                "--fast-hook",
                "--harness-name",
                "--harness-id",
                "harness_identity",
                "resolved_harness_id",
                "STARTUP_SERVICE",
                "STARTUP_FRESHNESS_CONTRACT_VERSION",
                "Programmatic Startup Payload",
                "_valid_session_start_payload",
                "_purge_previous_diagnostics",
                "GTKB_STARTUP_REQUESTED_AT",
                "subprocess.run",
                "hookSpecificOutput",
                "hookEventName",
                "SessionStart",
                "additionalContext",
                "startupFreshness",
                "request_started_at",
                "report_origin",
                "startup_payload_fresh",
                "last-session-start.json",
                "last-session-start.err",
            ],
        )
    )
    for forbidden_term in (
        "Would you like to optimize token consumption now or defer to the next session? (Y/N)",
        "Would you like to proceed with established priority actions? (Y/N)",
        "Token Consumption Reduction Options second",
        "Three Top Priority Actions third",
    ):
        if forbidden_term in text:
            errors.append(
                f"Codex SessionStart hook dispatcher {dispatcher_path.name} must not include legacy first-response prompt text: {forbidden_term}"
            )
    for term in ("last-session-start.json", "last-session-start.err"):
        if term not in text:
            errors.append(
                f"Codex SessionStart hook dispatcher {dispatcher_path.name} must capture stdout/stderr diagnostics"
            )
    if "--role-profile" in text:
        errors.append("Codex SessionStart hook dispatcher must discover the role profile instead of forcing one")
    if "Startup First-Response Directive" in text or "_live_bridge_index_context" in text:
        errors.append("Codex SessionStart hook dispatcher must not assemble startup content in the adapter")
    if "SHA-256" in text or "Mandatory Direct Live Bridge Index Read" in text:
        errors.append("Codex SessionStart hook dispatcher must not embed bridge excerpts or hashes")
    return errors


def _codex_formal_hook_groups(codex_hooks: dict[str, Any]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for group in codex_hooks.get("hooks", {}).get("PreToolUse", []):
        commands = [hook.get("command", "") for hook in group.get("hooks", []) if isinstance(hook.get("command"), str)]
        if any(
            _contains_hook_path(command, FORMAL_APPROVAL_HOOK)
            or _contains_hook_wrapper(command, CODEX_FORMAL_APPROVAL_WRAPPER)
            for command in commands
        ):
            groups.append(group)
    return groups


def _codex_bridge_compliance_hook_groups(codex_hooks: dict[str, Any], event_name: str) -> list[dict[str, Any]]:
    """Return Codex hook groups whose commands reference the bridge-compliance family."""
    groups: list[dict[str, Any]] = []
    for group in codex_hooks.get("hooks", {}).get(event_name, []):
        commands = [hook.get("command", "") for hook in group.get("hooks", []) if isinstance(hook.get("command"), str)]
        if any(
            _contains_hook_path(command, BRIDGE_COMPLIANCE_HOOK)
            or _contains_hook_wrapper(command, CODEX_BRIDGE_COMPLIANCE_WRAPPER)
            or _contains_hook_wrapper(command, CODEX_BRIDGE_COMPLIANCE_AUDIT_DISPATCHER)
            for command in commands
        ):
            groups.append(group)
    return groups


def _codex_workstream_hook_groups(codex_hooks: dict[str, Any], event_name: str) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for group in codex_hooks.get("hooks", {}).get(event_name, []):
        commands = [hook.get("command", "") for hook in group.get("hooks", []) if isinstance(hook.get("command"), str)]
        if any(
            _contains_hook_path(command, WORKSTREAM_FOCUS_HOOK)
            or _contains_hook_wrapper(command, CODEX_WORKSTREAM_FOCUS_WRAPPER)
            for command in commands
        ):
            groups.append(group)
    return groups


def _function_body_text(source_text: str, function_name: str) -> str:
    """Return the body of a top-level function as one ``str``.

    Uses ``ast`` to locate the function node so multi-line signatures
    (e.g. keyword-only parameters spread across several lines) are handled
    correctly.  The returned text spans from the first statement of the
    body through the function's last line (per ``ast.AST.end_lineno``).
    Returns ``""`` if the function is not found at module scope.
    """

    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return ""
    lines = source_text.splitlines()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            if not node.body:
                return ""
            # ``ast`` line numbers are 1-indexed; ``end_lineno`` is the
            # inclusive last line.  Slicing on 0-indexed ``lines`` therefore
            # uses ``body[0].lineno - 1`` as the start index and
            # ``end_lineno`` as the exclusive end index.
            start_line = node.body[0].lineno - 1
            end_line = node.end_lineno or len(lines)
            return "\n".join(lines[start_line:end_line])
    return ""


def _is_top_level_call_statement(stmt: ast.stmt, function_name: str) -> bool:
    """Return True if ``stmt`` is a top-level statement that directly calls
    ``function_name``.

    Matches both ``func_name()`` (parsed as ``ast.Expr(value=ast.Call)``) and
    assignment forms like ``x = func_name()`` (``ast.Assign(value=ast.Call)``).
    Does NOT match calls inside ``if``/``for``/``while``/``try``/``with``
    bodies, nested function/class/lambda bodies, or any other compound
    statement — only direct children of the enclosing function body.
    """

    call: ast.Call | None = None
    if isinstance(stmt, (ast.Expr, ast.Assign, ast.AnnAssign)) and isinstance(stmt.value, ast.Call):
        call = stmt.value
    if call is None:
        return False
    return isinstance(call.func, ast.Name) and call.func.id == function_name


def _main_call_order_error(source_text: str, label: str) -> str | None:
    """Verify ``_invalidate_session_role_marker()`` is a *direct, unconditional
    top-level statement* in ``main()`` *before* the first
    ``_bridge_dispatch_keyword_check()`` top-level call.

    The v3 fix (addresses verification NO-GO -011 F1) iterates only
    ``main_node.body`` — direct child statements of the function — rather
    than descending into control-flow bodies.  This rejects placements like
    ``if False: _invalidate_session_role_marker()`` where the call is
    structurally present but not guaranteed to execute.  Returns ``None`` on
    pass or an error string when the contract is violated.

    The v5 fix (addresses verification NO-GO -015 F1) orders the two calls by
    their full source position ``(lineno, col_offset)`` rather than by line
    number alone.  Python executes semicolon-separated top-level statements
    left-to-right, so a single physical line
    ``x = _bridge_dispatch_keyword_check(); _invalidate_session_role_marker()``
    parses as two body statements sharing one ``lineno``.  Comparing line
    numbers alone treated that as "not after" (``N > N`` is False) and let the
    post-dispatch placement pass.  The ``col_offset`` tiebreaker makes the
    comparison reflect true execution order for same-line statements.
    """

    try:
        tree = ast.parse(source_text)
    except SyntaxError as exc:
        return f"{label} could not parse source for main()-order check: {exc}"
    main_node: ast.FunctionDef | None = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            main_node = node
            break
    if main_node is None:
        return f"{label} must define top-level `main()` function (resolution-table receiver entry point)"

    # Track the source position ``(lineno, col_offset)`` of the first matching
    # top-level call for each function.  Tuple comparison is lexicographic, so
    # two statements on the same physical line (semicolon-separated) order by
    # column — the second call on the line is correctly "after" the first.
    invalidate_pos: tuple[int, int] | None = None
    dispatch_pos: tuple[int, int] | None = None
    for stmt in main_node.body:
        if invalidate_pos is None and _is_top_level_call_statement(stmt, "_invalidate_session_role_marker"):
            invalidate_pos = (stmt.lineno, stmt.col_offset)
        if dispatch_pos is None and _is_top_level_call_statement(stmt, "_bridge_dispatch_keyword_check"):
            dispatch_pos = (stmt.lineno, stmt.col_offset)

    if invalidate_pos is None:
        return (
            f"{label} `main()` must call `_invalidate_session_role_marker()` as a direct, "
            "unconditional top-level statement (Slice 3 pre-dispatch marker-invalidation "
            "contract; placements inside `if`/`for`/`while`/`try`/`with` bodies, nested "
            "function/class/lambda bodies, comments, and helper-only calls do not satisfy "
            "this guarantee of execution)"
        )
    if dispatch_pos is None:
        return (
            f"{label} `main()` must call `_bridge_dispatch_keyword_check()` as a top-level "
            "statement (IP-4 dispatch fork)"
        )
    if invalidate_pos > dispatch_pos:
        return (
            f"{label} `main()` must call `_invalidate_session_role_marker()` "
            "BEFORE `_bridge_dispatch_keyword_check()` (Slice 3 pre-dispatch contract; "
            f"found invalidation at line {invalidate_pos[0]} col {invalidate_pos[1]}, "
            f"dispatch at line {dispatch_pos[0]} col {dispatch_pos[1]})"
        )
    return None


def _enum_member_declarations(stmt: ast.stmt) -> list[tuple[str, ast.expr | None]]:
    """Return ``(name, value_node)`` pairs for every Enum member declared by
    a class-body ``stmt``.

    Python's ``Enum`` metaclass promotes class-body assignments to members
    regardless of assignment shape, so the closed-vocabulary check must walk
    every shape that Python accepts:

    - ``ast.AnnAssign`` with a ``Name`` target AND a non-``None`` value
      (e.g. ``A: str = "a"``).  Bare annotations like ``A: str`` assign
      nothing and produce no member.
    - ``ast.Assign`` with one or more ``Name`` targets — both the simple
      ``A = "a"`` form AND the chained form ``A = B = "v"``.  In a chained
      assignment, every target shares the single ``stmt.value``.
    - ``ast.Assign`` with a tuple/list target of ``Name`` elements
      (e.g. ``A, B = "a", "b"``).  When ``stmt.value`` is a tuple/list literal
      of equal length, each declared name is paired with the matching value
      element; otherwise (e.g. ``A, B = obj_returning_tuple()``) the value
      cannot be resolved statically but every ``Name`` still declares a
      member with ``value_node`` set to ``None``.

    Other shapes (``Starred``, ``Attribute``, ``Subscript``, nested tuples)
    cannot declare a canonical Enum member from a class body and are skipped.

    v4 expansion (verification NO-GO -013 F1): the v3 implementation handled
    only single-target ``Assign`` and ``AnnAssign``, leaving chained and
    tuple/list-target assignment as escape hatches that Codex's sidecar probe
    proved bypassed the closed-vocabulary check.
    """

    if isinstance(stmt, ast.AnnAssign):
        if isinstance(stmt.target, ast.Name) and stmt.value is not None:
            return [(stmt.target.id, stmt.value)]
        return []

    if not isinstance(stmt, ast.Assign):
        return []

    pairs: list[tuple[str, ast.expr | None]] = []
    for target in stmt.targets:
        if isinstance(target, ast.Name):
            pairs.append((target.id, stmt.value))
            continue
        if not isinstance(target, (ast.Tuple, ast.List)):
            continue
        value_elts: list[ast.expr] | None = None
        if isinstance(stmt.value, (ast.Tuple, ast.List)) and len(stmt.value.elts) == len(target.elts):
            value_elts = list(stmt.value.elts)
        for index, elt in enumerate(target.elts):
            if not isinstance(elt, ast.Name):
                continue
            elt_value = value_elts[index] if value_elts is not None else None
            pairs.append((elt.id, elt_value))
    return pairs


def _startup_decision_vocabulary_errors(source_text: str, label: str) -> list[str]:
    """Verify ``class StartupDecision(Enum)`` is the closed five-member set
    declared in ``_STARTUP_DECISION_EXPECTED``.

    Parses the ClassDef via ``ast`` and walks every assignment shape that
    Python's Enum metaclass treats as a member declaration (see
    ``_enum_member_declarations``).  An extra member, a missing member, or a
    divergent value all produce a deterministic error string (addresses
    verification NO-GO -006 F2, -009 F2, -011 F2, and -013 F1).
    """

    try:
        tree = ast.parse(source_text)
    except SyntaxError as exc:
        return [f"{label} could not parse source for StartupDecision vocabulary check: {exc}"]
    class_node: ast.ClassDef | None = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "StartupDecision":
            class_node = node
            break
    if class_node is None:
        return [
            f"{label} must define `class StartupDecision(Enum):` "
            "(IP-4 enum cleanup; spec-revision successor of scoping-003 INTERACTIVE_OVERRIDE_AUTHORIZED)"
        ]

    declared_names: set[str] = set()
    string_values: dict[str, str] = {}
    for stmt in class_node.body:
        for target_name, value_node in _enum_member_declarations(stmt):
            declared_names.add(target_name)
            if isinstance(value_node, ast.Constant) and isinstance(value_node.value, str):
                string_values[target_name] = value_node.value

    errors: list[str] = []
    expected_names = set(_STARTUP_DECISION_EXPECTED)
    for name in sorted(expected_names - declared_names):
        errors.append(
            f"{label} `StartupDecision` is missing member "
            f'`{name} = "{_STARTUP_DECISION_EXPECTED[name]}"` '
            "(IP-4 five-value vocabulary)"
        )
    for name in sorted(declared_names - expected_names):
        errors.append(
            f"{label} `StartupDecision` contains unapproved extra member `{name}` "
            "(IP-4 vocabulary is closed at five values per bridge "
            "gtkb-canonical-init-keyword-syntax-001-005..009)"
        )
    for name in sorted(expected_names & declared_names):
        expected_value = _STARTUP_DECISION_EXPECTED[name]
        if name not in string_values:
            errors.append(
                f"{label} `StartupDecision.{name}` must be assigned the string "
                f'`"{expected_value}"` (found non-string expression)'
            )
            continue
        if string_values[name] != expected_value:
            errors.append(
                f'{label} `StartupDecision.{name}` value must equal `"{expected_value}"`, '
                f'found `"{string_values[name]}"`'
            )
    return errors


def _bridge_dispatch_behavior_table_errors(source_text: str, label: str) -> list[str]:
    """Verify the ``_bridge_dispatch_keyword_check`` docstring contains the
    five-token behavior-table header row anchored to actual table structure
    (preceded AND followed by separator rows of ``=`` characters).

    v3 fix (addresses verification NO-GO -011 F3): line-based anchoring
    replaces the unanchored token-order regex.  A line matching exactly
    ``env-var keyword mode-in-role-set Decision Effect`` (whitespace-only
    between tokens) AND flanked above and below by separator rows (lines
    of ``=`` segments separated by whitespace, matching the
    reStructuredText-style table-rule pattern) is required.  Prose
    sentences containing the tokens in order with whitespace separation no
    longer match because they lack the surrounding ``=`` separator lines.
    """

    try:
        tree = ast.parse(source_text)
    except SyntaxError as exc:
        return [f"{label} could not parse source for behavior-table check: {exc}"]
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_bridge_dispatch_keyword_check":
            docstring = ast.get_docstring(node) or ""
            if not _docstring_has_anchored_header_row(docstring):
                return [
                    f"{label} `_bridge_dispatch_keyword_check` docstring must contain the "
                    "five-token behavior-table header row "
                    "(`env-var keyword mode-in-role-set Decision Effect`) anchored by "
                    "separator rows of `=` characters above AND below; prose mentions of the "
                    "tokens (even in order, even with whitespace separation) do not satisfy "
                    "this because they lack the table-structure anchor "
                    "(GO -004 acceptance criteria; NO-GO -011 F3)"
                ]
            return []
    # No FunctionDef found — assertion 6's "must define" path handles this.
    return []


def _docstring_has_anchored_header_row(docstring: str) -> bool:
    """Return True if ``docstring`` contains the behavior-table header row
    flanked by separator rows of ``=`` characters above AND below.
    """

    lines = docstring.splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not _HEADER_ROW_RE.match(stripped):
            continue
        if idx == 0 or idx == len(lines) - 1:
            continue
        if _SEPARATOR_ROW_RE.match(lines[idx - 1].strip()) and _SEPARATOR_ROW_RE.match(lines[idx + 1].strip()):
            return True
    return False


def _module_dict_literal_dump(source_text: str, name: str) -> str:
    """Return ``ast.dump`` of the module-level dict literal assigned to ``name``.

    Used to compare resolution-table dicts (e.g. ``_LABEL_TO_CANONICAL_MODE``)
    between the two SessionStart dispatchers byte-equivalently while
    normalising over insignificant whitespace differences.  Returns ``""`` if
    the assignment is absent or its right-hand side is not a dict literal.
    """

    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return ""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name and isinstance(node.value, ast.Dict):
                    return ast.dump(node.value)
    return ""


def _module_str_dict(source_text: str, name: str) -> dict[str, str] | None:
    """Return the module-level ``{str: str}`` dict literal assigned to ``name``.

    Returns ``None`` if the assignment is absent, its RHS is not a dict literal,
    or any key/value is not a string constant (so non-string drift is reported
    as "not a string dict" rather than silently accepted).
    """

    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name and isinstance(node.value, ast.Dict):
                result: dict[str, str] = {}
                for key_node, value_node in zip(node.value.keys, node.value.values):
                    if (
                        isinstance(key_node, ast.Constant)
                        and isinstance(key_node.value, str)
                        and isinstance(value_node, ast.Constant)
                        and isinstance(value_node.value, str)
                    ):
                        result[key_node.value] = value_node.value
                    else:
                        return None
                return result
    return None


def _resolution_table_parity_errors(project_root: Path) -> list[str]:
    """Resolution-table contract parity assertions for the SessionStart dispatch core.

    Slice D of GTKB-STARTUP-REFRACTOR-001 (WI-4272) extracted the shared
    SessionStart primitives from the two byte-identical wrappers into one core
    module (``scripts/session_start_dispatch_core.py``). The primitive
    assertions (marker constant, ``StartupDecision`` enum, canonical
    init-keyword regex, the label/profile dicts, marker invalidation, the
    behavior-table receiver, the audit-log primitives, the cache-writer
    invariant) now check the single core source. The wrappers are checked for
    (a) delegation to the core and (b) the intentional-difference guard
    (HARNESS_NAME + OUT_DIR). The resolver and UPS writer keep their own marker
    constant. Originally Slice 8 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
    (WI-3478); relocated by Slice D per
    ``bridge/gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-004.md``.
    """

    errors: list[str] = []
    core_path = project_root / SESSION_START_DISPATCH_CORE_PATH
    claude_dispatcher_path = project_root / CLAUDE_SESSION_START_DISPATCHER
    codex_dispatcher_path = project_root / CODEX_SESSION_START_DISPATCHER_PATH
    resolver_path = project_root / SESSION_ROLE_RESOLVER_PATH
    workstream_focus_path = project_root / WORKSTREAM_FOCUS_PATH

    required_sources: dict[str, Path] = {
        "SessionStart dispatch core": core_path,
        "Claude SessionStart dispatcher": claude_dispatcher_path,
        "Codex SessionStart dispatcher": codex_dispatcher_path,
        "Session role resolver (scripts/session_role_resolution.py)": resolver_path,
        "Workstream focus writer (scripts/workstream_focus.py)": workstream_focus_path,
    }
    sources: dict[str, str] = {}
    for label, path in required_sources.items():
        if not path.is_file():
            errors.append(f"{label} not found at {path.relative_to(project_root).as_posix()}")
            continue
        sources[label] = path.read_text(encoding="utf-8")
    if errors:
        return errors

    core_text = sources["SessionStart dispatch core"]
    claude_text = sources["Claude SessionStart dispatcher"]
    codex_text = sources["Codex SessionStart dispatcher"]
    core_label = "SessionStart dispatch core"

    # ----- Assertion 1: marker constant parity ----------------------------
    # The core (which invalidates the marker), the resolver, and the UPS writer
    # must contain the exact ``_SESSION_ROLE_MARKER_NAME = "active-session-role.json"``
    # literal. The thin wrappers delegate to the core and do not redefine it.
    for label in (
        "SessionStart dispatch core",
        "Session role resolver (scripts/session_role_resolution.py)",
        "Workstream focus writer (scripts/workstream_focus.py)",
    ):
        if _MARKER_CONSTANT_LITERAL not in sources[label]:
            errors.append(
                f"{label} must contain marker-constant literal "
                f"`{_MARKER_CONSTANT_LITERAL}` "
                "(DCL-SESSION-ROLE-RESOLUTION-001 Slice 4 invariant)"
            )

    # ----- Assertion 2: StartupDecision enum parity (CLOSED set) ----------
    # AST-parse the core's ``class StartupDecision(Enum)`` and verify the EXACT
    # five-member vocabulary. Closed-set semantics — extra/missing members or
    # wrong values all fail.
    errors.extend(_startup_decision_vocabulary_errors(core_text, core_label))

    # ----- Assertion 3: canonical init-keyword regex parity ---------------
    if _CANONICAL_KEYWORD_RE_LITERAL not in core_text:
        errors.append(
            f"{core_label} must contain canonical init-keyword regex literal "
            f"`{_CANONICAL_KEYWORD_RE_LITERAL}` "
            "(SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001)"
        )

    # ----- Assertion 4: label and profile map content ---------------------
    # Single-sourced: the old "two dispatchers must be ast-equivalent" check is
    # moot (one copy). Assert the core's dict literals equal the canonical
    # resolution-table mappings, so content drift in the single source fails.
    for dict_name, expected in _EXPECTED_RESOLUTION_DICTS.items():
        actual = _module_str_dict(core_text, dict_name)
        if actual is None:
            errors.append(f"{core_label} must define module-level string dict `{dict_name}` (resolution-table parity)")
        elif actual != expected:
            errors.append(
                f"{core_label} `{dict_name}` must equal the canonical resolution-table "
                f"mapping {expected!r}; found {actual!r} (resolution-table parity)"
            )

    # ----- Assertion 5: marker invalidation parity (PRE-DISPATCH order) ---
    # AST-walk the core's ``main()`` and verify
    # ``_invalidate_session_role_marker()`` is called as an executable statement
    # before the first ``_bridge_dispatch_keyword_check()`` call.
    if "def _invalidate_session_role_marker(" not in core_text:
        errors.append(
            f"{core_label} must define `_invalidate_session_role_marker()` "
            "(scoping-003 Slice 3 marker-invalidation parity)"
        )
    if "def _session_role_marker_path(" not in core_text:
        errors.append(
            f"{core_label} must define `_session_role_marker_path()` resolving to the canonical marker location"
        )
    order_error = _main_call_order_error(core_text, core_label)
    if order_error is not None:
        errors.append(order_error)

    # ----- Assertion 6: behavior-table parity -----------------------------
    # The core's ``_bridge_dispatch_keyword_check`` must reference each of the
    # five StartupDecision members AND document the behavior-table header row.
    if "def _bridge_dispatch_keyword_check(" not in core_text:
        errors.append(f"{core_label} must define `_bridge_dispatch_keyword_check()` (resolution-table receiver)")
    else:
        body_text = _function_body_text(core_text, "_bridge_dispatch_keyword_check")
        for member_name in (
            "StartupDecision.NORMAL_STARTUP",
            "StartupDecision.DISPATCH_AUTHORIZED",
            "StartupDecision.SPOOF_FALLBACK",
            "StartupDecision.LEGACY_FALLBACK",
            "StartupDecision.STRICT_DROP",
        ):
            if member_name not in body_text:
                errors.append(
                    f"{core_label} `_bridge_dispatch_keyword_check()` must reference "
                    f"`{member_name}` (IP-4 five-decision receiver vocabulary)"
                )
        errors.extend(_bridge_dispatch_behavior_table_errors(core_text, core_label))

    # ----- Assertion 7: audit-log parity ----------------------------------
    # The core must define ``_audit_log_misdirected_dispatch`` and carry the
    # canonical kind literal + dispatch-failures path token.
    if "def _audit_log_misdirected_dispatch(" not in core_text:
        errors.append(f"{core_label} must define `_audit_log_misdirected_dispatch()` (STRICT_DROP audit record)")
    if _AUDIT_LOG_KIND_LITERAL not in core_text:
        errors.append(f"{core_label} must reference audit-record kind literal {_AUDIT_LOG_KIND_LITERAL}")
    if _AUDIT_LOG_PATH_TOKEN not in core_text:
        errors.append(f"{core_label} must reference audit-log path token `{_AUDIT_LOG_PATH_TOKEN}`")

    # ----- Assertion 8: intentional-difference catalogue (wrappers) -------
    # Each WRAPPER must contain its OWN HARNESS_NAME and OUT_DIR assignments
    # AND must NOT contain the OTHER wrapper's assignments. Precise assignment
    # literals avoid false matches on docstring cross-references.
    if _CLAUDE_HARNESS_NAME_LITERAL not in claude_text:
        errors.append(
            f"Claude SessionStart dispatcher must contain `{_CLAUDE_HARNESS_NAME_LITERAL}` "
            "(intentional-difference guard)"
        )
    if _CODEX_HARNESS_NAME_LITERAL in claude_text:
        errors.append(
            f"Claude SessionStart dispatcher must not contain `{_CODEX_HARNESS_NAME_LITERAL}` "
            "(intentional-difference guard against copy-paste-of-harness-name drift)"
        )
    if _CODEX_HARNESS_NAME_LITERAL not in codex_text:
        errors.append(
            f"Codex SessionStart dispatcher must contain `{_CODEX_HARNESS_NAME_LITERAL}` (intentional-difference guard)"
        )
    if _CLAUDE_HARNESS_NAME_LITERAL in codex_text:
        errors.append(
            f"Codex SessionStart dispatcher must not contain `{_CLAUDE_HARNESS_NAME_LITERAL}` "
            "(intentional-difference guard against copy-paste-of-harness-name drift)"
        )
    if _CLAUDE_OUT_DIR_LITERAL not in claude_text:
        errors.append(
            f"Claude SessionStart dispatcher must contain `{_CLAUDE_OUT_DIR_LITERAL}` (intentional-difference guard)"
        )
    if _CODEX_OUT_DIR_LITERAL in claude_text:
        errors.append(
            f"Claude SessionStart dispatcher must not contain `{_CODEX_OUT_DIR_LITERAL}` (intentional-difference guard)"
        )
    if _CODEX_OUT_DIR_LITERAL not in codex_text:
        errors.append(
            f"Codex SessionStart dispatcher must contain `{_CODEX_OUT_DIR_LITERAL}` (intentional-difference guard)"
        )
    if _CLAUDE_OUT_DIR_LITERAL in codex_text:
        errors.append(
            f"Codex SessionStart dispatcher must not contain `{_CLAUDE_OUT_DIR_LITERAL}` (intentional-difference guard)"
        )

    # ----- Assertion 9: cache-writer parity (core single source) ----------
    # The core's ``_write_role_scoped_startup_relay_caches`` must iterate
    # ``_MODE_TO_ROLE_PROFILE`` and skip ``primary_mode`` and must NOT reference
    # ``_resolve_own_role_set`` (the pre-Slice-1 defective shape).
    if "def _write_role_scoped_startup_relay_caches(" not in core_text:
        errors.append(f"{core_label} must define `_write_role_scoped_startup_relay_caches()` (Slice 1 cache-writer)")
    else:
        body_text = _function_body_text(core_text, "_write_role_scoped_startup_relay_caches")
        if _CACHE_WRITER_LOOP_LITERAL not in body_text:
            errors.append(
                f"{core_label} `_write_role_scoped_startup_relay_caches()` must iterate "
                f"`{_CACHE_WRITER_LOOP_LITERAL}` "
                "(Slice 1 cache-writer fix; writes both -pb.md and -lo.md unconditionally per "
                "ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 2)"
            )
        if _CACHE_WRITER_SKIP_LITERAL not in body_text:
            errors.append(
                f"{core_label} `_write_role_scoped_startup_relay_caches()` must skip the primary "
                f"mode via `{_CACHE_WRITER_SKIP_LITERAL}` (Slice 1 cache-writer fix)"
            )
        if _CACHE_WRITER_FORBIDDEN_LITERAL in body_text:
            errors.append(
                f"{core_label} `_write_role_scoped_startup_relay_caches()` must NOT reference "
                f"`{_CACHE_WRITER_FORBIDDEN_LITERAL}` "
                "(pre-Slice-1 defective shape that conditioned cache writes on the durable "
                "role set; regression per scoping-003 line 71)"
            )

    # ----- Assertion 10: wrapper delegation (Slice D) ---------------------
    # Each thin wrapper must import the shared core and rebind its functions,
    # so the de-duplication cannot silently regress to local copies.
    for label, text in (
        ("Claude SessionStart dispatcher", claude_text),
        ("Codex SessionStart dispatcher", codex_text),
    ):
        if _CORE_IMPORT_TOKEN not in text:
            errors.append(
                f"{label} must delegate to the shared core via `{_CORE_IMPORT_TOKEN}` (Slice D de-duplication)"
            )
        if _CORE_REBIND_TOKEN not in text:
            errors.append(
                f"{label} must rebind shared core functions onto its namespace via "
                f"`{_CORE_REBIND_TOKEN}` (Slice D de-duplication)"
            )

    return errors


def check_project(project_root: Path = PROJECT_ROOT) -> list[str]:
    """Return parity errors for the configured project, or an empty list."""

    errors: list[str] = []
    codex_config_path = project_root / CODEX_CONFIG
    codex_hooks_path = project_root / CODEX_HOOKS
    claude_settings_path = project_root / CLAUDE_SETTINGS
    formal_hook_path = project_root / FORMAL_APPROVAL_HOOK
    bridge_compliance_hook_path = project_root / BRIDGE_COMPLIANCE_HOOK
    workstream_hook_path = project_root / WORKSTREAM_FOCUS_HOOK
    session_startup_path = project_root / SESSION_SELF_INITIALIZATION_SCRIPT
    harness_identity_path = project_root / HARNESS_IDENTITY_RECORD
    role_assignment_path = project_root / ROLE_ASSIGNMENT_RECORD

    for path in (
        codex_config_path,
        codex_hooks_path,
        claude_settings_path,
        formal_hook_path,
        bridge_compliance_hook_path,
        workstream_hook_path,
        session_startup_path,
        harness_identity_path,
        role_assignment_path,
    ):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(project_root).as_posix()}")

    if errors:
        return errors

    codex_config = _load_toml(codex_config_path)
    codex_hooks = _load_json(codex_hooks_path)
    claude_settings = _load_json(claude_settings_path)

    if codex_config.get("features", {}).get("codex_hooks") is not True:
        errors.append(".codex/config.toml must set [features].codex_hooks = true")

    claude_pre_tool_commands = _commands_for_event(claude_settings, "PreToolUse")
    if not any(_contains_hook_path(command, FORMAL_APPROVAL_HOOK) for command in claude_pre_tool_commands):
        errors.append(".claude/settings.json does not register the formal artifact approval PreToolUse hook")

    claude_session_commands = _commands_for_event(claude_settings, "SessionStart")
    # Per gtkb-claude-session-start-parity GO at -002, the Claude SessionStart
    # hook may register the canonical script directly (legacy contract) OR a
    # dispatcher under .claude/hooks/ whose source delegates to the canonical
    # script with the startup-service payload contract. Both shapes preserve
    # the same governance contract: a SessionStart hookSpecificOutput envelope
    # is produced from the canonical service.
    direct_session = any(
        _contains_hook_path(command, SESSION_SELF_INITIALIZATION_SCRIPT) for command in claude_session_commands
    )
    dispatcher_session = any(
        _contains_hook_path(command, CLAUDE_SESSION_START_DISPATCHER) for command in claude_session_commands
    )
    if not (direct_session or dispatcher_session):
        errors.append(
            ".claude/settings.json must register either the session-self-initialization "
            "SessionStart hook directly or a dispatcher under .claude/hooks/ that "
            "delegates to it"
        )

    if dispatcher_session:
        # Dispatcher pattern: Slice D — verify the wrapper delegates to the
        # shared core and the core carries the startup-service contract.
        dispatcher_path = PROJECT_ROOT / CLAUDE_SESSION_START_DISPATCHER
        core_path = PROJECT_ROOT / SESSION_START_DISPATCH_CORE_PATH
        if not dispatcher_path.is_file():
            errors.append(f"{CLAUDE_SESSION_START_DISPATCHER} referenced by SessionStart hook does not exist")
        elif not core_path.is_file():
            errors.append(f"{SESSION_START_DISPATCH_CORE_PATH} (shared SessionStart dispatch core) does not exist")
        else:
            dispatcher_source = dispatcher_path.read_text(encoding="utf-8")
            core_source = core_path.read_text(encoding="utf-8")
            if _CORE_IMPORT_TOKEN not in dispatcher_source:
                errors.append(f"Claude SessionStart dispatcher must delegate to the shared core ({_CORE_IMPORT_TOKEN})")
            if "session_self_initialization.py" not in core_source:
                errors.append("Claude SessionStart dispatch core must delegate to session_self_initialization.py")
            if "--emit-startup-service-payload" not in core_source:
                errors.append("Claude SessionStart dispatch core must use the --emit-startup-service-payload contract")
            if "--fast-hook" not in core_source:
                errors.append("Claude SessionStart dispatch core must use the fast lifecycle hook path")
            if "--harness-name" not in core_source:
                errors.append("Claude SessionStart dispatch core must pass --harness-name")
            if "claude" not in dispatcher_source:
                errors.append("Claude SessionStart dispatcher must identify the Claude harness type")
    elif direct_session:
        # Legacy direct-invocation pattern: preserve the original assertions.
        if not any("--emit-report" in command for command in claude_session_commands):
            errors.append("Claude SessionStart hook must emit the startup report")
        if not any("--fast-hook" in command for command in claude_session_commands):
            errors.append("Claude SessionStart hook must use the fast lifecycle hook path")
        if not any("--harness-name claude" in command for command in claude_session_commands):
            errors.append("Claude SessionStart hook must identify the Claude harness type")
    if any("--harness-id B" in command for command in claude_session_commands):
        errors.append("Claude SessionStart hook must resolve durable ID from harness-state/harness-identities.json")
    if any("--role-profile" in command for command in claude_session_commands):
        errors.append("Claude SessionStart hook must discover the role profile instead of forcing one")
    if not any(
        _contains_hook_path(command, SINGLE_HARNESS_AUTOMATION_SCRIPT) and "--ensure" in command
        for command in claude_session_commands
    ):
        errors.append(".claude/settings.json does not register the single-harness bridge automation SessionStart hook")

    claude_stop_commands = _commands_for_event(claude_settings, "Stop")
    if not any(_contains_hook_path(command, SESSION_SELF_INITIALIZATION_SCRIPT) for command in claude_stop_commands):
        errors.append(".claude/settings.json does not register the proactive session wrap-up Stop hook")
    if not any("--emit-wrapup" in command for command in claude_stop_commands):
        errors.append("Claude Stop hook must emit the proactive wrap-up report")
    if not any("--fast-hook" in command for command in claude_stop_commands):
        errors.append("Claude Stop hook must use the fast lifecycle hook path")
    if not any("--harness-name claude" in command for command in claude_stop_commands):
        errors.append("Claude Stop hook must identify the Claude harness type")
    if any("--harness-id B" in command for command in claude_stop_commands):
        errors.append("Claude Stop hook must resolve durable ID from harness-state/harness-identities.json")
    if any("--role-profile" in command for command in claude_stop_commands):
        errors.append("Claude Stop hook must discover the role profile instead of forcing one")
    if not any(
        _contains_hook_path(command, SINGLE_HARNESS_AUTOMATION_SCRIPT)
        and "--ensure" in command
        and "--dispatch-now" in command
        for command in claude_stop_commands
    ):
        errors.append(".claude/settings.json does not register the single-harness bridge automation Stop hook")

    formal_groups = _codex_formal_hook_groups(codex_hooks)
    if not formal_groups:
        errors.append(".codex/hooks.json does not register the formal artifact approval PreToolUse hook")
    for group in formal_groups:
        if group.get("matcher") != "Bash":
            errors.append("Codex formal artifact PreToolUse hook must use matcher = 'Bash'")
        for hook in group.get("hooks", []):
            command = hook.get("command", "")
            if not isinstance(command, str) or not (
                _contains_hook_path(command, FORMAL_APPROVAL_HOOK)
                or _contains_hook_wrapper(command, CODEX_FORMAL_APPROVAL_WRAPPER)
            ):
                continue
            if hook.get("type") != "command":
                errors.append("Codex formal artifact hook must be a command hook")
            if _uses_shell_command_substitution(command):
                errors.append("Codex formal artifact hook command must avoid shell command substitution")
            if not _contains_hook_wrapper(command, CODEX_FORMAL_APPROVAL_WRAPPER):
                errors.append("Codex formal artifact hook command must call the no-space wrapper")
            timeout = hook.get("timeout")
            if not isinstance(timeout, int) or timeout > 10:
                errors.append("Codex formal artifact hook timeout must be an integer no greater than 10 seconds")

    errors.extend(_wrapper_errors(CODEX_FORMAL_APPROVAL_WRAPPER, [FORMAL_APPROVAL_HOOK.replace("/", "\\")]))

    claude_has_bridge_compliance = any(
        _contains_hook_path(command, BRIDGE_COMPLIANCE_HOOK) for command in claude_pre_tool_commands
    )
    codex_hooks_enabled = codex_config.get("features", {}).get("codex_hooks") is True
    if claude_has_bridge_compliance and codex_hooks_enabled:
        bridge_pre_groups = _codex_bridge_compliance_hook_groups(codex_hooks, "PreToolUse")
        if not bridge_pre_groups:
            errors.append(
                ".codex/hooks.json must register the bridge-compliance PreToolUse:Bash hook when "
                "Claude's bridge-compliance-gate.py is active "
                "(per SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001 A1)"
            )
        for group in bridge_pre_groups:
            if group.get("matcher") != "Bash":
                errors.append("Codex bridge-compliance PreToolUse hook must use matcher = 'Bash'")
            for hook in group.get("hooks", []):
                command = hook.get("command", "")
                if not isinstance(command, str) or not (
                    _contains_hook_path(command, BRIDGE_COMPLIANCE_HOOK)
                    or _contains_hook_wrapper(command, CODEX_BRIDGE_COMPLIANCE_WRAPPER)
                ):
                    continue
                if hook.get("type") != "command":
                    errors.append("Codex bridge-compliance hook must be a command hook")
                if _uses_shell_command_substitution(command):
                    errors.append("Codex bridge-compliance hook command must avoid shell command substitution")
                if not _contains_hook_wrapper(command, CODEX_BRIDGE_COMPLIANCE_WRAPPER):
                    errors.append("Codex bridge-compliance hook command must call the no-space wrapper")
                timeout = hook.get("timeout")
                if not isinstance(timeout, int) or timeout > 5:
                    errors.append("Codex bridge-compliance hook timeout must be an integer no greater than 5 seconds")

        bridge_post_groups = _codex_bridge_compliance_hook_groups(codex_hooks, "PostToolUse")
        if not bridge_post_groups:
            errors.append(
                ".codex/hooks.json must register the bridge-compliance PostToolUse:Bash audit hook when "
                "Claude's bridge-compliance-gate.py is active "
                "(per SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001 A1)"
            )
        for group in bridge_post_groups:
            if group.get("matcher") not in ("Bash", None, ""):
                errors.append("Codex bridge-compliance PostToolUse hook must use matcher = 'Bash' or no matcher")
            for hook in group.get("hooks", []):
                command = hook.get("command", "")
                if not isinstance(command, str) or not (
                    _contains_hook_path(command, BRIDGE_COMPLIANCE_HOOK)
                    or _contains_hook_wrapper(command, CODEX_BRIDGE_COMPLIANCE_AUDIT_DISPATCHER)
                ):
                    continue
                if hook.get("type") != "command":
                    errors.append("Codex bridge-compliance audit hook must be a command hook")
                if _uses_shell_command_substitution(command):
                    errors.append("Codex bridge-compliance audit command must avoid shell command substitution")
                if not _contains_hook_wrapper(command, CODEX_BRIDGE_COMPLIANCE_AUDIT_DISPATCHER):
                    errors.append("Codex bridge-compliance audit command must call the no-space wrapper")
                timeout = hook.get("timeout")
                if not isinstance(timeout, int) or timeout > 5:
                    errors.append("Codex bridge-compliance audit timeout must be an integer no greater than 5 seconds")

        errors.extend(
            _wrapper_errors(
                CODEX_BRIDGE_COMPLIANCE_WRAPPER,
                [BRIDGE_COMPLIANCE_HOOK.replace("/", "\\"), "bridge-compliance-gate-bash-adapter.py"],
            )
        )
        errors.extend(
            _wrapper_errors(
                CODEX_BRIDGE_COMPLIANCE_ADAPTER,
                ["bridge-compliance-gate.py", "BRIDGE_FILE_WRITE_PATTERNS", "synthetic Claude-shape"],
            )
        )
        errors.extend(
            _wrapper_errors(
                CODEX_BRIDGE_COMPLIANCE_AUDIT_DISPATCHER,
                [BRIDGE_COMPLIANCE_HOOK.replace("/", "\\"), "--audit-only"],
            )
        )

    workstream_pre_tool_groups = _codex_workstream_hook_groups(codex_hooks, "PreToolUse")
    if not workstream_pre_tool_groups:
        errors.append(".codex/hooks.json does not register the workstream focus PreToolUse hook")
    for group in workstream_pre_tool_groups:
        if group.get("matcher") != "Bash":
            errors.append("Codex workstream focus PreToolUse hook must use matcher = 'Bash'")
        for hook in group.get("hooks", []):
            command = hook.get("command", "")
            if not isinstance(command, str) or not (
                _contains_hook_path(command, WORKSTREAM_FOCUS_HOOK)
                or _contains_hook_wrapper(command, CODEX_WORKSTREAM_FOCUS_WRAPPER)
            ):
                continue
            if hook.get("type") != "command":
                errors.append("Codex workstream focus hook must be a command hook")
            if _uses_shell_command_substitution(command):
                errors.append("Codex workstream focus hook command must avoid shell command substitution")
            if not _contains_hook_wrapper(command, CODEX_WORKSTREAM_FOCUS_WRAPPER):
                errors.append("Codex workstream focus hook command must call the no-space wrapper")
            timeout = hook.get("timeout")
            if not isinstance(timeout, int) or timeout > 10:
                errors.append("Codex workstream focus hook timeout must be an integer no greater than 10 seconds")

    workstream_prompt_groups = _codex_workstream_hook_groups(codex_hooks, "UserPromptSubmit")
    if not workstream_prompt_groups:
        errors.append(".codex/hooks.json does not register the workstream focus UserPromptSubmit hook")
    for group in workstream_prompt_groups:
        for hook in group.get("hooks", []):
            command = hook.get("command", "")
            if not isinstance(command, str) or not (
                _contains_hook_path(command, WORKSTREAM_FOCUS_HOOK)
                or _contains_hook_wrapper(command, CODEX_WORKSTREAM_FOCUS_WRAPPER)
            ):
                continue
            if hook.get("type") != "command":
                errors.append("Codex workstream focus UserPromptSubmit hook must be a command hook")
            if _uses_shell_command_substitution(command):
                errors.append("Codex workstream focus UserPromptSubmit command must avoid shell command substitution")
            if not _contains_hook_wrapper(command, CODEX_WORKSTREAM_FOCUS_WRAPPER):
                errors.append("Codex workstream focus UserPromptSubmit command must call the no-space wrapper")
            timeout = hook.get("timeout")
            if not isinstance(timeout, int) or timeout > 10:
                errors.append("Codex workstream focus UserPromptSubmit timeout must be no greater than 10 seconds")

    errors.extend(_wrapper_errors(CODEX_WORKSTREAM_FOCUS_WRAPPER, [WORKSTREAM_FOCUS_HOOK.replace("/", "\\")]))
    errors.extend(_wrapper_errors(CODEX_WORKSTREAM_FOCUS_WRAPPER, ["GTKB_HARNESS_NAME=codex"]))
    if CODEX_WORKSTREAM_FOCUS_WRAPPER.is_file() and "GTKB_HARNESS_ID=A" in CODEX_WORKSTREAM_FOCUS_WRAPPER.read_text(
        encoding="utf-8"
    ):
        errors.append("Codex workstream wrapper must resolve durable ID from harness-state/harness-identities.json")
    errors.extend(
        _wrapper_errors(
            CODEX_SESSION_START_WRAPPER,
            ["harness_identity.py", "GTKB_HARNESS_ID", "--harness-name codex", "--harness-id %GTKB_HARNESS_ID%"],
        )
    )
    errors.extend(
        _wrapper_errors(
            CODEX_SESSION_STOP_DISPATCHER,
            ["--emit-wrapup", "--harness-name", "--harness-id", 'HARNESS_NAME = "codex"', "resolved_harness_id"],
        )
    )
    if CODEX_SESSION_STOP_DISPATCHER.is_file() and 'HARNESS_ID = "A"' in CODEX_SESSION_STOP_DISPATCHER.read_text(
        encoding="utf-8"
    ):
        errors.append("Codex legacy session_stop_dispatch.py must not hardcode harness ID A")
    if CODEX_SESSION_STOP_DISPATCHER.is_file() and "--role-profile" in CODEX_SESSION_STOP_DISPATCHER.read_text(
        encoding="utf-8"
    ):
        errors.append("Codex legacy session_stop_dispatch.py must discover the role profile instead of forcing one")
    stop_commands = _commands_for_event(codex_hooks, "Stop")
    if not any(
        _contains_hook_path(command, SINGLE_HARNESS_AUTOMATION_SCRIPT)
        and "--ensure" in command
        and "--dispatch-now" in command
        for command in stop_commands
    ):
        errors.append(".codex/hooks.json does not register the single-harness bridge automation Stop hook")
    if any(
        _contains_hook_path(command, SESSION_SELF_INITIALIZATION_SCRIPT)
        or _contains_hook_wrapper(command, CODEX_SESSION_STOP_DISPATCHER)
        or _contains_hook_wrapper(command, CODEX_WRAPUP_TRIGGER_DISPATCHER)
        for command in stop_commands
    ):
        errors.append(
            "Codex wrap-up must not be registered on Stop; use the explicit UserPromptSubmit trigger dispatcher"
        )

    lifecycle_wrappers = {
        "SessionStart": (CODEX_SESSION_START_DISPATCHER, "--emit-report"),
        "UserPromptSubmit": (CODEX_WRAPUP_TRIGGER_DISPATCHER, "--emit-wrapup"),
    }

    for event_name, (wrapper_path, _required_flag) in lifecycle_wrappers.items():
        hook_entries = [
            hook
            for group in codex_hooks.get("hooks", {}).get(event_name, [])
            for hook in group.get("hooks", [])
            if isinstance(hook.get("command"), str)
        ]
        commands = [hook["command"] for hook in hook_entries]
        matching_commands = [
            command
            for command in commands
            if _contains_hook_path(command, SESSION_SELF_INITIALIZATION_SCRIPT)
            or _contains_hook_wrapper(command, wrapper_path)
        ]
        if not matching_commands:
            errors.append(f".codex/hooks.json does not register the {event_name} session lifecycle hook")
        for command in matching_commands:
            if _uses_shell_command_substitution(command):
                errors.append(f"Codex {event_name} hook command must avoid shell command substitution")
            if not _contains_hook_wrapper(command, wrapper_path):
                errors.append(f"Codex {event_name} hook command must call the no-space wrapper")
        if event_name == "SessionStart":
            if not any(
                _contains_hook_path(command, SINGLE_HARNESS_AUTOMATION_SCRIPT) and "--ensure" in command
                for command in commands
            ):
                errors.append(
                    ".codex/hooks.json does not register the single-harness bridge automation SessionStart hook"
                )
            for hook in hook_entries:
                command = hook["command"]
                if not (
                    _contains_hook_path(command, SESSION_SELF_INITIALIZATION_SCRIPT)
                    or _contains_hook_wrapper(command, wrapper_path)
                ):
                    continue
                timeout = hook.get("timeout")
                if not isinstance(timeout, int) or timeout < 60:
                    errors.append("Codex SessionStart hook timeout must be at least 60 seconds")
        if event_name == "UserPromptSubmit":
            errors.extend(_wrapup_trigger_errors(wrapper_path))
        else:
            errors.extend(_start_wrapper_errors(wrapper_path))

    # Slice 8 (WI-3478): resolution-table contract parity per bridge
    # gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-003.md
    # GO at -004.
    errors.extend(_resolution_table_parity_errors(project_root))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args(argv)

    errors = check_project(args.project_root.resolve())
    if errors:
        print("Codex hook parity: FAIL", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Codex hook parity: PASS")
    print("Note: Codex hook commands are checked for Windows shell-portable command forms.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
