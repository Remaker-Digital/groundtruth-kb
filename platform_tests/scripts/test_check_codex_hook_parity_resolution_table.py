"""Tests for the resolution-table parity assertions in
``scripts/check_codex_hook_parity.py`` (Slice 8 of
PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE; WI-3478; bridge
gtkb-interactive-session-role-override-slice-8-parity-check-resolution-table-003.md
GO at -004).

Each mutation test stages a fresh tmp copy of the four resolution-table-
relevant source files, mutates one specific primitive, and asserts the
expected error message appears in ``_resolution_table_parity_errors``.
The clean-state baseline test (test 1) verifies that no errors fire on the
unmutated copy; the regression test (test 16) verifies the same against the
real project root after this test module is added.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

# Resolve project root: ``platform_tests/scripts/`` -> repo root.
_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = _THIS_FILE.parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import check_codex_hook_parity as parity  # noqa: E402  (sys.path mutation above)

# Files the resolution-table helper reads.  The mutate-and-test pattern copies
# them into ``tmp_path`` per test so the real repo is never altered.
_RELEVANT_FILES = (
    ".claude/hooks/session_start_dispatch.py",
    ".codex/gtkb-hooks/session_start_dispatch.py",
    "scripts/session_role_resolution.py",
    "scripts/workstream_focus.py",
)


def _stage_relevant_files(tmp_path: Path) -> Path:
    """Copy the four relevant source files into ``tmp_path`` and return it.

    ``_resolution_table_parity_errors`` only reads these four files; staging
    the rest of the repo is unnecessary and would slow the suite down.
    """

    for relpath in _RELEVANT_FILES:
        src = PROJECT_ROOT / relpath
        dest = tmp_path / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return tmp_path


def _mutate_replace(path: Path, old: str, new: str, count: int = 1) -> None:
    """Replace the first ``count`` occurrences of ``old`` with ``new``."""

    text = path.read_text(encoding="utf-8")
    assert old in text, f"expected substring not present in {path}: {old!r}"
    path.write_text(text.replace(old, new, count), encoding="utf-8")


def _mutate_delete(path: Path, fragment: str) -> None:
    """Remove the first occurrence of ``fragment``."""

    _mutate_replace(path, fragment, "", count=1)


def _mutate_append(path: Path, fragment: str) -> None:
    """Append ``fragment`` to ``path`` (no replacement)."""

    text = path.read_text(encoding="utf-8")
    path.write_text(text + fragment, encoding="utf-8")


# ----------------------------------------------------------------------------
# Test 1: baseline clean state.
# ----------------------------------------------------------------------------
def test_resolution_table_clean_state_passes(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    errors = parity._resolution_table_parity_errors(project_root)
    assert errors == [], f"unexpected errors on clean state: {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 1: marker constant parity.
# ----------------------------------------------------------------------------
def test_marker_constant_missing_from_claude_dispatcher(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_delete(
        project_root / ".claude/hooks/session_start_dispatch.py",
        '_SESSION_ROLE_MARKER_NAME = "active-session-role.json"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any("Claude SessionStart dispatcher" in e and "marker-constant literal" in e for e in errors), (
        f"expected Claude marker-constant error in {errors!r}"
    )


def test_marker_constant_missing_from_codex_dispatcher(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_delete(
        project_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        '_SESSION_ROLE_MARKER_NAME = "active-session-role.json"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any("Codex SessionStart dispatcher" in e and "marker-constant literal" in e for e in errors), (
        f"expected Codex marker-constant error in {errors!r}"
    )


def test_marker_constant_missing_from_resolver(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_delete(
        project_root / "scripts/session_role_resolution.py",
        '_SESSION_ROLE_MARKER_NAME = "active-session-role.json"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any("Session role resolver" in e and "marker-constant literal" in e for e in errors), (
        f"expected resolver marker-constant error in {errors!r}"
    )


# ----------------------------------------------------------------------------
# Assertion 2: StartupDecision enum parity.
# ----------------------------------------------------------------------------
def test_startup_decision_enum_missing_member_in_claude(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_delete(
        project_root / ".claude/hooks/session_start_dispatch.py",
        'NORMAL_STARTUP = "normal_startup"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    # Assertion 2 AST-parses the StartupDecision class and reports a missing member.
    assert any(
        "Claude SessionStart dispatcher" in e and "is missing member" in e and "NORMAL_STARTUP" in e for e in errors
    ), f"expected Claude NORMAL_STARTUP missing-member error in {errors!r}"


def test_startup_decision_enum_value_diverges_between_dispatchers(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    # Change Claude's NORMAL_STARTUP value; Codex still has the canonical literal.
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        'NORMAL_STARTUP = "normal_startup"',
        'NORMAL_STARTUP = "renamed_value"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    # Assertion 2 reports the divergent value with both expected and found strings.
    assert any(
        "Claude SessionStart dispatcher" in e
        and "value must equal" in e
        and "StartupDecision.NORMAL_STARTUP" in e
        and '"normal_startup"' in e
        and '"renamed_value"' in e
        for e in errors
    ), f"expected divergent-value error for Claude in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 3: canonical init-keyword regex parity.
# ----------------------------------------------------------------------------
def test_canonical_init_keyword_regex_diverges(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        '_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")',
        '_CANONICAL_KEYWORD_RE = re.compile(r"^::init drift$")',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any("Codex SessionStart dispatcher" in e and "canonical init-keyword regex" in e for e in errors), (
        f"expected canonical-keyword regex error for Codex in {errors!r}"
    )


# ----------------------------------------------------------------------------
# Assertion 4: label-to-canonical-mode dict diverges.
# ----------------------------------------------------------------------------
def test_label_to_canonical_mode_dict_diverges(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    # Inject a spurious key into Claude's _LABEL_TO_CANONICAL_MODE dict literal.
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        "_LABEL_TO_CANONICAL_MODE = {",
        '_LABEL_TO_CANONICAL_MODE = {\n    "drifted_key": "pb",',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any("_LABEL_TO_CANONICAL_MODE" in e and "ast-equivalent" in e for e in errors), (
        f"expected _LABEL_TO_CANONICAL_MODE divergence error in {errors!r}"
    )


# ----------------------------------------------------------------------------
# Assertion 5: marker invalidation not called.
# ----------------------------------------------------------------------------
def test_invalidate_marker_not_called_in_main(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    # Remove the bare ``_invalidate_session_role_marker()`` call (empty parens
    # match only call sites, not the def signature with its parameter).
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        "_invalidate_session_role_marker()",
        "pass  # _invalidate_session_role_marker call removed",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e and "must call" in e and "_invalidate_session_role_marker" in e
        for e in errors
    ), f"expected missing-call error for Claude in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 6: behavior-table decision missing.
# ----------------------------------------------------------------------------
def test_bridge_dispatch_keyword_check_decision_missing(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    # Mutate one decision return in _bridge_dispatch_keyword_check to use a
    # non-existent member; the body still parses, but the receiver vocabulary
    # is now incomplete.
    _mutate_replace(
        project_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        "StartupDecision.NORMAL_STARTUP",
        "StartupDecision.MISSING_NORMAL",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Codex SessionStart dispatcher" in e
        and "_bridge_dispatch_keyword_check" in e
        and "StartupDecision.NORMAL_STARTUP" in e
        for e in errors
    ), f"expected missing-decision error for Codex in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 7: audit-log kind literal missing.
# ----------------------------------------------------------------------------
def test_audit_log_kind_literal_missing(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        '"misdirected_dispatch_strict_drop"',
        '"renamed_kind"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Codex SessionStart dispatcher" in e
        and "audit-record kind literal" in e
        and "misdirected_dispatch_strict_drop" in e
        for e in errors
    ), f"expected audit-log kind error for Codex in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 8: intentional-difference guards.
# ----------------------------------------------------------------------------
def test_claude_harness_name_appears_in_codex_dispatcher(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_append(
        project_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        '\n# drift sentinel: HARNESS_NAME = "claude"\n',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Codex SessionStart dispatcher must not contain" in e and 'HARNESS_NAME = "claude"' in e for e in errors
    ), f"expected intentional-difference error in {errors!r}"


def test_codex_out_dir_appears_in_claude_dispatcher(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_append(
        project_root / ".claude/hooks/session_start_dispatch.py",
        '\n# drift sentinel: OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"\n',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher must not contain" in e
        and 'OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"' in e
        for e in errors
    ), f"expected intentional-difference error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 9: cache-writer parity (Slice 8 NO-GO -002 F2 fix).
# ----------------------------------------------------------------------------
def test_cache_writer_iterates_role_set_instead_of_mode_map_claude(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    # Substitute the as-shipped loop with the pre-Slice-1 defective shape.
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        "for mode in sorted(_MODE_TO_ROLE_PROFILE):",
        "for role in sorted(_resolve_own_role_set()):",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e and "_write_role_scoped_startup_relay_caches" in e and "must iterate" in e
        for e in errors
    ), f"expected cache-writer loop error in {errors!r}"
    assert any(
        "Claude SessionStart dispatcher" in e
        and "_write_role_scoped_startup_relay_caches" in e
        and "must NOT reference" in e
        and "_resolve_own_role_set" in e
        for e in errors
    ), f"expected forbidden-reference error in {errors!r}"


def test_cache_writer_iterates_role_set_instead_of_mode_map_codex(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        "for mode in sorted(_MODE_TO_ROLE_PROFILE):",
        "for role in sorted(_resolve_own_role_set()):",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Codex SessionStart dispatcher" in e and "_write_role_scoped_startup_relay_caches" in e and "must iterate" in e
        for e in errors
    ), f"expected cache-writer loop error in {errors!r}"
    assert any(
        "Codex SessionStart dispatcher" in e
        and "_write_role_scoped_startup_relay_caches" in e
        and "must NOT reference" in e
        and "_resolve_own_role_set" in e
        for e in errors
    ), f"expected forbidden-reference error in {errors!r}"


# ----------------------------------------------------------------------------
# Test 16: regression — clean state still passes after this test module
# lands in platform_tests/scripts/ on the real project root.
# ----------------------------------------------------------------------------
def test_clean_state_still_passes_after_test_module_addition() -> None:
    """``platform_tests/scripts/`` is not on any resolution-table source path,
    so adding this test module to the repo must not change the helper's
    output on the real project root.
    """

    errors = parity._resolution_table_parity_errors(PROJECT_ROOT)
    assert errors == [], f"unexpected errors on real repo state: {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 5 strict tests — verification NO-GO -006 F1 (main()-order contract).
# ----------------------------------------------------------------------------
def test_invalidate_marker_call_only_in_comment_fails(tmp_path: Path) -> None:
    """Comment-only mentions of ``_invalidate_session_role_marker()`` do NOT
    satisfy the Slice 3 pre-dispatch contract; the AST-based check must fail
    because there is no Call node at top level of ``main()``.
    """

    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        "_invalidate_session_role_marker()",
        "# _invalidate_session_role_marker() removed",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and "top-level statement" in e
        for e in errors
    ), f"expected main()-order missing-call error for comment-only mutation in {errors!r}"


def test_invalidate_marker_call_only_in_helper_fails(tmp_path: Path) -> None:
    """A call inside a helper function outside ``main()`` does NOT satisfy
    the pre-dispatch contract; the AST-based check restricts the search to
    ``main()``'s body so an unused-helper containing the call must fail.
    """

    project_root = _stage_relevant_files(tmp_path)
    claude_path = project_root / ".claude/hooks/session_start_dispatch.py"
    text = claude_path.read_text(encoding="utf-8")
    # Remove the main() call and append a top-level helper that contains it.
    mutated = text.replace("_invalidate_session_role_marker()", "pass  # moved to helper", 1)
    mutated += "\n\ndef _unused_helper_with_invalidation() -> None:\n    _invalidate_session_role_marker()\n"
    claude_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        for e in errors
    ), f"expected main()-order missing-call error for helper-only mutation in {errors!r}"


def test_invalidate_marker_call_after_dispatch_fork_fails(tmp_path: Path) -> None:
    """A call placed AFTER ``_bridge_dispatch_keyword_check()`` violates the
    pre-dispatch ordering contract; the AST-based check compares ``lineno``
    and must fail when the invalidation lineno is greater than the
    dispatch lineno.
    """

    project_root = _stage_relevant_files(tmp_path)
    claude_path = project_root / ".claude/hooks/session_start_dispatch.py"
    text = claude_path.read_text(encoding="utf-8")
    # Remove the pre-dispatch invalidation call.
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    pass  # moved to after dispatch fork",
        1,
    )
    # Add a post-dispatch invalidation call by patching the line immediately
    # after the dispatch fork.  The dispatcher assigns the decision into
    # ``decision, _reason``; append the relocated call on the following line.
    dispatch_anchor = "    decision, _reason = _bridge_dispatch_keyword_check()"
    relocated = dispatch_anchor + "\n    _invalidate_session_role_marker()  # post-fork (drift)"
    mutated = mutated.replace(dispatch_anchor, relocated, 1)
    claude_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and "BEFORE" in e
        and "_bridge_dispatch_keyword_check" in e
        for e in errors
    ), f"expected post-fork ordering error for relocated-call mutation in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 2 strict test — verification NO-GO -006 F2 (closed-set vocabulary).
# ----------------------------------------------------------------------------
def test_startup_decision_enum_extra_member_fails(tmp_path: Path) -> None:
    """Adding an extra ``StartupDecision`` member must fail the closed-set
    check: the IP-4 vocabulary is closed at five values, and ungoverned
    drift is exactly the failure mode this assertion guards.
    """

    project_root = _stage_relevant_files(tmp_path)
    # Insert an extra enum member after STRICT_DROP so the class body parses
    # cleanly with six members instead of five.
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER = "extra"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "StartupDecision" in e
        and "unapproved extra member" in e
        and "EXTRA_MEMBER" in e
        for e in errors
    ), f"expected extra-member error for closed-set vocabulary in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 6 strict test — verification NO-GO -006 F3 (table header tokens).
# ----------------------------------------------------------------------------
def test_bridge_dispatch_behavior_table_header_token_missing(tmp_path: Path) -> None:
    """Removing a behavior-table column header from the
    ``_bridge_dispatch_keyword_check`` docstring must fail the assertion:
    the GO-approved Slice 8 scope named the 5-row table header as part of
    the contract.
    """

    project_root = _stage_relevant_files(tmp_path)
    # Replace ``Effect`` (the last column header) with ``Outcome`` in the
    # Codex dispatcher.  The header row appears once in the docstring; the
    # post-NO-GO-009 regex check requires all five tokens in order with
    # whitespace-only separation, so the substitution breaks the match.
    _mutate_replace(
        project_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        "env-var       keyword    mode-in-role-set      Decision             Effect",
        "env-var       keyword    mode-in-role-set      Decision             Outcome",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Codex SessionStart dispatcher" in e
        and "_bridge_dispatch_keyword_check" in e
        and "docstring" in e
        and "five-token behavior-table header row" in e
        for e in errors
    ), f"expected docstring-header row error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 5 v2 — verification NO-GO -009 F1 (nested-helper bypass).
# ----------------------------------------------------------------------------
def test_invalidate_marker_call_only_in_nested_helper_inside_main_fails(
    tmp_path: Path,
) -> None:
    """A call inside a nested function definition INSIDE ``main()`` is a
    definition, not an execution; the v2 main()-order check must fail because
    its guarded recursion prunes ``FunctionDef``/``AsyncFunctionDef``/
    ``ClassDef``/``Lambda`` bodies from the walk.

    This was the exact bypass Codex named in the corrective NO-GO -009 F1.
    """

    project_root = _stage_relevant_files(tmp_path)
    claude_path = project_root / ".claude/hooks/session_start_dispatch.py"
    text = claude_path.read_text(encoding="utf-8")
    # Remove the direct pre-dispatch call.
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    pass  # invalidation moved into nested helper",
        1,
    )
    # Define a nested helper inside main() BEFORE the dispatch fork.  The
    # helper body contains the call but the helper is never invoked, so the
    # call is not executed.
    dispatch_anchor = "    decision, _reason = _bridge_dispatch_keyword_check()"
    nested_helper = (
        "    def _unused_nested_helper() -> None:\n"
        "        _invalidate_session_role_marker()  # F1 bypass attempt (defined, not executed)\n\n"
        "    decision, _reason = _bridge_dispatch_keyword_check()"
    )
    mutated = mutated.replace(dispatch_anchor, nested_helper, 1)
    claude_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and "nested function/class/lambda" in e
        for e in errors
    ), f"expected nested-helper bypass error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 2 v2 — verification NO-GO -009 F2 (non-string extra-member bypass).
# ----------------------------------------------------------------------------
def test_startup_decision_enum_non_string_extra_member_fails(tmp_path: Path) -> None:
    """A class-body assignment whose value is not a string constant (e.g.
    ``EXTRA_MEMBER = object()``) is still a declared enum member; the v2
    vocabulary check must report it as drift even though no string value
    can be compared.

    This was the exact bypass Codex named in the corrective NO-GO -009 F2.
    """

    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER = object()',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "StartupDecision" in e
        and "unapproved extra member" in e
        and "EXTRA_MEMBER" in e
        for e in errors
    ), f"expected non-string extra-member error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 6 v2 — verification NO-GO -009 F3 (prose-only token bypass).
# ----------------------------------------------------------------------------
def test_bridge_dispatch_behavior_table_header_row_replaced_with_prose_fails(
    tmp_path: Path,
) -> None:
    """Removing the header ROW while preserving the same five words in prose
    elsewhere in the docstring must fail the v2 check: the regex requires
    the tokens consecutively with whitespace-only separation, so prose with
    commas/periods between the words cannot satisfy it.

    This was the exact bypass Codex named in the corrective NO-GO -009 F3.
    """

    project_root = _stage_relevant_files(tmp_path)
    # The mutation replaces the table header row with a prose sentence that
    # contains all five tokens but separates them with commas, so the
    # whitespace-only regex cannot match.
    _mutate_replace(
        project_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        "env-var       keyword    mode-in-role-set      Decision             Effect",
        "Behavior depends on env-var, keyword, mode-in-role-set, Decision, and Effect outcomes.",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Codex SessionStart dispatcher" in e
        and "_bridge_dispatch_keyword_check" in e
        and "docstring" in e
        and "five-token behavior-table header row" in e
        for e in errors
    ), f"expected prose-only header bypass error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 5 v3 — verification NO-GO -011 F1 (unreachable-conditional bypass).
# ----------------------------------------------------------------------------
def test_invalidate_marker_call_only_inside_if_false_block_fails(tmp_path: Path) -> None:
    """A call wrapped in ``if False:`` is structurally present in ``main()``
    but never executed; the v3 top-level statement check must reject it.
    The v2 check (which descended into control-flow nodes) accepted this
    placement — Codex's sidecar probe at NO-GO -011 F1 proved the bypass.
    """

    project_root = _stage_relevant_files(tmp_path)
    claude_path = project_root / ".claude/hooks/session_start_dispatch.py"
    text = claude_path.read_text(encoding="utf-8")
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    if False:\n        _invalidate_session_role_marker()  # unreachable",
        1,
    )
    claude_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and ("top-level statement" in e or "unconditional" in e)
        for e in errors
    ), f"expected unreachable-conditional bypass error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 2 v3 — verification NO-GO -011 F2 (annotated-assign bypass).
# ----------------------------------------------------------------------------
def test_startup_decision_enum_annotated_extra_member_fails(tmp_path: Path) -> None:
    """An annotated class-body assignment like ``EXTRA_MEMBER: object = object()``
    parses as ``ast.AnnAssign``, not ``ast.Assign``; the v2 check missed it.
    The v3 fix adds ``AnnAssign`` handling so the extra-member detection no
    longer has this escape hatch (Codex's NO-GO -011 F2 sidecar probe).
    """

    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER: object = object()',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "StartupDecision" in e
        and "unapproved extra member" in e
        and "EXTRA_MEMBER" in e
        for e in errors
    ), f"expected annotated-extra-member error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 6 v3 — verification NO-GO -011 F3 (prose-whitespace bypass).
# ----------------------------------------------------------------------------
def test_bridge_dispatch_behavior_table_header_replaced_with_whitespace_prose_fails(
    tmp_path: Path,
) -> None:
    """A prose sentence containing the five tokens in order with whitespace
    separation no longer suffices when the actual table-separator rows are
    missing.  The v3 anchored check requires lines of ``=`` separators above
    AND below the header row (Codex's NO-GO -011 F3 sidecar probe).
    """

    project_root = _stage_relevant_files(tmp_path)
    # Replace the entire table block (separators + header row) with a single
    # prose sentence that contains the tokens in order separated by whitespace.
    # Without the surrounding ``=`` separator rows, the anchored check fails
    # even though the tokens are syntactically present.
    table_block = (
        "    ============  =========  ====================  ===================  ====================================================\n"
        "    env-var       keyword    mode-in-role-set      Decision             Effect\n"
        "    ============  =========  ====================  ===================  ===================================================="
    )
    codex_path = project_root / ".codex/gtkb-hooks/session_start_dispatch.py"
    text = codex_path.read_text(encoding="utf-8")
    assert table_block in text, "expected docstring table block not found in fixture source"
    mutated = text.replace(
        table_block,
        "    A prose sentence says env-var keyword mode-in-role-set Decision Effect outcomes.",
        1,
    )
    codex_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Codex SessionStart dispatcher" in e
        and "_bridge_dispatch_keyword_check" in e
        and "docstring" in e
        and "anchored by" in e
        for e in errors
    ), f"expected anchored-header bypass error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 2 v4 — verification NO-GO -013 F1 (chained multi-target bypass).
# ----------------------------------------------------------------------------
def test_startup_decision_enum_multi_target_chained_extra_member_fails(
    tmp_path: Path,
) -> None:
    """A chained class-body assignment like
    ``EXTRA_MEMBER = ALSO_EXTRA = object()`` declares TWO enum members through
    Python's metaclass: ``StartupDecision.__members__`` contains both
    ``EXTRA_MEMBER`` and ``ALSO_EXTRA``.  The v3 vocabulary check only
    inspected single-target ``ast.Assign`` nodes (``len(stmt.targets) == 1``),
    so the entire chained form bypassed detection.  The v4 fix walks every
    ``Assign.targets`` entry, so both chained names contribute to
    ``declared_names`` and the closed-vocabulary comparison reports them as
    unapproved extras.

    Codex's NO-GO -013 F1 sidecar probe surfaced this bypass.
    """

    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER = ALSO_EXTRA = object()',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "StartupDecision" in e
        and "unapproved extra member" in e
        and ("EXTRA_MEMBER" in e or "ALSO_EXTRA" in e)
        for e in errors
    ), f"expected chained multi-target extra-member error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 2 v4 — verification NO-GO -013 F1 (tuple-target unpack bypass).
# ----------------------------------------------------------------------------
def test_startup_decision_enum_tuple_target_extra_members_fail(tmp_path: Path) -> None:
    """A tuple-target class-body assignment like
    ``EXTRA_MEMBER, OTHER = (object(), object())`` declares TWO enum members
    via Python's metaclass.  The v3 check rejected any ``ast.Assign`` whose
    ``len(stmt.targets) != 1``, AND when ``len(stmt.targets) == 1`` it required
    the single target to be a ``Name`` — so the single ``Tuple`` target form
    also slipped through.  The v4 fix recognises tuple/list targets and walks
    their ``Name`` elements.

    Codex's NO-GO -013 F1 sidecar probe surfaced this bypass.
    """

    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / ".claude/hooks/session_start_dispatch.py",
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER, OTHER = (object(), object())',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "StartupDecision" in e
        and "unapproved extra member" in e
        and ("EXTRA_MEMBER" in e or "OTHER" in e)
        for e in errors
    ), f"expected tuple-target extra-member error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 5 v5 — verification NO-GO -015 F1 (same-line semicolon bypass).
# ----------------------------------------------------------------------------
def test_invalidate_marker_call_same_line_after_dispatch_fails(tmp_path: Path) -> None:
    """A same-physical-line semicolon statement that runs
    ``_bridge_dispatch_keyword_check()`` first and
    ``_invalidate_session_role_marker()`` second shares ONE ``lineno`` for both
    calls.  The v4 check compared line numbers only, so ``N > N`` was False and
    the post-dispatch placement passed.  The v5 fix compares
    ``(lineno, col_offset)`` tuples, so the column tiebreaker correctly orders
    the second call as "after" the dispatch fork and the check fails.

    This was the exact bypass Codex named in the corrective NO-GO -015 F1:

        decision, reason = _bridge_dispatch_keyword_check(); _invalidate_session_role_marker()
    """

    project_root = _stage_relevant_files(tmp_path)
    claude_path = project_root / ".claude/hooks/session_start_dispatch.py"
    text = claude_path.read_text(encoding="utf-8")
    # Remove the direct pre-dispatch invalidation call.
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    pass  # v5: relocated to same-line post-dispatch",
        1,
    )
    # Append the invalidation onto the dispatch-fork line via a semicolon so
    # both calls share one physical line (and therefore one lineno).  Execution
    # order is dispatch-then-invalidate, which violates the pre-dispatch
    # contract; the v5 (lineno, col_offset) comparison must catch it.
    dispatch_anchor = "    decision, _reason = _bridge_dispatch_keyword_check()"
    same_line = dispatch_anchor + "; _invalidate_session_role_marker()  # v5 same-line post-fork bypass attempt"
    mutated = mutated.replace(dispatch_anchor, same_line, 1)
    claude_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher" in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and "BEFORE" in e
        and "_bridge_dispatch_keyword_check" in e
        for e in errors
    ), f"expected same-line post-dispatch ordering error in {errors!r}"


def test_invalidate_marker_call_same_line_before_dispatch_passes(tmp_path: Path) -> None:
    """The mirror of the v5 bypass: when the SAME physical line runs
    ``_invalidate_session_role_marker()`` FIRST and the dispatch fork second,
    execution order honors the pre-dispatch contract and the check must pass.

    This guards against an over-correction where the v5 fix would reject all
    same-line placements regardless of order.  Only dispatch-before-invalidate
    on one line is a violation.
    """

    project_root = _stage_relevant_files(tmp_path)
    claude_path = project_root / ".claude/hooks/session_start_dispatch.py"
    text = claude_path.read_text(encoding="utf-8")
    # Remove the standalone pre-dispatch invalidation call.
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    pass  # v5: relocated to same-line pre-dispatch",
        1,
    )
    # Prepend the invalidation onto the dispatch-fork line via a semicolon so
    # both calls share one physical line but invalidate executes first.
    dispatch_anchor = "    decision, _reason = _bridge_dispatch_keyword_check()"
    same_line = "    _invalidate_session_role_marker(); " + dispatch_anchor.lstrip()
    mutated = mutated.replace(dispatch_anchor, same_line, 1)
    claude_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    order_errors = [e for e in errors if "Claude SessionStart dispatcher" in e and "main()" in e and "BEFORE" in e]
    assert order_errors == [], f"unexpected order error on valid same-line pre-dispatch placement: {order_errors!r}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
