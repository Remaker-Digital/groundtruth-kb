"""WI-6365: the VERIFIED gate accepts post-commit finalization evidence.

Under owner canon the commit of the work product is the terminal state and
**precedes** the `VERIFIED` verdict. The gate previously demanded a
"Same-transaction path set" — evidence that verdict and work product entered git
in one commit — which a canonical verdict can never carry. This module pins the
corrected predicate: either form is accepted, and the audit guarantee is kept.

**Scope note (owner AUQ 2026-08-16).** These tests exercise the neutral baseline
and the non-projection copies. `.claude/` and `.goose/` are projector outputs and
are deliberately out of scope for this change: the projector has no per-file mode
and a full run writes 176 files per harness. They therefore still carry the old
predicate, and are asserted as such below so the deferral is visible rather than
silent.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

BASELINE = REPO_ROOT / ".harness-baseline-configuration" / "hooks" / "bridge-compliance-gate.py"

# In scope for WI-6365: the baseline plus every copy that is NOT a projector output.
IN_SCOPE_COPIES: tuple[Path, ...] = (
    BASELINE,
    REPO_ROOT / "config" / "hooks" / "gtkb-bridge-compliance-gate.py",
    REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py",
    REPO_ROOT
    / "groundtruth-kb"
    / "tests"
    / "fixtures"
    / "scaffold_golden"
    / "dual-agent"
    / ".claude"
    / "hooks"
    / "bridge-compliance-gate.py",
    REPO_ROOT
    / "groundtruth-kb"
    / "tests"
    / "fixtures"
    / "scaffold_golden"
    / "local-only"
    / ".claude"
    / "hooks"
    / "bridge-compliance-gate.py",
)

# Projector outputs. These were deferred out of the original change and, until
# the resync landed, still rejected the canonical post-commit form. They now
# carry the corrected predicate, so they are asserted positively below.
PROJECTION_COPIES: tuple[Path, ...] = (
    REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py",
    REPO_ROOT / ".goose" / "hooks" / "bridge-compliance-gate.py",
)

_COUNTER = iter(range(1000))


def _load(path: Path):
    if not path.is_file():
        pytest.skip(f"gate copy not present: {path}")
    name = f"bridge_compliance_gate_wi6365_{next(_COUNTER)}"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _verdict(section_body: str) -> str:
    return "VERIFIED\n\n# Verdict\n\n## Commit Finalization Evidence\n\n" + section_body + "\n"


POST_COMMIT = _verdict("Work-product commit: `a1b2c3d4e5f6`\n\n- `scripts/tool.py`\n- `platform_tests/test_tool.py`\n")
SAME_TRANSACTION = _verdict("Same-transaction path set:\n\n- `scripts/tool.py`\n")
EMPTY_PATH_SET = _verdict("Work-product commit: `a1b2c3d4e5f6`\n\n_None._\n")
NO_EVIDENCE_SECTION = "VERIFIED\n\n# Verdict\n\nNo finalization evidence here.\n"


def _ids(paths: tuple[Path, ...]) -> list[str]:
    return [p.relative_to(REPO_ROOT).as_posix() for p in paths]


@pytest.mark.parametrize("gate_path", IN_SCOPE_COPIES, ids=_ids(IN_SCOPE_COPIES))
def test_verified_with_post_commit_evidence_is_allowed(gate_path: Path) -> None:
    """The canonical form: commit precedes verdict, verdict cites the commit."""
    gate = _load(gate_path)
    assert gate._has_commit_finalization_evidence(POST_COMMIT) is True


@pytest.mark.parametrize("gate_path", IN_SCOPE_COPIES, ids=_ids(IN_SCOPE_COPIES))
def test_verified_with_same_transaction_path_set_still_allowed(gate_path: Path) -> None:
    """Backward compatibility: legacy atomic-helper output is unaffected."""
    gate = _load(gate_path)
    assert gate._has_commit_finalization_evidence(SAME_TRANSACTION) is True


@pytest.mark.parametrize("gate_path", IN_SCOPE_COPIES, ids=_ids(IN_SCOPE_COPIES))
def test_verified_without_any_finalization_evidence_still_blocked(gate_path: Path) -> None:
    """The audit guarantee survives: no evidence section is still refused."""
    gate = _load(gate_path)
    assert gate._has_commit_finalization_evidence(NO_EVIDENCE_SECTION) is False


@pytest.mark.parametrize("gate_path", IN_SCOPE_COPIES, ids=_ids(IN_SCOPE_COPIES))
def test_verified_with_empty_path_set_still_blocked(gate_path: Path) -> None:
    """Evidence must be substantive: a commit reference alone is not enough."""
    gate = _load(gate_path)
    assert gate._has_commit_finalization_evidence(EMPTY_PATH_SET) is False


def test_every_in_scope_copy_carries_the_same_predicate_behaviour() -> None:
    """Predicate-level parity, never file identity.

    File parity is impossible by construction: the baseline is a template whose
    `{{HARNESS...}}` placeholders the projector substitutes, renaming identifiers
    and rewriting paths. Parity is therefore asserted behaviourally.
    """
    outcomes = {
        path.relative_to(REPO_ROOT).as_posix(): (
            _load(path)._has_commit_finalization_evidence(POST_COMMIT),
            _load(path)._has_commit_finalization_evidence(SAME_TRANSACTION),
            _load(path)._has_commit_finalization_evidence(NO_EVIDENCE_SECTION),
        )
        for path in IN_SCOPE_COPIES
    }
    assert set(outcomes.values()) == {(True, True, False)}, outcomes


def test_scaffold_golden_fixtures_carry_corrected_predicate() -> None:
    """GOV-GTKB-ADOPTION-ENFORCEMENT-001: a freshly scaffolded adopter is not shipped the defect."""
    goldens = [p for p in IN_SCOPE_COPIES if "scaffold_golden" in p.as_posix()]
    assert goldens, "scaffold golden fixtures must be in scope"
    for path in goldens:
        assert _load(path)._has_commit_finalization_evidence(POST_COMMIT) is True


@pytest.mark.parametrize("gate_path", PROJECTION_COPIES, ids=_ids(PROJECTION_COPIES))
def test_projections_carry_the_corrected_predicate(gate_path: Path) -> None:
    """The deferred projection resync has landed; this is its inverted assertion.

    `.claude/` and `.goose/` are projector outputs that were excluded from the
    original change by owner decision, and while that deferral stood they
    rejected the canonical post-commit form. The predecessor of this test
    asserted that rejection so the gap stayed visible rather than silent, and it
    directed that the assertion be *inverted rather than deleted* once the
    resync landed. It has: both copies now accept the post-commit form.

    Inverting rather than deleting is what keeps the guarantee. A deleted test
    would let these copies regress to the old predicate unnoticed; asserting the
    corrected behaviour means a future projection that reintroduces the defect
    fails here.

    `SAME_TRANSACTION` remains accepted for backward compatibility with verdicts
    already written in that form.
    """
    gate = _load(gate_path)
    assert gate._has_commit_finalization_evidence(POST_COMMIT) is True
    assert gate._has_commit_finalization_evidence(SAME_TRANSACTION) is True
