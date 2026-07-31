"""Governed Git object-store maintenance actuator (WI-5440).

The implementation-start gate (``scripts/implementation_start_gate.py``) blocks
direct ``git gc`` / ``git prune`` / ``git repack`` / ``git reflog expire`` /
``git worktree prune`` and redirects the caller to
``python -m groundtruth_kb.git_lifecycle``. Before this module, that package
exposed only work-item branch-lifecycle and dispatcher-drain verbs, so the
redirect named a capability that did not exist and sanctioned object-store
maintenance was impossible.

This module supplies the sanctioned ``maintenance`` verb with three subverbs:

``plan``
    Read-only. Enumerates what would be reclaimed (object-store stats, stale
    worktree registrations, ``tmp_obj_*`` / ``tmp_pack_*`` garbage) and emits
    evidence. The default subverb; performs no mutation.

``run``
    Mutating and fail-closed. Requires a *held* bounded dispatcher drain lease
    (``DCL-DISPATCHER-QUIESCENCE-LEASE-001``) verified through the existing
    quiescence primitive; refuses to mutate when the lease is unheld. Writes an
    operation journal before any object-store mutation so an interrupted run is
    recoverable, then issues only the sanctioned maintenance commands and a
    bounded orphan sweep.

``recover``
    Cleans partial state left by an interrupted ``run`` -- including the bounded
    removal of orphaned ``tmp_obj_*`` / ``tmp_pack_*`` garbage -- and marks the
    journal recovered.

Hard invariants (enforced in code by :data:`_FORBIDDEN_TOKENS`): never rewrites
history, never force-pushes, never introduces Git LFS, and never removes
reachable objects. ``git gc`` prunes only unreachable objects, so work-item
branch bindings and their reachable objects are preserved
(``DCL-GIT-BRANCH-BINDING-PROMOTION-001``).

This actuator creates the sanctioned capability only. It does NOT execute
object-store reclamation on the canonical repository or untrack
``groundtruth.db``; both belong to dependent WI-5431.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, Protocol

from groundtruth_kb.git_lifecycle.commands import CommandBoundary, CommandResult, SubprocessCommandBoundary
from groundtruth_kb.git_lifecycle.models import OperationDenied

# Git tokens the maintenance actuator must never emit. The guard in
# :meth:`MaintenanceActuator._git` fails closed if any argument matches, so a
# history rewrite, force update, LFS command, or destructive working-tree
# operation cannot be issued even by a future coding mistake.
_FORBIDDEN_TOKENS = frozenset(
    {
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
)

# Partial-write temp artifacts left in the object store by interrupted git
# maintenance. Valid loose objects are named ``<38-hex>`` under a ``<2-hex>``
# directory and never match these prefixes, so the sweep can never remove a
# valid object.
_TMP_OBJECT_PREFIX = "tmp_obj_"
_TMP_PACK_PREFIX = "tmp_pack_"

_JOURNAL_PHASE_STARTED = "started"
_JOURNAL_PHASE_COMPLETE = "complete"
_JOURNAL_PHASE_RECOVERED = "recovered"


class QuiescenceVerifier(Protocol):
    """The subset of ``GitLifecycleService`` the actuator composes.

    ``verify_quiescence`` returns a status mapping when the bounded drain lease
    is held and raises :class:`OperationDenied` (or returns a non-``PASS``
    status) when it is not.
    """

    def verify_quiescence(self, *, operation_id: str) -> dict[str, Any]: ...


class MaintenanceActuator:
    """Sanctioned object-store maintenance bounded to non-destructive verbs."""

    def __init__(
        self,
        *,
        repo_root: Path,
        quiescence: QuiescenceVerifier,
        command: CommandBoundary | None = None,
        state_dir: Path | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._repo_root = Path(repo_root)
        self._quiescence = quiescence
        self._command = command or SubprocessCommandBoundary()
        self._state_dir = (
            Path(state_dir) if state_dir is not None else self._repo_root / ".gtkb-state" / "git-maintenance"
        )
        self._clock = clock

    # -- command boundary ------------------------------------------------

    def _git(self, argv: Iterable[str]) -> CommandResult:
        """Issue one sanctioned ``git`` command, failing closed on any
        forbidden token."""
        tail = tuple(str(item) for item in argv)
        forbidden = sorted(token for token in tail if token in _FORBIDDEN_TOKENS)
        if forbidden:
            raise OperationDenied(
                "maintenance_forbidden_command",
                "maintenance actuator refused a non-sanctioned git command",
                forbidden=forbidden,
                argv=list(tail),
            )
        return self._command.run(("git", *tail), cwd=self._repo_root)

    # -- object-store inspection (read-only) ------------------------------

    def _object_store(self) -> Path:
        return self._repo_root / ".git" / "objects"

    def _garbage_candidates(self) -> list[Path]:
        """Return existing ``tmp_obj_*`` / ``tmp_pack_*`` partial-write files."""
        objects = self._object_store()
        if not objects.is_dir():
            return []
        candidates: list[Path] = []
        for entry in sorted(objects.glob(f"*/{_TMP_OBJECT_PREFIX}*")):
            if entry.is_file():
                candidates.append(entry)
        pack_dir = objects / "pack"
        if pack_dir.is_dir():
            for entry in sorted(pack_dir.glob(f"{_TMP_PACK_PREFIX}*")):
                if entry.is_file():
                    candidates.append(entry)
        return candidates

    def _count_objects(self) -> dict[str, str]:
        result = self._git(("count-objects", "-v"))
        stats: dict[str, str] = {}
        for line in result.stdout.splitlines():
            key, _, value = line.partition(":")
            if value:
                stats[key.strip()] = value.strip()
        return stats

    def _stale_worktrees(self) -> int:
        result = self._git(("worktree", "list", "--porcelain"))
        return sum(1 for line in result.stdout.splitlines() if line.strip() == "prunable")

    def plan(self) -> dict[str, Any]:
        """Read-only reclamation plan. Issues only inspection commands and never
        mutates the object store."""
        garbage = self._garbage_candidates()
        return {
            "status": "PASS",
            "operation": "maintenance-plan",
            "object_store": self._count_objects(),
            "garbage_candidates": [str(path.relative_to(self._repo_root).as_posix()) for path in garbage],
            "garbage_count": len(garbage),
            "stale_worktrees": self._stale_worktrees(),
            "mutating": False,
        }

    # -- journal ----------------------------------------------------------

    def _journal_path(self, operation_id: str) -> Path:
        return self._state_dir / f"{operation_id}.json"

    def _write_journal(self, operation_id: str, phase: str, **extra: Any) -> None:
        self._state_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "operation_id": operation_id,
            "phase": phase,
            "updated_at": self._clock(),
            **extra,
        }
        self._journal_path(operation_id).write_text(
            json.dumps(record, ensure_ascii=True, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _read_journal(self, operation_id: str) -> dict[str, Any] | None:
        path = self._journal_path(operation_id)
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return data if isinstance(data, dict) else None

    # -- orphan sweep -----------------------------------------------------

    def _sweep_garbage(self, max_age_seconds: float) -> list[str]:
        """Remove ``tmp_obj_*`` / ``tmp_pack_*`` files older than the threshold.

        Bounded by construction: only partial-write temp artifacts are eligible;
        valid loose and packed objects never match the temp prefixes.
        """
        now = self._clock()
        removed: list[str] = []
        for candidate in self._garbage_candidates():
            try:
                age = now - candidate.stat().st_mtime
            except OSError:
                continue
            if age < max_age_seconds:
                continue
            try:
                candidate.unlink()
            except OSError:
                continue
            removed.append(candidate.relative_to(self._repo_root).as_posix())
        return removed

    # -- run --------------------------------------------------------------

    def run(
        self,
        *,
        operation_id: str,
        expire_spec: str = "now",
        prune_spec: str = "now",
        max_garbage_age_seconds: float = 86_400.0,
    ) -> dict[str, Any]:
        """Perform sanctioned maintenance behind a held drain lease.

        Fails closed with :class:`OperationDenied` before any mutation when the
        bounded dispatcher drain lease is not held.
        """
        op_id = operation_id.strip()
        if not op_id:
            raise OperationDenied("maintenance_operation_id_required", "maintenance run requires an --operation-id")

        # Quiescence precondition -- verified before any object-store mutation.
        self._require_held_lease(op_id)

        # Journal before any mutation so an interruption is recoverable.
        self._write_journal(op_id, _JOURNAL_PHASE_STARTED)

        self._git(("worktree", "prune", f"--expire={expire_spec}"))
        self._git(("reflog", "expire", f"--expire={expire_spec}", f"--expire-unreachable={expire_spec}", "--all"))
        self._git(("gc", f"--prune={prune_spec}"))
        swept = self._sweep_garbage(max_garbage_age_seconds)

        self._write_journal(op_id, _JOURNAL_PHASE_COMPLETE, swept=swept)
        return {
            "status": "PASS",
            "operation": "maintenance-run",
            "operation_id": op_id,
            "swept": swept,
            "swept_count": len(swept),
            "mutating": True,
        }

    def _require_held_lease(self, operation_id: str) -> None:
        try:
            status = self._quiescence.verify_quiescence(operation_id=operation_id)
        except OperationDenied as exc:
            raise OperationDenied(
                "maintenance_lease_not_held",
                "maintenance run requires a held bounded dispatcher drain lease",
                operation_id=operation_id,
                cause=exc.code,
            ) from exc
        if str(status.get("status")) != "PASS":
            raise OperationDenied(
                "maintenance_lease_not_held",
                "maintenance run requires a held bounded dispatcher drain lease",
                operation_id=operation_id,
            )

    # -- recover ----------------------------------------------------------

    def recover(
        self,
        *,
        reason: str,
        operation_id: str | None = None,
        max_garbage_age_seconds: float = 0.0,
    ) -> dict[str, Any]:
        """Clean partial state left by an interrupted run.

        The bounded orphan sweep is idempotent; ``recover`` uses an age
        threshold of ``0`` by default so it clears all remaining temp artifacts
        from the interrupted run.
        """
        if not reason.strip():
            raise OperationDenied("maintenance_recovery_reason_required", "maintenance recover requires a reason")

        swept = self._sweep_garbage(max_garbage_age_seconds)
        journal = self._read_journal(operation_id) if operation_id else None
        if operation_id and journal is not None and journal.get("phase") != _JOURNAL_PHASE_COMPLETE:
            self._write_journal(operation_id, _JOURNAL_PHASE_RECOVERED, reason=reason, swept=swept)

        return {
            "status": "PASS",
            "operation": "maintenance-recover",
            "operation_id": operation_id,
            "reason": reason,
            "swept": swept,
            "swept_count": len(swept),
            "recovered_journal": bool(operation_id and journal is not None),
        }
