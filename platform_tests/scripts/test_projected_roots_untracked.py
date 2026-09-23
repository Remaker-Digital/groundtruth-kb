"""Projected harness roots are generated, gitignored and untracked (owner ruling D14, 2026-09-17).

TEST-12566 (GOV-HARNESS-NEUTRAL-BASELINE-001; SPEC-INTAKE-c878d9 states the rule) and
WI-6691 acceptance alternative b: the projection trees are gitignored and untracked. The
five top-level projector roots and ``.api-harness`` are ignored wholesale by an anchored
rule in the repository's ``.gitignore``; no path under them is in this checkout's index;
every path a present projection manifest declares is ignored; ``.gitignore`` carries no
negation that re-includes a rendered path; the pre-commit pathspec check refuses the same
components, so the ignore rule and the refusal state one policy; and the derived timer
inventory location under ``.groundtruth/derived/`` is ignored and refused too. A checkout
therefore carries no projections: ``gt harness project <profile>`` runs for every profile
after a checkout or install.

M15 stage 1 (owner ruling D15 as amended by R3; D34): the baseline instruction file moved
to the tracked root ``AGENTS.md`` and the skills tree to ``.agents/skills`` (the one skills
source, tracked, never ignored); ``CLAUDE.md`` and ``.goosehints`` are tracked pointer
files declared in ``profiles.toml [root_pointers]``. The baseline keeps rules/, hooks/ and
routing.toml. The TEST-12566 binding text still describes the pre-move counts; its refresh
is task 15.8.
"""

from __future__ import annotations

import json
import subprocess
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PROJECTOR_ROOTS = (".agent", ".claude", ".codex", ".cursor", ".goose", ".api-harness")
PROFILES = ROOT / "scripts/harness_projection/profiles.toml"
BASELINE = ".harness-baseline-configuration"
SKILLS_ROOT = ".agents/skills"
ROOT_CARRIERS = ("AGENTS.md", "CLAUDE.md", ".goosehints")
# The tracked baseline after the D15 move: rules (32 after c107 retired active-workspace.md) + hooks incl.
# manifest.toml and _hook_context.py (11) + routing.toml + goose-execution-floor.toml, which the gated commit
# a3d2291 added as work product: it is the canonical Goose execution floor (scripts/goose_harness.py reads it and
# config/registry/sot-artifacts.toml declares it, and the harness refuses to run when it is absent). 15.8 refreshes
# TEST-12566 to this.
TRACKED_BASELINE_SHAPE = {"rules": 32, "hooks": 11}
TRACKED_BASELINE_SINGLETONS = ("routing.toml", "goose-execution-floor.toml")
TRACKED_BASELINE_FILES = 45


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _profile_dirs() -> dict[str, str]:
    payload = tomllib.loads(PROFILES.read_text(encoding="utf-8"))
    return {
        name: profile["config_dir"]
        for name, profile in payload["harnesses"].items()
        if profile.get("status") != "profile_pending"
    }


def _ignore_matches(paths: list[str]) -> dict[str, tuple[str, str] | None]:
    """Map each path to (source, pattern) of the ignore rule that matches it, or None."""
    result = _git("check-ignore", "-v", "--no-index", "--non-matching", "--", *paths)
    assert result.returncode in {0, 1}, result.stderr
    matches: dict[str, tuple[str, str] | None] = {}
    for line in result.stdout.splitlines():
        rule, path = line.split("\t", 1)
        source, _line_number, pattern = rule.split(":", 2)
        matches[path] = (source, pattern) if pattern else None
    assert set(matches) == set(paths), result.stdout
    return matches


def test_profiles_render_only_under_the_ignored_roots() -> None:
    dirs = _profile_dirs()
    assert len(dirs) == 8, sorted(dirs)
    assert {config_dir.split("/")[0] for config_dir in dirs.values()} == set(PROJECTOR_ROOTS)


@pytest.mark.parametrize("root", PROJECTOR_ROOTS)
def test_projector_root_is_ignored_by_one_anchored_rule_at_the_repository_root(root: str) -> None:
    samples = [f"{root}/.projection-manifest.json", f"{root}/nested/rendered.md", f"{root}/settings.local.json"]
    for path, match in _ignore_matches(samples).items():
        assert match == (".gitignore", f"/{root}/"), (path, match)


def test_every_declared_projection_path_is_ignored() -> None:
    for name, config_dir in _profile_dirs().items():
        manifest = ROOT / config_dir / ".projection-manifest.json"
        paths = [f"{config_dir}/.projection-manifest.json"]
        if manifest.is_file():
            declared = json.loads(manifest.read_text(encoding="utf-8"))["paths"]
            assert declared and all(path.startswith(config_dir + "/") for path in declared), name
            paths.extend(declared)
        unignored = [path for path, match in _ignore_matches(paths).items() if match is None]
        assert unignored == [], (name, unignored)


