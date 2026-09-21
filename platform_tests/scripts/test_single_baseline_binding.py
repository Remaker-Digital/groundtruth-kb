# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression guard for the single harness baseline layout (WI-6228, Change E; D15).

WHY THIS EXISTS. The baseline transition from ``.agents`` to
``.harness-baseline-configuration`` landed **inverted**: the old tree was emptied
before the repoint completed, leaving generators bound to a source root with zero
files. Nothing failed loudly — one generator's empty-baseline guard is the only
reason `.claude/skills` was not erased, because these generators prune anything
absent from the baseline via ``unlink(missing_ok=True)``.

THE D15 LAYOUT. Owner ruling D15 (plan milestone M15 shape), as amended by R3
under D34 (2026-09-19), splits the neutral baseline by artifact class and gives
each class exactly one source:

  - ``.agents/skills/<name>/SKILL.md`` (with its helpers and references) is the
    ONE skills source. Hosts that discover that directory natively read it in
    place; the others receive projector-rendered pointer stubs, never copies.
  - ``.harness-baseline-configuration/{rules,hooks,routing.toml}`` stays the
    source for rules (read on demand) and hook scripts (run in place).
  - The root ``AGENTS.md`` is the moved baseline instruction file: tracked
    source, not a projection (R1 option B).

A second rules or hooks tree under ``.agents``, a skills tree left behind under
``.harness-baseline-configuration``, or a second instruction file reproduces the
WI-6228 defect shape exactly: two candidate roots for one class, one of them
empty or stale, and generators silently bound to the wrong one.

Two assertions make a repeat detectable rather than silent:

  (i)  the tree has exactly the D15 shape (one skills root, one rules/hooks
       root, one instruction file; no leftover or duplicate tree), and
  (ii) no source file binds a retired baseline path.

Assertion (ii) is the load-bearing one. A future rename that repoints some
consumers and not others reproduces the original defect exactly, and (ii) is what
turns that into a red test instead of a silently inert tree.

WHAT COUNTS AS A BINDING. Not every ``.agents`` token is a baseline reference,
and conflating them would make this guard both noisy and wrong. Two classes of
legitimate use exist in-tree and are deliberately excluded:

  - ``.agents/skills`` — since D15 this IS the skills source, so a binding to
    that prefix is the correct shape rather than a retired one. The detector
    excludes exactly that segment; ``.agents/rules``, ``.agents/hooks``,
    ``.agents/commands`` and a bare ``.agents`` root binding stay retired.
  - ``src.agents.containers.*`` — Python module paths for Agent Red's agent
    containers. Dotted module names, not filesystem baseline paths.

(A third class, the opt-in ``Path.home() / ".agents"`` extension-discovery path
of the SQLite-era startup generator, left the tree with that generator in 2026-09.)

The detector therefore matches the retired name only where it is used as a
project-relative *path* into retired baseline content, which is the shape that
actually binds a generator to a wrong source root.

Authority: ``bridge/gtkb-wi6228-baseline-path-binding-repoint-002.md`` (GO),
Implementation Guidance item 5, which requires assertion (ii) be demonstrated
against a synthetic retired-path binding rather than merely passing today; owner
ruling D15 as amended by R3 (D34, 2026-09-19) for the layout pinned by (i).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASELINE = ".harness-baseline-configuration"
SKILLS_ROOT = ".agents/skills"
ROOT_INSTRUCTIONS = "AGENTS.md"

# Trees whose existence means a second source root for a class that has exactly
# one under D15, or the emptied predecessor of the class that moved.
FORBIDDEN_TREES = (
    ".agents/rules",
    ".agents/hooks",
    ".harness-baseline-configuration/skills",
)
# The instruction file moved to the root under R1 (B); a copy left behind in the
# baseline directory is a second instruction carrier.
FORBIDDEN_FILES = (".harness-baseline-configuration/AGENTS.md",)

