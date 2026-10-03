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

c123 (batch design WP5, G44(d)): the root and package READMEs and
CONTRIBUTING files are scanned, and so are the test roots (platform_tests,
groundtruth-kb/tests, conftest.py) with every token except the program labels,
which are inert in test comments. New tokens: approval_state, owner_approved,
target_role, activity envelope, a quoted "deferred" literal, and the program's
own labels (two-digit D labels, B20 to B199, O-7 R<n>, and single-digit D
labels in "(D3)", "ruling D3" or "decision D3"); the TAFE token is widened
(TAFE_X, _TAFE_SCHEMA, tafe_canonical) and DEFERRED no longer counts SQL's
INITIALLY DEFERRED. When a count rises: regenerate the baseline if the new
reference is a refusal or a census, remove it if it asserts the retired rule.
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
    ".harness-baseline-configuration/skills",
    "scripts",
    "groundtruth-kb/src",
    "groundtruth-kb/templates",
    "groundtruth-kb/docs",
    "config",
    "AGENTS.md",
    "CLAUDE.md",
    ".githooks",
    "CONTRIBUTING.md",
    "README.md",
    "groundtruth-kb/README.md",
    "groundtruth-kb/CONTRIBUTING.md",
)
EXCLUDED_PARTS = frozenset({"__pycache__", "tests", "archive", ".pytest-tmp", "node_modules"})
# c123 (G44(d)): the test roots, scanned with every token except the program labels.
TEST_ROOTS = ("platform_tests", "groundtruth-kb/tests", "conftest.py")
TEST_EXCLUDED_PARTS = EXCLUDED_PARTS - {"tests"}
TEST_EXEMPT_FILES = frozenset(
    {
        "platform_tests/scripts/test_retired_concept_references.py",
        "platform_tests/fixtures/retired_reference_baseline.json",
    }
)
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
    # SQL's DEFERRABLE INITIALLY DEFERRED is a keyword, not the retired status (c123).
    "DEFERRED": re.compile(r"(?<!INITIALLY )\bDEFERRED\b"),
    "PAUTH": re.compile(r"\bPAUTH\b"),
    "DECISION-NNNN": re.compile(r"\bDECISION-\d{3,}\b"),
    "project_authorizations": re.compile(r"\bproject_authorizations\b"),
    ".gtkb-state": re.compile(r"\.gtkb-state\b"),
    "harness-state/": re.compile(r"\bharness-state/"),
    "formal-artifact-approvals": re.compile(r"formal-artifact-approvals"),
    # c123 (G43, G44(d)): widened, so TAFE_X, _TAFE_SCHEMA and tafe_canonical count too.
    "TAFE": re.compile(r"(?i)(?<![a-z0-9])tafe(?![a-z0-9])"),
    "retired-dispatch-mechanism": re.compile(r"(?i)\b(?:dispatcher[_ -]daemon|(?:bridge[_ -])?smart[_ -]poller)\b"),
    "config/agent-control": re.compile(r"config/agent-control"),
    # c123 (G44(d)): the retired approval and role-change fields, the activity envelope, and the DEFERRED status written
    # as a quoted literal in code or data (prose like "deferred to later" is not counted).
    "approval_state": re.compile(r"\bapproval_state\b"),
    "owner_approved": re.compile(r"\bowner_approved\b"),
    "target_role": re.compile(r"\btarget_role\b"),
    "activity-envelope": re.compile(r"(?i)\bactivity[- ]envelope\b"),
    "deferred-literal": re.compile(r"(?<![\w])(['\"])deferred\1"),
    # The realignment program's own labels: two-digit D labels, B20 to B199, O-7 R<n>, and single-digit D labels only
    # in "(D3)", "ruling D3" or "decision D3" (an Azure "D1" or a quality dimension "D3" is not one).
    "program-label": re.compile(r"\bD\d{2}\b|\bB(?:[2-9]\d|1\d\d)\b|\bO-7 R\d+\b|\(D\d\)|\b(?:ruling|decision) D\d\b"),
}
# Program labels are inert in test comments, so the test roots do not count them.
TEST_ROOT_SKIPPED_TOKENS = frozenset({"program-label"})

# The single code of record for the vocabulary must name the historical-inert
# tokens so committed history can be read; nothing else may.
EXEMPT_FILES = frozenset({"groundtruth-kb/src/groundtruth_kb/bridge/vocabulary.py"})

# Surfaces already purged. Add a path here when its purge lands; it then fails
# on the first reintroduced reference instead of being ratcheted.
MUST_BE_CLEAN: tuple[str, ...] = (
    ".githooks/pre-commit",
    # c123 (G43): the retired flow engine's env key prefix and the contributor guide's bridge description are purged.
    "groundtruth-kb/src/groundtruth_kb/env_sot.py",
    "CONTRIBUTING.md",
)


def _iter_surface(project_root: Path, surfaces: tuple[str, ...], excluded_parts: frozenset[str]) -> Iterator[Path]:
    for surface in surfaces:
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
            if excluded_parts & set(path.relative_to(project_root).parts):
                continue
            if path.suffix.lower() not in SCANNED_SUFFIXES:
                continue
            yield path


