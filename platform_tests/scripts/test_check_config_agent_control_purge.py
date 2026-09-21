"""Absence checks for the retired secondary baseline (TEST-12124).

Clause 1 asserts directory absence in the selected checkout. Clause 2 asserts
that the retired path survives on the executable surfaces only where an
executable refusal names it (owner ruling D21, 2026-09-17): the bridge
artifact-path guard and the commit pathspec-safety hook. A literal reference
scan cannot distinguish a dependency from a prohibition, so clause 2 enumerates
the prohibitions exactly instead of counting them, and also checks the
Path-join form a path-literal scan misses. The canon carriers AGENTS.md and
CLAUDE.md stay under the retired-concept ratchet
(test_retired_concept_references.py); their retirement route is the baseline
rendering, not this module. Complete reader, writer, registration, migration
and recovery qualification remains the broader WI-6260 / TEST-11922
obligation; historical permission or collision exemptions do not establish
completion.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PURGE_DIR = "config/agent-control"

EXECUTABLE_SURFACES = (
    ".harness-baseline-configuration",
    "scripts",
    "groundtruth-kb/src",
    "groundtruth-kb/templates",
    "config",
    ".githooks",
    ".gitattributes",
)
EXCLUDED_PARTS = frozenset({"__pycache__", "tests", "archive", ".pytest-tmp", "node_modules"})
# Derived output regenerated from the sources above (scripts/timer_inventory.py); it carries historical
# identities and is not an executable surface. Owner ruling D14 (2026-09-17) relocates it out of config/.
DERIVED_OUTPUTS = frozenset({"config/governance/timer-inventory.toml"})
SCANNED_SUFFIXES = frozenset({".py", ".md", ".toml", ".json", ".sh", ".ps1", ".txt", ".yml", ".yaml", ""})
PATH_TOKEN = re.compile(r"config/agent-control")
PATH_JOIN_TOKEN = re.compile(r"""["']agent-control["']""")
# The two executable refusals D21 keeps, each naming the path exactly once.
EXECUTABLE_REFUSALS = {
    "groundtruth-kb/src/groundtruth_kb/bridge/native.py": 1,
    "scripts/check_commit_pathspec_safety.py": 1,
}


def _executable_files(project_root: Path = PROJECT_ROOT) -> Iterator[Path]:
    for surface in EXECUTABLE_SURFACES:
        root = project_root / surface
        if root.is_file():
            yield root
            continue
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            relative = path.relative_to(project_root)
            if not path.is_file() or EXCLUDED_PARTS & set(relative.parts) or relative.as_posix() in DERIVED_OUTPUTS:
                continue
            if path.suffix.lower() in SCANNED_SUFFIXES:
                yield path


def scan_executable_surfaces(project_root: Path = PROJECT_ROOT) -> tuple[dict[str, int], dict[str, int]]:
    """Return ({file: path-literal count}, {file: quoted-component count}) for files with at least one hit."""
    literal: dict[str, int] = {}
    joined: dict[str, int] = {}
    for path in _executable_files(project_root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = path.relative_to(project_root).as_posix()
        if count := len(PATH_TOKEN.findall(text)):
            literal[rel] = count
        if path.suffix == ".py" and (count := len(PATH_JOIN_TOKEN.findall(text))):
            joined[rel] = count
    return literal, joined


def test_config_agent_control_directory_is_absent() -> None:
    """TEST-12124 clause 1: the obsolete second baseline directory must not exist."""
    purge_path = PROJECT_ROOT / PURGE_DIR
    surviving = (
        sorted(p.relative_to(PROJECT_ROOT).as_posix() for p in purge_path.rglob("*") if p.is_file())
        if purge_path.exists()
        else []
    )

    assert not purge_path.exists(), (
        f"{PURGE_DIR} still exists with {len(surviving)} file(s). "
        "GOV-SOT-SINGLETON-001 permits exactly one baseline; "
        ".harness-baseline-configuration is canonical. "
        f"First surviving paths: {surviving[:10]}"
    )


def test_retired_path_survives_only_as_the_two_executable_refusals() -> None:
    """TEST-12124 clause 2: no reader, configuration, attribute or comment on an executable surface names the
    retired path; the two executable refusals name it exactly once each; no Path-join form exists anywhere."""
    literal, joined = scan_executable_surfaces()
    assert literal == EXECUTABLE_REFUSALS, (
        "the retired secondary baseline is named outside its two executable refusal sites "
        f"(a reader, a compatibility pointer or guidance was reintroduced): {literal}"
    )
    assert joined == {}, f"the retired path is assembled by Path-join instead of named: {joined}"


def test_executable_surface_scan_sees_a_reintroduced_reader(tmp_path: Path) -> None:
    """The clause-2 scan is not vacuous: a reader in either form is found and attributed to its file."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "reader.py").write_text(
        'FLOOR = root / "config" / "agent-control" / "floor.toml"\n', encoding="utf-8"
    )
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "pointer.toml").write_text('path = "config/agent-control/**"\n', encoding="utf-8")
    literal, joined = scan_executable_surfaces(tmp_path)
    assert literal == {"config/pointer.toml": 1}
    assert joined == {"scripts/reader.py": 1}
