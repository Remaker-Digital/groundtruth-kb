# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 line 236: ``init scaffolds adopter-owned paths``.

Spec: every registry record with ``ownership=adopter-owned`` whose
``initial_profiles`` includes the active profile lands on disk after
``gt project init``.

Outside-in surface: ``scaffold_project`` output directory + the public
registry loader ``artifacts_for_scaffold(profile)``.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    artifacts_for_scaffold,
)


def test_clean_adopter_contains_every_adopter_owned_file(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Walk the registry's adopter-owned FILE rows for the dual-agent profile;
    each ``target_path`` must exist in the scaffolded adopter tree.

    Mirrors Slice 2's AST-coverage approach but runs against a live scaffold
    rather than the template tree — catches scaffold/registry divergence that
    would let an adopter-owned file silently disappear from the scaffold.
    """
    adopter, _ = clean_adopter
    artifacts = artifacts_for_scaffold("dual-agent")
    adopter_owned: list[FileArtifact] = [
        a
        for a in artifacts
        if isinstance(a, FileArtifact) and a.ownership is not None and a.ownership.ownership == "adopter-owned"
    ]
    assert adopter_owned, (
        "registry must declare at least one adopter-owned FileArtifact for "
        "dual-agent profile; the empty case indicates registry drift"
    )
    missing: list[str] = []
    for artifact in adopter_owned:
        if not (adopter / artifact.target_path).exists():
            missing.append(artifact.target_path)
    assert not missing, (
        f"clean adopter is missing {len(missing)} adopter-owned files declared "
        f"in the registry: {missing[:5]}{'...' if len(missing) > 5 else ''}"
    )


def test_clean_adopter_scaffold_count_is_nonzero(
    clean_adopter: tuple[Path, Path],
) -> None:
    """A clean adopter has more than the bare-minimum 5 base files.

    Guards against the regression mode where ``scaffold_project`` silently
    falls through to a near-empty tree (e.g., template-dir resolution
    failure). The exact count varies by profile/version; the floor is
    deliberately conservative.
    """
    adopter, _ = clean_adopter
    file_count = sum(1 for _ in adopter.rglob("*") if _.is_file())
    assert file_count >= 20, f"clean adopter has only {file_count} files; scaffold output looks truncated"


@pytest.mark.parametrize(
    "rel_path",
    [
        "groundtruth.toml",
        "groundtruth.db",
        ".gitignore",
        "CLAUDE.md",
        "MEMORY.md",
        "README.md",
        "memory/work_list.md",
        "memory/release-readiness.md",
        ".codex/hooks.json",
        ".groundtruth/formal-artifact-approvals/.gitkeep",
    ],
)
def test_clean_adopter_phase9_section1_artifacts_present(clean_adopter: tuple[Path, Path], rel_path: str) -> None:
    """Phase 9 §1 enumeration items appear in the scaffolded tree.

    These are the unconditional core outputs declared by Slice 3's
    ``enumerate_scaffold_outputs`` (see ``scaffold.py``). One assertion per
    path so failures surface the exact missing artifact.
    """
    adopter, _ = clean_adopter
    assert (adopter / rel_path).exists(), f"Phase 9 §1 artifact missing: {rel_path}"
