# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Single authored baseline, with generated discovery kept distinct (WI-6228).

The historical inverted baseline move emptied a source tree before its readers
were repointed. Preserve that regression duty: a missing/empty source refuses,
and current generators cannot silently declare an old source root.

Rules, hooks, routing and authored Skills now live only under
.harness-baseline-configuration. The root AGENTS.md and declared root pointer
files remain authored carriers. Native .agents/skills and the Goose plugin are
generated discovery output; references to those destinations are legitimate,
but declaring .agents/skills as the authored skills_root is not.

The detector recognizes retired rules/hooks/root bindings and separately checks
source-root declarations, so generated catalog references remain usable without
restoring a second authored source. Dotted Agent Red module paths are unrelated.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASELINE = ".harness-baseline-configuration"
SKILLS_ROOT = ".harness-baseline-configuration/skills"
ROOT_INSTRUCTIONS = "AGENTS.md"

# Trees whose existence means a second source root for a class that has exactly
# one in the universal baseline, or the emptied predecessor of the class that moved.
FORBIDDEN_TREES = (
    ".agents/rules",
    ".agents/hooks",
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
# The trailing lookaheads exclude generated native Skills and the D52 plugin
# discovery tree in both shapes (`.agents/skills...`, `.agents\plugins...`,
# `Path(".agents") / "skills"`); the segment must be exactly `skills` or
# `plugins`, so `.agents/skills-archive/` and `.agents/plugins-old/` still fire.
_BINDING_RE = re.compile(
    r"(?<![\w.])"  # not preceded by word char or dot -> excludes `src.agents`
    r"\.agents"
    r"(?=[\"'/\\])"  # used as a path: quoted segment, or followed by a separator
    r"(?![/\\]+(?:skills|plugins)(?![\w-]))"  # ... unless the generated native catalog or the D52 plugin tree
    r"(?![\"'][\s)]*/\s*[\"'](?:skills|plugins)[\"'])"  # ... also in the `Path(".agents") / "skills"` shape
)

# Explicit source-root fields/variables cannot point at the generated catalog.
_SOURCE_SKILLS_BINDING_RE = re.compile(
    r"\b(?:skills_root|SKILLS_ROOT|BASELINE_SKILLS|shared_skills)\s*=\s*[^\n]*"
    r"\.agents(?:[/\\]+skills|[\"'][\s)]*/\s*[\"']skills[\"'])"
)

# Files permitted to mention a retired baseline for reasons other than binding.
# Each entry is a deliberate, documented exception rather than a suppression.
ALLOWED_FILES = {
    # This guard names the retired baseline in order to detect it.
    "platform_tests/scripts/test_single_baseline_binding.py",
    # Governance classification rule `pattern = ".agents/**"`, which assigns a
    # mutation class to every path under the generated `.agents` tree; it also
    # covers a reappearing rules/hooks tree so
    # it classifies rather than falling through as `unclassified`). It is a
    # classifier entry, not a consumer binding: nothing projects from it. R3
    # keeps it (rulings R3 row: "taxonomy row ... kept").
    "config/governance/project-authorization-operation-taxonomy.toml",
    # This negative guard rejects generated .agents targets; it does not read a baseline.
    "scripts/check_commit_pathspec_safety.py",
    # This read-only inventory enumerates generated target roots; it is not an authored-source binding.
    "scripts/inventory_projection_authority_references.py",
    # This inventory classifies .agents as generated output. The scanner test separately
    # pins its actual roots and rejects an explicit authored-Skills declaration here.
    "config/governance/neutral-source-inventory.toml",
}

SCANNED_DIRS = ("scripts", "config")
SCANNED_SUFFIXES = {".py", ".toml", ".json"}


def _retired_baseline_bindings(text: str) -> list[str]:
    """Return every retired-baseline path binding found in ``text``.

    References to generated native Skills are not source bindings. Explicit old
    authored source declarations remain refused. Split out so the detector itself
    can be exercised against synthetic input — see the reintroduction tests.
    """
    return [m.group(0) for pattern in (_BINDING_RE, _SOURCE_SKILLS_BINDING_RE) for m in pattern.finditer(text)]


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
        f"skills source {SKILLS_ROOT!r} is absent. It is the one authored skills "
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
        f"second or leftover baseline tree(s) present: {surviving_trees}. The baseline gives "
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
    inventory_text = (PROJECT_ROOT / "config/governance/neutral-source-inventory.toml").read_text(encoding="utf-8")
    inventory = tomllib.loads(inventory_text)
    assert inventory["roots"] == {
        "harness_baseline": BASELINE,
        "config": "config",
        "scripts": "scripts",
        "groundtruth_kb_src": "groundtruth-kb/src/groundtruth_kb",
    }
    assert ".agents/" in inventory["projection_prefixes"]["paths"]
    assert not _SOURCE_SKILLS_BINDING_RE.search(inventory_text)

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
        'prefix=".agents/plugins-old/"',
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
        'BASELINE_SKILLS = Path(".harness-baseline-configuration") / "skills"',
        'prefix=".harness-baseline-configuration/skills/"',
        r're.compile(r"\.harness-baseline-configuration/skills/([^/]+)/helpers/")',
        'SKILLS_ROOT = ".harness-baseline-configuration/skills"',
        "path = Path('.harness-baseline-configuration\\\\skills')",
    ],
)
def test_detector_allows_the_d15_skills_source(skills_source: str) -> None:
    """The historical selector now pins five forms of the sole authored baseline Skill source."""
    assert not _retired_baseline_bindings(skills_source), (
        f"detector flagged the authored baseline Skill source as retired: {skills_source!r}"
    )


@pytest.mark.parametrize(
    "plugin_output",
    [
        'extra_output_roots = [".agents/plugins/gtkb"]',
        'storage_path = ".agents/plugins/gtkb/hooks/hooks.json"',
        "Goose discovers its hook plugin only under .agents/plugins/<name>/",
        'PLUGINS = Path(".agents") / "plugins"',
    ],
)
def test_detector_allows_the_d52_plugin_output_root(plugin_output: str) -> None:
    """D52: the Goose hook plugin renders under ``.agents/plugins/gtkb``, projector output rather than a baseline source."""
    assert not _retired_baseline_bindings(plugin_output), (
        f"detector flagged the D52 plugin output root as a retired baseline binding: {plugin_output!r}"
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


@pytest.mark.parametrize(
    "declaration",
    [
        'skills_root = ".agents/skills"',
        'BASELINE_SKILLS = Path(".agents") / "skills"',
        'shared_skills = ".agents/skills"',
    ],
)
def test_generated_native_catalog_cannot_be_declared_as_authored_source(declaration: str) -> None:
    assert _retired_baseline_bindings(declaration)


@pytest.mark.parametrize(
    "output",
    [
        'AGENTS_SKILLS_OUTPUT_ROOT = ".agents/skills"',
        'storage_path = ".agents/skills/example/SKILL.md"',
        'projected = root / ".agents" / "skills"',
    ],
)
def test_generated_native_catalog_references_do_not_bind_an_authored_source(output: str) -> None:
    assert not _retired_baseline_bindings(output)
