"""Retired-concept reference ratchet (owner-direct enforcement reset, 2026-09-07).

Canon v8.92 retires a set of concepts: the NO-ACTION and DEFERRED statuses,
project authorization records (PAUTH), DECISION-NNNN records, the .gtkb-state
and harness-state trees, .groundtruth/formal-artifact-approvals, TAFE, and
config/agent-control. Every live enforcement surface that still names one of
them is a place where an agent can be re-taught the retired model, and a hook
or writer that still reads one of them enforces a rule the canon no longer
has.

The inventory is far too large to purge in one step, so this test is a
ratchet. ``platform_tests/fixtures/retired_reference_baseline.json`` fixes the
current per-file, per-token counts; the test fails when a count rises, when a
file starts referencing a retired concept, or when a count falls without the
baseline being lowered to match. Lower the baseline as each surface is purged
by running:

    GTKB_RETIRED_REFERENCE_BASELINE_WRITE=1 python -m pytest platform_tests/scripts/test_retired_concept_references.py

Surfaces that must carry no reference at all are listed in MUST_BE_CLEAN.
The vocabulary module is exempt because it is the one place that must name
the historical-inert tokens in order to grandfather committed history.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = PROJECT_ROOT / "platform_tests" / "fixtures" / "retired_reference_baseline.json"
WRITE_ENV = "GTKB_RETIRED_REFERENCE_BASELINE_WRITE"

SURFACES = (
    ".harness-baseline-configuration",
    ".agents/skills",
    "scripts",
    "groundtruth-kb/src",
    "groundtruth-kb/templates",
    "groundtruth-kb/docs",
    "config",
    "AGENTS.md",
    "CLAUDE.md",
    ".githooks",
)
EXCLUDED_PARTS = frozenset({"__pycache__", "tests", "archive", ".pytest-tmp", "node_modules"})
SCANNED_SUFFIXES = frozenset({".py", ".md", ".toml", ".json", ".sh", ".ps1", ".txt", ".yml", ".yaml", ""})
MAX_BYTES = 2_000_000
EXCLUDED_RELATIVE_PATHS = frozenset(
    {
        "config/governance/timer-inventory.toml",
        "memory/topics/reference_openai_api_key.md",
        ".quality/release-candidate-tracked-secrets.json",
        "groundtruth-kb/tests/fixtures/bridge_spike_minimized_governance_hooks/credential_scan.py",
        "applications/Agent_Red/docs/owner-messages-all.json",
    }
)

TOKENS: dict[str, re.Pattern[str]] = {
    "NO-ACTION": re.compile(r"\bNO-ACTION\b"),
    "DEFERRED": re.compile(r"\bDEFERRED\b"),
    "PAUTH": re.compile(r"\bPAUTH\b"),
    "DECISION-NNNN": re.compile(r"\bDECISION-\d{3,}\b"),
    "project_authorizations": re.compile(r"\bproject_authorizations\b"),
    ".gtkb-state": re.compile(r"\.gtkb-state\b"),
    "harness-state/": re.compile(r"\bharness-state/"),
    "formal-artifact-approvals": re.compile(r"formal-artifact-approvals"),
    "TAFE": re.compile(r"\bTAFE\b"),
    "retired-dispatch-mechanism": re.compile(r"(?i)\b(?:dispatcher[_ -]daemon|(?:bridge[_ -])?smart[_ -]poller)\b"),
    "config/agent-control": re.compile(r"config/agent-control"),
}

# The single code of record for the vocabulary must name the historical-inert
# tokens so committed history can be read; nothing else may.
EXEMPT_FILES = frozenset({"groundtruth-kb/src/groundtruth_kb/bridge/vocabulary.py"})

# Surfaces already purged. Add a path here when its purge lands; it then fails
# on the first reintroduced reference instead of being ratcheted.
MUST_BE_CLEAN: tuple[str, ...] = (".githooks/pre-commit",)


def _iter_files(project_root: Path = PROJECT_ROOT) -> Iterator[Path]:
    for surface in SURFACES:
        root = project_root / surface
        if root.is_file():
            yield root
            continue
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.relative_to(project_root).as_posix() in EXCLUDED_RELATIVE_PATHS:
                continue
            if not path.is_file():
                continue
            if EXCLUDED_PARTS & set(path.relative_to(project_root).parts):
                continue
            if path.suffix.lower() not in SCANNED_SUFFIXES:
                continue
            yield path


def _count_tokens(text: str) -> dict[str, int]:
    return {name: len(pattern.findall(text)) for name, pattern in TOKENS.items()}


def scan(project_root: Path = PROJECT_ROOT) -> dict[str, dict[str, int]]:
    """Return {relative path: {token: count}} for every file with at least one hit."""
    inventory: dict[str, dict[str, int]] = {}
    for path in _iter_files(project_root):
        rel = path.relative_to(project_root).as_posix()
        if rel in EXEMPT_FILES:
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        counts = {name: count for name, count in _count_tokens(text).items() if count}
        if counts:
            inventory[rel] = counts
    return inventory


def _load_baseline() -> dict[str, dict[str, int]]:
    if not BASELINE_PATH.is_file():
        return {}
    payload = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    files = payload.get("files")
    assert isinstance(files, dict), f"{BASELINE_PATH}: 'files' must be an object"
    return {str(path): {str(k): int(v) for k, v in counts.items()} for path, counts in files.items()}


def _write_baseline(inventory: dict[str, dict[str, int]]) -> None:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "purpose": (
            "Per-file counts of references to concepts retired by canon v8.92, "
            "asserted as a ratchet by test_retired_concept_references.py."
        ),
        "tokens": sorted(TOKENS),
        "files": {path: dict(sorted(counts.items())) for path, counts in sorted(inventory.items())},
    }
    BASELINE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _differences(baseline: dict[str, dict[str, int]], current: dict[str, dict[str, int]]) -> list[str]:
    problems: list[str] = []
    for path in sorted(set(baseline) | set(current)):
        before = baseline.get(path, {})
        after = current.get(path, {})
        for token in sorted(set(before) | set(after)):
            old = before.get(token, 0)
            new = after.get(token, 0)
            if new > old:
                problems.append(f"{path}: {token} rose from {old} to {new} (a retired concept was reintroduced)")
            elif new < old:
                problems.append(f"{path}: {token} fell from {old} to {new} (lower the baseline to lock it in)")
    return problems


def test_retired_concept_references_do_not_grow() -> None:
    current = scan()
    if os.environ.get(WRITE_ENV) == "1":
        _write_baseline(current)
    baseline = _load_baseline()
    assert baseline, f"{BASELINE_PATH} is missing; generate it with {WRITE_ENV}=1"
    problems = _differences(baseline, current)
    assert problems == [], (
        "retired-concept references drifted from the baseline:\n  "
        + "\n  ".join(problems)
        + f"\nRegenerate with {WRITE_ENV}=1 only after confirming each change is a purge, not a reintroduction."
    )


def test_purged_surfaces_stay_clean() -> None:
    current = scan()
    dirty = {path: current[path] for path in MUST_BE_CLEAN if path in current}
    assert dirty == {}, f"purged surfaces reference retired concepts again: {dirty}"


def test_purged_tokens_keep_a_zero_allowance(tmp_path: Path) -> None:
    """A retired concept that no surface references any more stays in TOKENS: reaching zero establishes a zero
    allowance, and the first reintroduction anywhere in a scanned surface is a regression finding."""
    current = scan()
    seen = {token for counts in current.values() for token in counts}
    purged = sorted(set(TOKENS) - seen)
    assert "DECISION-NNNN" in purged, "DECISION-NNNN has been reintroduced somewhere; the baseline check names the file"
    assert not [p for p in _differences(_load_baseline(), current) if "DECISION-NNNN" in p], (
        "no finding for a purged token"
    )
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "reintroduced.py").write_text("# refers to DECISION-1234 again\n", encoding="utf-8")
    reintroduced = scan(tmp_path)
    assert reintroduced == {"scripts/reintroduced.py": {"DECISION-NNNN": 1}}
    assert _differences({}, reintroduced) == [
        "scripts/reintroduced.py: DECISION-NNNN rose from 0 to 1 (a retired concept was reintroduced)"
    ]


def test_skill_move_keeps_authored_guidance_in_the_ratchet_subject(tmp_path):
    path = tmp_path / ".agents/skills/example/SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("Current guidance names PAUTH", encoding="utf-8")
    assert scan(tmp_path)[".agents/skills/example/SKILL.md"]["PAUTH"] == 1


def test_timer_inventory_is_excluded_before_any_content_read(tmp_path, monkeypatch):
    path = tmp_path / "config/governance/timer-inventory.toml"
    path.parent.mkdir(parents=True)
    path.write_text("excluded fixture", encoding="utf-8")
    original = Path.read_text

    def guarded(current, *args, **kwargs):
        assert current != path, "broad reference scans must not read the timer inventory"
        return original(current, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded)
    assert scan(tmp_path) == {}


def test_authored_docs_are_covered_by_retired_dispatch_reference_check(tmp_path):
    path = tmp_path / "groundtruth-kb/docs/current-guide.md"
    path.parent.mkdir(parents=True)
    path.write_text("Start the dispatcher daemon and smart-poller.", encoding="utf-8")
    assert scan(tmp_path) == {"groundtruth-kb/docs/current-guide.md": {"retired-dispatch-mechanism": 2}}
