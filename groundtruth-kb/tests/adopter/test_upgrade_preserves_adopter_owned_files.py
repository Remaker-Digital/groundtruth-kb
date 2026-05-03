# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 line 239: ``upgrade preserves adopter-owned files``.

Spec: customizations to ``ownership=adopter-owned`` files survive
``gt project upgrade --apply`` byte-equal — the upgrade must not
overwrite or revert adopter content.

Outside-in surface: scaffold + customize + plan + execute, then byte-compare.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from groundtruth_kb.project.managed_registry import (
    FileArtifact,
    artifacts_for_scaffold,
)
from groundtruth_kb.project.upgrade import execute_upgrade, plan_upgrade

from .conftest import _setup_git


def _commit_all(adopter: Path, message: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=adopter, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", message], cwd=adopter, check=True, capture_output=True)


def _first_adopter_owned_existing_file(adopter: Path) -> Path:
    """Return the first ``ownership=adopter-owned`` registry path that exists in the scaffold."""
    for artifact in artifacts_for_scaffold("dual-agent"):
        if (
            isinstance(artifact, FileArtifact)
            and artifact.ownership is not None
            and artifact.ownership.ownership == "adopter-owned"
        ):
            candidate = adopter / artifact.target_path
            if candidate.exists():
                return candidate
    raise AssertionError("registry has no adopter-owned FileArtifact whose target_path exists in the scaffold")


def test_adopter_owned_file_preserves_customization_through_upgrade(
    clean_adopter: tuple[Path, Path], tmp_path: Path
) -> None:
    """Customize an adopter-owned file → upgrade leaves it byte-equal."""
    adopter, _ = clean_adopter
    customized = _first_adopter_owned_existing_file(adopter)
    sentinel_line = "\n# adopter customization sentinel S5-T5\n"
    original = customized.read_text(encoding="utf-8")
    customized_text = original + sentinel_line
    customized.write_text(customized_text, encoding="utf-8")

    # Trigger an upgrade action by deleting a managed hook so plan_upgrade
    # has substantive work to do. Without an action, execute_upgrade short-
    # circuits and the test never exercises the preserve path.
    managed_file = adopter / ".claude" / "hooks" / "assertion-check.py"
    managed_file.unlink()

    _setup_git(adopter)

    actions = plan_upgrade(adopter)
    # See test_upgrade_applies_registry_diff_under_receipts.py for the
    # ``enforce_isolation=False`` rationale.
    execute_upgrade(adopter, actions, product_root=tmp_path, enforce_isolation=False)

    after = customized.read_text(encoding="utf-8")
    assert after == customized_text, (
        f"adopter-owned file at {customized} lost its customization through upgrade; "
        f"sentinel stripped or content rewritten"
    )