# A binding is the retired name used as a filesystem path component. Two shapes
# occur in practice and BOTH must be caught:
#
#   Path(".agents") / "rules"       -> the name is a standalone quoted segment
#   prefix=".agents/hooks/"         -> the name is followed by a separator
#
# The first shape is the one the Claude generator actually carried, so a detector
# that only matched the second would pass vacuously against the real defect.
#
# The lookbehind excludes dotted module names: in `src.agents.containers` the
# `.agents` is preceded by a word character, so it never matches.
#
# The two trailing lookaheads exclude the D15 skills source in both shapes
# (`.agents/skills...`, `.agents\skills...`, `Path(".agents") / "skills"`); the
# segment must be exactly `skills`, so `.agents/skills-archive/` still fires.
_BINDING_RE = re.compile(
    r"(?<![\w.])"  # not preceded by word char or dot -> excludes `src.agents`
    r"\.agents"
    r"(?=[\"'/\\])"  # used as a path: quoted segment, or followed by a separator
    r"(?![/\\]+skills(?![\w-]))"  # ... unless it is the D15 skills source
    r"(?![\"'][\s)]*/\s*[\"']skills[\"'])"  # ... also in its `Path(".agents") / "skills"` shape
)

# Files permitted to mention a retired baseline for reasons other than binding.
# Each entry is a deliberate, documented exception rather than a suppression.
ALLOWED_FILES = {
    # This guard names the retired baseline in order to detect it.
    "platform_tests/scripts/test_single_baseline_binding.py",
    # Governance classification rule `pattern = ".agents/**"`, which assigns a
    # mutation class to every path under the `.agents` tree (since D15 that is
    # the skills source; the rule also covers a reappearing rules/hooks tree so
    # it classifies rather than falling through as `unclassified`). It is a
    # classifier entry, not a consumer binding: nothing projects from it. R3
    # keeps it (rulings R3 row: "taxonomy row ... kept").
    "config/governance/project-authorization-operation-taxonomy.toml",
    # This negative guard rejects non-skill .agents paths; it does not read a baseline.
    "scripts/check_commit_pathspec_safety.py",
}

SCANNED_DIRS = ("scripts", "config")
SCANNED_SUFFIXES = {".py", ".toml", ".json"}


def _retired_baseline_bindings(text: str) -> list[str]:
    """Return every retired-baseline path binding found in ``text``.

    Bindings to the D15 skills source (``.agents/skills``) are not retired and
    are not returned. Split out from the filesystem walk so the detector itself
    can be exercised against synthetic input — see the reintroduction tests.
    """
    return [m.group(0) for m in _BINDING_RE.finditer(text)]


def _scanned_files() -> list[Path]:
    files: list[Path] = []
    for rel in SCANNED_DIRS:
        root = PROJECT_ROOT / rel
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
                continue
            if "__pycache__" in path.parts:
                continue
            if path.relative_to(PROJECT_ROOT).as_posix() == "config/governance/timer-inventory.toml":
                continue
            files.append(path)
    return files


def test_baseline_shape_is_exactly_the_d15_layout() -> None:
    """Assertion (i): one skills root, one rules/hooks root, one instruction file."""
    baseline = PROJECT_ROOT / BASELINE
    assert baseline.is_dir(), (
        f"harness baseline {BASELINE!r} is absent; rules are read and hooks run from "
        "it, so its absence is a platform-wide outage rather than drift"
    )

    skills_root = PROJECT_ROOT / SKILLS_ROOT
    assert skills_root.is_dir(), (
        f"skills source {SKILLS_ROOT!r} is absent. Under D15 it is the one skills "
        "root; a projector run against a missing root would prune every stub, "
        "which is the WI-6228 defect this guard exists to prevent."
    )
    manifests = sorted(skills_root.glob("*/SKILL.md"))
    assert manifests, (
        f"skills source {SKILLS_ROOT!r} exists but holds no <name>/SKILL.md: an "
        "empty source root is exactly the inverted-move state of WI-6228"
    )

    surviving_trees = [name for name in FORBIDDEN_TREES if (PROJECT_ROOT / name).exists()]
    assert not surviving_trees, (
        f"second or leftover baseline tree(s) present: {surviving_trees}. D15 gives "
        f"every artifact class one source ({SKILLS_ROOT} for skills; {BASELINE}/rules "
        f"and {BASELINE}/hooks for rules and hooks). Two candidate roots means a "
        "generator run can silently project from the wrong one."
    )

    surviving_files = [name for name in FORBIDDEN_FILES if (PROJECT_ROOT / name).exists()]
    assert not surviving_files, (
        f"second instruction carrier(s) present: {surviving_files}. The baseline "
        f"instruction file moved to the root {ROOT_INSTRUCTIONS} (R1 option B)."
    )
    assert (PROJECT_ROOT / ROOT_INSTRUCTIONS).is_file(), (
        f"root instruction file {ROOT_INSTRUCTIONS!r} is absent or not a regular file"
    )