def test_projection_root_has_no_tracked_files() -> None:
    """TEST-12566: for every profile's config_dir the index is empty, the rendered root is still present and
    non-empty on disk (untracking is non-destructive), the baseline stays tracked; the derived timer inventory
    is absent from the index as well (retired by staged deletion, never by editing a rendered root)."""
    result = _git("ls-files", "-z", "--", *PROJECTOR_ROOTS, "config/governance/timer-inventory.toml")
    assert result.returncode == 0, result.stderr
    tracked = sorted(path for path in result.stdout.split("\0") if path)
    assert tracked == [], (
        f"{len(tracked)} derived paths are still tracked; retire them with a staged deletion "
        "(the pathspec check passes deletions), never by editing the rendered root: " + ", ".join(tracked[:10])
    )
    for name, config_dir in _profile_dirs().items():
        rendered = ROOT / config_dir
        assert rendered.is_dir() and any(rendered.iterdir()), (name, config_dir)


def _paths(result: subprocess.CompletedProcess[str]) -> set[str]:
    assert result.returncode == 0, result.stderr
    return {path for path in result.stdout.split("\0") if path}


def _tracked(*pathspecs: str) -> set[str]:
    """Index entries under ``pathspecs`` minus the ones deleted in the working tree.

    A draft tree carries the D15 move unstaged until the gated commit (the draft makes no
    commits), so the index still lists the pre-move paths their working-tree deletion
    retires; the set the commit carries is the index minus those deletions.
    """
    listed = _paths(_git("ls-files", "-z", "--", *pathspecs))
    return listed - _paths(_git("ls-files", "-z", "--deleted", "--", *pathspecs))


def _stageable(*pathspecs: str) -> set[str]:
    """Untracked, unignored files under ``pathspecs``: exactly what ``git add`` would track."""
    return _paths(_git("ls-files", "-z", "--others", "--exclude-standard", "--", *pathspecs))


def test_tracked_source_shape_after_the_d15_move() -> None:
    """D15 (R1 option B, R15): the baseline tracks rules, hooks and routing only; the skills source is
    ``.agents/skills``; the instruction file is the root ``AGENTS.md``; the root pointers are tracked."""
    # The frozen authored cohort includes new shared hook/rule sources before the gated commit.
    baseline = _tracked(BASELINE) | _stageable(f"{BASELINE}/hooks", f"{BASELINE}/rules")
    assert f"{BASELINE}/AGENTS.md" not in baseline, "the instruction file moved to the root (R1 option B)"
    assert not [path for path in baseline if path.startswith(f"{BASELINE}/skills/")], "the skills tree moved"
    shape = {
        kind: sorted(path for path in baseline if path.startswith(f"{BASELINE}/{kind}/"))
        for kind in TRACKED_BASELINE_SHAPE
    }
    assert {kind: len(paths) for kind, paths in shape.items()} == TRACKED_BASELINE_SHAPE, shape
    assert baseline == {
        *shape["rules"],
        *shape["hooks"],
        *(f"{BASELINE}/{name}" for name in TRACKED_BASELINE_SINGLETONS),
    }, sorted(baseline)
    assert len(baseline) == TRACKED_BASELINE_FILES

    assert _tracked(*ROOT_CARRIERS) == set(ROOT_CARRIERS)
    for carrier in ROOT_CARRIERS:
        assert (ROOT / carrier).is_file() and not (ROOT / carrier).is_symlink(), carrier

    skills = _tracked(SKILLS_ROOT) | _stageable(SKILLS_ROOT)
    manifests = sorted(path for path in skills if path.count("/") == 3 and path.endswith("/SKILL.md"))
    assert len(manifests) >= 38, manifests
    assert all(path.startswith(f"{SKILLS_ROOT}/") for path in skills)
    assert not _paths(_git("ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--", SKILLS_ROOT)), (
        "the skills source is never ignored"
    )


def test_skills_source_is_outside_every_projector_root_and_never_ignored() -> None:
    assert ".agents" not in PROJECTOR_ROOTS
    assert not any(config_dir.split("/")[0] == ".agents" for config_dir in _profile_dirs().values())
    samples = [f"{SKILLS_ROOT}/x/SKILL.md", f"{SKILLS_ROOT}/x/helpers/run.py", SKILLS_ROOT, ".agents"]
    assert _ignore_matches(samples) == dict.fromkeys(samples)


def test_gitignore_carries_no_negation_for_a_rendered_root() -> None:
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    negations = [line for line in lines if line.startswith("!") and line.lstrip("!/").split("/")[0] in PROJECTOR_ROOTS]
    assert negations == []
    for root in PROJECTOR_ROOTS:
        assert f"/{root}/" in lines, root


def test_pathspec_check_refuses_the_same_roots() -> None:
    from scripts.check_commit_pathspec_safety import NONPRODUCT_PREFIXES, RUNTIME_COMPONENTS

    assert set(PROJECTOR_ROOTS) <= RUNTIME_COMPONENTS
    assert ".agents" not in RUNTIME_COMPONENTS, "the skills source is work product (D15)"
    assert ".groundtruth/derived" in NONPRODUCT_PREFIXES


def test_derived_timer_inventory_location_is_ignored_and_outside_the_governance_catalog() -> None:
    from scripts.timer_inventory import GENERATED_ARTIFACT_REL

    relative = GENERATED_ARTIFACT_REL.as_posix()
    assert relative.startswith(".groundtruth/derived/")
    assert _ignore_matches([relative]) == {relative: (".gitignore", "/.groundtruth/*")}
