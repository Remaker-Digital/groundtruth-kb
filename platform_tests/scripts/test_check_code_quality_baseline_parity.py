from __future__ import annotations

import subprocess
import sys
from pathlib import Path

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
        )
    )
    proposal.write_text(
        "bridge_kind: implementation_proposal\n## Code Quality Baseline\n"
        "| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |\n|---|---|---|---|---|\n" + rows,
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
        "| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |\n|---|---|---|---|---|\n"
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