def test_no_source_file_binds_a_retired_baseline_path() -> None:
    """Assertion (ii): no scanned source file binds a retired baseline path."""
    offenders: dict[str, list[str]] = {}
    for path in _scanned_files():
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        if rel in ALLOWED_FILES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:  # pragma: no cover - unreadable file is not a binding
            continue
        found = _retired_baseline_bindings(text)
        if found:
            offenders[rel] = sorted(set(found))

    assert not offenders, (
        "source files still bind a retired baseline path:\n"
        + "\n".join(f"  {rel}: {hits}" for rel, hits in sorted(offenders.items()))
        + "\nRepoint them at "
        + BASELINE
        + " (rules, hooks) or "
        + SKILLS_ROOT
        + " (skills), or add a documented entry to ALLOWED_FILES if the reference "
        "is genuinely not a baseline binding."
    )


@pytest.mark.parametrize(
    "synthetic",
    [
        'BASELINE_RULES = Path(".agents") / "rules"',
        'prefix=".agents/hooks/"',
        r're.compile(r"\.agents/rules/([^/]+)\.md")',
        'source_of_truth = ".agents/hooks/"',
        "path = Path('.agents\\\\rules')",
        'root = Path(".agents")',
        'prefix=".agents/skills-archive/"',
    ],
)
def test_detector_fires_on_a_reintroduced_binding(synthetic: str) -> None:
    """Guidance item 5: the guard must fail on reintroduction, not merely pass today.

    A guard that only ever sees a clean tree proves nothing about whether it can
    detect the defect. Each case above is a real shape the retired binding took
    before WI-6228 repointed it, re-targeted at the trees D15 keeps retired; the
    bare-root and near-miss cases pin that the skills-source exclusion is exact.
    """
    assert _retired_baseline_bindings(synthetic), (
        f"detector failed to flag a reintroduced retired-baseline binding: {synthetic!r}. "
        "Assertion (ii) would pass vacuously against this shape."
    )


@pytest.mark.parametrize(
    "skills_source",
    [
        'BASELINE_SKILLS = Path(".agents") / "skills"',
        'prefix=".agents/skills/"',
        r're.compile(r"\.agents/skills/([^/]+)/helpers/")',
        'SKILLS_ROOT = ".agents/skills"',
        "path = Path('.agents\\\\skills')",
    ],
)
def test_detector_allows_the_d15_skills_source(skills_source: str) -> None:
    """Under D15 a binding to ``.agents/skills`` is the correct shape, not a retired one.

    These are the exact strings the pre-D15 guard refused (the first three were
    its own reintroduction fixtures). Consumers re-pointed at the skills source in
    later M15 stages must not trip assertion (ii).
    """
    assert not _retired_baseline_bindings(skills_source), (
        f"detector flagged a binding to the D15 skills source as retired: {skills_source!r}"
    )


@pytest.mark.parametrize(
    "legitimate",
    [
        '("intent-classifier", "src.agents.containers.intent_classifier_app", 8081)',
        'AGENTS = {"co-pilot": "src.agents.containers.co_pilot_app:app"}',
        "from src.agents.containers import analytics_collector_app",
    ],
)
def test_detector_does_not_fire_on_unrelated_agents_tokens(legitimate: str) -> None:
    """The detector must not conflate dotted module names with baseline paths.

    ``src.agents.containers`` is an Agent Red Python module path. Treating it as a
    baseline binding would make this guard fail permanently for an unrelated
    reason, and the usual remedy for a noisy guard is to disable it.

    The user-home case ``Path.home() / ".agents" / "rules"`` is deliberately NOT
    listed here: textually it is indistinguishable from a real binding, so it is
    handled by an explicit ``ALLOWED_FILES`` entry rather than by weakening the
    pattern. Excluding it here instead would blind the detector to
    ``Path(".agents") / "rules"``, the exact shape the defect took.
    """
    assert not _retired_baseline_bindings(legitimate), (
        f"detector wrongly flagged an unrelated token as a baseline binding: {legitimate!r}"
    )
