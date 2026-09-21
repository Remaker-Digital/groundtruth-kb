"""Authored successor instructions and their actual local Markdown closure.

This text check is separate from native binding/claim behavior and actual-host
qualification. It discovers authored baseline rules and follows linked
resources without requiring those resources to appear in a frozen file list.
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
    "AGENTS.md",
    ".harness-baseline-configuration/rules/bridge-essential.md",
    ".harness-baseline-configuration/rules/canonical-terminology.md",
    ".harness-baseline-configuration/rules/file-bridge-protocol.md",
    ".harness-baseline-configuration/rules/operating-model.md",
    ".harness-baseline-configuration/rules/session-bootstrap.md",
    ".harness-baseline-configuration/rules/way-of-working.md",
    ".agents/skills/gtkb-bridge/SKILL.md",
    ".agents/skills/gtkb-harness-parity-review/SKILL.md",
    ".agents/skills/gtkb-hygiene-investigation/SKILL.md",
    ".agents/skills/gtkb-hygiene-sweep/SKILL.md",
    ".agents/skills/gtkb-lo-hygiene-assessment/SKILL.md",
    ".agents/skills/gtkb-session-wrap/SKILL.md",
    ".agents/skills/gtkb-session-wrap-scan/SKILL.md",
    ".agents/skills/gtkb-session-wrap/references/audit-checklist.md",
    ".agents/skills/gtkb-session-wrap/references/handoff-template.md",
    ".agents/skills/gtkb-verify/SKILL.md",
    "groundtruth-kb/docs/method/06-dual-agent.md",
    "groundtruth-kb/docs/method/07-sessions.md",
    "groundtruth-kb/docs/method/12-file-bridge-automation.md",
    "groundtruth-kb/docs/method/14-lifecycle.md",
    "groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md",
    ".agents/skills/gtkb-bridge-propose/SKILL.md",
    ".agents/skills/gtkb-proposal-review/SKILL.md",
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
        r"\b(?:bridge state|status-bearing (?:numbered |versioned )?files?)\b.{0,90}\b(?:are|is) canonical\b", re.I
    ),
    "active DEFERRED routing": re.compile(
        r"\bDEFERRED\b(?:\s*[:—-]\s*|\s+(?:(?:messages|items)\s+)?"
        r"(?:is|are|means|denotes|remains|serves as)\s+)(?!not\b|no longer\b|never\b)"
        r"[^.\n]{0,70}\b(?:owner-directed|parking|parked|non-actionable|(?:active|current|valid)\s+status)\b",
        re.I,
    ),
    "original implementer tenure": re.compile(r"\bowns implementation follow-through\b", re.I),
    "persistent prompt dependency": re.compile(r"\bsession_prompts\b", re.I),
}

# These current entry points must teach the positive contract, not merely avoid
# a list of old words. Other sources in the closure must not contradict it.
RECEIPT_REQUIREMENTS = (
    r"authoritative.{0,100}(?:receives|loads|receipt)",
    r"(?:no continuing authority|never thereafter)",
    r"re-query.{0,40}canonical",
    r"(?:one|next).{0,30}artifact",
    r"successor.{0,80}(?:own claim|fresh claim)",
)
POSITIVE_REQUIREMENTS = {
    "AGENTS.md": (
        r"ephemeral.{0,30}(?:agent )?contexts",
        r"role is immutable",
        r"claims the next artifact",
        r"no enduring ownership",
        r"independently reviews and verifies work it did not author",
    ),
    ".harness-baseline-configuration/rules/bridge-essential.md": RECEIPT_REQUIREMENTS,
    ".harness-baseline-configuration/rules/way-of-working.md": RECEIPT_REQUIREMENTS,
    ".harness-baseline-configuration/rules/operating-model.md": RECEIPT_REQUIREMENTS,
    "groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md": RECEIPT_REQUIREMENTS,
}


def _read_required(path: Path) -> str:
    assert path.is_file(), f"required WI-7804 instruction source is missing: {path}"
    return path.read_text(encoding="utf-8", errors="strict")


def _resolve_local_markdown_link(source: Path, raw_target: str, root: Path) -> Path | None:
    target = raw_target.strip().split("#", 1)[0].strip()
    if not target or "://" in target or target.startswith(("mailto:", "#")):
        return None
    resolved = (source.parent / target).resolve()
    assert resolved.is_relative_to(root), f"instruction link leaves selected root: {source} -> {raw_target}"
    return resolved if resolved.suffix.lower() == ".md" else None


def _discover_linked_sources(root: Path, seeds: Iterable[Path]) -> set[Path]:
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
            if linked is not None and linked not in discovered:
                pending.append(linked)
    return discovered


def _continuity_violations(paths: Iterable[Path]) -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for path in paths:
        text = " ".join(_read_required(path).split())
        matched = [label for label, pattern in PROHIBITED_CONTINUITY.items() if pattern.search(text)]
        if matched:
            findings[path.as_posix()] = matched
    return findings


def _instruction_seeds(root: Path) -> set[Path]:
    rules = root / ".harness-baseline-configuration/rules"
    assert rules.is_dir(), "the canonical rule source is missing"
    authored_rules = set(rules.rglob("*.md"))
    assert authored_rules, "the authored rule closure is empty"
    return {root / relative for relative in SOURCE_MATRIX} | authored_rules


def test_canonical_instruction_closure_routes_each_artifact_to_a_fresh_role_bound_session() -> None:
    seeds = _instruction_seeds(PROJECT_ROOT)
    discovered = _discover_linked_sources(PROJECT_ROOT, seeds)
    assert seeds <= discovered
    assert _continuity_violations(discovered) == {}
    for relative, requirements in POSITIVE_REQUIREMENTS.items():
        text = " ".join(_read_required(PROJECT_ROOT / relative).split())
        missing = [pattern for pattern in requirements if not re.search(pattern, text, re.I)]
        assert not missing, f"{relative} lacks required successor-session semantics: {missing}"


def test_recursive_link_discovery_accepts_clean_linked_resource(tmp_path: Path) -> None:
    nested = tmp_path / "references/successor.md"
    nested.parent.mkdir()
    nested.write_text("A fresh role-bound session delivers the next artifact.\n", encoding="utf-8")
    seed = tmp_path / "SKILL.md"
    seed.write_text("Read [the successor rule](references/successor.md).\n", encoding="utf-8")
    discovered = _discover_linked_sources(tmp_path.resolve(), [seed.resolve()])
    assert discovered == {seed.resolve(), nested.resolve()}
    assert _continuity_violations(discovered) == {}


def test_recursive_link_discovery_rejects_continuity_in_linked_resource(tmp_path: Path) -> None:
    nested = tmp_path / "references/continuity.md"
    nested.parent.mkdir()
    nested.write_text("Prime Builder corrects and resubmits.\n", encoding="utf-8")
    seed = tmp_path / "SKILL.md"
    seed.write_text("Read [the lifecycle rule](references/continuity.md).\n", encoding="utf-8")
    discovered = _discover_linked_sources(tmp_path.resolve(), [seed.resolve()])
    assert "earlier agent corrects and resubmits" in _continuity_violations(discovered)[nested.as_posix()]


def test_source_matrix_missing_file_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(AssertionError, match="required WI-7804 instruction source is missing"):
        _discover_linked_sources(tmp_path.resolve(), [tmp_path / "missing.md"])


def test_unlisted_recursive_resource_cannot_escape_the_instruction_check(tmp_path: Path) -> None:
    seed = tmp_path / "SKILL.md"
    middle = tmp_path / "references/next.md"
    end = tmp_path / "references/nested/end.md"
    end.parent.mkdir(parents=True)
    seed.write_text("[Next](references/next.md)", encoding="utf-8")
    middle.write_text("[Final](nested/end.md)", encoding="utf-8")
    end.write_text("Bridge state is canonical.\n[Cycle](../next.md)", encoding="utf-8")
    discovered = _discover_linked_sources(tmp_path.resolve(), [seed.resolve()])
    assert discovered == {seed, middle, end}
    assert "continuing canonical bridge authority" in _continuity_violations(discovered)[end.as_posix()]
    end.unlink()
    with pytest.raises(AssertionError, match="required WI-7804 instruction source is missing"):
        _discover_linked_sources(tmp_path.resolve(), [seed.resolve()])


def test_a_new_authored_rule_is_included_without_a_matrix_amendment(tmp_path: Path) -> None:
    rules = tmp_path / ".harness-baseline-configuration/rules"
    rules.mkdir(parents=True)
    added = rules / "new-control.md"
    added.write_text("New control", encoding="utf-8")
    activity = rules / "activity.md"
    activity.write_text("Explicit activity input", encoding="utf-8")
    seeds = _instruction_seeds(tmp_path)
    assert added in seeds and activity in seeds


@pytest.mark.parametrize(
    ("statement", "rejected"),
    [
        (
            "Historical nonconforming messages, including NO-ACTION and DEFERRED, are readable "
            "only with their actual status and disposition. Obsolete statuses do not become current aliases.",
            False,
        ),
        ("DEFERRED is an owner-directed parking status.", True),
        ("DEFERRED: non-actionable parking for later work.", True),
        ("DEFERRED items are parked for later owner direction.", True),
        ("DEFERRED is not an active status.", False),
        (
            "Historical nonconforming messages, including NO-ACTION and DEFERRED, are readable "
            "only with their actual status and disposition. DEFERRED remains a current status.",
            True,
        ),
    ],
)
def test_deferred_matcher_distinguishes_inert_history_from_active_routing(tmp_path, statement, rejected):
    path = tmp_path / "routing.md"
    path.write_text(statement, encoding="utf-8")
    found = _continuity_violations([path])
    assert ("active DEFERRED routing" in found.get(path.as_posix(), [])) is rejected
