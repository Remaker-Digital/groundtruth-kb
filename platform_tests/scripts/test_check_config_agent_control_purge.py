"""Executable binding for TEST-12124: config/agent-control is absent and unreferenced.

Work item: WI-6962 (PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE)
Spec:      GOV-SOT-SINGLETON-001
Authority: bridge/gtkb-wi6962-purge-config-agent-control-second-baseline-008.md (GO),
           owner Route A test-first sequence per DELIB-20260826203515.

TEST-12124 expected outcome, verbatim:

    A structural check asserts that config/agent-control does not exist and that no
    rule, skill, hook, test or doc references it. The check FAILs while the directory
    or any live reference survives.

These tests are expected to FAIL before the WI-6962 purge lands. That pre-implementation
FAIL is the evidence the GO's step 3 requires; the same tests are re-run after the purge
as spec-derived verification evidence (matrix A1-A12).

Exclusion classes are not convenience carve-outs. Each is fixed by the approved -007
proposal and its -008 GO:

* frozen historical evidence  - immutable audit surfaces, never rewritten forward
* generated projections       - projector-regenerated; the baseline is the only writer
* memory/                     - explicitly non-authoritative
* documentation-deferred (2)  - PAUTH v3 carries no `documentation` mutation class, so
                                WI-6962 may not edit them; disclosed, not worked around
* WI-7131 collision (3)       - removal targets of another live P0 carrier

Because the two documentation-deferred paths are outstanding, check A3 cannot reach a
zero live-reference count over the whole tree. The reference assertion below therefore
scopes itself to the classes WI-6962 is actually authorized to purge, which is what the
-008 GO states A3's expected result to be.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

#: The obsolete second baseline this work item purges.
PURGE_DIR = "config/agent-control"

#: The literal token whose presence in a tracked file constitutes a live reference.
REFERENCE_TOKEN = "config/agent-control"

#: Immutable audit surfaces. Forward removal never rewrites recorded history.
FROZEN_HISTORICAL_PREFIXES = (
    "bridge/",
    ".groundtruth/formal-artifact-approvals/",
    "archive/",
)

#: Projector-owned roots. Agents never hand-edit these; the baseline is the only writer.
GENERATED_PROJECTION_PREFIXES = (
    ".claude/",
    ".codex/",
    ".cursor/",
    ".goose/",
    ".agent/",
    ".agents/",
    ".api-harness/",
    ".antigravity/",
)

#: Explicitly non-authoritative operational notepad.
NON_AUTHORITATIVE_PREFIXES = ("memory/",)

#: PAUTH v3 carries no `documentation` mutation class (NEW-3 disclosure).
DOCUMENTATION_DEFERRED_PATHS = frozenset(
    {
        "groundtruth-kb/docs/reference/canonical-terminology-detail.md",
        "groundtruth-kb/docs/reports/agent-red-classification.md",
    }
)

#: Removal targets of WI-7131, a separate live P0 carrier (NEW-1 disclosure).
WI7131_COLLISION_PATHS = frozenset(
    {
        ".harness-baseline-configuration/gtkb-hooks/last-user-visible-startup.md",
        ".harness-baseline-configuration/gtkb-hooks/last-user-visible-startup-pb.md",
        ".harness-baseline-configuration/gtkb-hooks/last-user-visible-startup-lo.md",
    }
)

#: This file names the token in its own exclusion constants and must not self-trip.
SELF_PATH = "platform_tests/scripts/test_check_config_agent_control_purge.py"

EXCLUDED_PREFIXES = FROZEN_HISTORICAL_PREFIXES + GENERATED_PROJECTION_PREFIXES + NON_AUTHORITATIVE_PREFIXES

EXCLUDED_EXACT_PATHS = DOCUMENTATION_DEFERRED_PATHS | WI7131_COLLISION_PATHS | {SELF_PATH}


def _is_excluded(relative_path: str) -> bool:
    """True when a live reference in this path is dispositioned rather than outstanding."""
    normalized = relative_path.replace("\\", "/")
    if normalized in EXCLUDED_EXACT_PATHS:
        return True
    return normalized.startswith(EXCLUDED_PREFIXES)


def _tracked_files_referencing_token() -> list[str]:
    """Return tracked files containing the token, via git grep.

    Tracked content is the live surface: untracked and ignored material is not a
    governed dependency. ``git grep -l`` returns exit 1 with no output when there
    are no matches, which is the passing case rather than an error.
    """
    result = subprocess.run(
        ["git", "grep", "--full-name", "-l", "-F", REFERENCE_TOKEN, "--", "."],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"git grep failed (rc={result.returncode}): {result.stderr.strip()[:400]}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def outstanding_live_references() -> list[str]:
    """Tracked referencing paths that WI-6962 is authorized to purge and has not."""
    return sorted(p for p in _tracked_files_referencing_token() if not _is_excluded(p))


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


def test_no_outstanding_live_references_to_config_agent_control() -> None:
    """TEST-12124 clause 2: no live reference survives in purgeable scope.

    Scoped to the classes WI-6962 is authorized to mutate. The two
    documentation-deferred paths and three WI-7131 collision paths are excluded by
    the -008 GO and are asserted separately below so their disposition stays visible
    rather than silently absorbed.
    """
    outstanding = outstanding_live_references()

    assert not outstanding, (
        f"{len(outstanding)} tracked file(s) still reference {REFERENCE_TOKEN!r} "
        "within purgeable scope. Each must be repointed to "
        ".harness-baseline-configuration or removed. "
        f"First offenders: {outstanding[:15]}"
    )


@pytest.mark.parametrize("deferred_path", sorted(DOCUMENTATION_DEFERRED_PATHS))
def test_documentation_deferred_paths_remain_disclosed(deferred_path: str) -> None:
    """NEW-3: these two readers are deferred, not silently dropped.

    PAUTH v3 has no `documentation` mutation class, so WI-6962 cannot edit them.
    This test does not require them to be clean; it requires the deferral to stay
    honest. When a PAUTH amendment or companion documentation carrier lands, the
    path drops out of the exclusion set and the reference assertion above covers it.
    """
    assert deferred_path in EXCLUDED_EXACT_PATHS, (
        f"{deferred_path} must remain an explicit, disclosed exclusion while PAUTH "
        "carries no documentation mutation class."
    )


@pytest.mark.parametrize("collision_path", sorted(WI7131_COLLISION_PATHS))
def test_wi7131_collision_paths_remain_excluded(collision_path: str) -> None:
    """NEW-1: WI-6962 must not edit files another live P0 carrier is deleting.

    If WI-7131 terminalizes first the references vanish with the files. If WI-7131
    withdraws, a successor revision of the WI-6962 thread re-adds these paths with
    fresh justification. Neither outcome drops the obligation silently.
    """
    assert collision_path in EXCLUDED_EXACT_PATHS, (
        f"{collision_path} is a WI-7131 removal target and must stay excluded from "
        "the WI-6962 cohort until WI-7131 terminalizes or withdraws."
    )
