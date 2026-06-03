"""Regression tests for the bridge-proposal pattern lint (WI-3482).

Covers the new ``git-hooks-path-mismatch`` detector that flags a bridge proposal
targeting an inactive Git-hook surface (``.git/hooks`` or the legacy
``scripts/guardrails/pre-commit`` staging path) while ``core.hooksPath`` differs.

Authority: bridge/gtkb-git-hooks-path-mismatch-lint-002.md (GO);
PAUTH-WI-3482-GIT-HOOKS-PATH-LINT-001 under PROJECT-GTKB-RELIABILITY-FIXES.

Tests are hermetic: the active hook path is injected via ``active_hooks_path``
(or, for the ``main()``/``--strict`` path, by monkeypatching the resolver), so no
test reads or mutates real Git config.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import scripts.bridge_proposal_pattern_lint as lint

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
# The repository's real non-default active hook path; used as the injected value.
_ACTIVE = ".githooks"


def _pattern_ids(findings: list[lint.Finding]) -> list[str]:
    return [f.pattern_id for f in findings]


def _has_mismatch(findings: list[lint.Finding]) -> bool:
    return "git-hooks-path-mismatch" in _pattern_ids(findings)


# --- Positive cases (detector fires) -----------------------------------------


def test_positive_target_paths_git_hooks_pre_commit_ruff_gate_case() -> None:
    """Reproduces gtkb-ruff-format-pre-file-gate-002 F1 on the target_paths surface."""
    text = 'target_paths: ["scripts/check_ruff_format.py", ".git/hooks/pre-commit"]\n'
    findings = lint.lint_text(text, active_hooks_path=_ACTIVE)
    assert _has_mismatch(findings)


def test_positive_register_at_git_hooks_commit_scope_case() -> None:
    """Reproduces gtkb-commit-scope-bundling-detection-001-prop-002 F1."""
    text = 'target_paths: [".git/hooks/pre-commit"]\nRegister the bundling guard at the pre-commit entry point.\n'
    findings = lint.lint_text(text, active_hooks_path=_ACTIVE)
    assert _has_mismatch(findings)


def test_positive_legacy_guardrails_staging_token() -> None:
    text = "Plan: stage the guard at scripts/guardrails/pre-commit before promotion.\n"
    findings = lint.lint_text(text, active_hooks_path=_ACTIVE)
    assert _has_mismatch(findings)


def test_positive_backslash_path_separator_is_normalized() -> None:
    """GO -002 condition: a Windows-style backslash path must still match."""
    text = 'target_paths: [".git\\hooks\\pre-commit"]\n'
    assert "\\" in text  # the proposal text really contains backslashes
    findings = lint.lint_text(text, active_hooks_path=_ACTIVE)
    assert _has_mismatch(findings)


# --- Negative cases (no false positive) --------------------------------------


def test_negative_default_hook_path_empty_no_finding() -> None:
    text = 'target_paths: [".git/hooks/pre-commit"]\n'
    findings = lint.lint_text(text, active_hooks_path="")
    assert not _has_mismatch(findings)


def test_negative_default_hook_path_explicit_no_finding() -> None:
    text = 'target_paths: [".git/hooks/pre-commit"]\n'
    findings = lint.lint_text(text, active_hooks_path=".git/hooks")
    assert not _has_mismatch(findings)


def test_negative_correct_active_surface_no_finding() -> None:
    text = 'target_paths: [".githooks/pre-commit"]\n'
    findings = lint.lint_text(text, active_hooks_path=_ACTIVE)
    assert not _has_mismatch(findings)


def test_negative_self_documentation_no_finding() -> None:
    """A proposal describing the hazard must not self-trigger."""
    text = (
        "Because core.hooksPath overrides the default, every .git/hooks/ file is inert.\n"
        "A proposal that lists .git/hooks/pre-commit in its target_paths would modify a "
        "directory Git never consults.\n"
    )
    findings = lint.lint_text(text, active_hooks_path=_ACTIVE)
    assert not _has_mismatch(findings)


def test_self_documentation_holds_on_real_wi3482_proposal() -> None:
    """The actual WI-3482 proposal (which describes the hazard) must not self-trigger."""
    proposal = _PROJECT_ROOT / "bridge" / "gtkb-git-hooks-path-mismatch-lint-001.md"
    findings = lint.lint_text(proposal.read_text(encoding="utf-8"), active_hooks_path=_ACTIVE)
    offenders = [f.render() for f in findings if f.pattern_id == "git-hooks-path-mismatch"]
    assert not offenders, offenders


# --- Diagnostic-by-default / --strict contract -------------------------------


def test_strict_exit_code_contract(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Findings exit 0 unless --strict; non-zero only through --strict (preserved)."""
    monkeypatch.setattr(lint, "_resolve_active_hooks_path", lambda *a, **k: _ACTIVE)
    draft = tmp_path / "draft-proposal.md"
    draft.write_text('target_paths: [".git/hooks/pre-commit"]\n', encoding="utf-8")

    assert lint.main(["--file", str(draft), "--strict"]) == 1
    assert lint.main(["--file", str(draft)]) == 0


# --- Helper-level unit coverage ----------------------------------------------


def test_normalize_path_separators_folds_backslashes() -> None:
    assert lint._normalize_path_separators(".git\\hooks\\pre-commit") == ".git/hooks/pre-commit"


def test_line_targets_inactive_surface_excludes_hazard_docs() -> None:
    assert lint._line_targets_inactive_hook_surface('target_paths: [".git/hooks/pre-commit"]')
    assert not lint._line_targets_inactive_hook_surface(
        "the .git/hooks directory is inert because core.hooksPath overrides the default"
    )
