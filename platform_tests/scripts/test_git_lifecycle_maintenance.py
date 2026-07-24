"""Spec-derived tests for the governed git-maintenance actuator (WI-5440).

Coverage maps to the proposal's Spec-Derived Verification Plan:

- ``DCL-DISPATCHER-QUIESCENCE-LEASE-001`` -- run fails closed without a held
  drain lease; composes the existing quiescence primitive when held.
- ``GOV-WORK-TREE-HYGIENE-001`` -- worktree prune removes only stale
  registrations; the orphan sweep is bounded to ``tmp_obj_*`` / ``tmp_pack_*``.
- ``DCL-GIT-BRANCH-BINDING-PROMOTION-001`` -- maintenance preserves bound
  work-item refs and their reachable objects.
- ``GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`` -- existing lifecycle verbs are
  unchanged; plan is read-only.
- interruption safety -- recover cleans partial state.
- hard invariants -- no history-rewrite / force / LFS command is ever issued.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from groundtruth_kb.git_lifecycle.commands import CommandResult, SubprocessCommandBoundary
from groundtruth_kb.git_lifecycle.maintenance import MaintenanceActuator
from groundtruth_kb.git_lifecycle.models import OperationDenied


class RecordingBoundary:
    """Command boundary that records argv and returns canned stdout."""

    def __init__(self, stdout_map: dict[str, str] | None = None) -> None:
        self.calls: list[tuple[str, ...]] = []
        self._stdout_map = stdout_map or {}

    def run(self, argv, *, cwd):  # noqa: ANN001 - matches CommandBoundary protocol
        recorded = tuple(str(item) for item in argv)
        self.calls.append(recorded)
        verb = recorded[1] if len(recorded) > 1 else ""
        return CommandResult(argv=recorded, returncode=0, stdout=self._stdout_map.get(verb, ""), stderr="")


class HeldQuiescence:
    def verify_quiescence(self, *, operation_id: str) -> dict[str, object]:
        return {"status": "PASS", "operation": "drain-verify", "operation_id": operation_id}


class UnheldQuiescence:
    def verify_quiescence(self, *, operation_id: str) -> dict[str, object]:
        raise OperationDenied("drain_not_held", "no bounded drain lease is held")


def _git_init(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "t@example.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True, capture_output=True)


def _actuator(repo_root: Path, *, quiescence, command, state_dir: Path, clock=None) -> MaintenanceActuator:
    kwargs = {"repo_root": repo_root, "quiescence": quiescence, "command": command, "state_dir": state_dir}
    if clock is not None:
        kwargs["clock"] = clock
    return MaintenanceActuator(**kwargs)


# -- DCL-DISPATCHER-QUIESCENCE-LEASE-001 --------------------------------------


def test_run_without_drain_lease_fails_closed(tmp_path: Path) -> None:
    boundary = RecordingBoundary()
    actuator = _actuator(tmp_path, quiescence=UnheldQuiescence(), command=boundary, state_dir=tmp_path / "state")
    with pytest.raises(OperationDenied) as exc:
        actuator.run(operation_id="op-1")
    assert exc.value.code == "maintenance_lease_not_held"
    # Fail-closed BEFORE any object-store mutation: no git command, no journal.
    assert boundary.calls == []
    assert not (tmp_path / "state" / "op-1.json").exists()


def test_run_composes_existing_drain_lease(tmp_path: Path) -> None:
    boundary = RecordingBoundary()
    actuator = _actuator(tmp_path, quiescence=HeldQuiescence(), command=boundary, state_dir=tmp_path / "state")
    result = actuator.run(operation_id="op-1")
    assert result["status"] == "PASS"
    assert ("git", "worktree", "prune", "--expire=now") in boundary.calls
    assert any(call[:3] == ("git", "reflog", "expire") for call in boundary.calls)
    assert any(call[:2] == ("git", "gc") for call in boundary.calls)
    journal = json.loads((tmp_path / "state" / "op-1.json").read_text())
    assert journal["phase"] == "complete"


# -- GOV-WORK-TREE-HYGIENE-001 ------------------------------------------------


def test_worktree_prune_removes_only_stale_registrations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _git_init(repo)
    subprocess.run(["git", "-C", str(repo), "commit", "--allow-empty", "-qm", "init"], check=True, capture_output=True)
    stale = tmp_path / "wt_stale"
    live = tmp_path / "wt_live"
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", str(stale)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", str(live)], check=True, capture_output=True)
    # Make `stale` stale by removing its working directory.
    import shutil

    shutil.rmtree(stale)
    actuator = _actuator(
        repo, quiescence=HeldQuiescence(), command=SubprocessCommandBoundary(), state_dir=tmp_path / "s"
    )
    actuator.run(operation_id="op-1", expire_spec="now")
    listing = subprocess.run(
        ["git", "-C", str(repo), "worktree", "list", "--porcelain"], capture_output=True, text=True
    ).stdout
    assert "wt_live" in listing  # live registration preserved
    assert "wt_stale" not in listing  # stale registration pruned


def test_orphan_sweep_bounded_to_tmp_artifacts(tmp_path: Path) -> None:
    objects = tmp_path / ".git" / "objects"
    (objects / "ab").mkdir(parents=True)
    (objects / "pack").mkdir(parents=True)
    valid = objects / "ab" / ("c" * 38)  # valid loose object name
    old_obj = objects / "ab" / "tmp_obj_OLD"
    old_pack = objects / "pack" / "tmp_pack_OLD"
    recent_obj = objects / "ab" / "tmp_obj_RECENT"
    for path in (valid, old_obj, old_pack, recent_obj):
        path.write_text("x")
    os.utime(valid, (0, 0))
    os.utime(old_obj, (0, 0))
    os.utime(old_pack, (0, 0))
    os.utime(recent_obj, (999_999.9, 999_999.9))
    actuator = _actuator(
        tmp_path,
        quiescence=HeldQuiescence(),
        command=RecordingBoundary(),
        state_dir=tmp_path / "s",
        clock=lambda: 1_000_000.0,
    )
    swept = actuator._sweep_garbage(max_age_seconds=1.0)
    assert valid.exists()  # a valid loose object is never a candidate
    assert recent_obj.exists()  # below the age threshold -> preserved
    assert not old_obj.exists()  # aged tmp object removed
    assert not old_pack.exists()  # aged tmp pack removed
    assert set(swept) == {".git/objects/ab/tmp_obj_OLD", ".git/objects/pack/tmp_pack_OLD"}


# -- DCL-GIT-BRANCH-BINDING-PROMOTION-001 -------------------------------------


def test_maintenance_preserves_bound_workitem_refs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _git_init(repo)
    (repo / "f.txt").write_text("hello")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "c1"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "branch", "wi-5440-branch"], check=True, capture_output=True)
    tip = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "wi-5440-branch"], check=True, capture_output=True, text=True
    ).stdout.strip()
    actuator = _actuator(
        repo, quiescence=HeldQuiescence(), command=SubprocessCommandBoundary(), state_dir=tmp_path / "s"
    )
    actuator.run(operation_id="op-1", expire_spec="now", prune_spec="now")
    tip_after = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "wi-5440-branch"], capture_output=True, text=True
    ).stdout.strip()
    assert tip_after == tip  # bound ref preserved
    exists = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", tip], capture_output=True)
    assert exists.returncode == 0  # reachable object not pruned


# -- GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 ---------------------------------


def test_existing_lifecycle_verbs_unchanged() -> None:
    from groundtruth_kb.git_lifecycle import __main__ as glm

    parser = glm._parser()
    # Pre-existing verbs still parse unchanged.
    assert parser.parse_args(["show", "--work-item-id", "WI-1"]).command == "show"
    assert parser.parse_args(["drain", "acquire", "--operation-id", "op"]).command == "drain"
    # The maintenance verb is additive.
    parsed = parser.parse_args(["maintenance", "plan"])
    assert parsed.command == "maintenance"
    assert parsed.action == "plan"


def test_plan_is_read_only(tmp_path: Path) -> None:
    boundary = RecordingBoundary(stdout_map={"count-objects": "count: 5\nsize: 100\n"})
    actuator = _actuator(tmp_path, quiescence=HeldQuiescence(), command=boundary, state_dir=tmp_path / "s")
    result = actuator.plan()
    assert result["mutating"] is False
    mutating_verbs = {"gc", "prune", "expire", "repack"}
    for call in boundary.calls:
        assert not (set(call) & mutating_verbs), f"plan issued a mutating command: {call}"


# -- hard invariants ----------------------------------------------------------


def test_no_history_rewrite_or_lfs_paths(tmp_path: Path) -> None:
    boundary = RecordingBoundary()
    actuator = _actuator(tmp_path, quiescence=HeldQuiescence(), command=boundary, state_dir=tmp_path / "s")
    actuator.plan()
    actuator.run(operation_id="op-1")
    forbidden = {
        "filter-branch",
        "filter-repo",
        "fast-import",
        "replace",
        "push",
        "--force",
        "--force-with-lease",
        "-f",
        "reset",
        "update-ref",
        "lfs",
        "clean",
        "rm",
    }
    for call in boundary.calls:
        assert not (set(call) & forbidden), f"forbidden token issued: {call}"
    # The guard rejects a forbidden command by construction.
    with pytest.raises(OperationDenied) as exc:
        actuator._git(("push", "--force"))
    assert exc.value.code == "maintenance_forbidden_command"


# -- interruption safety ------------------------------------------------------


def test_recover_cleans_partial_run(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    objects = repo / ".git" / "objects" / "ab"
    objects.mkdir(parents=True)
    partial = objects / "tmp_obj_PARTIAL"
    partial.write_text("partial")
    os.utime(partial, (0, 0))
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    # An interrupted run left a journal in the `started` phase.
    (state_dir / "op-1.json").write_text(json.dumps({"operation_id": "op-1", "phase": "started"}))
    actuator = _actuator(
        repo, quiescence=HeldQuiescence(), command=RecordingBoundary(), state_dir=state_dir, clock=lambda: 1_000_000.0
    )
    result = actuator.recover(reason="simulated interruption", operation_id="op-1")
    assert not partial.exists()  # partial garbage cleaned
    assert result["recovered_journal"] is True
    journal = json.loads((state_dir / "op-1.json").read_text())
    assert journal["phase"] == "recovered"
