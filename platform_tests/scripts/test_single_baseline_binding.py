# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression guard for the single harness baseline (WI-6228, Change E).

WHY THIS EXISTS. The baseline transition from ``.agents`` to
``.harness-baseline-configuration`` landed **inverted**: the old tree was emptied
before the repoint completed, leaving generators bound to a source root with zero
files. Nothing failed loudly — one generator's empty-baseline guard is the only
reason `.claude/skills` was not erased, because these generators prune anything
absent from the baseline via ``unlink(missing_ok=True)``.

Two assertions make a repeat detectable rather than silent:

  (i)  exactly one baseline directory exists, and
  (ii) no source file binds a retired baseline path.

Assertion (ii) is the load-bearing one. A future rename that repoints some
consumers and not others reproduces the original defect exactly, and (ii) is what
turns that into a red test instead of a silently inert tree.

WHAT COUNTS AS A BINDING. Not every ``.agents`` token is a baseline reference,
and conflating them would make this guard both noisy and wrong. One class of
legitimate, unrelated use exists in-tree and is deliberately excluded:

  - ``src.agents.containers.*`` — Python module paths for Agent Red's agent
    containers. Dotted module names, not filesystem baseline paths.

(A second class, the opt-in ``Path.home() / ".agents"`` extension-discovery path
of the SQLite-era startup generator, left the tree with that generator in 2026-09.)

The detector therefore matches the retired name only where it is used as a
project-relative *path* into baseline content, which is the shape that actually
binds a generator to a source root.

Authority: ``bridge/gtkb-wi6228-baseline-path-binding-repoint-002.md`` (GO),
Implementation Guidance item 5, which requires assertion (ii) be demonstrated
against a synthetic retired-path binding rather than merely passing today.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CURRENT_BASELINE = ".harness-baseline-configuration"
RETIRED_BASELINES = (".agents",)

# Directories that a baseline tree contains. The retired name only constitutes a
# binding when it is used as a path into one of these, which is what distinguishes
# a real source-root binding from an unrelated dotted module name.
BASELINE_CONTENT_DIRS = ("skills", "hooks", "rules", "commands")

# A binding is the retired name used as a filesystem path component. Two shapes
# occur in practice and BOTH must be caught:
#
#   Path(".agents") / "skills"      -> the name is a standalone quoted segment
#   prefix=".agents/skills/"        -> the name is followed by a separator
#
# The first shape is the one the Claude generator actually carried, so a detector
# that only matched the second would pass vacuously against the real defect.
#
# The lookbehind excludes dotted module names: in `src.agents.containers` the
# `.agents` is preceded by a word character, so it never matches.
_BINDING_RE = re.compile(
    r"(?<![\w.])"  # not preceded by word char or dot -> excludes `src.agents`
    r"\.agents"
    r"(?=[\"'/\\])"  # used as a path: quoted segment, or followed by a separator
)

# Files permitted to mention a retired baseline for reasons other than binding.
# Each entry is a deliberate, documented exception rather than a suppression.
ALLOWED_FILES = {
    # This guard names the retired baseline in order to detect it.
    "platform_tests/scripts/test_single_baseline_binding.py",
    # Governance classification rule `pattern = ".agents/**"`, which assigns a
    # mutation class to paths under the retired tree. It is a classifier entry,
    # not a consumer binding: nothing projects from it, and retaining it means a
    # reappearing tree still classifies rather than falling through as
    # `unclassified`. Outside WI-6228's authorized target_paths; its disposition
    # (retain as a safety net vs. retire as dead config) is recorded as follow-on
    # in the implementation report rather than decided here.
    "config/governance/project-authorization-operation-taxonomy.toml",
}

SCANNED_DIRS = ("scripts", "config")
SCANNED_SUFFIXES = {".py", ".toml", ".json"}


def _retired_baseline_bindings(text: str) -> list[str]:
    """Return every retired-baseline path binding found in ``text``.

    Split out from the filesystem walk so the detector itself can be exercised
    against synthetic input — see the reintroduction test below.
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
            files.append(path)
    return files


def test_exactly_one_baseline_directory_exists() -> None:
    """Assertion (i): the current baseline is present and no retired tree survives."""
    current = PROJECT_ROOT / CURRENT_BASELINE
    assert current.is_dir(), (
        f"current harness baseline {CURRENT_BASELINE!r} is absent; every generator "
        "projects from it, so its absence is a platform-wide outage rather than drift"
    )

    surviving = [name for name in RETIRED_BASELINES if (PROJECT_ROOT / name).exists()]
    assert not surviving, (
        f"retired baseline tree(s) still present: {surviving}. Two baselines means "
        "generator runs can silently project from the wrong one, which is the "
        "WI-6228 defect this guard exists to prevent."
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
        + CURRENT_BASELINE
        + ", or add a documented entry to ALLOWED_FILES if the reference is "
        "genuinely not a baseline binding."
    )


@pytest.mark.parametrize(
    "synthetic",
    [
        'BASELINE_SKILLS = Path(".agents") / "skills"',
        'prefix=".agents/skills/"',
        r're.compile(r"\.agents/skills/([^/]+)/helpers/")',
        'source_of_truth = ".agents/hooks/"',
        "path = Path('.agents\\\\rules')",
    ],
)
def test_detector_fires_on_a_reintroduced_binding(synthetic: str) -> None:
    """Guidance item 5: the guard must fail on reintroduction, not merely pass today.

    A guard that only ever sees a clean tree proves nothing about whether it can
    detect the defect. Each case above is a real shape the retired binding took
    before WI-6228 repointed it.
    """
    assert _retired_baseline_bindings(synthetic), (
        f"detector failed to flag a reintroduced retired-baseline binding: {synthetic!r}. "
        "Assertion (ii) would pass vacuously against this shape."
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

    The user-home case ``Path.home() / ".agents" / "skills"`` is deliberately NOT
    listed here: textually it is indistinguishable from a real binding, so it is
    handled by an explicit ``ALLOWED_FILES`` entry rather than by weakening the
    pattern. Excluding it here instead would blind the detector to
    ``Path(".agents") / "skills"``, the exact shape the defect took.
    """
    assert not _retired_baseline_bindings(legitimate), (
        f"detector wrongly flagged an unrelated token as a baseline binding: {legitimate!r}"
    )
