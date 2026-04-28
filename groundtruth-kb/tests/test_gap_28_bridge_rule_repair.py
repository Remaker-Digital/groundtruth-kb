# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Gap 2.8 — upgrade-repair for same-version missing bridge rules.

The non-disruptive-upgrade investigation flagged that ``file-bridge-protocol.md``,
``bridge-essential.md``, and ``deliberation-protocol.md`` were scaffold-copied
for dual-agent projects but NOT in ``_MANAGED_RULES``, so ``gt project upgrade``
could not repair a deleted rule file. Doctor simultaneously required them
(``_REQUIRED_BRIDGE_RULES``) — creating a user-visible gap: doctor says
"Missing bridge rule file(s)" but upgrade takes no action.

C1 closes the gap by making the registry's ``managed_profiles`` axis the
source of truth. These tests verify that at current scaffold version, a
missing bridge rule produces an ``add`` action in ``plan_upgrade`` and is
actually copied by ``execute_upgrade``.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from groundtruth_kb import __version__
from groundtruth_kb.project.upgrade import execute_upgrade, plan_upgrade


def _write_minimal_toml(target: Path, profile: str, version: str) -> None:
    """Minimal groundtruth.toml mirroring the helper in tests/test_upgrade.py."""
    (target / "groundtruth.toml").write_text(
        f"""[groundtruth]
db_path = "groundtruth.db"

[project]
project_name = "Test"
owner = "Test Owner"
profile = "{profile}"
copyright_notice = ""
cloud_provider = "none"
scaffold_version = "{version}"
created_at = "2026-01-01T00:00:00Z"
""",
        encoding="utf-8",
    )


def _setup_git_for_upgrade(target: Path) -> None:
    """Initialize git + commit current tree so execute_upgrade preconditions pass.

    Per bridge ``gtkb-rollback-receipts-014`` GO, execute_upgrade uses a
    payload-branch-and-merge flow that anchors the rollback receipt on a
    real merge commit. Tests must run inside a git work tree with clean
    state so that precondition gates pass.
    """
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=target, check=True)
    # Disable Windows CRLF auto-conversion so byte-level file assertions
    # don't trip on line endings that git would rewrite during checkouts.
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True)
    subprocess.run(
        ["git", "commit", "-m", "pre-upgrade snapshot", "--allow-empty"],
        cwd=target,
        check=True,
        capture_output=True,
    )


@pytest.mark.parametrize(
    "rule_filename",
    [
        "file-bridge-protocol.md",
        "bridge-essential.md",
        "deliberation-protocol.md",
    ],
)
def test_plan_upgrade_adds_missing_bridge_rule_at_same_version(tmp_path: Path, rule_filename: str) -> None:
    """At current scaffold version, missing bridge rule → ``add`` action."""
    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    actions = plan_upgrade(tmp_path)
    rule_target = f".claude/rules/{rule_filename}"
    adds = [a for a in actions if a.action == "add" and a.file == rule_target]
    assert adds, (
        f"expected add action for missing {rule_target} at same version; got: {[(a.action, a.file) for a in actions]}"
    )


@pytest.mark.parametrize(
    "rule_filename",
    [
        "file-bridge-protocol.md",
        "bridge-essential.md",
        "deliberation-protocol.md",
    ],
)
def test_execute_creates_missing_bridge_rule_at_same_version(tmp_path: Path, rule_filename: str) -> None:
    """``plan_upgrade`` + ``execute_upgrade`` copy a missing bridge rule from template."""
    _write_minimal_toml(tmp_path, profile="dual-agent", version=__version__)
    rule_path = tmp_path / ".claude" / "rules" / rule_filename
    assert not rule_path.exists()

    actions = plan_upgrade(tmp_path)
    _setup_git_for_upgrade(tmp_path)
    execute_upgrade(tmp_path, actions, force=False)

    assert rule_path.exists(), f"{rule_filename} should be copied by execute_upgrade at same version"
    content = rule_path.read_text(encoding="utf-8")
    assert content.strip(), f"{rule_filename} is empty after repair"
