"""Worktree-aware canonical-root resolution in the bridge-compliance gate (WI-3353).

Covers IP-2 (route bridge-compliance-gate.py project-state access through the
canonical root) and IP-5 (the scaffold-template copy carries the byte-identical
fix). Every test is parametrized over both hook copies -- the live hook and the
scaffold template -- so template parity is verified mechanically.

Spec coverage:
- GOV-FILE-BRIDGE-AUTHORITY-001: the gate does not falsely block a valid NEW
  proposal filed from a worktree session.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 /
  DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001: the WI/project membership
  check reads the canonical database, and still fails for a genuinely absent WI
  (no governance coverage removed).
- ADR-CODEX-HOOK-PARITY-FALLBACK-001: live hook and scaffold template parity.

Per bridge/gtkb-governance-hook-worktree-root-resolution-005.md (Codex GO at -006).
"""

from __future__ import annotations

import importlib.util
import shutil
import sqlite3
import subprocess
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
TEMPLATE_HOOK = REPO_ROOT / "groundtruth-kb" / "templates" / "hooks" / "bridge-compliance-gate.py"

_AUTH_ID = "PAUTH-TEST-WORKTREE"
_PROJECT_ID = "PROJECT-TEST-WORKTREE"
_WI_ID = "WI-7353"
_SPEC_LINKS = "## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"


def _load_gate(path: Path, module_name: str) -> ModuleType:
    """Load a hyphenated bridge-compliance-gate.py copy as a module."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=["live", "template"])
def gate(request: pytest.FixtureRequest) -> ModuleType:
    """The bridge-compliance gate, parametrized over both hook copies (IP-5 parity)."""
    if request.param == "live":
        return _load_gate(LIVE_HOOK, "bcg_live")
    return _load_gate(TEMPLATE_HOOK, "bcg_template")


def _require_git() -> None:
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")


def _build_canonical_and_worktree(tmp_path: Path) -> tuple[Path, Path]:
    """Build a synthetic GT-KB canonical checkout with a linked worktree under
    .claude/worktrees/test-wt. Returns (canonical_root, worktree_root).

    The worktree carries its own committed copy of groundtruth.toml, reproducing
    the WI-3353 defect surface. Requires git.
    """
    ident = [
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "-c",
        "commit.gpgsign=false",
    ]
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / "groundtruth.toml").write_text("# synthetic GT-KB root\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "add", "groundtruth.toml"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "commit", "-m", "init"], cwd=canonical, check=True, capture_output=True)
    worktree = canonical / ".claude" / "worktrees" / "test-wt"
    worktree.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", *ident, "worktree", "add", "--detach", str(worktree)],
        cwd=canonical,
        check=True,
        capture_output=True,
    )
    return canonical, worktree


def _make_db(
    db_path: Path,
    *,
    membership: tuple[str, str, str] | None,
    authorization: dict | None,
) -> None:
    """Build a fixture groundtruth.db with the two MemBase views the gate reads.

    Mirrors test_bridge_compliance_gate_wi_project_membership.py::_make_db: the
    hook only SELECTs from current_project_work_item_memberships and
    current_project_authorizations, so plain tables are behaviorally equivalent.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE current_project_work_item_memberships (work_item_id TEXT, project_id TEXT, status TEXT)"
        )
        conn.execute(
            "CREATE TABLE current_project_authorizations "
            "(id TEXT, project_id TEXT, status TEXT, expires_at TEXT, "
            "included_work_item_ids TEXT, excluded_work_item_ids TEXT)"
        )
        if membership is not None:
            conn.execute(
                "INSERT INTO current_project_work_item_memberships VALUES (?, ?, ?)",
                membership,
            )
        if authorization is not None:
            conn.execute(
                "INSERT INTO current_project_authorizations "
                "(id, project_id, status, expires_at, included_work_item_ids, "
                "excluded_work_item_ids) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    authorization["id"],
                    authorization["project_id"],
                    authorization["status"],
                    authorization["expires_at"],
                    authorization["included_work_item_ids"],
                    authorization["excluded_work_item_ids"],
                ),
            )
        conn.commit()
    finally:
        conn.close()


