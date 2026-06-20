"""Spec-derived tests for the harness-local scratchpad non-authority boundary.

Implements the spec-to-test mapping in
``bridge/gtkb-harness-local-scratchpad-boundary-003.md`` for:

- ``DELIB-20260619-HARNESS-SCRATCHPAD-NON-AUTHORITY``.
- ``ADR-ISOLATION-APPLICATION-PLACEMENT-001``.
- ``DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001``.
- ``.claude/rules/project-root-boundary.md``.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.doctor import _check_harness_local_scratchpad_boundary

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BOUNDARY_DOCS = (
    PROJECT_ROOT / "AGENTS.md",
    PROJECT_ROOT / ".claude" / "rules" / "project-root-boundary.md",
)
REQUIRED_BOUNDARY_TERMS = (
    "Harness-local scratchpads",
    "non-authoritative",
    "Antigravity planning/brain files",
    "Codex automation memory",
    "Claude Code auto-memory",
    "`MEMORY.md` hierarchy",
    "formal GT-KB artifacts",
    "implementation reports",
    "verification verdicts",
    "tests",
    "doctor checks",
    "bridge evidence",
    "governed decisions",
    "release evidence",
    "dependency closure",
    "promoted into governed in-root artifacts",
)

GOOD_BOUNDARY_TEXT = """# Boundary

Harness-local scratchpads are non-authoritative. This includes Antigravity planning/brain files,
Codex automation memory, Claude Code auto-memory, and the
`MEMORY.md` hierarchy.

Formal GT-KB artifacts, implementation reports, verification verdicts, tests,
doctor checks, bridge evidence, governed decisions, release evidence, and
dependency closure must not read from or depend on harness-local scratchpads as
authority. Project-relevant information originating in a scratchpad must be
promoted into governed in-root artifacts before it is cited.
"""


def _write_boundary_project(tmp_path: Path, *, agents_text: str, rule_text: str) -> Path:
    """Create the two boundary surfaces consumed by the doctor check."""
    rules_dir = tmp_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_text(agents_text, encoding="utf-8")
    (rules_dir / "project-root-boundary.md").write_text(rule_text, encoding="utf-8")
    return tmp_path


def test_live_boundary_docs_declare_scratchpads_non_authoritative() -> None:
    """The live operator-facing surfaces carry the complete boundary vocabulary."""
    for doc in BOUNDARY_DOCS:
        text = doc.read_text(encoding="utf-8")
        lowered = text.lower()
        missing = [term for term in REQUIRED_BOUNDARY_TERMS if term.lower() not in lowered]
        assert not missing, f"{doc.relative_to(PROJECT_ROOT)} missing boundary terms: {missing}"


def test_live_doctor_check_passes_for_current_boundary_docs() -> None:
    """The deterministic doctor check passes against the current repository text."""
    result = _check_harness_local_scratchpad_boundary(PROJECT_ROOT)

    assert result.status == "pass", f"expected pass; got {result.status}: {result.message}"
    assert "scratchpad non-authority boundary declared" in result.message


def test_external_harness_exception_remains_executable_only() -> None:
    """The scratchpad boundary must not broaden the external-harness exception."""
    rule_text = (PROJECT_ROOT / ".claude" / "rules" / "project-root-boundary.md").read_text(encoding="utf-8")

    assert "External Harness Executable Resolution Exception remains executable-only" in rule_text
    assert "not reading, writing" in rule_text
    assert "verifying, or requiring harness-local files" in rule_text


def test_doctor_check_passes_for_synthetic_declared_boundary(tmp_path: Path) -> None:
    """Synthetic project: both required surfaces declare the boundary, so the check passes."""
    project = _write_boundary_project(tmp_path, agents_text=GOOD_BOUNDARY_TEXT, rule_text=GOOD_BOUNDARY_TEXT)

    result = _check_harness_local_scratchpad_boundary(project)

    assert result.status == "pass", f"expected pass; got {result.status}: {result.message}"


def test_doctor_check_fails_when_boundary_terms_are_missing(tmp_path: Path) -> None:
    """Synthetic project: missing required boundary vocabulary is a doctor failure."""
    incomplete = "# Boundary\n\nHarness-local scratchpads are operational notes.\n"
    project = _write_boundary_project(tmp_path, agents_text=GOOD_BOUNDARY_TEXT, rule_text=incomplete)

    result = _check_harness_local_scratchpad_boundary(project)

    assert result.status == "fail", f"expected fail; got {result.status}: {result.message}"
    assert "project-root-boundary.md missing required term" in result.message


def test_doctor_check_fails_positive_authority_regression(tmp_path: Path) -> None:
    """Synthetic project: MEMORY.md cannot regress into canonical release evidence."""
    bad_rule = GOOD_BOUNDARY_TEXT + "\nMEMORY.md is canonical release evidence for dependency closure.\n"
    project = _write_boundary_project(tmp_path, agents_text=GOOD_BOUNDARY_TEXT, rule_text=bad_rule)

    result = _check_harness_local_scratchpad_boundary(project)

    assert result.status == "fail", f"expected fail; got {result.status}: {result.message}"
    assert "grants scratchpad authority" in result.message
    assert "MEMORY.md is canonical release evidence" in result.message
