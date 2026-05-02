# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GTKB-ISOLATION-017 Slice 2: AST gate for managed-artifact registry coverage.

Two paired tests prove the registry covers the template-source tree:

T1a (forward existence): every FILE-class registry record's ``template_path``
resolves to an existing file under ``groundtruth-kb/templates/``.

T1b (reverse coverage): every file under ``groundtruth-kb/templates/`` is
referenced by some FILE-class record's ``template_path`` (or is in the
explicit non-scaffolded allowlist).

Per Codex `-002` F1 fix: uses ``template_path`` (the source-tree key), not
``classify_path()`` (which is keyed on scaffold ``target_path``). T6 in
``test_registry_target_path_round_trip.py`` exercises ``classify_path()``
on actual ``target_path`` values.

Bridge authority: ``bridge/gtkb-isolation-017-slice2-registry-isolation-004.md`` GO.
"""

from __future__ import annotations

from pathlib import Path

# Files under templates/ that are NOT scaffolded into adopter projects (e.g.,
# documentation, README templates rendered by string substitution rather than
# file-copy). These are excluded from the reverse-coverage walk.
#
# Each entry must be either:
#   - a basename (e.g., "MEMORY.md") that matches by file name anywhere in tree,
#   - a posix-style relative path under templates/ (e.g., "ci/full/build.yml").
_NON_SCAFFOLDED_TEMPLATE_FILES: frozenset[str] = frozenset(
    {
        # Documentation rendered from strings, not file-copied.
        "MEMORY.md",
        "README.md",
        "CLAUDE.md",
        "BRIDGE-INVENTORY.md",
        "bridge-os-poller-setup-prompt.md",
        # The registry files themselves are not their own scaffold targets.
        "managed-artifacts.toml",
        "scaffold-ownership.toml",
    }
)

# Owner-approved Slice 3 deferral, authorized at S326 in
# bridge/gtkb-isolation-017-slice2-registry-isolation-007.md
# (Codex `-006` F1 fix).
#
# These 22 scaffolded template files do not have FILE-class registry
# rows yet because adding them requires extending the file-class enum
# (`Literal["hook","rule","skill",...]`) with new categories. That work
# is owned by Slice 3 (`gt project init` adopter-subject defaults +
# scaffold deliverables) per scoping bridge `-003` lines 95-115.
#
# Retire-by gate: GTKB-ISOLATION-017 closeout requires this list to be
# empty. Slice 3 NO-GO if it ships without registering all 22.
#
# T-DEFERRAL asserts every path in this list exists under templates/
# (catches accidental deletions that would silently retire a deferral).
_OWNER_APPROVED_SLICE3_DEFERRAL: frozenset[str] = frozenset(
    {
        # CI templates (10 files; Slice 3 scaffold-deliverable scope).
        "ci/build.yml",
        "ci/deploy.yml",
        "ci/test.yml",
        "ci/full/build.yml",
        "ci/full/deploy.yml",
        "ci/full/test.yml",
        "ci/minimal/test.yml",
        "ci/standard/test.yml",
        "ci/integrations/.coderabbitai.yaml",
        "ci/integrations/dependabot.yml",
        # Project-root scaffold templates (8 files; Slice 3 scope).
        "project/.editorconfig",
        "project/.pre-commit-config.yaml",
        "project/AGENTS.md",
        "project/Dockerfile",
        "project/Makefile",
        "project/docker-compose.yml",
        "project/env.example",
        "project/settings.local.json",
        # Codex bootstrap docs (4 files; Slice 3 dual-agent scope).
        "project/codex-bootstrap/CODEX-REVIEW-OPERATING-CONTRACT.md",
        "project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md",
        "project/codex-bootstrap/CODEX-WAY-OF-WORKING.md",
        "project/codex-bootstrap/LOYAL-OPPOSITION-LOG.md",
    }
)


def _templates_dir() -> Path:
    """Locate ``groundtruth-kb/templates/`` from this test file."""
    here = Path(__file__).resolve()
    # tests/test_registry_ast_coverage.py -> groundtruth-kb/templates/
    return here.parents[1] / "templates"


def test_every_file_class_record_template_path_exists() -> None:
    """T1a (forward): every FILE-class registry row's ``template_path`` exists.

    Per Phase 9 §"Regression Visibility" line 406. Detects registry rows
    pointing at deleted/missing template files (a class of registry drift).
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    templates_root = _templates_dir()
    resolver = OwnershipResolver()
    missing: list[str] = []

    for record in resolver.all_records():
        if record.source_class != "file" or record.source is None:
            continue
        template_path = getattr(record.source, "template_path", None)
        if not template_path:
            continue
        if not (templates_root / template_path).is_file():
            missing.append(f"{record.id}: {template_path}")

    assert not missing, (
        f"{len(missing)} FILE-class registry rows reference missing template "
        f"files. First 5: {missing[:5]}. Either restore the template file or "
        f"remove the registry row in templates/managed-artifacts.toml."
    )


def test_every_template_source_file_has_registry_coverage() -> None:
    """T1b (reverse): every file under templates/ has a registry entry.

    Per Phase 9 §"Regression Visibility" line 406. Walks templates/ and
    asserts each file appears as a ``template_path`` of some FILE-class
    record (or is in the explicit non-scaffolded allowlist).

    Per Codex `-002` F1 fix: uses ``template_path`` enumeration, not
    ``classify_path()`` (which is keyed on ``target_path``).
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    templates_root = _templates_dir()
    resolver = OwnershipResolver()
    registered_template_paths: set[str] = set()
    for record in resolver.all_records():
        if record.source_class != "file" or record.source is None:
            continue
        template_path = getattr(record.source, "template_path", None)
        if template_path:
            registered_template_paths.add(template_path)

    unregistered: list[str] = []
    for path in templates_root.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(templates_root).as_posix()
        if rel in _NON_SCAFFOLDED_TEMPLATE_FILES or path.name in _NON_SCAFFOLDED_TEMPLATE_FILES:
            continue
        if rel in _OWNER_APPROVED_SLICE3_DEFERRAL:
            continue
        if rel not in registered_template_paths:
            unregistered.append(rel)

    assert not unregistered, (
        f"AST gate failure: {len(unregistered)} template-source files lack "
        f"registry coverage (no FILE-class record's template_path matches). "
        f"First 5: {unregistered[:5]}. Add a FILE-class record to "
        f"templates/managed-artifacts.toml, OR add to the explicit "
        f"_NON_SCAFFOLDED_TEMPLATE_FILES allowlist if the file is "
        f"intentionally template-only (documentation, README)."
    )


def test_owner_approved_slice3_deferral_paths_exist() -> None:
    """T-DEFERRAL per Codex `-006` F1 fix: every deferral allowlist entry
    must correspond to a real template file under groundtruth-kb/templates/.

    Catches accidental deletions: if a file is removed from templates/ but
    its entry remains in the deferral list, the deferral becomes meaningless
    (we'd be deferring registration of a file that doesn't exist).
    """
    templates_root = _templates_dir()
    missing: list[str] = []
    for rel in _OWNER_APPROVED_SLICE3_DEFERRAL:
        if not (templates_root / rel).is_file():
            missing.append(rel)
    assert not missing, (
        f"{len(missing)} deferral entries reference missing files. "
        f"First 5: {missing[:5]}. Either restore the template file or "
        f"remove the entry from _OWNER_APPROVED_SLICE3_DEFERRAL "
        f"(deferring registration of a nonexistent file is meaningless)."
    )