def _iter_files(project_root: Path = PROJECT_ROOT) -> Iterator[tuple[Path, bool]]:
    """Each scanned file once, with whether it lies under a test root (c123, G44(d))."""
    seen: set[Path] = set()
    for path in _iter_surface(project_root, SURFACES, EXCLUDED_PARTS):
        seen.add(path)
        yield path, False
    for path in _iter_surface(project_root, TEST_ROOTS, TEST_EXCLUDED_PARTS):
        if path not in seen and path.relative_to(project_root).as_posix() not in TEST_EXEMPT_FILES:
            yield path, True


def _under_test_root(relative: str) -> bool:
    """Whether a scanned path lies under a test root and outside every product surface (c123, G44(d))."""

    def within(roots: tuple[str, ...]) -> bool:
        return any(relative == root or relative.startswith(root + "/") for root in roots)

    return within(TEST_ROOTS) and not within(SURFACES)


def _count_tokens(text: str, *, test_root: bool = False) -> dict[str, int]:
    return {
        name: len(pattern.findall(text))
        for name, pattern in TOKENS.items()
        if not (test_root and name in TEST_ROOT_SKIPPED_TOKENS)
    }


def scan(project_root: Path = PROJECT_ROOT) -> dict[str, dict[str, int]]:
    """Return {relative path: {token: count}} for every file with at least one hit."""
    inventory: dict[str, dict[str, int]] = {}
    for path, test_root in _iter_files(project_root):
        rel = path.relative_to(project_root).as_posix()
        if rel in EXEMPT_FILES:
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        counts = {name: count for name, count in _count_tokens(text, test_root=test_root).items() if count}
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
        + f"\nRegenerate with {WRITE_ENV}=1 only after confirming each change is a purge, not a reintroduction: when a"
        " count rose, regenerate if the new reference is a refusal or a census, and remove it if it asserts the retired"
        " rule."
    )


def test_purged_surfaces_stay_clean() -> None:
    current = scan()
    dirty = {path: current[path] for path in MUST_BE_CLEAN if path in current}
    assert dirty == {}, f"purged surfaces reference retired concepts again: {dirty}"


def test_purged_tokens_keep_a_zero_allowance(tmp_path: Path) -> None:
    """A retired concept that no surface references any more stays in TOKENS: reaching zero establishes a zero
    allowance, and the first reintroduction anywhere in a scanned surface is a regression finding. The product surfaces
    are judged here; a test root may hold a retired token as test data (c123: the decision tracker's regex fixtures)."""
    current = scan()
    seen = {token for path, counts in current.items() if not _under_test_root(path) for token in counts}
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
    path = tmp_path / ".harness-baseline-configuration/skills/example/SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text("Current guidance names PAUTH", encoding="utf-8")
    assert scan(tmp_path)[".harness-baseline-configuration/skills/example/SKILL.md"]["PAUTH"] == 1


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


def test_the_c123_tokens_count_what_they_name_and_nothing_else(tmp_path):
    """G44(d) fixtures on a product surface: each counted form once, and the look-alikes not at all."""
    path = tmp_path / "scripts" / "sample.py"
    path.parent.mkdir(parents=True)
    path.write_text(
        'state = "deferred"\n'
        "# An Azure D1 machine; quality dimension D3.\n"
        "# DEFERRABLE INITIALLY DEFERRED; deferred to later.\n"
        "# Owner ruling (D61), B90 and O-7 R22; ruling D3.\n"
        "TAFE_X = _TAFE_SCHEMA = 1\n"
        "approval_state = owner_approved = target_role = None  # an activity envelope\n",
        encoding="utf-8",
    )
    assert scan(tmp_path) == {
        "scripts/sample.py": {
            "TAFE": 2,
            "activity-envelope": 1,
            "approval_state": 1,
            "deferred-literal": 1,
            "owner_approved": 1,
            "program-label": 4,
            "target_role": 1,
        }
    }


def test_a_test_root_is_scanned_without_program_labels(tmp_path):
    """A file under a test root is scanned with every token except the program labels, which are inert there."""
    platform = tmp_path / "platform_tests" / "test_sample.py"
    platform.parent.mkdir(parents=True)
    platform.write_text('# Owner decision (D61) and B90.\nassert record["approval_state"] is None\n', encoding="utf-8")
    package = tmp_path / "groundtruth-kb" / "tests" / "test_db.py"
    package.parent.mkdir(parents=True)
    package.write_text("owner_approved = True\n", encoding="utf-8")
    assert scan(tmp_path) == {
        "groundtruth-kb/tests/test_db.py": {"owner_approved": 1},
        "platform_tests/test_sample.py": {"approval_state": 1},
    }


def test_the_readmes_and_contributing_files_are_scanned_and_the_ratchet_itself_is_not(tmp_path):
    (tmp_path / "CONTRIBUTING.md").write_text("Bridge files and TAFE are canonical.\n", encoding="utf-8")
    (tmp_path / "groundtruth-kb").mkdir()
    (tmp_path / "groundtruth-kb" / "README.md").write_text("Approve with owner_approved.\n", encoding="utf-8")
    for exempt in sorted(TEST_EXEMPT_FILES):
        (tmp_path / exempt).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / exempt).write_text("TAFE owner_approved approval_state\n", encoding="utf-8")
    assert scan(tmp_path) == {"CONTRIBUTING.md": {"TAFE": 1}, "groundtruth-kb/README.md": {"owner_approved": 1}}
