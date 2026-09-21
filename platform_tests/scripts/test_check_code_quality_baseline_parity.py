from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.hooks.code_quality_baseline_proposal_check import hook_response

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_code_quality_baseline_parity.py"


def test_parity_script_returns_0_on_clean_file(tmp_path: Path) -> None:
    proposal = tmp_path / "clean.md"
    rows = "\n".join(
        f"| {rule} | Yes | plan | pytest | |"
        for rule in (
            "CQ-SECRETS-001",
            "CQ-PATHS-001",
            "CQ-CONSTANTS-001",
            "CQ-DOCS-001",
            "CQ-COMPLEXITY-001",
            "CQ-TESTS-001",
            "CQ-LOGGING-001",
            "CQ-SECURITY-001",
            "CQ-VERIFICATION-001",
            "CQ-PERF-001",
            "CQ-DEPS-001",
        )
    )
    proposal.write_text(
        "bridge_kind: implementation_proposal\n| Project | Scope |\n|---|---|\n| Example | src |\n"
        "## Code Quality Baseline\n"
        "| Rule ID | Applies? | Compliance plan | Verification | N/A reason |\n|---|---|---|---|---|\n"
        + rows
        + "\n## Other review\n| Separate | Table |\n|---|---|\n| a | b |\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(proposal)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_parity_script_returns_1_on_invalid_rule(tmp_path: Path) -> None:
    proposal = tmp_path / "bad.md"
    proposal.write_text(
        "bridge_kind: implementation_proposal\n## Code Quality Baseline\n"
        "| Rule ID | Applies? | Compliance plan | Verification | N/A reason |\n|---|---|---|---|---|\n"
        "| CQ-BAD-001 | Yes | plan | pytest | |\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(proposal)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "unknown_rule_id" in result.stdout


def test_parity_script_returns_1_on_missing_heading(tmp_path: Path) -> None:
    proposal = tmp_path / "bad.md"
    proposal.write_text("bridge_kind: implementation_proposal\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(proposal)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "missing_heading" in result.stdout


def test_parity_script_ignores_verdicts(tmp_path: Path) -> None:
    verdict = tmp_path / "verdict.md"
    verdict.write_text("GO\n\n# Review\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(verdict)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0


# This independent list is the eleven IDs in SPEC-CODE-QUALITY-CHECKLIST-001.
QUALITY_RULES = (
    "CQ-SECRETS-001",
    "CQ-PATHS-001",
    "CQ-CONSTANTS-001",
    "CQ-DOCS-001",
    "CQ-COMPLEXITY-001",
    "CQ-TESTS-001",
    "CQ-LOGGING-001",
    "CQ-SECURITY-001",
    "CQ-VERIFICATION-001",
    "CQ-PERF-001",
    "CQ-DEPS-001",
)


def _quality_proposal(*, omit=None, replacement=None, extra=None):
    rows = [
        f"| {rule} | Yes | Exercise the changed behavior | pytest selected_module | |"
        for rule in QUALITY_RULES
        if rule != omit
    ]
    if replacement is not None:
        rows[0] = replacement
    if extra is not None:
        rows.append(extra)
    return (
        "bridge_kind: implementation_proposal\n## Code Quality Baseline\n"
        "| Rule ID | Applies? | Compliance plan | Verification | N/A reason |\n"
        "|---|---|---|---|---|\n" + "\n".join(rows)
    )


@pytest.mark.parametrize("rule", QUALITY_RULES)
def test_quality_hook_requires_each_current_rule(rule) -> None:
    response = hook_response(_quality_proposal(omit=rule))
    assert response["decision"] == "block"
    assert "missing_rules" in response["reason"] and rule in response["reason"]


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        ("| CQ-SECRETS-001 | Yes | | pytest | |", "empty_yes_cells"),
        ("| CQ-SECRETS-001 | Yes | Validate input | | |", "empty_yes_cells"),
        ("| CQ-SECRETS-001 | N/A | | | |", "empty_na_reason"),
        (
            "| CQ-SECRETS-001 | Owner waiver: CQ-SECRETS-001 - DELIB-OLD - owner said yes | | | |",
            "bad_applies",
        ),
        ("| CQ-SECRETS-001 | No | | | historical approval |", "bad_applies"),
    ],
)
def test_quality_hook_requires_concrete_plan_verification_or_nonapplicability(row, reason) -> None:
    response = hook_response(_quality_proposal(replacement=row))
    assert response["decision"] == "block"
    assert reason in response["reason"]


def test_quality_hook_accepts_concrete_nonapplicability_without_a_waiver_carrier() -> None:
    proposal = _quality_proposal(replacement="| CQ-SECRETS-001 | N/A | | | Only moves a public documentation heading |")
    assert hook_response(proposal) == {}


def test_quality_hook_rejects_duplicate_conflicting_rule_rows() -> None:
    proposal = _quality_proposal(extra="| CQ-SECRETS-001 | N/A | | | Different scope claim |")
    response = hook_response(proposal)
    assert response["decision"] == "block"
    assert "duplicate_rule_id" in response["reason"]
