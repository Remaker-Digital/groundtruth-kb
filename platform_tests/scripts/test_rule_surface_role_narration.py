"""Executable acceptance boundary for WI-7804 role narration.

The governed instruction sources must describe durable roles and canonical
domain state without implying that one agent owns a work item or returns for a
later bridge phase.  This test intentionally reads canonical baseline and
adopter-source files, never generated harness projections.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from pathlib import Path

import pytest

DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(os.environ.get("GTKB_ROLE_NARRATION_ROOT", DEFAULT_PROJECT_ROOT)).resolve()

SOURCE_MATRIX = (
    ".harness-baseline-configuration/AGENTS.md",
    ".harness-baseline-configuration/rules/bridge-essential.md",
    ".harness-baseline-configuration/rules/canonical-terminology.md",
    ".harness-baseline-configuration/rules/decision-ledger.md",
    ".harness-baseline-configuration/rules/file-bridge-protocol.md",
    ".harness-baseline-configuration/rules/operating-model.md",
    ".harness-baseline-configuration/rules/prime-bridge-collaboration-protocol.md",
    ".harness-baseline-configuration/rules/session-bootstrap.md",
    ".harness-baseline-configuration/rules/way-of-working.md",
    ".harness-baseline-configuration/skills/gtkb-bridge-config/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-bridge/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-harness-parity-review/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-hygiene-investigation/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-hygiene-sweep/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-lo-hygiene-assessment/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-session-wrap/SKILL.md",
    ".harness-baseline-configuration/skills/gtkb-session-wrap/references/audit-checklist.md",
    ".harness-baseline-configuration/skills/gtkb-session-wrap/references/handoff-template.md",
    ".harness-baseline-configuration/skills/gtkb-verify/SKILL.md",
    "groundtruth-kb/docs/method/06-dual-agent.md",
    "groundtruth-kb/docs/method/07-sessions.md",
    "groundtruth-kb/docs/method/12-file-bridge-automation.md",
    "groundtruth-kb/docs/method/14-lifecycle.md",
    "groundtruth-kb/docs/reference/canonical-terminology-detail.md",
    "groundtruth-kb/templates/project/AGENTS.md",
    "groundtruth-kb/templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md",
    "groundtruth-kb/templates/project/codex-bootstrap/CODEX-WAY-OF-WORKING.md",
    "groundtruth-kb/templates/rules/bridge-essential.md",
    "groundtruth-kb/templates/rules/canonical-terminology.md",
    "groundtruth-kb/templates/rules/file-bridge-protocol.md",
    "groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md",
    "groundtruth-kb/templates/skills/gtkb-bridge/SKILL.md",
)

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

PROHIBITED_CONTINUITY = {
    "earlier agent revises and resubmits": re.compile(r"\brevises and resubmits\b", re.I),
    "earlier agent corrects and resubmits": re.compile(r"\bcorrects and resubmits\b", re.I),
    "same-agent lifecycle cycle": re.compile(r"\bthe cycle continues\b", re.I),
    "return-to-terminal instruction": re.compile(r"\bdo not respond unless\b", re.I),
    "queue ownership": re.compile(r"\b(?:prime builder\s+)?queue ownership\b", re.I),
    "durable bridge handoff": re.compile(
        r"\bbridge state\b.{0,80}\b(?:durable|authoritative)\b.{0,40}\bhandoff\b", re.I
    ),
    "continuing canonical bridge authority": re.compile(
        r"\b(?:bridge state|status-bearing versioned files?)\b.{0,90}\b(?:are|is) canonical\b",
        re.I,
    ),
    "active DEFERRED routing": re.compile(
        r"\bDEFERRED\b.{0,100}\b(?:owner-directed|parking|parked|non-actionable|status)\b",
        re.I,
    ),
}

POSITIVE_REQUIREMENTS = {
    ".harness-baseline-configuration/AGENTS.md": (
        re.compile(r"agents are \*\*ephemeral\*\*", re.I),
        re.compile(r"agent owns only the immediate bridge action", re.I),
        re.compile(r"must not assume it will resume the work", re.I),
    ),
    ".harness-baseline-configuration/rules/bridge-essential.md": (
        re.compile(r"authoritative.{0,80}(?:receives|loads|receipt)", re.I),
        re.compile(r"(?:no continuing authority|never thereafter)", re.I),
        re.compile(r"(?:one|next).{0,30}artifact", re.I),
        re.compile(r"re-quer(?:y|ies).{0,50}canonical", re.I),
    ),
    ".harness-baseline-configuration/rules/way-of-working.md": (
        re.compile(r"authoritative.{0,80}(?:receives|loads|receipt)", re.I),
        re.compile(r"(?:no continuing authority|never thereafter)", re.I),
        re.compile(r"(?:one|next).{0,30}artifact", re.I),
        re.compile(r"re-quer(?:y|ies).{0,50}canonical", re.I),
    ),
    ".harness-baseline-configuration/rules/operating-model.md": (
        re.compile(r"whichever.{0,40}session.{0,40}next holds.{0,30}role", re.I),
        re.compile(r"(?:one|next).{0,30}artifact", re.I),
    ),
    ".harness-baseline-configuration/rules/prime-bridge-collaboration-protocol.md": (
        re.compile(r"whichever.{0,40}session.{0,40}next holds.{0,30}role", re.I),
        re.compile(r"(?:one|next).{0,30}artifact", re.I),
    ),
}


def _read_required(path: Path) -> str:
    assert path.is_file(), f"required WI-7804 instruction source is missing: {path}"
    return path.read_text(encoding="utf-8", errors="strict")


def _resolve_local_markdown_link(source: Path, raw_target: str, root: Path) -> Path | None:
    target = raw_target.strip().split("#", 1)[0].strip()
    if not target or "://" in target or target.startswith(("mailto:", "#")):
        return None
    resolved = (source.parent / target).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved if resolved.suffix.lower() == ".md" else None


def _discover_linked_sources(root: Path, seeds: Iterable[Path], allowed: set[Path]) -> set[Path]:
    pending = list(seeds)
    discovered: set[Path] = set()
    while pending:
        source = pending.pop()
        if source in discovered:
            continue
        text = _read_required(source)
        discovered.add(source)
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            linked = _resolve_local_markdown_link(source, raw_target, root)
            if linked is not None and linked in allowed and linked not in discovered:
                pending.append(linked)
    return discovered


def _continuity_violations(paths: Iterable[Path]) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for path in paths:
        text = _read_required(path)
        matched = [label for label, pattern in PROHIBITED_CONTINUITY.items() if pattern.search(text)]
        if matched:
            findings[path.as_posix()] = matched
    return findings


def test_canonical_instruction_closure_routes_each_artifact_to_a_fresh_role_bound_session() -> None:
    """The exact canonical/adopter closure teaches no cross-artifact agent tenure."""
    matrix = {PROJECT_ROOT / relative for relative in SOURCE_MATRIX}
    discovered = _discover_linked_sources(PROJECT_ROOT, sorted(matrix), matrix)

    assert discovered == matrix, "the exact WI-7804 source matrix was not completely traversed"
    assert _continuity_violations(discovered) == {}

    for relative, requirements in POSITIVE_REQUIREMENTS.items():
        text = _read_required(PROJECT_ROOT / relative)
        missing = [pattern.pattern for pattern in requirements if not pattern.search(text)]
        assert not missing, f"{relative} lacks required successor-session semantics: {missing}"


def test_recursive_link_discovery_accepts_clean_linked_resource(tmp_path: Path) -> None:
    nested = tmp_path / "references" / "successor.md"
    nested.parent.mkdir()
    nested.write_text("A fresh role-bound session delivers the next artifact.\n", encoding="utf-8")
    seed = tmp_path / "SKILL.md"
    seed.write_text("Read [the successor rule](references/successor.md).\n", encoding="utf-8")

    allowed = {seed.resolve(), nested.resolve()}
    discovered = _discover_linked_sources(tmp_path.resolve(), [seed.resolve()], allowed)

    assert discovered == allowed
    assert _continuity_violations(discovered) == {}


def test_recursive_link_discovery_rejects_continuity_in_linked_resource(tmp_path: Path) -> None:
    nested = tmp_path / "references" / "continuity.md"
    nested.parent.mkdir()
    nested.write_text("Prime Builder corrects and resubmits.\n", encoding="utf-8")
    seed = tmp_path / "SKILL.md"
    seed.write_text("Read [the lifecycle rule](references/continuity.md).\n", encoding="utf-8")

    allowed = {seed.resolve(), nested.resolve()}
    discovered = _discover_linked_sources(tmp_path.resolve(), [seed.resolve()], allowed)
    findings = _continuity_violations(discovered)

    assert nested.as_posix() in findings
    assert "earlier agent corrects and resubmits" in findings[nested.as_posix()]


def test_source_matrix_missing_file_fails_closed(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"

    with pytest.raises(AssertionError, match="required WI-7804 instruction source is missing"):
        _discover_linked_sources(tmp_path.resolve(), [missing], {missing})
