"""Recoverable branch binding, scoped commit, and promotion service."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
import tomllib
from collections.abc import Callable, Sequence
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.git_lifecycle.commands import (
    CommandBoundary,
    CommandResult,
    SubprocessCommandBoundary,
)
from groundtruth_kb.git_lifecycle.models import OperationDenied, OperationResult, PromotionEvidence
from groundtruth_kb.git_lifecycle.quiescence import (
    WorkerProbe,
    acquire_dispatcher_quiescence,
    active_dispatcher_workers,
    recover_dispatcher_quiescence,
    release_dispatcher_quiescence,
    verify_dispatcher_quiescence,
)
from groundtruth_kb.git_lifecycle.repository import GitRepository, normalize_repo_path
from groundtruth_kb.git_lifecycle.state import LifecycleState, canonical_json, sha256_json
from groundtruth_kb.session.envelope import EnvelopeError, resolve_worker_role_provenance

_WORK_ITEM = re.compile(r"^[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+$")
_OPERATION_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{2,127}$")
_BRANCH = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._/-]{0,126}[A-Za-z0-9])?$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
_PULL_REQUEST_URL = re.compile(r"^https://github\.com/[^/\s]+/[^/\s]+/pull/[1-9][0-9]*$")
_BRIDGE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,191}$")
_PROTECTED_REMOTE_BRANCHES = frozenset({"develop", "stage", "main", "master"})
_PROMOTION_RECEIPT_ISSUER = "groundtruth-kb.git-lifecycle"

CrashHook = Callable[[str], None]


def deterministic_work_branch(work_item_id: str, title: str) -> str:
    """Derive the immutable work-item branch name from identity and title."""
    if not _WORK_ITEM.fullmatch(work_item_id):
        raise OperationDenied("work_item_id_invalid", "work-item id cannot produce a deterministic branch name")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        raise OperationDenied("work_item_title_invalid", "work-item title cannot produce a deterministic branch name")
    return f"work-item/{work_item_id.lower()}-{slug[:64].rstrip('-')}"


def _record_hash(record: dict[str, Any]) -> str:
    return sha256_json({key: value for key, value in record.items() if key != "record_hash"})


def _path_is_within_scope(path: str, scope: tuple[str, ...]) -> bool:
    return any(path == allowed or path.startswith(f"{allowed.rstrip('/')}/") for allowed in scope)


class GitLifecycleService:
    """Production service for one repository's governed local Git lifecycle."""

    def __init__(
        self,
        repo_root: Path,
        *,
        state_dir: Path | None = None,
        dispatcher_state_dir: Path | None = None,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
        worker_probe: WorkerProbe | None = None,
        command_boundary: CommandBoundary | None = None,
    ) -> None:
        self.repo = GitRepository(repo_root)
        self.state = LifecycleState(state_dir or self.repo.root / ".gtkb-state" / "git-lifecycle")
        self.dispatcher_state_dir = (dispatcher_state_dir or self.repo.root / ".gtkb-state" / "bridge-poller").resolve()
        self.clock = clock
        self.sleep = sleep
        self.worker_probe = worker_probe
        self.command_boundary = command_boundary or SubprocessCommandBoundary()

    @classmethod
    def production(
        cls,
        repo_root: Path,
        *,
        command_boundary: CommandBoundary | None = None,
    ) -> GitLifecycleService:
        """Construct the production service with canonical repository-local state."""
        return cls(repo_root, command_boundary=command_boundary)

    @classmethod
    def for_testing(
        cls,
        repo_root: Path,
        *,
        state_dir: Path | None = None,
        dispatcher_state_dir: Path | None = None,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
        worker_probe: WorkerProbe | None = None,
        command_boundary: CommandBoundary | None = None,
    ) -> GitLifecycleService:
        """Construct an explicitly non-production service with injectable substrates."""
        return cls(
            repo_root,
            state_dir=state_dir,
            dispatcher_state_dir=dispatcher_state_dir,
            clock=clock,
            sleep=sleep,
            worker_probe=worker_probe,
            command_boundary=command_boundary,
        )

    def _timestamp(self) -> str:
        return datetime.fromtimestamp(self.clock(), tz=UTC).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _validate_operation_id(operation_id: str) -> str:
        if not _OPERATION_ID.fullmatch(operation_id):
            raise OperationDenied("operation_id_invalid", "operation id has an unsafe or non-deterministic form")
        return operation_id

    @staticmethod
    def _validate_branch_name(branch: str, *, expected_prefix: str | None = None) -> str:
        if (
            not _BRANCH.fullmatch(branch)
            or ".." in branch
            or "//" in branch
            or branch.endswith(".lock")
            or (expected_prefix is not None and not branch.startswith(expected_prefix))
        ):
            raise OperationDenied("branch_name_invalid", "branch name is unsafe or non-canonical", branch=branch)
        return branch

    @staticmethod
    def validate_remote_push(source_branch: str, destination_branch: str) -> None:
        """Deny direct updates to governed integration and release branches."""
        GitLifecycleService._validate_branch_name(source_branch)
        GitLifecycleService._validate_branch_name(destination_branch)
        if destination_branch in _PROTECTED_REMOTE_BRANCHES:
            raise OperationDenied(
                "direct_push_prohibited",
                "governed target branches may advance only through a pull request",
                destination_branch=destination_branch,
            )
        if source_branch != destination_branch:
            raise OperationDenied(
                "remote_ref_rewrite_prohibited",
                "remote publication may update only the source branch's same-name ref",
                source_branch=source_branch,
                destination_branch=destination_branch,
            )

    def create_work_item_branch(
        self,
        *,
        work_item_id: str,
        title: str,
        project_branch: str,
        operation_id: str | None = None,
        ttl_seconds: float = 120.0,
        wait_seconds: float = 30.0,
        crash_hook: CrashHook | None = None,
    ) -> OperationResult:
        """Create and select one deterministic work-item branch."""
        branch = deterministic_work_branch(work_item_id, title)
        self._validate_branch_name(project_branch, expected_prefix="project/")
        if not self.repo.branch_exists(project_branch):
            raise OperationDenied("project_branch_missing", "project branch does not exist")
        if not self.repo.is_clean():
            raise OperationDenied("branch_create_worktree_dirty", "branch creation requires a clean worktree")
        project_head = self.repo.head(project_branch)
        if self.repo.branch_exists(branch):
            if self.repo.head(branch) != project_head and not self.repo.is_ancestor(project_branch, branch):
                raise OperationDenied("branch_ancestry_invalid", "existing work-item branch has the wrong ancestry")
            if self.repo.current_branch() != branch:
                op_id = self._validate_operation_id(
                    operation_id or f"select-{work_item_id.lower()}-{project_head[:12]}"
                )
                self._acquire_quiescence(op_id, ttl_seconds, wait_seconds)
                try:
                    self._verify_quiescence_lease(op_id)
                    self.repo.checkout(branch)
                    self._verify_quiescence_lease(op_id)
                except Exception:
                    self._release_after_preflight_denial(op_id)
                    raise
                release_dispatcher_quiescence(self.dispatcher_state_dir, operation_id=op_id, now=self.clock())
            return OperationResult(
                operation="create",
                code="work_branch_already_exists",
                work_item_id=work_item_id,
                branch=branch,
                commit_sha=self.repo.head(branch),
                details={"project_branch": project_branch},
            )
        current = self.repo.current_branch()
        if current != project_branch:
            raise OperationDenied(
                "wrong_branch",
                "new work-item branches must be created while the project branch is selected",
                expected=project_branch,
                current=current,
            )
        op_id = self._validate_operation_id(operation_id or f"create-{work_item_id.lower()}-{project_head[:12]}")
        self._acquire_quiescence(op_id, ttl_seconds, wait_seconds)
        transaction = {
            "schema_version": 1,
            "operation": "create",
            "operation_id": op_id,
            "phase": "prepared",
            "work_item_id": work_item_id,
            "expected_branch": branch,
            "project_branch": project_branch,
            "before_head": project_head,
            "prepared_at": self._timestamp(),
        }
        self.state.save_transaction(op_id, transaction)
        try:
            self._verify_quiescence_lease(op_id)
            self.repo.create_branch(branch, project_head)
            self.repo.checkout(branch)
            self._verify_quiescence_lease(op_id)
        except Exception:
            self._release_after_preflight_denial(op_id)
            raise
        if crash_hook is not None:
            crash_hook(branch)
        transaction.update({"phase": "completed", "commit_sha": project_head, "completed_at": self._timestamp()})
        self.state.save_transaction(op_id, transaction)
        release_dispatcher_quiescence(self.dispatcher_state_dir, operation_id=op_id, now=self.clock())
        return OperationResult(
            operation="create",
            code="work_branch_created",
            work_item_id=work_item_id,
            branch=branch,
            commit_sha=project_head,
            details={"operation_id": op_id, "project_branch": project_branch},
        )

    def attach_work_item(
        self,
        *,
        work_item_id: str,
        title: str,
        project_branch: str,
        scope_paths: tuple[str, ...],
        required_checks: tuple[str, ...],
    ) -> OperationResult:
        """Attach the selected deterministic branch to its immutable lifecycle record."""
        return self.bind_work_item(
            work_item_id=work_item_id,
            title=title,
            project_branch=project_branch,
            scope_paths=scope_paths,
            required_checks=required_checks,
        )

    def _binding(self, work_item_id: str) -> tuple[dict[str, Any], int]:
        registry = self.state.load_registry()
        binding = registry["bindings"].get(work_item_id)
        if not isinstance(binding, dict):
            raise OperationDenied("binding_missing", "work item has no branch binding", work_item_id=work_item_id)
        if binding.get("record_hash") != _record_hash(binding):
            raise OperationDenied("binding_hash_mismatch", "branch binding record hash is not current")
        return binding, registry["generation"]

    def _assert_branch(self, expected: str) -> None:
        current = self.repo.current_branch()
        if current != expected:
            raise OperationDenied(
                "wrong_branch",
                "operation is not running on the branch bound for this lifecycle phase",
                expected=expected,
                current=current,
            )

    def show_binding(self, work_item_id: str) -> dict[str, Any]:
        binding, registry_generation = self._binding(work_item_id)
        return {**binding, "registry_generation": registry_generation}

    def validate_binding(self, work_item_id: str) -> OperationResult:
        binding, _ = self._binding(work_item_id)
        if not self.repo.branch_exists(binding["project_branch"]):
            raise OperationDenied("project_branch_missing", "bound project branch no longer exists")
        if not self.repo.branch_exists(binding["branch"]):
            raise OperationDenied("work_branch_missing", "bound work-item branch no longer exists")
        if not self.repo.is_ancestor(binding["project_branch"], binding["branch"]):
            raise OperationDenied("branch_ancestry_invalid", "work-item branch is not descended from project branch")
        return OperationResult(
            operation="validate",
            code="binding_valid",
            work_item_id=work_item_id,
            branch=binding["branch"],
            commit_sha=self.repo.head(binding["branch"]),
            details={
                "binding_id": binding["binding_id"],
                "lifecycle_state": binding["lifecycle_state"],
                "project_branch": binding["project_branch"],
            },
        )

    def close_work_item(self, *, work_item_id: str, operation_id: str | None = None) -> OperationResult:
        binding, _ = self._binding(work_item_id)
        self._assert_branch(binding["project_branch"])
        if binding.get("lifecycle_state") != "promoted" or not binding.get("promoted_commit"):
            raise OperationDenied("binding_not_promoted", "only a promoted work-item binding can close")
        op_id = self._validate_operation_id(operation_id or f"close-{work_item_id.lower()}-{binding['generation'] + 1}")
        updated = self._transition(
            work_item_id=work_item_id,
            expected_record_generation=binding["generation"],
            event_type="work_item_binding_closed",
            changes={"lifecycle_state": "closed", "closed_at": self._timestamp()},
            operation_id=op_id,
        )
        return OperationResult(
            operation="close",
            code="binding_closed",
            work_item_id=work_item_id,
            branch=binding["project_branch"],
            commit_sha=binding["promoted_commit"],
            details={"operation_id": op_id, "generation": updated["generation"]},
        )

    def _transition(
        self,
        *,
        work_item_id: str,
        expected_record_generation: int,
        event_type: str,
        changes: dict[str, Any],
        operation_id: str,
    ) -> dict[str, Any]:
        with self.state.lock():
            registry = self.state.load_registry()
            binding = registry["bindings"].get(work_item_id)
            if not isinstance(binding, dict):
                raise OperationDenied("binding_missing", "binding disappeared during operation")
            if binding.get("generation") != expected_record_generation:
                raise OperationDenied(
                    "binding_generation_changed",
                    "binding changed concurrently; operation cannot overwrite current state",
                    expected=expected_record_generation,
                    current=binding.get("generation"),
                )
            updated = {**binding, **changes, "generation": expected_record_generation + 1}
            updated["record_hash"] = _record_hash(updated)
            registry["bindings"][work_item_id] = updated
            registry["generation"] += 1
            self.state.commit_registry_and_audit(
                registry,
                {
                    "event_type": event_type,
                    "operation_id": operation_id,
                    "occurred_at": self._timestamp(),
                    "registry_generation": registry["generation"],
                    "record_generation": updated["generation"],
                    "record_hash": updated["record_hash"],
                    "work_item_id": work_item_id,
                },
                operation_id=operation_id,
            )
            return updated

    def bind_work_item(
        self,
        *,
        work_item_id: str,
        title: str,
        project_branch: str,
        scope_paths: tuple[str, ...],
        required_checks: tuple[str, ...],
    ) -> OperationResult:
        branch = deterministic_work_branch(work_item_id, title)
        self._assert_branch(branch)
        if not project_branch.startswith("project/") or not self.repo.branch_exists(project_branch):
            raise OperationDenied("project_branch_invalid", "bound project branch is missing or non-canonical")
        if not self.repo.is_ancestor(project_branch, "HEAD"):
            raise OperationDenied(
                "branch_ancestry_invalid",
                "work-item branch is not descended from its project branch",
            )
        scope = tuple(sorted({normalize_repo_path(self.repo.root, path) for path in scope_paths}))
        checks = tuple(sorted({item.strip() for item in required_checks if item.strip()}))
        if not scope:
            raise OperationDenied("scope_empty", "branch binding requires at least one attributable scope path")
        if not checks:
            raise OperationDenied("required_checks_empty", "branch binding requires objective promotion checks")
        with self.state.lock():
            registry = self.state.load_registry()
            existing = registry["bindings"].get(work_item_id)
            immutable = {
                "work_item_id": work_item_id,
                "title": title,
                "branch": branch,
                "project_branch": project_branch,
                "scope_paths": list(scope),
                "required_checks": list(checks),
            }
            if isinstance(existing, dict):
                if all(existing.get(key) == value for key, value in immutable.items()):
                    return OperationResult(
                        operation="bind",
                        code="binding_already_current",
                        work_item_id=work_item_id,
                        branch=branch,
                        details={"binding_id": existing["binding_id"], "generation": existing["generation"]},
                    )
                raise OperationDenied("binding_conflict", "work item already has a different immutable binding")
            collision = next(
                (
                    item_id
                    for item_id, item in registry["bindings"].items()
                    if isinstance(item, dict) and item.get("branch") == branch
                ),
                None,
            )
            if collision is not None:
                raise OperationDenied(
                    "branch_collision",
                    "deterministic branch is already bound",
                    other_work_item=collision,
                )
            binding_id = "BIND-" + hashlib.sha256(canonical_json(immutable).encode("ascii")).hexdigest()[:16].upper()
            record: dict[str, Any] = {
                **immutable,
                "binding_id": binding_id,
                "base_commit": self.repo.head(project_branch),
                "created_at": self._timestamp(),
                "generation": 1,
                "lifecycle_state": "active",
                "preserved_commit": None,
                "promoted_commit": None,
            }
            record["record_hash"] = _record_hash(record)
            registry["bindings"][work_item_id] = record
            registry["generation"] += 1
            self.state.commit_registry_and_audit(
                registry,
                {
                    "event_type": "binding_created",
                    "operation_id": f"bind-{work_item_id.lower()}",
                    "occurred_at": self._timestamp(),
                    "record_generation": 1,
                    "record_hash": record["record_hash"],
                    "registry_generation": registry["generation"],
                    "work_item_id": work_item_id,
                },
                operation_id=f"bind-{work_item_id.lower()}",
            )
        return OperationResult(
            operation="bind",
            code="binding_created",
            work_item_id=work_item_id,
            branch=branch,
            details={"binding_id": binding_id, "generation": 1},
        )

    def _acquire_quiescence(self, operation_id: str, ttl_seconds: float, wait_seconds: float) -> None:
        acquire_dispatcher_quiescence(
            self.dispatcher_state_dir,
            operation_id=operation_id,
            ttl_seconds=ttl_seconds,
            wait_seconds=wait_seconds,
            clock=self.clock,
            sleep=self.sleep,
            worker_probe=self.worker_probe,
        )

    def _verify_quiescence_lease(self, operation_id: str) -> dict[str, Any]:
        try:
            marker = verify_dispatcher_quiescence(
                self.dispatcher_state_dir,
                operation_id=operation_id,
                now=self.clock(),
            )
            probe = self.worker_probe or (
                lambda: active_dispatcher_workers(self.dispatcher_state_dir, now=self.clock())
            )
            workers = probe()
            if not isinstance(workers, int) or isinstance(workers, bool) or workers != 0:
                raise OperationDenied(
                    "quiescence_not_ready",
                    "dispatcher gained an inflight worker after drain acquisition",
                    observed_workers=workers,
                )
            return marker
        except OperationDenied as exc:
            raise OperationDenied(
                "quiescence_lease_lost",
                "dispatcher quiescence ownership was lost before lifecycle completion",
                cause=exc.code,
                operation_id=operation_id,
            ) from exc

    def _verify_operation_guard(
        self,
        *,
        operation_id: str,
        authority: dict[str, Any],
        work_item_id: str | None = None,
        project_id: str | None = None,
        required_paths: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        """Revalidate drain and canonical authority at one Git-effect boundary."""
        marker = self._verify_quiescence_lease(operation_id)
        current = self._current_authority(
            bridge_id=authority["bridge_id"],
            work_item_id=work_item_id,
            project_id=project_id,
            required_paths=required_paths,
        )
        if current["binding_hash"] != authority["binding_hash"]:
            raise OperationDenied(
                "authorization_evidence_stale",
                "PAUTH, claim, or implementation-start evidence changed at the Git-effect boundary",
                operation_id=operation_id,
            )
        return marker

    @staticmethod
    def _json_hash(payload: dict[str, Any], *, excluded: frozenset[str] = frozenset()) -> str:
        return (
            hashlib.sha256(
                json.dumps(
                    {key: value for key, value in payload.items() if key not in excluded},
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("utf-8")
            )
            .hexdigest()
            .upper()
        )

    @staticmethod
    def _parse_utc(value: Any, *, label: str) -> datetime:
        if not isinstance(value, str) or not value.strip():
            raise OperationDenied("authority_evidence_invalid", f"{label} is missing or malformed")
        try:
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError as exc:
            raise OperationDenied("authority_evidence_invalid", f"{label} is malformed") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    @staticmethod
    def _json_list(value: Any, *, label: str, optional: bool = False) -> list[str]:
        if value is None and optional:
            return []
        try:
            parsed = json.loads(value) if isinstance(value, str) else value
        except json.JSONDecodeError as exc:
            raise OperationDenied("authority_evidence_invalid", f"{label} is malformed") from exc
        if not isinstance(parsed, list) or any(not isinstance(item, str) or not item for item in parsed):
            raise OperationDenied("authority_evidence_invalid", f"{label} is malformed")
        return parsed

    def _groundtruth_db_path(self) -> Path:
        config_path = self.repo.root / "groundtruth.toml"
        if not config_path.is_file():
            return self.repo.root / "groundtruth.db"
        try:
            config = tomllib.loads(config_path.read_text(encoding="utf-8"))
            configured = config.get("groundtruth", {}).get("db_path")
        except (OSError, tomllib.TOMLDecodeError, AttributeError) as exc:
            raise OperationDenied("authority_store_unavailable", "groundtruth.toml is unreadable") from exc
        if not isinstance(configured, str) or not configured.strip():
            return self.repo.root / "groundtruth.db"
        candidate = Path(configured)
        return candidate.resolve() if candidate.is_absolute() else (self.repo.root / candidate).resolve()

    @staticmethod
    def _target_authorizes(path: str, targets: tuple[str, ...]) -> bool:
        return any(
            path == target
            or (target.endswith("/**") and path.startswith(target[:-3].rstrip("/") + "/"))
            or path.startswith(target.rstrip("/") + "/")
            for target in targets
        )

    def _authority_packet(self, bridge_id: str) -> tuple[dict[str, Any], Path]:
        if not _BRIDGE_ID.fullmatch(bridge_id):
            raise OperationDenied("authority_bridge_id_invalid", "authority bridge id is unsafe")
        path = self.repo.root / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{bridge_id}.json"
        try:
            packet = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise OperationDenied(
                "implementation_start_missing", "named implementation-start packet is missing"
            ) from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise OperationDenied(
                "implementation_start_invalid", "named implementation-start packet is malformed"
            ) from exc
        if not isinstance(packet, dict) or packet.get("schema_version") != 3 or packet.get("bridge_id") != bridge_id:
            raise OperationDenied("implementation_start_invalid", "named implementation-start packet schema is invalid")
        expected_hash = "sha256:" + self._json_hash(packet, excluded=frozenset({"packet_hash"})).lower()
        if packet.get("packet_hash") != expected_hash:
            raise OperationDenied("implementation_start_invalid", "named implementation-start packet hash is invalid")
        if packet.get("latest_status") != "GO":
            raise OperationDenied("implementation_start_invalid", "implementation-start packet is not based on GO")
        return packet, path

    def _current_authority(
        self,
        *,
        bridge_id: str | None = None,
        work_item_id: str | None = None,
        project_id: str | None = None,
        required_paths: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        if bridge_id is None:
            packet_dir = self.repo.root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
            candidates: list[str] = []
            for path in sorted(packet_dir.glob("*.json")) if packet_dir.is_dir() else ():
                try:
                    candidate = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                pauth = candidate.get("project_authorization") if isinstance(candidate, dict) else None
                if not isinstance(pauth, dict):
                    continue
                if (
                    work_item_id is not None
                    and pauth.get("work_item_id") == work_item_id
                    or project_id is not None
                    and pauth.get("project_id") == project_id
                ):
                    candidates.append(path.stem)
            if len(candidates) != 1:
                raise OperationDenied(
                    "implementation_start_ambiguous" if candidates else "implementation_start_missing",
                    "exactly one current implementation-start packet must resolve the lifecycle subject",
                    candidates=candidates,
                )
            bridge_id = candidates[0]

        packet, packet_path = self._authority_packet(bridge_id)
        start = packet.get("implementation_start")
        embedded_pauth = packet.get("project_authorization")
        if not isinstance(start, dict) or start.get("schema_version") != 1 or not isinstance(embedded_pauth, dict):
            raise OperationDenied(
                "implementation_start_invalid", "implementation-start authority envelope is incomplete"
            )
        if start.get("bridge_id") != bridge_id:
            raise OperationDenied("implementation_start_invalid", "implementation-start bridge binding is inconsistent")
        session_id = start.get("session_id")
        provenance = start.get("worker_role_provenance")
        if (
            not isinstance(session_id, str)
            or not isinstance(provenance, dict)
            or provenance.get("role") != "prime-builder"
            or provenance.get("session_id") != session_id
        ):
            raise OperationDenied(
                "implementation_start_invalid", "implementation-start PB session provenance is invalid"
            )
        try:
            canonical_provenance = resolve_worker_role_provenance(
                self.repo.root,
                current_session_id=session_id,
                harness_name=provenance.get("harness_name"),
            )
        except EnvelopeError as exc:
            raise OperationDenied(
                "implementation_start_invalid",
                "implementation-start session provenance is absent or ambiguous in the canonical store",
            ) from exc
        if (
            canonical_provenance.get("role") != "prime-builder"
            or canonical_provenance.get("session_id") != session_id
            or canonical_provenance.get("harness_id") != provenance.get("harness_id")
        ):
            raise OperationDenied(
                "implementation_start_invalid",
                "implementation-start packet conflicts with canonical PB session provenance",
            )

        packet_targets = packet.get("target_path_globs")
        start_targets = start.get("target_path_globs")
        if (
            not isinstance(packet_targets, list)
            or any(not isinstance(item, str) for item in packet_targets)
            or start_targets != packet_targets
        ):
            raise OperationDenied("implementation_start_invalid", "implementation-start target binding is invalid")
        targets = tuple(packet_targets)
        uncovered = sorted(path for path in required_paths if not self._target_authorizes(path, targets))
        if uncovered:
            raise OperationDenied(
                "implementation_start_scope_mismatch",
                "implementation-start packet does not authorize the bound mutation scope",
                paths=uncovered,
            )

        go_file = packet.get("go_file")
        if not isinstance(go_file, str) or not go_file.startswith("bridge/"):
            raise OperationDenied("implementation_start_invalid", "implementation-start GO reference is invalid")
        go_path = self._evidence_path(go_file)
        go_lines = [line.strip() for line in go_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        if not go_lines or go_lines[0] != "GO":
            raise OperationDenied("implementation_start_invalid", "implementation-start GO reference is not GO")
        go_sha256 = self._file_sha256(go_path)
        latest_bridge_path, latest_bridge_lines = self._latest_bridge_entry(bridge_id)
        latest_bridge_status = latest_bridge_lines[0] if latest_bridge_lines else ""
        latest_bridge_version = self._bridge_version(latest_bridge_path, bridge_id)
        latest_bridge_file = latest_bridge_path.relative_to(self.repo.root).as_posix()
        latest_bridge_sha256 = self._file_sha256(latest_bridge_path)
        if latest_bridge_status == "GO":
            current_go_matches = (
                latest_bridge_file == go_file
                and latest_bridge_sha256 == go_sha256
                and latest_bridge_version is not None
            )
            if not current_go_matches:
                raise OperationDenied(
                    "implementation_start_superseded",
                    "current bridge GO does not exactly match the implementation-start packet",
                    bound_go_file=go_file,
                    current_bridge_file=latest_bridge_file,
                    current_bridge_sha256=latest_bridge_sha256,
                    current_bridge_version=latest_bridge_version,
                )
        elif latest_bridge_status != "VERIFIED" or latest_bridge_version is None:
            raise OperationDenied(
                "implementation_start_superseded",
                "current bridge entry supersedes the implementation-start GO",
                bound_go_file=go_file,
                current_bridge_file=latest_bridge_file,
                current_bridge_sha256=latest_bridge_sha256,
                current_bridge_status=latest_bridge_status,
                current_bridge_version=latest_bridge_version,
            )

        db_path = self._groundtruth_db_path()
        try:
            connection = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
            connection.row_factory = sqlite3.Row
            authorization_id = embedded_pauth.get("id")
            pauth_row = connection.execute(
                "SELECT * FROM current_project_authorizations WHERE id = ?", (authorization_id,)
            ).fetchone()
            claim_row = connection.execute(
                "SELECT * FROM work_intent_claims WHERE thread_slug = ?", (bridge_id,)
            ).fetchone()
        except sqlite3.Error as exc:
            raise OperationDenied("authority_store_unavailable", "canonical authority store cannot be read") from exc
        finally:
            if "connection" in locals():
                connection.close()
        if pauth_row is None or claim_row is None:
            raise OperationDenied("authority_evidence_missing", "current PAUTH or work-intent claim is missing")
        pauth = dict(pauth_row)
        claim = dict(claim_row)
        if (
            pauth.get("status") != "active"
            or embedded_pauth.get("id") != pauth.get("id")
            or embedded_pauth.get("version") != pauth.get("version")
            or embedded_pauth.get("project_id") != pauth.get("project_id")
        ):
            raise OperationDenied("project_authorization_inactive", "current PAUTH does not match the start packet")
        if project_id is not None and pauth.get("project_id") != project_id:
            raise OperationDenied("project_authorization_subject_mismatch", "PAUTH targets another project")
        included_work_items = self._json_list(
            pauth.get("included_work_item_ids"), label="PAUTH included_work_item_ids", optional=True
        )
        excluded_work_items = self._json_list(
            pauth.get("excluded_work_item_ids"), label="PAUTH excluded_work_item_ids", optional=True
        )
        if work_item_id is not None and (
            work_item_id in excluded_work_items
            or (included_work_items and work_item_id not in included_work_items)
            or embedded_pauth.get("work_item_id") != work_item_id
        ):
            raise OperationDenied("project_authorization_subject_mismatch", "PAUTH does not authorize this work item")
        expires_at = pauth.get("expires_at")
        now = datetime.fromtimestamp(self.clock(), tz=UTC)
        if expires_at and now >= self._parse_utc(expires_at, label="PAUTH expiry"):
            raise OperationDenied("project_authorization_inactive", "PAUTH is expired")
        packet_expires_at = packet.get("expires_at")
        if now >= self._parse_utc(packet_expires_at, label="implementation-start packet expiry"):
            raise OperationDenied("implementation_start_expired", "implementation-start packet is expired")
        forbidden = self._json_list(
            pauth.get("forbidden_operations"), label="PAUTH forbidden_operations", optional=True
        )
        if any(item in {"git_commit", "git_promotion", "git_lifecycle"} for item in forbidden):
            raise OperationDenied("project_authorization_operation_denied", "PAUTH forbids Git lifecycle mutation")

        embedded_claim = start.get("work_intent_claim")
        if not isinstance(embedded_claim, dict):
            raise OperationDenied("work_intent_claim_invalid", "start packet has no claim binding")
        if (
            claim.get("session_id") != session_id
            or claim.get("claim_kind") != "go_implementation"
            or claim.get("acting_role") != "prime-builder"
            or claim.get("project_id") != pauth.get("project_id")
            or embedded_claim.get("thread_slug") != bridge_id
            or embedded_claim.get("session_id") != session_id
            or embedded_claim.get("claim_kind") != "go_implementation"
        ):
            raise OperationDenied("work_intent_claim_invalid", "current claim does not match the PB start session")
        claim_expiry = claim.get("implementation_grace_expires_at") or claim.get("ttl_expires_at")
        if now >= self._parse_utc(claim_expiry, label="work-intent claim expiry"):
            raise OperationDenied("work_intent_claim_expired", "current work-intent claim is expired")
        decision = start.get("project_authorization_decision")
        if (
            not isinstance(decision, dict)
            or decision.get("allowed") is not True
            or decision.get("authorization_id") != pauth.get("id")
            or decision.get("authorization_version") != pauth.get("version")
            or decision.get("normalized_operation") != "implementation_start"
        ):
            raise OperationDenied("implementation_start_invalid", "operation-time PAUTH decision is invalid")

        authority_material = {
            "bridge_id": bridge_id,
            "packet_sha256": self._file_sha256(packet_path),
            "pauth": pauth,
            "claim": claim,
            "session_id": session_id,
            "session_provenance": canonical_provenance,
            "go_file": go_file,
            "go_sha256": go_sha256,
            "latest_bridge_file": latest_bridge_file,
            "latest_bridge_sha256": latest_bridge_sha256,
            "latest_bridge_status": latest_bridge_status,
            "latest_bridge_version": latest_bridge_version,
        }
        authority_material["binding_hash"] = sha256_json(authority_material)
        return authority_material

    def acquire_quiescence(
        self,
        *,
        operation_id: str,
        ttl_seconds: float,
        wait_seconds: float,
    ) -> dict[str, Any]:
        op_id = self._validate_operation_id(operation_id)
        return acquire_dispatcher_quiescence(
            self.dispatcher_state_dir,
            operation_id=op_id,
            ttl_seconds=ttl_seconds,
            wait_seconds=wait_seconds,
            clock=self.clock,
            sleep=self.sleep,
            worker_probe=self.worker_probe,
        )

    def verify_quiescence(self, *, operation_id: str) -> dict[str, Any]:
        return self._verify_quiescence_lease(self._validate_operation_id(operation_id))

    def release_quiescence(self, *, operation_id: str) -> dict[str, Any]:
        op_id = self._validate_operation_id(operation_id)
        release_dispatcher_quiescence(self.dispatcher_state_dir, operation_id=op_id, now=self.clock())
        return {"status": "PASS", "operation": "drain-release", "operation_id": op_id}

    def _release_after_preflight_denial(self, operation_id: str) -> None:
        # Concurrent marker corruption remains fail-closed for explicit recovery.
        with suppress(OperationDenied):
            release_dispatcher_quiescence(
                self.dispatcher_state_dir,
                operation_id=operation_id,
                now=self.clock(),
            )

    def _acquire_fresh_recovery_quiescence(self, operation_id: str) -> None:
        marker = self.dispatcher_state_dir / "dispatch-drain.json"
        if marker.exists():
            release_dispatcher_quiescence(
                self.dispatcher_state_dir,
                operation_id=operation_id,
                now=self.clock(),
                allow_expired=True,
            )
        self._acquire_quiescence(operation_id, 120.0, 30.0)

    def preserve_scoped_changes(
        self,
        *,
        work_item_id: str,
        message: str,
        operation_id: str | None = None,
        ttl_seconds: float = 120.0,
        wait_seconds: float = 30.0,
        crash_hook: CrashHook | None = None,
    ) -> OperationResult:
        binding, _ = self._binding(work_item_id)
        self._assert_branch(binding["branch"])
        scope = tuple(binding["scope_paths"])
        authority = self._current_authority(work_item_id=work_item_id, required_paths=scope)
        if self.repo.is_clean(scope):
            raise OperationDenied("scope_has_no_changes", "no attributable changes exist in the bound scope")
        initial_head = self.repo.head()
        op_id = self._validate_operation_id(
            operation_id or f"commit-{work_item_id.lower()}-{binding['generation'] + 1}-{initial_head[:12].lower()}"
        )
        self._acquire_quiescence(op_id, ttl_seconds, wait_seconds)
        try:
            self._assert_branch(binding["branch"])
            current_binding, _ = self._binding(work_item_id)
            if current_binding["record_hash"] != binding["record_hash"] or self.repo.head() != initial_head:
                raise OperationDenied(
                    "operation_inputs_changed",
                    "binding or Git head changed while dispatcher quiescence was acquired",
                )
            self._verify_operation_guard(
                operation_id=op_id,
                authority=authority,
                work_item_id=work_item_id,
                required_paths=scope,
            )
        except Exception:
            self._release_after_preflight_denial(op_id)
            raise
        before_head = initial_head
        transaction = {
            "schema_version": 1,
            "operation": "preserve",
            "operation_id": op_id,
            "phase": "prepared",
            "work_item_id": work_item_id,
            "expected_branch": binding["branch"],
            "before_head": before_head,
            "scope_paths": list(scope),
            "binding_generation": binding["generation"],
            "authority_bridge_id": authority["bridge_id"],
            "authority_binding_hash": authority["binding_hash"],
            "prepared_at": self._timestamp(),
        }
        self.state.save_transaction(op_id, transaction)
        self._verify_operation_guard(
            operation_id=op_id,
            authority=authority,
            work_item_id=work_item_id,
            required_paths=scope,
        )
        try:
            commit_sha = self.repo.scoped_commit(scope, message)
        except Exception:
            transaction["phase"] = "failed_before_commit"
            self.state.save_transaction(op_id, transaction)
            release_dispatcher_quiescence(
                self.dispatcher_state_dir,
                operation_id=op_id,
                now=self.clock(),
            )
            raise
        try:
            self._verify_operation_guard(
                operation_id=op_id,
                authority=authority,
                work_item_id=work_item_id,
                required_paths=scope,
            )
        except OperationDenied:
            transaction.update(
                {
                    "phase": "guard_lost_after_commit",
                    "commit_sha": commit_sha,
                    "recovery_authorized": False,
                }
            )
            self.state.save_transaction(op_id, transaction)
            self._release_after_preflight_denial(op_id)
            raise
        if crash_hook is not None:
            crash_hook(commit_sha)
        self._validate_preservation_effect(transaction, commit_sha)
        self._transition(
            work_item_id=work_item_id,
            expected_record_generation=binding["generation"],
            event_type="scoped_commit_preserved",
            changes={"lifecycle_state": "preserved", "preserved_commit": commit_sha},
            operation_id=op_id,
        )
        transaction.update({"phase": "completed", "commit_sha": commit_sha, "completed_at": self._timestamp()})
        self.state.save_transaction(op_id, transaction)
        release_dispatcher_quiescence(self.dispatcher_state_dir, operation_id=op_id, now=self.clock())
        return OperationResult(
            operation="preserve",
            code="scoped_commit_preserved",
            work_item_id=work_item_id,
            branch=binding["branch"],
            commit_sha=commit_sha,
            details={"committed_paths": list(self.repo.committed_paths(commit_sha)), "operation_id": op_id},
        )

    def _validate_preservation_effect(self, transaction: dict[str, Any], commit_sha: str) -> None:
        parents = self.repo.parents(commit_sha)
        if parents != (transaction["before_head"],):
            raise OperationDenied(
                "preservation_head_changed",
                "scoped commit does not have the prepared head as sole parent",
            )
        scope = tuple(transaction["scope_paths"])
        committed_paths = self.repo.committed_paths(commit_sha)
        if not committed_paths or any(not _path_is_within_scope(path, scope) for path in committed_paths):
            raise OperationDenied(
                "preservation_scope_violation",
                "commit contains a path outside the immutable binding scope",
                committed_paths=list(committed_paths),
            )

    @staticmethod
    def _file_sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest().upper()

    def _evidence_path(self, relative: str) -> Path:
        normalized = normalize_repo_path(self.repo.root, relative)
        path = (self.repo.root / normalized).resolve()
        if not path.is_file():
            raise OperationDenied(
                "evidence_artifact_missing", "promotion evidence artifact is missing", path=normalized
            )
        return path

    def _promotion_receipt_dir(self) -> Path:
        path = (self.state.state_dir / "promotion-receipts").resolve()
        try:
            path.relative_to(self.repo.root)
        except ValueError as exc:
            raise OperationDenied(
                "promotion_issuer_location_invalid",
                "trusted promotion receipts must live inside the exact repository root",
            ) from exc
        return path

    def _promotion_receipt_audit(self) -> Path:
        return self._promotion_receipt_dir() / "issuer-audit.jsonl"

    def _receipt_audit_events(self) -> list[dict[str, Any]]:
        path = self._promotion_receipt_audit()
        if not path.exists():
            return []
        try:
            lines = path.read_text(encoding="ascii").splitlines()
        except OSError as exc:
            raise OperationDenied("promotion_issuer_audit_invalid", "promotion issuer audit is unreadable") from exc
        events: list[dict[str, Any]] = []
        previous = "0" * 64
        for line in lines:
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise OperationDenied("promotion_issuer_audit_invalid", "promotion issuer audit is malformed") from exc
            if (
                not isinstance(event, dict)
                or event.get("previous_hash") != previous
                or event.get("event_hash")
                != sha256_json({key: value for key, value in event.items() if key != "event_hash"})
            ):
                raise OperationDenied("promotion_issuer_audit_invalid", "promotion issuer audit chain is invalid")
            previous = event["event_hash"]
            events.append(event)
        return events

    def _append_promotion_receipt(self, payload: dict[str, Any]) -> PromotionEvidence:
        receipt_dir = self._promotion_receipt_dir()
        receipt_dir.mkdir(parents=True, exist_ok=True)
        with self.state.lock():
            events = self._receipt_audit_events()
            sequence = (
                max(
                    len(events),
                    len(tuple(receipt_dir.glob("receipt-*.json"))),
                )
                + 1
            )
            payload = dict(payload)
            payload["schema_version"] = 2
            payload["issuer"] = {
                "id": _PROMOTION_RECEIPT_ISSUER,
                "version": 1,
                "issued_at": self._timestamp(),
                "sequence": sequence,
            }
            receipt_id = f"receipt-{sequence:06d}-{sha256_json(payload)[:12].lower()}"
            payload["receipt_id"] = receipt_id
            path = receipt_dir / f"{receipt_id}.json"
            data = canonical_json(payload) + "\n"
            try:
                with path.open("x", encoding="ascii", newline="\n") as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
            except FileExistsError as exc:
                raise OperationDenied(
                    "promotion_receipt_conflict", "append-only promotion receipt already exists"
                ) from exc
            relative = path.relative_to(self.repo.root).as_posix()
            receipt_sha256 = self._file_sha256(path)
            event = {
                "schema_version": 1,
                "issuer": _PROMOTION_RECEIPT_ISSUER,
                "sequence": sequence,
                "receipt_id": receipt_id,
                "receipt_path": relative,
                "receipt_sha256": receipt_sha256,
                "subject_commit": payload.get("subject_commit") or payload.get("source_commit"),
                "previous_hash": events[-1]["event_hash"] if events else "0" * 64,
            }
            event["event_hash"] = sha256_json(event)
            audit_path = self._promotion_receipt_audit()
            with audit_path.open("a", encoding="ascii", newline="\n") as handle:
                handle.write(canonical_json(event) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        return PromotionEvidence(bundle_path=relative, bundle_sha256=receipt_sha256)

    @staticmethod
    def _bridge_version(path: Path, bridge_id: str) -> int | None:
        if path.name == f"{bridge_id}.md":
            return 1
        match = re.fullmatch(rf"{re.escape(bridge_id)}-(\d{{3,}})\.md", path.name)
        return int(match.group(1)) if match else None

    def _latest_bridge_entry(self, bridge_id: str) -> tuple[Path, list[str]]:
        if not _BRIDGE_ID.fullmatch(bridge_id):
            raise OperationDenied("authority_bridge_id_invalid", "authority bridge id is unsafe")
        bridge_dir = self.repo.root / "bridge"
        candidates: list[tuple[int, Path]] = []
        for path in bridge_dir.glob(f"{bridge_id}*.md") if bridge_dir.is_dir() else ():
            version = self._bridge_version(path, bridge_id)
            if version is not None:
                candidates.append((version, path))
        if not candidates:
            raise OperationDenied("verification_missing", "canonical bridge verdict is missing")
        path = max(candidates, key=lambda item: item[0])[1]
        try:
            lines = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        except OSError as exc:
            raise OperationDenied("verification_missing", "canonical bridge verdict is unreadable") from exc
        return path, lines

    def _canonical_session_receipt(self, session_id: str, *, expected_role: str) -> dict[str, Any]:
        try:
            provenance = resolve_worker_role_provenance(
                self.repo.root,
                current_session_id=session_id,
            )
        except EnvelopeError as exc:
            raise OperationDenied(
                "verification_session_invalid",
                "verification session is absent or ambiguous in the canonical session store",
                session_id=session_id,
            ) from exc
        if provenance.get("role") != expected_role:
            raise OperationDenied(
                "verification_role_invalid",
                "canonical verification session has the wrong role",
                expected_role=expected_role,
                session_id=session_id,
            )
        harness_name = provenance.get("harness_name")
        if not isinstance(harness_name, str):
            raise OperationDenied("verification_session_invalid", "canonical session harness is missing")
        path = (self.repo.root / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json").resolve()
        try:
            path.relative_to(self.repo.root)
        except ValueError as exc:
            raise OperationDenied(
                "verification_session_invalid", "canonical session path escaped the repository"
            ) from exc
        if not path.is_file():
            raise OperationDenied("verification_session_invalid", "canonical session document is missing")
        return {
            "session_id": session_id,
            "role": expected_role,
            "harness_id": provenance["harness_id"],
            "harness_name": harness_name,
            "path": path.relative_to(self.repo.root).as_posix(),
            "sha256": self._file_sha256(path),
        }

    def _verified_verdict(
        self,
        *,
        bridge_id: str,
        authority: dict[str, Any],
        expected_fields: dict[str, str],
    ) -> dict[str, Any]:
        path, lines = self._latest_bridge_entry(bridge_id)
        if not lines or lines[0] != "VERIFIED":
            raise OperationDenied("verification_missing", "latest canonical bridge entry is not VERIFIED")
        fields: dict[str, str] = {}
        for line in lines[1:]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            if key in fields:
                raise OperationDenied("verification_malformed", "canonical VERIFIED metadata is duplicated", field=key)
            fields[key] = value.strip()
        author_session = authority["session_id"]
        verifier_session = fields.get("Verifier-Session")
        required = {
            **expected_fields,
            "Author-Session": author_session,
        }
        if any(fields.get(key) != value for key, value in required.items()):
            raise OperationDenied("verification_subject_mismatch", "canonical VERIFIED entry binds another subject")
        if fields.get("Author-Role") != "prime-builder" or fields.get("Verifier-Role") != "loyal-opposition":
            raise OperationDenied("verification_role_invalid", "canonical VERIFIED entry has invalid role provenance")
        if not isinstance(verifier_session, str) or not verifier_session or verifier_session == author_session:
            raise OperationDenied("verification_not_independent", "VERIFIED requires a distinct verifier session")
        if fields.get("author_session_context_id") != verifier_session:
            raise OperationDenied(
                "verification_session_mismatch",
                "canonical VERIFIED author metadata does not identify the verifier session",
            )
        author_receipt = self._canonical_session_receipt(author_session, expected_role="prime-builder")
        verifier_receipt = self._canonical_session_receipt(verifier_session, expected_role="loyal-opposition")
        return {
            "path": path.relative_to(self.repo.root).as_posix(),
            "sha256": self._file_sha256(path),
            "author_session": author_receipt,
            "verifier_session": verifier_receipt,
        }

    def issue_work_item_promotion_evidence(
        self,
        *,
        work_item_id: str,
        bridge_id: str,
        checks: dict[str, dict[str, Any]],
    ) -> PromotionEvidence:
        """Issue one append-only receipt from canonical authority and verdict stores."""
        binding, _ = self._binding(work_item_id)
        source_commit = binding.get("preserved_commit")
        if binding.get("lifecycle_state") != "preserved" or not isinstance(source_commit, str):
            raise OperationDenied("preserved_commit_missing", "promotion receipt requires a preserved work-item head")
        authority = self._current_authority(bridge_id=bridge_id, work_item_id=work_item_id)
        verdict = self._verified_verdict(
            bridge_id=bridge_id,
            authority=authority,
            expected_fields={
                "Subject-Commit": source_commit,
                "Work-Item": work_item_id,
                "Branch": binding["branch"],
            },
        )
        if set(checks) != set(binding["required_checks"]):
            raise OperationDenied("required_check_missing", "promotion receipt requires every bound check")
        normalized_checks: dict[str, dict[str, str]] = {}
        for check_id in sorted(checks):
            check = checks[check_id]
            if (
                not isinstance(check, dict)
                or check.get("status") != "PASS"
                or check.get("subject_commit") != source_commit
            ):
                raise OperationDenied("required_check_missing", "promotion check is non-passing or stale")
            normalized_checks[check_id] = {"status": "PASS", "subject_commit": source_commit}
        return self._append_promotion_receipt(
            {
                "receipt_kind": "work_item_promotion",
                "work_item_id": work_item_id,
                "branch": binding["branch"],
                "subject_commit": source_commit,
                "checks": normalized_checks,
                "authority_bridge_id": bridge_id,
                "authority_binding_hash": authority["binding_hash"],
                "authority_provenance": {
                    "packet_sha256": authority["packet_sha256"],
                    "pauth_id": authority["pauth"]["id"],
                    "pauth_version": authority["pauth"]["version"],
                    "claim_session": authority["claim"]["session_id"],
                    "start_session": authority["session_id"],
                },
                "verdict": verdict,
            }
        )

    def issue_branch_promotion_evidence(
        self,
        *,
        bridge_id: str,
        promotion_kind: str,
        subject_id: str,
        source_branch: str,
        target_branch: str,
        required_receipts: tuple[str, ...],
        receipts: dict[str, dict[str, Any]],
    ) -> PromotionEvidence:
        """Issue a branch-promotion receipt after resolving canonical provenance."""
        source_commit = self.repo.head(source_branch)
        target_commit = self.repo.head(target_branch)
        authority = self._current_authority(bridge_id=bridge_id)
        verdict = self._verified_verdict(
            bridge_id=bridge_id,
            authority=authority,
            expected_fields={
                "Promotion-Kind": promotion_kind,
                "Subject": subject_id,
                "Source-Branch": source_branch,
                "Target-Branch": target_branch,
                "Subject-Commit": source_commit,
                "Target-Commit": target_commit,
            },
        )
        if set(receipts) != set(required_receipts):
            raise OperationDenied("promotion_receipt_missing", "branch promotion receipts are incomplete")
        normalized: dict[str, dict[str, str]] = {}
        for receipt_id in sorted(receipts):
            receipt = receipts[receipt_id]
            if (
                not isinstance(receipt, dict)
                or receipt.get("status") != "PASS"
                or receipt.get("subject_commit") != source_commit
                or receipt.get("target_commit") != target_commit
            ):
                raise OperationDenied("promotion_receipt_missing", "branch promotion receipt is non-passing or stale")
            normalized[receipt_id] = {
                "status": "PASS",
                "subject_commit": source_commit,
                "target_commit": target_commit,
            }
        return self._append_promotion_receipt(
            {
                "receipt_kind": "branch_promotion",
                "promotion_kind": promotion_kind,
                "subject_id": subject_id,
                "source_branch": source_branch,
                "target_branch": target_branch,
                "source_commit": source_commit,
                "target_commit": target_commit,
                "receipts": normalized,
                "authority_bridge_id": bridge_id,
                "authority_binding_hash": authority["binding_hash"],
                "authority_provenance": {
                    "packet_sha256": authority["packet_sha256"],
                    "pauth_id": authority["pauth"]["id"],
                    "pauth_version": authority["pauth"]["version"],
                    "claim_session": authority["claim"]["session_id"],
                    "start_session": authority["session_id"],
                },
                "verdict": verdict,
            }
        )

    def _load_promotion_bundle(self, evidence: PromotionEvidence) -> dict[str, Any]:
        bundle_path = self._evidence_path(evidence.bundle_path)
        receipt_dir = self._promotion_receipt_dir()
        if bundle_path.parent != receipt_dir or not bundle_path.name.startswith("receipt-"):
            raise OperationDenied(
                "promotion_evidence_untrusted",
                "promotion evidence was not issued by the lifecycle append-only receipt store",
            )
        if self._file_sha256(bundle_path) != evidence.bundle_sha256.upper():
            raise OperationDenied("evidence_bundle_hash_mismatch", "promotion evidence bundle hash is not current")
        try:
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise OperationDenied("evidence_bundle_malformed", "promotion evidence bundle is malformed") from exc
        if (
            not isinstance(bundle, dict)
            or bundle.get("schema_version") != 2
            or not isinstance(bundle.get("issuer"), dict)
            or bundle["issuer"].get("id") != _PROMOTION_RECEIPT_ISSUER
            or bundle["issuer"].get("version") != 1
        ):
            raise OperationDenied("evidence_bundle_malformed", "promotion evidence bundle schema is invalid")
        relative = bundle_path.relative_to(self.repo.root).as_posix()
        matching_events = [
            event
            for event in self._receipt_audit_events()
            if event.get("receipt_id") == bundle.get("receipt_id")
            and event.get("receipt_path") == relative
            and event.get("receipt_sha256") == evidence.bundle_sha256.upper()
        ]
        if len(matching_events) != 1:
            raise OperationDenied(
                "promotion_evidence_untrusted",
                "promotion receipt is absent from the trusted append-only issuer audit",
            )
        bridge_id = bundle.get("authority_bridge_id")
        if not isinstance(bridge_id, str):
            raise OperationDenied("evidence_bundle_malformed", "promotion receipt authority binding is missing")
        authority = self._current_authority(
            bridge_id=bridge_id,
            work_item_id=bundle.get("work_item_id") if bundle.get("receipt_kind") == "work_item_promotion" else None,
        )
        if authority["binding_hash"] != bundle.get("authority_binding_hash"):
            raise OperationDenied("authorization_evidence_stale", "promotion receipt authority is no longer current")
        if bundle.get("receipt_kind") == "work_item_promotion":
            expected_fields = {
                "Subject-Commit": bundle.get("subject_commit"),
                "Work-Item": bundle.get("work_item_id"),
                "Branch": bundle.get("branch"),
            }
        elif bundle.get("receipt_kind") == "branch_promotion":
            expected_fields = {
                "Promotion-Kind": bundle.get("promotion_kind"),
                "Subject": bundle.get("subject_id"),
                "Source-Branch": bundle.get("source_branch"),
                "Target-Branch": bundle.get("target_branch"),
                "Subject-Commit": bundle.get("source_commit"),
                "Target-Commit": bundle.get("target_commit"),
            }
        else:
            raise OperationDenied("evidence_bundle_malformed", "promotion receipt kind is invalid")
        if any(not isinstance(value, str) for value in expected_fields.values()):
            raise OperationDenied("evidence_bundle_malformed", "promotion receipt subject binding is malformed")
        verdict = self._verified_verdict(
            bridge_id=bridge_id,
            authority=authority,
            expected_fields=expected_fields,
        )
        if verdict != bundle.get("verdict"):
            raise OperationDenied("verification_stale", "canonical VERIFIED provenance changed after receipt issuance")
        return bundle

    def _validate_promotion_evidence(
        self,
        binding: dict[str, Any],
        evidence: PromotionEvidence,
        source_commit: str,
    ) -> dict[str, Any]:
        bundle = self._load_promotion_bundle(evidence)
        if bundle.get("work_item_id") != binding["work_item_id"] or bundle.get("branch") != binding["branch"]:
            raise OperationDenied(
                "verification_subject_mismatch", "promotion evidence targets another work item or branch"
            )
        if bundle.get("subject_commit") != source_commit:
            raise OperationDenied("verification_stale", "verification does not bind the current work-item head")

        checks = bundle.get("checks")
        if not isinstance(checks, dict):
            raise OperationDenied("required_check_missing", "promotion required-check evidence is missing")
        for required in binding["required_checks"]:
            check = checks.get(required)
            if (
                not isinstance(check, dict)
                or check.get("status") != "PASS"
                or check.get("subject_commit") != source_commit
            ):
                raise OperationDenied(
                    "required_check_missing",
                    "promotion required check is missing, non-passing, or stale",
                    required_check=required,
                )
        return bundle

    def _promotion_authority(
        self,
        bundle: dict[str, Any],
        *,
        work_item_id: str | None = None,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        bridge_id = bundle.get("authority_bridge_id")
        if not isinstance(bridge_id, str):
            raise OperationDenied("evidence_bundle_malformed", "promotion authority bridge id is missing")
        authority = self._current_authority(
            bridge_id=bridge_id,
            work_item_id=work_item_id,
            project_id=project_id,
        )
        if authority["binding_hash"] != bundle.get("authority_binding_hash"):
            raise OperationDenied("authorization_evidence_stale", "promotion authority receipt is no longer current")
        return authority

    def _verify_transaction_authority(self, transaction: dict[str, Any]) -> dict[str, Any]:
        bridge_id = transaction.get("authority_bridge_id")
        binding_hash = transaction.get("authority_binding_hash")
        if not isinstance(bridge_id, str) or not isinstance(binding_hash, str):
            raise OperationDenied("authority_evidence_missing", "lifecycle transaction has no authority binding")
        operation = transaction.get("operation")
        work_item_id = transaction.get("work_item_id") if operation in {"preserve", "promote"} else None
        required_paths = tuple(transaction.get("scope_paths", ())) if operation == "preserve" else ()
        authority = self._current_authority(
            bridge_id=bridge_id,
            work_item_id=work_item_id if isinstance(work_item_id, str) else None,
            required_paths=required_paths,
        )
        if authority["binding_hash"] != binding_hash:
            raise OperationDenied("authorization_evidence_stale", "transaction authority is no longer current")
        return authority

    def _validate_branch_promotion_evidence(
        self,
        *,
        evidence: PromotionEvidence,
        promotion_kind: str,
        subject_id: str,
        source_branch: str,
        target_branch: str,
        source_commit: str,
        target_commit: str,
        required_receipts: tuple[str, ...],
    ) -> dict[str, Any]:
        bundle = self._load_promotion_bundle(evidence)
        expected = {
            "promotion_kind": promotion_kind,
            "subject_id": subject_id,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "source_commit": source_commit,
            "target_commit": target_commit,
        }
        mismatches = {key: value for key, value in expected.items() if bundle.get(key) != value}
        if mismatches:
            raise OperationDenied(
                "promotion_evidence_stale",
                "branch promotion evidence does not bind the current source and target",
                mismatches=sorted(mismatches),
            )
        receipts = bundle.get("receipts")
        if not isinstance(receipts, dict):
            raise OperationDenied("promotion_receipt_missing", "branch promotion receipts are missing")
        for receipt_id in required_receipts:
            receipt = receipts.get(receipt_id)
            if (
                not isinstance(receipt, dict)
                or receipt.get("status") != "PASS"
                or receipt.get("subject_commit") != source_commit
                or receipt.get("target_commit") != target_commit
            ):
                raise OperationDenied(
                    "promotion_receipt_missing",
                    "required branch promotion receipt is absent, non-passing, or stale",
                    receipt_id=receipt_id,
                )
        return bundle

    @staticmethod
    def _parse_json_output(result: CommandResult, *, label: str) -> Any:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise OperationDenied(
                "pull_request_response_malformed",
                "GitHub command returned malformed JSON",
                label=label,
            ) from exc

    def _run_hosted_command(
        self,
        *,
        operation_id: str,
        step: str,
        argv: Sequence[str],
        transaction: dict[str, Any],
    ) -> CommandResult:
        exact = tuple(str(item) for item in argv)
        authority = {
            "bridge_id": transaction.get("authority_bridge_id"),
            "binding_hash": transaction.get("authority_binding_hash"),
        }
        project_id = transaction.get("authority_project_id")
        if not isinstance(authority["bridge_id"], str) or not isinstance(authority["binding_hash"], str):
            raise OperationDenied("authority_evidence_missing", "hosted promotion transaction has no authority binding")
        transaction.update({"phase": f"before_{step}", "next_command": list(exact)})
        self.state.save_transaction(operation_id, transaction)
        self._verify_operation_guard(
            operation_id=operation_id,
            authority=authority,
            project_id=project_id if isinstance(project_id, str) else None,
        )
        result = self.command_boundary.run(exact, cwd=self.repo.root)
        if result.argv != exact:
            transaction.update(
                {
                    "phase": "failed_command_boundary",
                    "next_command": None,
                    "recovery_authorized": False,
                }
            )
            self.state.save_transaction(operation_id, transaction)
            raise OperationDenied(
                "command_boundary_mismatch",
                "command boundary returned evidence for a different argument vector",
            )
        receipt = {
            "argv": list(exact),
            "returncode": result.returncode,
            "stdout_sha256": hashlib.sha256(result.stdout.encode("utf-8")).hexdigest().upper(),
            "stderr_sha256": hashlib.sha256(result.stderr.encode("utf-8")).hexdigest().upper(),
        }
        transaction.setdefault("command_receipts", []).append(receipt)
        try:
            self._verify_operation_guard(
                operation_id=operation_id,
                authority=authority,
                project_id=project_id if isinstance(project_id, str) else None,
            )
        except OperationDenied:
            transaction.update(
                {
                    "phase": f"lease_lost_after_{step}",
                    "next_command": None,
                    "recovery_authorized": False,
                }
            )
            self.state.save_transaction(operation_id, transaction)
            raise
        if result.returncode != 0:
            transaction.update(
                {
                    "phase": f"failed_{step}",
                    "next_command": None,
                    "recovery_authorized": False,
                }
            )
            self.state.save_transaction(operation_id, transaction)
            raise OperationDenied(
                "pull_request_command_failed",
                "hosted promotion command failed without advancing lifecycle evidence",
                command=list(exact),
                returncode=result.returncode,
                reason=(result.stderr or result.stdout).strip()[:500],
                step=step,
            )
        transaction.update({"phase": f"after_{step}", "next_command": None})
        self.state.save_transaction(operation_id, transaction)
        return result

    @staticmethod
    def _validate_pull_request(
        payload: Any,
        *,
        source_branch: str,
        target_branch: str,
        source_commit: str,
        target_commit: str,
        expected_body: str,
        required_checks: tuple[str, ...],
        require_merged: bool,
    ) -> tuple[str, str | None]:
        if not isinstance(payload, dict):
            raise OperationDenied("pull_request_response_malformed", "pull request response must be an object")
        url = payload.get("url")
        state = payload.get("state")
        if (
            not isinstance(url, str)
            or not _PULL_REQUEST_URL.fullmatch(url)
            or payload.get("headRefName") != source_branch
            or payload.get("baseRefName") != target_branch
            or payload.get("headRefOid") != source_commit
            or payload.get("body") != expected_body
            or state not in {"OPEN", "MERGED"}
        ):
            raise OperationDenied(
                "pull_request_subject_mismatch",
                "pull request does not bind the prepared source and target refs",
            )
        checks = payload.get("statusCheckRollup")
        if not isinstance(checks, list) or not checks:
            raise OperationDenied("pull_request_checks_missing", "pull request has no completed required checks")
        check_names = [check.get("name") if isinstance(check, dict) else None for check in checks]
        if (
            any(not isinstance(name, str) or not name for name in check_names)
            or len(check_names) != len(set(check_names))
            or set(check_names) != set(required_checks)
        ):
            raise OperationDenied(
                "pull_request_checks_mismatch",
                "pull request check set does not exactly match the prepared promotion contract",
                expected=sorted(required_checks),
                observed=sorted(name for name in check_names if isinstance(name, str)),
            )
        for check in checks:
            conclusion = check.get("conclusion") if isinstance(check, dict) else None
            if conclusion != "SUCCESS":
                raise OperationDenied("pull_request_checks_failed", "pull request required checks are not passing")
        merge_commit = payload.get("mergeCommit")
        merge_sha = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
        if not require_merged and payload.get("baseRefOid") != target_commit:
            raise OperationDenied(
                "pull_request_subject_mismatch",
                "open pull request base no longer matches the prepared target commit",
            )
        if require_merged and (state != "MERGED" or not isinstance(merge_sha, str) or not _COMMIT.fullmatch(merge_sha)):
            raise OperationDenied("pull_request_not_merged", "pull request did not produce a valid merge commit")
        return url, merge_sha

    def _validate_merged_commit_parents(
        self,
        *,
        transaction: dict[str, Any],
        pr_url: str,
        merge_sha: str,
    ) -> None:
        match = _PULL_REQUEST_URL.fullmatch(pr_url)
        if match is None:
            raise OperationDenied("pull_request_url_invalid", "pull request URL cannot identify its repository")
        path_parts = pr_url.removeprefix("https://github.com/").split("/")
        owner, repository = path_parts[0], path_parts[1]
        result = self._run_hosted_command(
            operation_id=transaction["operation_id"],
            step="merge_commit_view",
            argv=("gh", "api", f"repos/{owner}/{repository}/git/commits/{merge_sha}"),
            transaction=transaction,
        )
        payload = self._parse_json_output(result, label="merge_commit_view")
        if not isinstance(payload, dict):
            raise OperationDenied("pull_request_response_malformed", "merge commit response must be an object")
        parents = payload.get("parents")
        parent_shas = (
            [parent.get("sha") if isinstance(parent, dict) else None for parent in parents]
            if isinstance(parents, list)
            else []
        )
        expected_parents = [transaction["target_commit"], transaction["source_commit"]]
        if payload.get("sha") != merge_sha or parent_shas != expected_parents:
            raise OperationDenied(
                "pull_request_merge_parent_mismatch",
                "merged pull request is not the prepared target/source compare-and-swap result",
                expected_parents=expected_parents,
                observed_parents=parent_shas,
            )

    def _query_pull_requests(
        self,
        *,
        transaction: dict[str, Any],
        operation_id: str,
    ) -> list[dict[str, Any]]:
        result = self._run_hosted_command(
            operation_id=operation_id,
            step="pr_list",
            argv=(
                "gh",
                "pr",
                "list",
                "--head",
                transaction["source_branch"],
                "--base",
                transaction["target_branch"],
                "--state",
                "all",
                "--json",
                "url,state,body,headRefName,baseRefName,headRefOid,baseRefOid,mergeCommit,statusCheckRollup",
            ),
            transaction=transaction,
        )
        payload = self._parse_json_output(result, label="pr_list")
        if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
            raise OperationDenied("pull_request_response_malformed", "pull request list response is malformed")
        matching = [
            item
            for item in payload
            if item.get("headRefName") == transaction["source_branch"]
            and item.get("baseRefName") == transaction["target_branch"]
            and item.get("headRefOid") == transaction["source_commit"]
        ]
        if len(matching) > 1:
            raise OperationDenied("pull_request_ambiguous", "multiple pull requests match the immutable source commit")
        return matching

    def _continue_pull_request_promotion(self, transaction: dict[str, Any]) -> OperationResult:
        op_id = transaction["operation_id"]
        source_branch = transaction["source_branch"]
        target_branch = transaction["target_branch"]
        source_commit = transaction["source_commit"]
        target_commit = transaction["target_commit"]
        if transaction["promotion_kind"] == "project_to_develop":
            self.validate_remote_push(source_branch, source_branch)
            self._run_hosted_command(
                operation_id=op_id,
                step="publish_source",
                argv=("git", "push", "--set-upstream", "origin", f"{source_branch}:{source_branch}"),
                transaction=transaction,
            )
        matches = self._query_pull_requests(transaction=transaction, operation_id=op_id)
        if matches:
            pr_url = matches[0].get("url")
        else:
            created = self._run_hosted_command(
                operation_id=op_id,
                step="pr_create",
                argv=(
                    "gh",
                    "pr",
                    "create",
                    "--head",
                    source_branch,
                    "--base",
                    target_branch,
                    "--title",
                    transaction["title"],
                    "--body",
                    transaction["pr_body"],
                ),
                transaction=transaction,
            )
            pr_url = created.stdout.strip()
        if not isinstance(pr_url, str) or not _PULL_REQUEST_URL.fullmatch(pr_url):
            raise OperationDenied("pull_request_url_invalid", "GitHub did not return a canonical pull request URL")
        transaction["pr_url"] = pr_url
        self.state.save_transaction(op_id, transaction)
        viewed = self._run_hosted_command(
            operation_id=op_id,
            step="pr_view_before_merge",
            argv=(
                "gh",
                "pr",
                "view",
                pr_url,
                "--json",
                "url,state,body,headRefName,baseRefName,headRefOid,baseRefOid,mergeCommit,statusCheckRollup",
            ),
            transaction=transaction,
        )
        view_payload = self._parse_json_output(viewed, label="pr_view_before_merge")
        already_merged = view_payload.get("state") == "MERGED" if isinstance(view_payload, dict) else False
        _, merge_sha = self._validate_pull_request(
            view_payload,
            source_branch=source_branch,
            target_branch=target_branch,
            source_commit=source_commit,
            target_commit=target_commit,
            expected_body=transaction["pr_body"],
            required_checks=tuple(transaction.get("required_hosted_checks", transaction["required_receipts"])),
            require_merged=already_merged,
        )
        if view_payload["state"] != "MERGED":
            evidence = PromotionEvidence(**transaction["evidence"])
            self._validate_branch_promotion_evidence(
                evidence=evidence,
                promotion_kind=transaction["promotion_kind"],
                subject_id=transaction["subject_id"],
                source_branch=source_branch,
                target_branch=target_branch,
                source_commit=source_commit,
                target_commit=target_commit,
                required_receipts=tuple(transaction["required_receipts"]),
            )
            self._run_hosted_command(
                operation_id=op_id,
                step="pr_merge",
                argv=("gh", "pr", "merge", pr_url, "--merge", "--delete-branch=false"),
                transaction=transaction,
            )
            final = self._run_hosted_command(
                operation_id=op_id,
                step="pr_view_after_merge",
                argv=(
                    "gh",
                    "pr",
                    "view",
                    pr_url,
                    "--json",
                    "url,state,body,headRefName,baseRefName,headRefOid,baseRefOid,mergeCommit,statusCheckRollup",
                ),
                transaction=transaction,
            )
            view_payload = self._parse_json_output(final, label="pr_view_after_merge")
            _, merge_sha = self._validate_pull_request(
                view_payload,
                source_branch=source_branch,
                target_branch=target_branch,
                source_commit=source_commit,
                target_commit=target_commit,
                expected_body=transaction["pr_body"],
                required_checks=tuple(transaction.get("required_hosted_checks", transaction["required_receipts"])),
                require_merged=True,
            )
        elif merge_sha is None:
            _, merge_sha = self._validate_pull_request(
                view_payload,
                source_branch=source_branch,
                target_branch=target_branch,
                source_commit=source_commit,
                target_commit=target_commit,
                expected_body=transaction["pr_body"],
                required_checks=tuple(transaction.get("required_hosted_checks", transaction["required_receipts"])),
                require_merged=True,
            )
        if not isinstance(merge_sha, str):
            raise OperationDenied("pull_request_not_merged", "pull request completion has no merge commit")
        self._validate_merged_commit_parents(transaction=transaction, pr_url=pr_url, merge_sha=merge_sha)
        if transaction.get("completion_merge_commit") not in {None, merge_sha}:
            raise OperationDenied("pull_request_completion_conflict", "recovered merge commit changed")
        with self.state.lock():
            current = self.state.load_transaction(op_id)
            if current.get("phase") == "completed":
                if current.get("commit_sha") != merge_sha or current.get("pr_url") != pr_url:
                    raise OperationDenied("pull_request_completion_conflict", "completed promotion evidence changed")
                transaction = current
            else:
                completion_occurred_at = self._timestamp()
                transaction = {
                    **current,
                    "phase": "completed",
                    "completion_occurred_at": completion_occurred_at,
                    "completion_merge_commit": merge_sha,
                    "completed_at": completion_occurred_at,
                    "commit_sha": merge_sha,
                    "pr_url": pr_url,
                }
                event = {
                    "event_type": "pull_request_promotion_completed",
                    "operation_id": op_id,
                    "occurred_at": completion_occurred_at,
                    "promotion_kind": transaction["promotion_kind"],
                    "source_branch": source_branch,
                    "source_commit": source_commit,
                    "target_branch": target_branch,
                    "target_commit": target_commit,
                    "merge_commit": merge_sha,
                    "pr_url": pr_url,
                    "evidence_bundle_sha256": transaction["evidence"]["bundle_sha256"],
                }
                transaction = self.state.commit_transaction_and_audit(op_id, transaction, event)
        release_dispatcher_quiescence(self.dispatcher_state_dir, operation_id=op_id, now=self.clock())
        return OperationResult(
            operation="promote",
            code=f"{transaction['promotion_kind']}_completed",
            work_item_id=transaction["subject_id"],
            branch=target_branch,
            commit_sha=merge_sha,
            details={"operation_id": op_id, "pr_url": pr_url, "source_commit": source_commit},
        )

    def _promote_branch_via_pull_request(
        self,
        *,
        promotion_kind: str,
        subject_id: str,
        title: str,
        source_branch: str,
        target_branch: str,
        evidence: PromotionEvidence,
        required_receipts: tuple[str, ...],
        operation_id: str | None,
        ttl_seconds: float,
        wait_seconds: float,
    ) -> OperationResult:
        self._validate_branch_name(source_branch)
        self._validate_branch_name(target_branch)
        if self.repo.current_branch() != source_branch:
            raise OperationDenied("wrong_branch", "hosted promotion must run from its immutable source branch")
        if not self.repo.is_clean():
            raise OperationDenied("promotion_worktree_dirty", "hosted promotion requires a clean worktree")
        if not self.repo.branch_exists(target_branch) or not self.repo.is_ancestor(target_branch, source_branch):
            raise OperationDenied("promotion_ancestry_invalid", "target branch is not an ancestor of the source branch")
        source_commit = self.repo.head(source_branch)
        target_commit = self.repo.head(target_branch)
        bundle = self._validate_branch_promotion_evidence(
            evidence=evidence,
            promotion_kind=promotion_kind,
            subject_id=subject_id,
            source_branch=source_branch,
            target_branch=target_branch,
            source_commit=source_commit,
            target_commit=target_commit,
            required_receipts=required_receipts,
        )
        authority_project_id = subject_id if promotion_kind == "project_to_develop" else None
        authority = self._promotion_authority(bundle, project_id=authority_project_id)
        op_id = self._validate_operation_id(
            operation_id or f"pr-{promotion_kind.replace('_', '-')}-{source_commit[:12].lower()}"
        )
        self._acquire_quiescence(op_id, ttl_seconds, wait_seconds)
        try:
            if (
                self.repo.current_branch() != source_branch
                or self.repo.head(source_branch) != source_commit
                or self.repo.head(target_branch) != target_commit
                or not self.repo.is_clean()
            ):
                raise OperationDenied("promotion_state_changed", "hosted promotion inputs changed during drain")
            self._validate_branch_promotion_evidence(
                evidence=evidence,
                promotion_kind=promotion_kind,
                subject_id=subject_id,
                source_branch=source_branch,
                target_branch=target_branch,
                source_commit=source_commit,
                target_commit=target_commit,
                required_receipts=required_receipts,
            )
            self._verify_operation_guard(
                operation_id=op_id,
                authority=authority,
                project_id=authority_project_id,
            )
        except Exception:
            self._release_after_preflight_denial(op_id)
            raise
        transaction = {
            "schema_version": 1,
            "operation": "pull_request_promotion",
            "operation_id": op_id,
            "phase": "prepared",
            "promotion_kind": promotion_kind,
            "subject_id": subject_id,
            "title": title,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "source_commit": source_commit,
            "target_commit": target_commit,
            "required_receipts": list(required_receipts),
            "required_hosted_checks": list(required_receipts),
            "authority_bridge_id": authority["bridge_id"],
            "authority_binding_hash": authority["binding_hash"],
            "authority_project_id": authority_project_id,
            "evidence": {
                "bundle_path": evidence.bundle_path,
                "bundle_sha256": evidence.bundle_sha256.upper(),
            },
            "prepared_at": self._timestamp(),
            "command_receipts": [],
        }
        transaction["pr_body"] = "GT-KB-Promotion: " + canonical_json(
            {
                "evidence_sha256": transaction["evidence"]["bundle_sha256"],
                "operation_id": op_id,
                "source_commit": source_commit,
                "target_commit": target_commit,
            }
        )
        self.state.save_transaction(op_id, transaction)
        try:
            return self._continue_pull_request_promotion(transaction)
        except OperationDenied:
            phase = str(transaction.get("phase", ""))
            if not (phase.startswith("failed_") or phase.startswith("lease_lost_after_")):
                transaction.update(
                    {
                        "phase": "failed_hosted_validation",
                        "recovery_authorized": False,
                    }
                )
                self.state.save_transaction(op_id, transaction)
            self._release_after_preflight_denial(op_id)
            raise
        except Exception:
            self._release_after_preflight_denial(op_id)
            raise

    def promote_project_to_develop(
        self,
        *,
        project_id: str,
        project_branch: str,
        evidence: PromotionEvidence,
        operation_id: str | None = None,
        ttl_seconds: float = 120.0,
        wait_seconds: float = 30.0,
    ) -> OperationResult:
        self._validate_branch_name(project_branch, expected_prefix="project/")
        return self._promote_branch_via_pull_request(
            promotion_kind="project_to_develop",
            subject_id=project_id,
            title=f"promote({project_id}): project to develop",
            source_branch=project_branch,
            target_branch="develop",
            evidence=evidence,
            required_receipts=("verification",),
            operation_id=operation_id,
            ttl_seconds=ttl_seconds,
            wait_seconds=wait_seconds,
        )

    def promote_develop_to_stage(
        self,
        *,
        release_id: str,
        evidence: PromotionEvidence,
        operation_id: str | None = None,
        ttl_seconds: float = 120.0,
        wait_seconds: float = 30.0,
    ) -> OperationResult:
        return self._promote_branch_via_pull_request(
            promotion_kind="develop_to_stage",
            subject_id=release_id,
            title=f"promote({release_id}): develop to stage",
            source_branch="develop",
            target_branch="stage",
            evidence=evidence,
            required_receipts=("integration", "non-impairment"),
            operation_id=operation_id,
            ttl_seconds=ttl_seconds,
            wait_seconds=wait_seconds,
        )

    def promote_work_item(
        self,
        *,
        work_item_id: str,
        evidence: PromotionEvidence,
        operation_id: str | None = None,
        ttl_seconds: float = 120.0,
        wait_seconds: float = 30.0,
        crash_hook: CrashHook | None = None,
    ) -> OperationResult:
        binding, _ = self._binding(work_item_id)
        self._assert_branch(binding["project_branch"])
        source_commit = binding.get("preserved_commit")
        if binding.get("lifecycle_state") != "preserved" or not isinstance(source_commit, str):
            raise OperationDenied("preserved_commit_missing", "promotion requires a completed scoped preservation")
        if self.repo.head(binding["branch"]) != source_commit:
            raise OperationDenied("work_branch_advanced", "work-item branch changed after preservation")
        if not self.repo.is_clean():
            raise OperationDenied("promotion_worktree_dirty", "promotion requires a clean target worktree")
        bundle = self._validate_promotion_evidence(binding, evidence, source_commit)
        authority = self._promotion_authority(bundle, work_item_id=work_item_id)
        initial_target_head = self.repo.head()
        op_id = self._validate_operation_id(
            operation_id or f"promote-{work_item_id.lower()}-{binding['generation'] + 1}-{source_commit[:12].lower()}"
        )
        self._acquire_quiescence(op_id, ttl_seconds, wait_seconds)
        try:
            self._assert_branch(binding["project_branch"])
            current_binding, _ = self._binding(work_item_id)
            if (
                not self.repo.is_clean()
                or self.repo.head() != initial_target_head
                or self.repo.head(binding["branch"]) != source_commit
                or current_binding["record_hash"] != binding["record_hash"]
            ):
                raise OperationDenied("promotion_state_changed", "promotion inputs changed after quiescence")
            self._validate_promotion_evidence(binding, evidence, source_commit)
            self._verify_operation_guard(
                operation_id=op_id,
                authority=authority,
                work_item_id=work_item_id,
            )
        except Exception:
            self._release_after_preflight_denial(op_id)
            raise
        before_head = initial_target_head
        transaction = {
            "schema_version": 1,
            "operation": "promote",
            "operation_id": op_id,
            "phase": "prepared",
            "work_item_id": work_item_id,
            "expected_branch": binding["project_branch"],
            "before_head": before_head,
            "source_commit": source_commit,
            "source_branch": binding["branch"],
            "binding_generation": binding["generation"],
            "authority_bridge_id": authority["bridge_id"],
            "authority_binding_hash": authority["binding_hash"],
            "prepared_at": self._timestamp(),
        }
        self.state.save_transaction(op_id, transaction)
        self._verify_operation_guard(
            operation_id=op_id,
            authority=authority,
            work_item_id=work_item_id,
        )
        try:
            commit_sha = self.repo.merge_no_ff(
                binding["branch"],
                f"promote({work_item_id}): verified work item",
            )
        except Exception:
            transaction["phase"] = "failed_before_commit"
            self.state.save_transaction(op_id, transaction)
            release_dispatcher_quiescence(self.dispatcher_state_dir, operation_id=op_id, now=self.clock())
            raise
        try:
            self._verify_operation_guard(
                operation_id=op_id,
                authority=authority,
                work_item_id=work_item_id,
            )
        except OperationDenied:
            transaction.update(
                {
                    "phase": "guard_lost_after_commit",
                    "commit_sha": commit_sha,
                    "recovery_authorized": False,
                }
            )
            self.state.save_transaction(op_id, transaction)
            self._release_after_preflight_denial(op_id)
            raise
        if crash_hook is not None:
            crash_hook(commit_sha)
        self._validate_promotion_effect(transaction, commit_sha)
        self._transition(
            work_item_id=work_item_id,
            expected_record_generation=binding["generation"],
            event_type="work_item_promoted",
            changes={"lifecycle_state": "promoted", "promoted_commit": commit_sha},
            operation_id=op_id,
        )
        transaction.update({"phase": "completed", "commit_sha": commit_sha, "completed_at": self._timestamp()})
        self.state.save_transaction(op_id, transaction)
        release_dispatcher_quiescence(self.dispatcher_state_dir, operation_id=op_id, now=self.clock())
        return OperationResult(
            operation="promote",
            code="work_item_promoted",
            work_item_id=work_item_id,
            branch=binding["project_branch"],
            commit_sha=commit_sha,
            details={"operation_id": op_id, "source_commit": source_commit},
        )

    def _validate_promotion_effect(self, transaction: dict[str, Any], commit_sha: str) -> None:
        if self.repo.parents(commit_sha) != (transaction["before_head"], transaction["source_commit"]):
            raise OperationDenied("promotion_effect_invalid", "promotion commit parents do not match prepared heads")

    def _resume_create_operation(self, transaction: dict[str, Any]) -> OperationResult:
        op_id = transaction["operation_id"]
        branch = transaction["expected_branch"]
        work_item_id = transaction["work_item_id"]
        if transaction.get("phase") == "completed":
            marker = self.dispatcher_state_dir / "dispatch-drain.json"
            if marker.exists():
                release_dispatcher_quiescence(
                    self.dispatcher_state_dir,
                    operation_id=op_id,
                    now=self.clock(),
                    allow_expired=True,
                )
            return OperationResult(
                operation="resume",
                code="operation_already_completed",
                work_item_id=work_item_id,
                branch=branch,
                commit_sha=transaction.get("commit_sha"),
                details={"operation_id": op_id},
            )
        if transaction.get("phase") != "prepared":
            raise OperationDenied("operation_not_resumable", "branch creation transaction is not resumable")
        if not self.repo.branch_exists(branch) or self.repo.head(branch) != transaction["before_head"]:
            raise OperationDenied("create_effect_unprovable", "prepared branch creation effect cannot be proven")
        if not self.repo.is_clean():
            raise OperationDenied("branch_create_worktree_dirty", "branch creation recovery requires a clean worktree")
        self._acquire_fresh_recovery_quiescence(op_id)
        try:
            if (
                not self.repo.branch_exists(branch)
                or self.repo.head(branch) != transaction["before_head"]
                or not self.repo.is_clean()
            ):
                raise OperationDenied("create_effect_unprovable", "branch creation recovery inputs changed")
            self.repo.checkout(branch)
            transaction.update(
                {"phase": "completed", "commit_sha": transaction["before_head"], "completed_at": self._timestamp()}
            )
            self.state.save_transaction(op_id, transaction)
        except Exception:
            self._release_after_preflight_denial(op_id)
            raise
        release_dispatcher_quiescence(self.dispatcher_state_dir, operation_id=op_id, now=self.clock())
        return OperationResult(
            operation="resume",
            code="create_recovered",
            work_item_id=work_item_id,
            branch=branch,
            commit_sha=transaction["before_head"],
            details={"operation_id": op_id},
        )

    def _resume_pull_request_operation(self, transaction: dict[str, Any]) -> OperationResult:
        op_id = transaction["operation_id"]
        if transaction.get("phase") == "completed":
            marker = self.dispatcher_state_dir / "dispatch-drain.json"
            if marker.exists():
                release_dispatcher_quiescence(
                    self.dispatcher_state_dir,
                    operation_id=op_id,
                    now=self.clock(),
                    allow_expired=True,
                )
            return OperationResult(
                operation="resume",
                code="operation_already_completed",
                work_item_id=transaction["subject_id"],
                branch=transaction["target_branch"],
                commit_sha=transaction.get("commit_sha"),
                details={"operation_id": op_id, "pr_url": transaction.get("pr_url")},
            )
        phase = str(transaction.get("phase", ""))
        if (phase.startswith("failed_") or phase.startswith("lease_lost_after_")) and not transaction.get(
            "recovery_authorized"
        ):
            raise OperationDenied(
                "explicit_recovery_required",
                "failed or lease-lost hosted promotion requires an explicit recovery record",
            )
        source_branch = transaction["source_branch"]
        target_branch = transaction["target_branch"]
        if (
            self.repo.current_branch() != source_branch
            or self.repo.head(source_branch) != transaction["source_commit"]
            or self.repo.head(target_branch) != transaction["target_commit"]
            or not self.repo.is_clean()
        ):
            raise OperationDenied("promotion_state_changed", "hosted promotion recovery inputs changed")
        evidence = PromotionEvidence(**transaction["evidence"])
        self._validate_branch_promotion_evidence(
            evidence=evidence,
            promotion_kind=transaction["promotion_kind"],
            subject_id=transaction["subject_id"],
            source_branch=source_branch,
            target_branch=target_branch,
            source_commit=transaction["source_commit"],
            target_commit=transaction["target_commit"],
            required_receipts=tuple(transaction["required_receipts"]),
        )
        self._acquire_quiescence(op_id, 120.0, 30.0)
        try:
            return self._continue_pull_request_promotion(transaction)
        except OperationDenied:
            phase = str(transaction.get("phase", ""))
            if not (phase.startswith("failed_") or phase.startswith("lease_lost_after_")):
                transaction.update(
                    {
                        "phase": "failed_hosted_validation",
                        "recovery_authorized": False,
                    }
                )
                self.state.save_transaction(op_id, transaction)
            self._release_after_preflight_denial(op_id)
            raise
        except Exception:
            self._release_after_preflight_denial(op_id)
            raise

    def resume_operation(self, operation_id: str) -> OperationResult:
        """Finalize a prepared transaction only when its exact Git effect is provable."""
        op_id = self._validate_operation_id(operation_id)
        with self.state.lock():
            transaction = self.state.load_transaction(op_id)
        operation = transaction.get("operation")
        if operation == "create":
            return self._resume_create_operation(transaction)
        if operation == "pull_request_promotion":
            return self._resume_pull_request_operation(transaction)
        if transaction.get("phase") == "completed":
            binding, _ = self._binding(transaction["work_item_id"])
            marker = self.dispatcher_state_dir / "dispatch-drain.json"
            if marker.exists():
                release_dispatcher_quiescence(
                    self.dispatcher_state_dir,
                    operation_id=op_id,
                    now=self.clock(),
                    allow_expired=True,
                )
            return OperationResult(
                operation="resume",
                code="operation_already_completed",
                work_item_id=transaction["work_item_id"],
                branch=transaction["expected_branch"],
                commit_sha=transaction.get("commit_sha"),
                details={"lifecycle_state": binding["lifecycle_state"], "operation_id": op_id},
            )
        if transaction.get("phase") != "prepared":
            raise OperationDenied("operation_not_resumable", "transaction is not in a resumable prepared state")
        work_item_id = transaction["work_item_id"]
        binding, _ = self._binding(work_item_id)
        self._assert_branch(transaction["expected_branch"])
        commit_sha = self.repo.head()
        initial_already_applied = (
            operation == "preserve"
            and binding.get("lifecycle_state") == "preserved"
            and binding.get("preserved_commit") == commit_sha
        ) or (
            operation == "promote"
            and binding.get("lifecycle_state") == "promoted"
            and binding.get("promoted_commit") == commit_sha
        )
        if not initial_already_applied and commit_sha == transaction["before_head"]:
            raise OperationDenied(
                "resume_has_no_git_effect",
                "prepared operation made no Git effect; start a fresh operation",
            )
        self._verify_transaction_authority(transaction)
        self._acquire_fresh_recovery_quiescence(op_id)
        try:
            self._verify_quiescence_lease(op_id)
            current_binding, _ = self._binding(work_item_id)
            self._assert_branch(transaction["expected_branch"])
            if self.repo.head() != commit_sha:
                raise OperationDenied("recovery_state_changed", "local Git recovery head changed during drain")
            self._verify_transaction_authority(transaction)
            already_applied = (
                operation == "preserve"
                and current_binding.get("lifecycle_state") == "preserved"
                and current_binding.get("preserved_commit") == commit_sha
            ) or (
                operation == "promote"
                and current_binding.get("lifecycle_state") == "promoted"
                and current_binding.get("promoted_commit") == commit_sha
            )
            state_transition_already_applied = already_applied
            self._verify_quiescence_lease(op_id)
            if not already_applied:
                if current_binding.get("generation") != transaction["binding_generation"]:
                    raise OperationDenied("binding_generation_changed", "binding changed before local Git recovery")
                if operation == "preserve":
                    self._validate_preservation_effect(transaction, commit_sha)
                    changes = {"lifecycle_state": "preserved", "preserved_commit": commit_sha}
                    event_type = "scoped_commit_recovered"
                elif operation == "promote":
                    self._validate_promotion_effect(transaction, commit_sha)
                    changes = {"lifecycle_state": "promoted", "promoted_commit": commit_sha}
                    event_type = "promotion_recovered"
                else:
                    raise OperationDenied("operation_not_resumable", "transaction operation type is unsupported")
                self._transition(
                    work_item_id=work_item_id,
                    expected_record_generation=transaction["binding_generation"],
                    event_type=event_type,
                    changes=changes,
                    operation_id=op_id,
                )
            self._verify_quiescence_lease(op_id)
            transaction.update({"phase": "completed", "commit_sha": commit_sha, "completed_at": self._timestamp()})
            self.state.save_transaction(op_id, transaction)
        except Exception:
            self._release_after_preflight_denial(op_id)
            raise
        release_dispatcher_quiescence(self.dispatcher_state_dir, operation_id=op_id, now=self.clock())
        return OperationResult(
            operation="resume",
            code=f"{operation}_recovered",
            work_item_id=work_item_id,
            branch=transaction["expected_branch"],
            commit_sha=commit_sha,
            details={
                "operation_id": op_id,
                "state_transition_already_applied": state_transition_already_applied,
            },
        )

    def recover_quiescence(self, *, reason: str) -> dict[str, Any]:
        return recover_dispatcher_quiescence(self.dispatcher_state_dir, now=self.clock(), reason=reason)

    def recover_operation(self, *, operation_id: str, reason: str) -> dict[str, Any]:
        """Authorize a bounded retry after a recorded effect-boundary failure."""
        op_id = self._validate_operation_id(operation_id)
        if not reason.strip():
            raise OperationDenied("recovery_reason_required", "operation recovery requires a reason")
        with self.state.lock():
            transaction = self.state.load_transaction(op_id)
        phase = str(transaction.get("phase", ""))
        operation = transaction.get("operation")
        hosted_recovery = operation == "pull_request_promotion" and (
            phase.startswith("failed_") or phase.startswith("lease_lost_after_")
        )
        local_guard_recovery = operation in {"preserve", "promote"} and phase == "guard_lost_after_commit"
        if not hosted_recovery and not local_guard_recovery:
            raise OperationDenied("operation_recovery_denied", "operation is not in an explicitly recoverable phase")
        if local_guard_recovery:
            self._verify_transaction_authority(transaction)
        marker = self.dispatcher_state_dir / "dispatch-drain.json"
        recovered_quiescence: dict[str, Any] | None = None
        if marker.exists():
            recovered_quiescence = recover_dispatcher_quiescence(
                self.dispatcher_state_dir,
                now=self.clock(),
                reason=reason,
            )
        with self.state.lock():
            current = self.state.load_transaction(op_id)
            if current.get("phase") != phase or current.get("transaction_hash") != transaction.get("transaction_hash"):
                raise OperationDenied("operation_recovery_conflict", "operation changed before recovery was recorded")
            recovery_count = current.get("recovery_count", 0)
            if not isinstance(recovery_count, int) or isinstance(recovery_count, bool) or recovery_count < 0:
                raise OperationDenied("operation_recovery_state_invalid", "operation recovery counter is malformed")
            recovery_count += 1
            occurred_at = self._timestamp()
            current.update(
                {
                    "phase": "recovery_authorized" if hosted_recovery else "prepared",
                    "recovery_authorized": True,
                    "recovery_count": recovery_count,
                    "recovery_reason": reason,
                    "recovery_recorded_at": occurred_at,
                }
            )
            event = {
                "event_type": (
                    "hosted_promotion_recovery_authorized"
                    if hosted_recovery
                    else "local_git_effect_recovery_authorized"
                ),
                "operation_id": f"{op_id}.recovery.{recovery_count}",
                "recovered_operation_id": op_id,
                "occurred_at": occurred_at,
                "reason": reason,
                "prior_phase": phase,
            }
            self.state.commit_transaction_and_audit(op_id, current, event)
        return {
            "status": "PASS",
            "operation": "recover",
            "operation_id": op_id,
            "prior_phase": phase,
            "quiescence": recovered_quiescence,
        }
