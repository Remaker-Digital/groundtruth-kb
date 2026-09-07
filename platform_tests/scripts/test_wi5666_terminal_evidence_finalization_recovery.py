"""Work item 5666 terminal-evidence recovery - specification-derived tests.

Cites all fifteen governing specifications (strict spec-derived runner mapping):

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- SPEC-AUQ-POLICY-ENGINE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-STANDING-BACKLOG-001
- ADR-CODEX-HOOK-PARITY-FALLBACK-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- GOV-WORK-TREE-HYGIENE-001

These tests use deterministic in-root fixtures and read-only repository /
governance observations. They do NOT alter the four historical implementation
paths, the real bridge index, MemBase, formal approvals, dispatcher/TAFE state,
or runtime carriers.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PROPOSAL = REPO_ROOT / "bridge" / "gtkb-wi5666-skill-rename-parent-terminal-evidence-recovery-001.md"
BRIDGE_GO = REPO_ROOT / "bridge" / "gtkb-wi5666-skill-rename-parent-terminal-evidence-recovery-002.md"

PARENT_PAUTH_ID = "PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION"
MEMBERSHIP_ID = "PWM-GTKB-SKILL-RENAME-REFERENCE-SWEEP-WI-5666"
PROJECT_ID = "GTKB-SKILL-RENAME-REFERENCE-SWEEP"
HISTORICAL_COMMIT = "ad19a3662baf1c8d206901e9a4bc83b7f3d7ecfd"
FOUR_HISTORICAL_PATHS = [
    ".gitignore",
    "docs/harness-parity-phase-2-matrix.md",
    "docs/procedures/per-thread-finalization-repair.md",
    "groundtruth-kb/docs/reference/canonical-terminology-detail.md",
]
EIGHT_SCRATCH_PROBES = [
    ".claude/skills/gtkb-bridge/helpers/draft-x.md",
    ".claude/skills/gtkb-verify/helpers/draft-x.md",
    ".claude/skills/gtkb-verify/helpers/_temp_verdict_x",
    ".claude/skills/gtkb-verify/helpers/x-draft-body.md",
    ".claude/skills/gtkb-verify/helpers/tmp_gtkb-wi1-draft.md",
    ".claude/skills/gtkb-verify/helpers/write_bridge_x.py",
    ".codex/skills/gtkb-verify/helpers/tmp_gtkb-wi1-draft.md",
    ".codex/skills/gtkb-verify/helpers/gtkb-wi1-draft-body.md",
]
SPEC_IDS = [
    "GOV-FILE-BRIDGE-AUTHORITY-001",
    "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
    "SPEC-AUQ-POLICY-ENGINE-001",
    "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
    "GOV-STANDING-BACKLOG-001",
    "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
    "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
    "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
    "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
    "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
    "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
    "GOV-WORK-TREE-HYGIENE-001",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_fresh_recovery_bridge_chain_is_append_only_role_separated_and_exactly_linked() -> None:
    """GOV-FILE-BRIDGE-AUTHORITY-001 / PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001."""
    assert BRIDGE_PROPOSAL.exists(), "fresh recovery v001 proposal must exist"
    proposal = _read(BRIDGE_PROPOSAL)
    assert "Version: 001" in proposal or "Version: 001" in proposal
    assert "bridge_kind: prime_proposal" in proposal
    assert "Work Item: WI-5666" in proposal
    assert PROJECT_ID in proposal
    assert PARENT_PAUTH_ID in proposal
    # Independent v002 GO must exist and be role-separated (LO verdict).
    assert BRIDGE_GO.exists(), "independent v002 GO must exist"
    go = _read(BRIDGE_GO)
    assert "GO" in go.splitlines()[0]
    assert "loyal-opposition" in go.lower() or "lo_verdict" in go
    # The report under review is part of the durable chain.  Validate the
    # existing append-only sequence instead of requiring that report to be
    # absent, so this assertion is reproducible both before and after filing.
    prefix = "gtkb-wi5666-skill-rename-parent-terminal-evidence-recovery-"
    versions = sorted((REPO_ROOT / "bridge").glob(f"{prefix}[0-9][0-9][0-9].md"))
    numbers = [int(path.stem.rsplit("-", 1)[1]) for path in versions]
    assert numbers == list(range(1, numbers[-1] + 1)), "numbered chain must have no gaps"

    expected_prefix = {1: "NEW", 2: "GO", 3: "NEW", 4: "NO-GO"}
    for version, expected_status in expected_prefix.items():
        path = REPO_ROOT / "bridge" / f"{prefix}{version:03d}.md"
        assert path.exists(), f"required recovery-chain version {version:03d} must exist"
        assert _read(path).splitlines()[0].strip() == expected_status

    # Any correction cycles after the first NO-GO alternate PB REVISED reports
    # and independent LO verdicts.  This remains valid after the report and
    # terminal verdict are filed.
    for path in versions[4:]:
        version = int(path.stem.rsplit("-", 1)[1])
        text = _read(path)
        status = text.splitlines()[0].strip()
        if version % 2:
            assert status == "REVISED"
            assert "bridge_kind: implementation_report" in text
            assert "prime-builder" in text.lower()
        else:
            assert status in {"NO-GO", "VERIFIED"}
            assert "loyal-opposition" in text.lower() or "bridge_kind: lo_verdict" in text


def test_owner_decisions_unique_membership_and_parent_pauth_cover_wi5666_recovery() -> None:
    """SPEC-AUQ-POLICY-ENGINE-001 / GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001."""
    proposal = _read(BRIDGE_PROPOSAL)
    assert "DELIB-20260801-WI5666-CANONICAL-PARENT-SELECTION" in proposal
    assert "DELIB-20260730-WI5666-SPEC-DERIVED-TEST-EXPANSION" in proposal
    assert MEMBERSHIP_ID in proposal
    assert PARENT_PAUTH_ID in proposal
    # Parent PAUTH declares bounded classes and retained bans (no mutation of
    # dispatcher/credential/release/history).
    for ban in ("dispatcher", "credential", "push", "history-rewrite", "deployment", "release", "destructive-cleanup"):
        assert ban in proposal.lower()


def test_historical_commit_has_exact_four_path_boundary_and_current_paths_are_clean() -> None:
    """ADR-ISOLATION-APPLICATION-PLACEMENT-001 / GOV-WORK-TREE-HYGIENE-001."""
    show = subprocess.run(
        ["git", "show", "--name-only", "--format=", HISTORICAL_COMMIT],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert show.returncode == 0, show.stderr
    touched = [ln for ln in show.stdout.splitlines() if ln.strip()]
    for path in FOUR_HISTORICAL_PATHS:
        assert path in touched, f"historical commit must touch {path}"
    status = subprocess.run(
        ["git", "status", "--porcelain", "--", *FOUR_HISTORICAL_PATHS],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert status.returncode == 0, status.stderr
    assert status.stdout.strip() == "", "the four current paths must be clean/unstaged at HEAD"


def test_all_eight_canonical_scratch_patterns_ignore_their_probe_paths() -> None:
    """ADR-CODEX-HOOK-PARITY-FALLBACK-001: Claude/Codex scratch-ignore probes are equivalent."""
    for probe in EIGHT_SCRATCH_PROBES:
        check = subprocess.run(
            ["git", "check-ignore", "--quiet", probe],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert check.returncode == 0, f"probe must be ignored: {probe}"


def test_four_historical_targets_have_zero_residual_mapped_skill_paths() -> None:
    """ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001: no residual bare skill-directory references."""
    banned_fragments = [
        ".claude/skills/bridge",
        ".claude/skills/verify",
        ".claude/skills/bridge-propose",
        ".claude/skills/assertion-triage",
        "skills/verify/helpers/write_verdict.py",
        "skills/bridge-propose/helpers",
    ]
    for rel in FOUR_HISTORICAL_PATHS:
        text = _read(REPO_ROOT / rel)
        for frag in banned_fragments:
            assert frag not in text, f"{rel} must not reference {frag}"


def test_module_declares_all_fifteen_specs_for_derived_test_discovery() -> None:
    """DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: citation lock prevents silent mapping loss."""
    docstring = sys.modules[__name__].__doc__ or ""
    for spec_id in SPEC_IDS:
        assert spec_id in docstring, f"module docstring must cite {spec_id}"