def _active_auth() -> dict:
    return {
        "id": _AUTH_ID,
        "project_id": _PROJECT_ID,
        "status": "active",
        "expires_at": None,
        "included_work_item_ids": None,
        "excluded_work_item_ids": None,
    }


def _proposal(*, wi: str = _WI_ID) -> str:
    return (
        "NEW\n\n"
        "# Test Proposal\n\n"
        f"Project Authorization: {_AUTH_ID}\n"
        f"Project: {_PROJECT_ID}\n"
        f"Work Item: {wi}\n\n" + _SPEC_LINKS
    )


def test_canonical_project_root_resolves_from_worktree_cwd(gate: ModuleType, tmp_path: Path) -> None:
    """IP-2: _canonical_project_root resolves the canonical main-worktree root
    from a worktree-shaped cwd via the dependency-free git-common-dir fallback."""
    _require_git()
    canonical, worktree = _build_canonical_and_worktree(tmp_path)
    resolved = gate._canonical_project_root(worktree)
    assert resolved.resolve() == canonical.resolve()


def test_wi_project_membership_reads_canonical_db(gate: ModuleType, tmp_path: Path) -> None:
    """IP-2 / DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001: the membership
    check reads the canonical database, not the worktree's empty scaffold copy."""
    _require_git()
    canonical, worktree = _build_canonical_and_worktree(tmp_path)
    # The canonical DB carries the membership + authorization rows.
    _make_db(
        canonical / "groundtruth.db",
        membership=(_WI_ID, _PROJECT_ID, "active"),
        authorization=_active_auth(),
    )
    # The worktree carries an empty scaffold DB (schema only, no rows) -- the
    # exact defect surface the fix must look past.
    _make_db(worktree / "groundtruth.db", membership=None, authorization=None)

    reason = gate._wi_project_membership_gap(_proposal(), worktree)
    assert reason is None, f"valid WI incorrectly denied against the canonical DB: {reason}"


def test_compliance_gate_no_false_wi_not_found_in_worktree(gate: ModuleType, tmp_path: Path) -> None:
    """GOV-FILE-BRIDGE-AUTHORITY-001: the gate does not emit
    wi-not-found-in-project for a valid NEW proposal in a worktree session."""
    _require_git()
    canonical, worktree = _build_canonical_and_worktree(tmp_path)
    _make_db(
        canonical / "groundtruth.db",
        membership=(_WI_ID, _PROJECT_ID, "active"),
        authorization=_active_auth(),
    )
    _make_db(worktree / "groundtruth.db", membership=None, authorization=None)

    reason = gate._deny_reason_for_content(
        cwd_path=worktree,
        file_path="bridge/test-worktree-root-001.md",
        content=_proposal(),
        run_pending_preflight=False,
    )
    assert reason is None or "wi-not-found-in-project" not in reason, (
        f"worktree session falsely blocked by the gate: {reason}"
    )


def test_wi_project_membership_still_fails_for_absent_wi(gate: ModuleType, tmp_path: Path) -> None:
    """DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001: governance coverage is
    preserved -- a genuinely absent WI still fails against the canonical DB."""
    _require_git()
    canonical, worktree = _build_canonical_and_worktree(tmp_path)
    # The canonical DB has the authorization but NO membership row for the WI.
    _make_db(canonical / "groundtruth.db", membership=None, authorization=_active_auth())
    reason = gate._wi_project_membership_gap(_proposal(wi="WI-9999999"), worktree)
    assert reason is not None and "wi-not-found-in-project" in reason


def test_canonical_project_root_fail_soft_floor(gate: ModuleType, tmp_path: Path) -> None:
    """IP-2: when neither the package import nor git resolves a canonical root
    consistent with cwd_path, _canonical_project_root falls back to cwd_path --
    a synthetic non-git directory is returned unchanged (pre-fix behavior, the
    invariant that keeps hermetic unit tests from reading the live project)."""
    synthetic = tmp_path / "synthetic-non-git"
    synthetic.mkdir()
    assert gate._canonical_project_root(synthetic).resolve() == synthetic.resolve()
