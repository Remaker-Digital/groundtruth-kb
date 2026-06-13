"""Tests for the resolution-table parity assertions in
``scripts/check_codex_hook_parity.py``.

Originally Slice 8 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE (WI-3478).
Slice D of GTKB-STARTUP-REFRACTOR-001 (WI-4272; bridge
``gtkb-startup-refractor-slice-d-sessionstart-hook-dedup-004.md`` GO) extracted
the shared SessionStart primitives into a single core module
(``scripts/session_start_dispatch_core.py``). The primitive drift-class tests
therefore mutate the CORE source (the new single home); the intentional-
difference guard (Assertion 8) and the new delegation guard (Assertion 10)
still mutate the WRAPPER sources.

Each mutation test stages a fresh tmp copy of the resolution-table-relevant
source files, mutates one primitive, and asserts the expected error message
appears in ``_resolution_table_parity_errors``. The clean-state baseline
(test 1) verifies no errors fire on the unmutated copy; the regression test
verifies the same against the real project root after this module is added.
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

# Files the resolution-table helper reads. Slice D added the shared core module
# (the single home of the extracted primitives). The mutate-and-test pattern
# copies them into ``tmp_path`` per test so the real repo is never altered.
_CORE = "scripts/session_start_dispatch_core.py"
_CLAUDE = ".claude/hooks/session_start_dispatch.py"
_CODEX = ".codex/gtkb-hooks/session_start_dispatch.py"
_RELEVANT_FILES = (
    _CORE,
    _CLAUDE,
    _CODEX,
    "scripts/session_role_resolution.py",
    "scripts/workstream_focus.py",
)
_CORE_LABEL = "SessionStart dispatch core"


def _stage_relevant_files(tmp_path: Path) -> Path:
    """Copy the resolution-table source files into ``tmp_path`` and return it."""

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
# Assertion 1: marker constant parity (core + resolver + workstream).
# ----------------------------------------------------------------------------
def test_marker_constant_missing_from_core(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_delete(
        project_root / _CORE,
        '_SESSION_ROLE_MARKER_NAME = "active-session-role.json"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(_CORE_LABEL in e and "marker-constant literal" in e for e in errors), (
        f"expected core marker-constant error in {errors!r}"
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


def test_marker_constant_missing_from_workstream(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_delete(
        project_root / "scripts/workstream_focus.py",
        '_SESSION_ROLE_MARKER_NAME = "active-session-role.json"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any("Workstream focus writer" in e and "marker-constant literal" in e for e in errors), (
        f"expected workstream marker-constant error in {errors!r}"
    )


# ----------------------------------------------------------------------------
# Assertion 2: StartupDecision enum parity (core single source).
# ----------------------------------------------------------------------------
def test_startup_decision_enum_missing_member_in_core(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_delete(project_root / _CORE, 'NORMAL_STARTUP = "normal_startup"')
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(_CORE_LABEL in e and "is missing member" in e and "NORMAL_STARTUP" in e for e in errors), (
        f"expected core NORMAL_STARTUP missing-member error in {errors!r}"
    )


def test_startup_decision_enum_value_diverges_in_core(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        'NORMAL_STARTUP = "normal_startup"',
        'NORMAL_STARTUP = "renamed_value"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e
        and "value must equal" in e
        and "StartupDecision.NORMAL_STARTUP" in e
        and '"normal_startup"' in e
        and '"renamed_value"' in e
        for e in errors
    ), f"expected divergent-value error for core in {errors!r}"


def test_startup_decision_enum_extra_member_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER = "extra"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e and "StartupDecision" in e and "unapproved extra member" in e and "EXTRA_MEMBER" in e
        for e in errors
    ), f"expected extra-member error for closed-set vocabulary in {errors!r}"


def test_startup_decision_enum_non_string_extra_member_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER = object()',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e and "StartupDecision" in e and "unapproved extra member" in e and "EXTRA_MEMBER" in e
        for e in errors
    ), f"expected non-string extra-member error in {errors!r}"


def test_startup_decision_enum_annotated_extra_member_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER: object = object()',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e and "StartupDecision" in e and "unapproved extra member" in e and "EXTRA_MEMBER" in e
        for e in errors
    ), f"expected annotated-extra-member error in {errors!r}"


def test_startup_decision_enum_multi_target_chained_extra_member_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER = ALSO_EXTRA = object()',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e
        and "StartupDecision" in e
        and "unapproved extra member" in e
        and ("EXTRA_MEMBER" in e or "ALSO_EXTRA" in e)
        for e in errors
    ), f"expected chained multi-target extra-member error in {errors!r}"


def test_startup_decision_enum_tuple_target_extra_members_fail(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        'STRICT_DROP = "strict_drop"',
        'STRICT_DROP = "strict_drop"\n    EXTRA_MEMBER, OTHER = (object(), object())',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e
        and "StartupDecision" in e
        and "unapproved extra member" in e
        and ("EXTRA_MEMBER" in e or "OTHER" in e)
        for e in errors
    ), f"expected tuple-target extra-member error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 3: canonical init-keyword regex parity (core).
# ----------------------------------------------------------------------------
def test_canonical_init_keyword_regex_diverges(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        '_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")',
        '_CANONICAL_KEYWORD_RE = re.compile(r"^::init drift$")',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(_CORE_LABEL in e and "canonical init-keyword regex" in e for e in errors), (
        f"expected canonical-keyword regex error for core in {errors!r}"
    )


# ----------------------------------------------------------------------------
# Assertion 4: resolution-table dict content (core single source).
# ----------------------------------------------------------------------------
def test_label_to_canonical_mode_dict_content_drifts(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    # Inject a spurious key into the core's _LABEL_TO_CANONICAL_MODE dict.
    _mutate_replace(
        project_root / _CORE,
        "_LABEL_TO_CANONICAL_MODE = {",
        '_LABEL_TO_CANONICAL_MODE = {\n    "drifted_key": "pb",',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e and "_LABEL_TO_CANONICAL_MODE" in e and "canonical resolution-table" in e for e in errors
    ), f"expected _LABEL_TO_CANONICAL_MODE content-drift error in {errors!r}"


def test_mode_to_role_profile_dict_value_drifts(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        '"pb": "prime-builder",',
        '"pb": "loyal-opposition",',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e and "_MODE_TO_ROLE_PROFILE" in e and "canonical resolution-table" in e for e in errors
    ), f"expected _MODE_TO_ROLE_PROFILE content-drift error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 5: marker invalidation main()-order contract (core).
# ----------------------------------------------------------------------------
def test_invalidate_marker_not_called_in_main(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        "_invalidate_session_role_marker()",
        "pass  # _invalidate_session_role_marker call removed",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(_CORE_LABEL in e and "must call" in e and "_invalidate_session_role_marker" in e for e in errors), (
        f"expected missing-call error for core in {errors!r}"
    )


def test_invalidate_marker_call_only_in_comment_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        "_invalidate_session_role_marker()",
        "# _invalidate_session_role_marker() removed",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and "top-level statement" in e
        for e in errors
    ), f"expected main()-order missing-call error for comment-only mutation in {errors!r}"


def test_invalidate_marker_call_after_dispatch_fork_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    core_path = project_root / _CORE
    text = core_path.read_text(encoding="utf-8")
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    pass  # moved to after dispatch fork",
        1,
    )
    dispatch_anchor = "    decision, _reason = _bridge_dispatch_keyword_check()"
    relocated = dispatch_anchor + "\n    _invalidate_session_role_marker()  # post-fork (drift)"
    mutated = mutated.replace(dispatch_anchor, relocated, 1)
    core_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and "BEFORE" in e
        and "_bridge_dispatch_keyword_check" in e
        for e in errors
    ), f"expected post-fork ordering error for relocated-call mutation in {errors!r}"


def test_invalidate_marker_call_only_in_nested_helper_inside_main_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    core_path = project_root / _CORE
    text = core_path.read_text(encoding="utf-8")
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    pass  # invalidation moved into nested helper",
        1,
    )
    dispatch_anchor = "    decision, _reason = _bridge_dispatch_keyword_check()"
    nested_helper = (
        "    def _unused_nested_helper() -> None:\n"
        "        _invalidate_session_role_marker()  # defined, not executed\n\n"
        "    decision, _reason = _bridge_dispatch_keyword_check()"
    )
    mutated = mutated.replace(dispatch_anchor, nested_helper, 1)
    core_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and "nested function/class/lambda" in e
        for e in errors
    ), f"expected nested-helper bypass error in {errors!r}"


def test_invalidate_marker_call_only_inside_if_false_block_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    core_path = project_root / _CORE
    text = core_path.read_text(encoding="utf-8")
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    if False:\n        _invalidate_session_role_marker()  # unreachable",
        1,
    )
    core_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and ("top-level statement" in e or "unconditional" in e)
        for e in errors
    ), f"expected unreachable-conditional bypass error in {errors!r}"


def test_invalidate_marker_call_same_line_after_dispatch_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    core_path = project_root / _CORE
    text = core_path.read_text(encoding="utf-8")
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    pass  # relocated to same-line post-dispatch",
        1,
    )
    dispatch_anchor = "    decision, _reason = _bridge_dispatch_keyword_check()"
    same_line = dispatch_anchor + "; _invalidate_session_role_marker()  # same-line post-fork bypass attempt"
    mutated = mutated.replace(dispatch_anchor, same_line, 1)
    core_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        and "BEFORE" in e
        and "_bridge_dispatch_keyword_check" in e
        for e in errors
    ), f"expected same-line post-dispatch ordering error in {errors!r}"


def test_invalidate_marker_call_same_line_before_dispatch_passes(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    core_path = project_root / _CORE
    text = core_path.read_text(encoding="utf-8")
    mutated = text.replace(
        "    _invalidate_session_role_marker()",
        "    pass  # relocated to same-line pre-dispatch",
        1,
    )
    dispatch_anchor = "    decision, _reason = _bridge_dispatch_keyword_check()"
    same_line = "    _invalidate_session_role_marker(); " + dispatch_anchor.lstrip()
    mutated = mutated.replace(dispatch_anchor, same_line, 1)
    core_path.write_text(mutated, encoding="utf-8")
    errors = parity._resolution_table_parity_errors(project_root)
    order_errors = [e for e in errors if _CORE_LABEL in e and "main()" in e and "BEFORE" in e]
    assert order_errors == [], f"unexpected order error on valid same-line pre-dispatch placement: {order_errors!r}"


# ----------------------------------------------------------------------------
# Assertion 6: behavior-table receiver (core).
# ----------------------------------------------------------------------------
def test_bridge_dispatch_keyword_check_decision_missing(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        "StartupDecision.NORMAL_STARTUP",
        "StartupDecision.MISSING_NORMAL",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e and "_bridge_dispatch_keyword_check" in e and "StartupDecision.NORMAL_STARTUP" in e
        for e in errors
    ), f"expected missing-decision error for core in {errors!r}"


def test_bridge_dispatch_behavior_table_header_token_missing(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        "env-var       keyword    mode-in-role-set      Decision             Effect",
        "env-var       keyword    mode-in-role-set      Decision             Outcome",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e
        and "_bridge_dispatch_keyword_check" in e
        and "docstring" in e
        and "five-token behavior-table header row" in e
        for e in errors
    ), f"expected docstring-header row error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 7: audit-log primitives (core).
# ----------------------------------------------------------------------------
def test_audit_log_kind_literal_missing(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        '"dispatch_role_mismatch_authorized"',
        '"renamed_kind"',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e and "audit-record kind literal" in e and "dispatch_role_mismatch_authorized" in e
        for e in errors
    ), f"expected audit-log kind error for core in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 8: intentional-difference guards (wrappers — unchanged by Slice D).
# ----------------------------------------------------------------------------
def test_claude_harness_name_appears_in_codex_dispatcher(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_append(
        project_root / _CODEX,
        '\n# drift sentinel: HARNESS_NAME = "claude"\n',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Codex SessionStart dispatcher must not contain" in e and 'HARNESS_NAME = "claude"' in e for e in errors
    ), f"expected intentional-difference error in {errors!r}"


def test_codex_out_dir_appears_in_claude_dispatcher(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_append(
        project_root / _CLAUDE,
        '\n# drift sentinel: OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"\n',
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        "Claude SessionStart dispatcher must not contain" in e
        and 'OUT_DIR = PROJECT_ROOT / ".codex" / "gtkb-hooks"' in e
        for e in errors
    ), f"expected intentional-difference error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 9: cache-writer parity (core single source).
# ----------------------------------------------------------------------------
def test_cache_writer_iterates_role_set_instead_of_mode_map(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CORE,
        "for mode in sorted(_MODE_TO_ROLE_PROFILE):",
        "for role in sorted(_resolve_own_role_set()):",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any(
        _CORE_LABEL in e and "_write_role_scoped_startup_relay_caches" in e and "must iterate" in e for e in errors
    ), f"expected cache-writer loop error in {errors!r}"
    assert any(
        _CORE_LABEL in e
        and "_write_role_scoped_startup_relay_caches" in e
        and "must NOT reference" in e
        and "_resolve_own_role_set" in e
        for e in errors
    ), f"expected forbidden-reference error in {errors!r}"


# ----------------------------------------------------------------------------
# Assertion 10: wrapper delegation (Slice D de-duplication guard).
# ----------------------------------------------------------------------------
def test_claude_wrapper_missing_core_import_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CLAUDE,
        "import session_start_dispatch_core as _core",
        "_core = None  # delegation removed",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any("Claude SessionStart dispatcher must delegate to the shared core" in e for e in errors), (
        f"expected delegation (import) error for Claude in {errors!r}"
    )


def test_codex_wrapper_missing_rebind_fails(tmp_path: Path) -> None:
    project_root = _stage_relevant_files(tmp_path)
    _mutate_replace(
        project_root / _CODEX,
        "types.FunctionType(",
        "_no_rebind(",
    )
    errors = parity._resolution_table_parity_errors(project_root)
    assert any("Codex SessionStart dispatcher must rebind shared core functions" in e for e in errors), (
        f"expected delegation (rebind) error for Codex in {errors!r}"
    )


# ----------------------------------------------------------------------------
# Regression: clean state still passes on the real project root after this
# module lands (``platform_tests/scripts/`` is not a resolution-table source).
# ----------------------------------------------------------------------------
def test_clean_state_still_passes_after_test_module_addition() -> None:
    errors = parity._resolution_table_parity_errors(PROJECT_ROOT)
    assert errors == [], f"unexpected errors on real repo state: {errors!r}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
