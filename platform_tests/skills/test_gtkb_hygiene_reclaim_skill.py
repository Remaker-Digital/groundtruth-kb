# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Contract tests for the canonical GT-KB hygiene-reclaim managed skill.

These checks cover the canonical source owned by WI-5142 phase 1. Generated
adapter, manifest, capability-registry, and catalog integration are completed
and verified by the parent managed-skill lifecycle work.
"""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _REPO_ROOT / ".claude" / "skills" / "gtkb-hygiene-reclaim" / "SKILL.md"

_PRODUCTION_COMMANDS = (
    "gt hygiene reclaim plan",
    "gt hygiene reclaim history",
    "gt hygiene reclaim trash",
    "gt hygiene reclaim restore",
)

_FORBIDDEN_OPERATIONS = (
    "permanent purge",
    "git gc",
    "git prune",
    "git reflog expire",
    "git stash drop",
    "git stash clear",
    "branch deletion",
    "commit, push, release, or deployment",
    "credential",
)


def _skill_text() -> str:
    assert _SKILL.is_file(), f"missing canonical skill: {_SKILL}"
    return _SKILL.read_text(encoding="utf-8")


def _split_frontmatter(text: str) -> tuple[str, str]:
    assert text.startswith("---"), "SKILL.md must open with YAML frontmatter"
    parts = text.split("---", 2)
    assert len(parts) == 3, "SKILL.md frontmatter must close with ---"
    return parts[1], parts[2]


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    assert match, f"frontmatter is missing {key!r}"
    return match.group(1).strip()


def test_canonical_skill_has_trigger_effective_frontmatter() -> None:
    frontmatter, body = _split_frontmatter(_skill_text())
    assert _frontmatter_value(frontmatter, "name") == "gtkb-hygiene-reclaim"
    description = _frontmatter_value(frontmatter, "description").lower()
    for phrase in ("gt hygiene reclaim", "plan/history/trash/restore", "registry", "quiescence"):
        assert phrase in description
    assert body.strip(), "skill body must not be empty"


def test_skill_reuses_only_the_production_cli_contract() -> None:
    text = _skill_text()
    for command in _PRODUCTION_COMMANDS:
        assert command in text, f"skill must surface production command {command!r}"
    assert "production `gt hygiene reclaim` interface is the only execution surface" in text
    assert "Do not create or invoke a private reclaim script or duplicate CLI" in text


def test_skill_starts_compact_and_limits_payload_ingestion() -> None:
    text = _skill_text()
    compact_start = text.index("gt hygiene reclaim plan --json")
    actuator_start = text.index("## Actuator Contract")
    assert compact_start < actuator_start
    for phrase in (
        "registry readiness",
        "Git readiness",
        "Do not load the complete manifest or every candidate payload",
        "Inspect exact details only when they are needed",
        "Keep the read-only `plan` and `history` phase separate",
    ):
        assert phrase in text


def test_trash_requires_exact_batch_evidence_and_single_owner_decision() -> None:
    text = _skill_text()
    for phrase in (
        "immutable plan hash exactly matches",
        "exact item IDs",
        "batch-specific owner evidence and apply evidence",
        "fresh quiescence evidence",
        "OWNER ACTION REQUIRED",
        "Present one owner decision at a time",
        "then stop and wait",
        "Approval in conversation is not itself sufficient actuator input",
    ):
        assert phrase in text
    trash_command = next(line for line in text.splitlines() if line.startswith("gt hygiene reclaim trash --run-id"))
    for option in (
        "--plan-hash",
        "--item-id",
        "--owner-evidence",
        "--quiescence-evidence",
    ):
        assert option in trash_command
    assert trash_command.count("--owner-evidence") == 2
    assert "--apply-evidence" not in trash_command


def test_skill_preserves_authority_and_revalidates_actuators() -> None:
    text = _skill_text()
    for phrase in (
        "Every registry match is a preservation veto",
        "refs, worktree HEADs",
        "stashes, valid reflog object IDs, and every index stage",
        "Preserve bridge files",
        "operation-time revalidation",
        "After either `trash` or `restore`, verify append-only history",
        "known or newly discovered non-passing registry state blocks live trash",
        "zero physical bytes",
    ):
        assert phrase in text


def test_current_go_forbids_live_actuation_and_integration_claims() -> None:
    text = _skill_text()
    for phrase in (
        "GO 002",
        "It authorizes no\nlive `trash` or `restore`",
        "generated Codex adapter",
        "capability registry",
        "scenario\nrouter",
    ):
        assert phrase in text
    assert "Do not add this operator-invoked skill to, or claim a change to, the scenario" in text


def test_skill_explicitly_forbids_destructive_and_release_operations() -> None:
    text = _skill_text().lower()
    for operation in _FORBIDDEN_OPERATIONS:
        assert operation in text, f"skill must explicitly forbid {operation!r}"
