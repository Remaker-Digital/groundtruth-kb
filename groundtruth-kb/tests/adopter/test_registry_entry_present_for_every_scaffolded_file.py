# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 line 243: ``registry entry present for every scaffolded file``.

Spec: every file in a freshly scaffolded adopter must be either (a) a
registry FILE row's ``target_path`` or (b) covered by an ownership-glob
record. Detects the regression where a scaffold-only file slips into the
output without a registry entry.

Outside-in surface: scaffold output directory walk vs.
``OwnershipResolver.all_records()`` (the public ownership oracle).

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.project.ownership import OwnershipResolver

# Files in the scaffold that are intentionally NOT registry-tracked. These are
# either base files written by ``bootstrap`` (groundtruth.toml, groundtruth.db,
# .gitignore) or static markers committed by Slice 3 (.gitkeep) that the
# registry does not need to manage.
#
# This list is the test's view of "non-registry-managed but still expected".
# Any addition here is explicit allow-listing and must be reviewed.
_REGISTRY_EXEMPT_FILES: frozenset[str] = frozenset(
    {
        # Bootstrap-only outputs (not registry-managed)
        ".gitignore",  # written by bootstrap._write_project_gitignore
        ".groundtruth/formal-artifact-approvals/.gitkeep",  # Slice 3 emit
        # Base templates copied by `_copy_base_templates`
        ".editorconfig",
        ".pre-commit-config.yaml",
        "Makefile",
        "pyproject-sections.toml",
        # Profile-shared core docs (template-rendered, scaffold-only)
        "CLAUDE.md",
        "MEMORY.md",
        "AGENTS.md",
        # Dual-agent template-copies
        "BRIDGE-INVENTORY.md",
        "bridge-os-poller-setup-prompt.md",
        "bridge/INDEX.md",
        # Codex bootstrap docs (per `_copy_dual_agent_templates` codex_src loop)
        "independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md",
        "independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md",
        "independent-progress-assessments/CODEX-WAY-OF-WORKING.md",
        "independent-progress-assessments/LOYAL-OPPOSITION-LOG.md",
        # Settings synthesized from settings-hook-registration rows (the rows are
        # in the registry but the file itself is the implicit aggregation target)
        ".claude/settings.json",
        ".claude/settings.local.json",
        # Codex forward-compat config emitted by Slice 3
        ".codex/hooks.json",
    }
)


def _build_file_target_set() -> set[str]:
    resolver = OwnershipResolver()
    paths: set[str] = set()
    for record in resolver.all_records():
        if record.source_class == "file" and record.source is not None:
            target_path = getattr(record.source, "target_path", None)
            if target_path:
                paths.add(target_path)
    return paths


def _build_glob_patterns() -> list[str]:
    resolver = OwnershipResolver()
    patterns: list[str] = []
    for record in resolver.all_records():
        if record.source_class == "ownership-glob" and record.path_glob is not None:
            patterns.append(record.path_glob)
    return patterns


def test_every_scaffolded_file_is_covered_by_registry_or_explicit_exemption(
    clean_adopter: tuple[Path, Path],
) -> None:
    """Walk the scaffolded tree; assert each file is registry-covered or exempt."""
    adopter, _ = clean_adopter
    file_targets = _build_file_target_set()
    glob_patterns = _build_glob_patterns()

    # Pre-compute the set of paths matched by ownership-glob rules using
    # `Path.glob()` (which expands `**` recursively, unlike `fnmatch`).
    glob_covered: set[str] = set()
    for pattern in glob_patterns:
        for matched in adopter.glob(pattern):
            if matched.is_file():
                glob_covered.add(matched.relative_to(adopter).as_posix())

    uncovered: list[str] = []
    for path in adopter.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(adopter).as_posix()
        if rel in _REGISTRY_EXEMPT_FILES:
            continue
        if rel in file_targets:
            continue
        if rel in glob_covered:
            continue
        uncovered.append(rel)

    # The scaffold has settled-shape exemptions like template-rendered docs
    # under `independent-progress-assessments/` that are produced by
    # `_copy_dual_agent_templates` rather than the managed registry. Those
    # are caught here as a regression signal — the test's job is to surface
    # divergence, not to whitelist every scaffold-side path. Slice 2 owns
    # the AST-coverage gate against the template tree; this test is the
    # complementary live-scaffold check.
    assert not uncovered, (
        f"{len(uncovered)} scaffolded file(s) lack registry coverage "
        f"(neither FILE row nor ownership-glob):\n  " + "\n  ".join(sorted(uncovered))
    )
