"""Native bridge delivery and immutable session attribution.

An attempt is canonical coordination state. Its messages are disposable, and
their content is never copied into knowledge history. A claim reserves one
successor artifact, expires after 600 seconds, and is consumed by delivery.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Literal
from uuid import uuid4

from psycopg import sql
from psycopg.types.json import Jsonb
from pydantic import Field

from groundtruth_kb.bridge.taxonomy import BridgeKind
from groundtruth_kb.bridge.vocabulary import (
    CANONICAL_STATUSES,
    LOYAL_OPPOSITION_ACTIONABLE_STATUSES,
    LOYAL_OPPOSITION_AUTHORED_STATUSES,
    NON_DISPATCHABLE_STATUSES,
    PRIME_ACTIONABLE_STATUSES,
    PRIME_AUTHORED_STATUSES,
    THREAD_START_STATUSES,
    TRANSITIONS,
)
from groundtruth_kb.native_authority import (
    Identifier,
    Mutation,
    Request,
    Text,
    _current_parent,
    _error,
    _project_commit,
    _project_dependency_readiness,
    _related,
    _require_project_dependencies,
    _required,
    _work_evidence,
    _work_formal_sources,
    _write,
)
from groundtruth_kb.postgres_kernel import PostgresKernel, PostgresKernelError, PostgresTransaction, parse_json_bytes
from groundtruth_kb.session.worktree import (
    SessionWorktreeError,
    materialize_context_worktree,
    project_worktree,
    publish_context_work,
)

ROLE_NAMES = {"pb": "prime-builder", "lo": "loyal-opposition"}
ROLE_TOKENS = {value: key for key, value in ROLE_NAMES.items()}
INIT = re.compile(r"^::init (gtkb|application) (pb|lo)$")
ACTIVITIES = {"ops", "deliberation", "build", "test", "spec", "project"}


class BindSession(Request):
    native_context_id: Text
    init_command: Text


class SessionRequest(Request):
    native_context_id: Text


class ClaimRequest(SessionRequest):
    work_item_id: Identifier | None = None
    expected_version: int = Field(ge=0)
    intended_status: Text
    request_id: Identifier


class FenceRequest(SessionRequest):
    fence: int = Field(ge=1)


class DeliverRequest(FenceRequest):
    content: Text
    mode: Literal["interactive", "headless"] = "interactive"


class PublishWorkRequest(FenceRequest):
    expected_artifacts: dict[str, str | None]


class AbandonRequest(SessionRequest):
    expected_version: int = Field(ge=0)
    reason: Text


def _hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _public(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value.astimezone(UTC).isoformat() if isinstance(value, datetime) else value for key, value in row.items()
    }


def _paths(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(item, str) for item in value):
        _error("invalid_bridge_header", f"{label} must be a nonempty JSON list of relative artifact paths")
    normalized = []
    for path in value:
        parts = PurePosixPath(path)
        if (
            not path
            or not parts.parts
            or any(ord(character) < 32 for character in path)
            or "\\" in path
            or ":" in path
            or parts.is_absolute()
            or ".." in parts.parts
            or path != parts.as_posix()
            or any(
                part.casefold() in {".git", ".gtkb-state", "harness-state", "scratchpad", ".worktrees"}
                for part in parts.parts
            )
            or parts.parts[0].casefold() == "bridge"
            or path.casefold().startswith(".groundtruth/formal-artifact-approvals/")
        ):
            _error("invalid_bridge_header", f"{label} contains an invalid or forbidden artifact path")
        normalized.append(path.casefold())
    if len(set(normalized)) != len(normalized):
        _error("invalid_bridge_header", f"{label} contains duplicate artifact paths")
    return value


def parse_authored_message(content: str) -> dict[str, Any]:
    """Validate the author's complete header, preserving the submitted text."""
    lines = [line.strip() for line in content.splitlines()]
    nonblank = [line for line in lines if line]
    statuses = [line for line in nonblank[:3] if line in CANONICAL_STATUSES]
    if len(statuses) != 1:
        _error("invalid_bridge_header", "Exactly one canonical status must occupy the first three nonblank lines")
    status = statuses[0]
    metadata: dict[str, str] = {}
    init_lines, open_lines = [], []
    seen_status = False
    for line in lines:
        if not line:
            if metadata:
                break
            continue
        if line in CANONICAL_STATUSES:
            if line != status or seen_status:
                _error("invalid_bridge_header", "The header contains more than one status")
            seen_status = True
            continue
        if line.startswith("::init"):
            init_lines.append(line)
            continue
        if line.startswith("::open"):
            open_lines.append(line)
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9 _-]*):\s*(.*)", line)
        if match is None:
            break
        key = re.sub(r"[ -]", "_", match[1].casefold())
        if key in metadata:
            _error("invalid_bridge_header", "Metadata keys must not be repeated")
        metadata[key] = match[2]
    required = {
        "bridge_kind",
        "document",
        "version",
        "date",
        "author_identity",
        "author_harness_id",
        "author_session_context_id",
        "author_model",
        "project",
        "work_item",
    }
    if status == "ADVISORY":
        required -= {"project", "work_item"}
    if any(not metadata.get(key) for key in required):
        _error("invalid_bridge_header", "The authored header is missing required provenance or work linkage")
    if metadata["bridge_kind"] not in {kind.value for kind in BridgeKind}:
        _error("invalid_bridge_header", "bridge_kind must use the current canonical taxonomy")
    if status == "ADVISORY" and metadata["bridge_kind"] != BridgeKind.GOVERNANCE_ADVISORY.value:
        _error("invalid_bridge_header", "ADVISORY requires governance_advisory")
    retired = {"target_role", "project_authorization", "pauth", "receiver_kind", "spec_ids"} & metadata.keys()
    if retired:
        _error("invalid_bridge_header", "The header contains retired fields", fields=sorted(retired))
    try:
        version = int(metadata["version"])
        if version < 1 or not metadata["version"].isascii() or not metadata["version"].isdecimal():
            raise ValueError()
        if date.fromisoformat(metadata["date"]).isoformat() != metadata["date"]:
            raise ValueError()
    except ValueError:
        _error("invalid_bridge_header", "Version must be a positive integer and Date an ISO calendar date")
    role = (
        "pb"
        if status in PRIME_ACTIONABLE_STATUSES
        else "lo"
        if status in LOYAL_OPPOSITION_ACTIONABLE_STATUSES
        else None
    )
    if status in NON_DISPATCHABLE_STATUSES:
        if init_lines or open_lines or "recipient_role" in metadata:
            _error("invalid_bridge_header", "A non-dispatchable message has no init, activity or recipient role")
    else:
        if (
            init_lines != [f"::init gtkb {role}"]
            or len(open_lines) != 1
            or open_lines[0] not in {f"::open {activity}" for activity in ACTIVITIES}
            or init_lines[0] not in nonblank[:3]
            or open_lines[0] not in nonblank[:3]
            or metadata.get("recipient_role") != ROLE_NAMES[role]
        ):
            _error("invalid_bridge_header", "The authored envelope and recipient must name the next responder")
    result: dict[str, Any] = {"status": status, "version": version, "metadata": metadata}
    if status in {"NEW", "REVISED"}:
        if metadata["bridge_kind"] != "implementation_proposal":
            _error("invalid_bridge_header", "NEW and REVISED require implementation_proposal")
        try:
            observed_work_version = metadata.get("work_item_version", "")
            result["work_item_version"] = int(observed_work_version)
            if (
                not observed_work_version.isascii()
                or not observed_work_version.isdecimal()
                or not 1 <= result["work_item_version"] < 2_147_483_647
            ):
                raise ValueError()
        except ValueError:
            _error(
                "invalid_bridge_header",
                "work_item_version must identify the observed positive integer work-item version",
            )
        for key in ("target_paths", "test_artifact_targets", "spec_versions"):
            try:
                result[key] = parse_json_bytes(metadata.get(key, "").encode("utf-8"))
            except PostgresKernelError:
                _error("invalid_bridge_header", f"{key} must be authored as JSON")
        _paths(result["target_paths"], "target_paths")
        _paths(result["test_artifact_targets"], "test_artifact_targets")
        if (
            not isinstance(result["spec_versions"], dict)
            or not result["spec_versions"]
            or any(
                not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}", key)
                or type(version) is not int
                or not 1 <= version < 2_147_483_647
                for key, version in result["spec_versions"].items()
            )
        ):
            _error(
                "invalid_bridge_header",
                "spec_versions must map each applicable formal ID to its observed positive integer version",
            )
    if status == "READY" and metadata["bridge_kind"] != "implementation_report":
        _error("invalid_bridge_header", "READY requires implementation_report")
    if status in {"GO", "NO-GO", "NOT-READY", "VERIFIED", "SUPERSEDED"} and metadata["bridge_kind"] != "lo_verdict":
        _error("invalid_bridge_header", "An LO verdict requires lo_verdict")
    return result


class NativeBridgeService:
    def __init__(self, kernel: PostgresKernel, project_root: Path) -> None:
        self.kernel = kernel
        self.project_root = project_root.resolve()

    def work_root(self, project_id: str, *, create: bool = True, refresh_base: bool = False) -> Path:
        try:
            return project_worktree(self.project_root, project_id, create=create, refresh_base=refresh_base)
        except SessionWorktreeError as error:
            raise PostgresKernelError(error.code, str(error)) from error

    def bind(self, request: BindSession) -> dict[str, Any]:
        markers = {line for line in request.init_command.splitlines() if INIT.fullmatch(line)}
        if len(markers) != 1:
            _error("invalid_init_command", "Supply one distinct exact role-bearing init marker")
        marker = markers.pop()
        subject, role = INIT.fullmatch(marker).groups()
        identity = _hash(marker)
        with self.kernel.transaction(serializable=False) as tx:
            existing = self._binding(tx, request.native_context_id, required=False)
            if existing:
                if existing["subject"] != subject or existing["role"] != ROLE_NAMES[role]:
                    _error("session_init_conflict", "An existing context's subject and role cannot change")
                return _public(existing)
            tx.cursor.execute(
                sql.SQL(
                    "INSERT INTO {}.session_init_bindings (native_context_id,session_context_id,subject,role,"
                    "minimum_idempotency_identity) VALUES (%s,%s,%s,%s,%s) "
                    "ON CONFLICT (native_context_id) DO NOTHING RETURNING *"
                ).format(sql.Identifier(tx.schema)),
                (request.native_context_id, f"SENV-{uuid4().hex}", subject, ROLE_NAMES[role], identity),
            )
            inserted = tx.cursor.fetchone()
            binding = dict(inserted) if inserted else self._binding(tx, request.native_context_id)
            if binding["subject"] != subject or binding["role"] != ROLE_NAMES[role]:
                _error("session_init_conflict", "An existing context's subject and role cannot change")
            return _public(binding)

    @staticmethod
    def _binding(tx: PostgresTransaction, native_context_id: str, *, required: bool = True) -> dict[str, Any] | None:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.session_init_bindings WHERE native_context_id=%s").format(
                sql.Identifier(tx.schema)
            ),
            (native_context_id,),
        )
        row = tx.cursor.fetchone()
        if row is None and required:
            _error("no_session_binding", "The native context has no immutable binding; initialize that exact context")
        return dict(row) if row else None

    def session(self, native_context_id: str) -> dict[str, Any]:
        with self.kernel.transaction(read_only=True) as tx:
            return _public(self._binding(tx, native_context_id))

    @staticmethod
    def _attempt(tx: PostgresTransaction, document: str, *, lock: bool = False) -> dict[str, Any] | None:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.bridge_attempts WHERE id=%s{}").format(
                sql.Identifier(tx.schema), sql.SQL(" FOR UPDATE" if lock else "")
            ),
            (document,),
        )
        row = tx.cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def _head(tx: PostgresTransaction, attempt: dict[str, Any]) -> dict[str, Any] | None:
        if attempt["head_version"] == 0:
            return None
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.bridge_items WHERE attempt_id=%s AND version=%s").format(
                sql.Identifier(tx.schema)
            ),
            (attempt["id"], attempt["head_version"]),
        )
        row = tx.cursor.fetchone()
        if row is None:
            _error("broken_bridge_chain", "The current delivery is missing; reconcile the canonical attempt")
        return dict(row)

    @staticmethod
    def _author(binding: dict[str, Any], status: str) -> None:
        allowed = PRIME_AUTHORED_STATUSES if binding["role"] == "prime-builder" else LOYAL_OPPOSITION_AUTHORED_STATUSES
        if binding["subject"] != "gtkb" or status not in allowed:
            _error("wrong_author_role", "The immutable context role cannot author this status")

    @staticmethod
    def _scope(tx: PostgresTransaction, attempt: dict[str, Any], *, lock: bool = False) -> None:
        work = _required(tx, "work_items", attempt["work_item_id"], lock=lock)
        if attempt["work_item_version"] is not None and work["version"] != attempt["work_item_version"]:
            _error("scope_changed", "Current work scope changed; reconcile this attempt before further effects")
        if _current_parent(tx, work["id"])["project_id"] != attempt["project_id"]:
            _error("scope_changed", "The work item's project changed; reconcile the attempt")
        for current in _work_formal_sources(
            tx, work, attempt["project_id"], additional_ids=list(attempt["spec_versions"]), lock=lock
        ):
            key = current["id"]
            if current["version"] != attempt["spec_versions"].get(key) or current["status"] != "active":
                _error("scope_changed", "Applicable formal knowledge changed; reconcile the attempt", id=key)

    @staticmethod
    def _overlap(left: list[str], right: list[str]) -> bool:
        return any(
            a.casefold() == b.casefold()
            or a.casefold().startswith(b.casefold() + "/")
            or b.casefold().startswith(a.casefold() + "/")
            for a in left
            for b in right
        )

    def _dependency_readiness(self, tx, work_item_id, *, attempt=None, lock=False, cross_project_only=False):
        work = _required(tx, "work_items", work_item_id, lock=lock)
        project_id = _current_parent(tx, work_item_id)["project_id"]
        if attempt is None:
            tx.cursor.execute(
                sql.SQL("SELECT * FROM {}.bridge_attempts WHERE work_item_id=%s AND disposition='active'").format(
                    sql.Identifier(tx.schema)
                ),
                (work_item_id,),
            )
            attempts = tx.cursor.fetchall()
            attempt = dict(attempts[0]) if len(attempts) == 1 else None
        change_paths = []
        if attempt and attempt["go_context_id"] and attempt["head_status"] in {"GO", "READY", "NOT-READY", "VERIFIED"}:
            try:
                self._scope(tx, attempt, lock=lock)
            except PostgresKernelError as error:
                if error.code not in {"scope_changed", "not_found"}:
                    raise
            else:
                # An accepted successor intentionally changes these artifacts.
                # Project finalization independently verifies every final map.
                change_paths = attempt["proposal_paths"] + attempt["test_targets"]
        results = []
        for predecessor_id in work.get("depends_on_work_items") or []:
            predecessor = _required(tx, "work_items", predecessor_id, lock=lock)
            parent = _current_parent(tx, predecessor_id)["project_id"]
            if cross_project_only and parent == project_id:
                continue
            project = _required(tx, "projects", parent, lock=lock)
            required = (
                "project_commit" if parent != project_id or project["status"] == "verified" else "independent_review"
            )
            reason, changed_paths = None, []
            if predecessor["resolution_status"] != "verified":
                reason = "predecessor_not_verified"
            elif required == "project_commit":
                commit = _project_commit(tx, parent)
                if project["status"] != "verified" or not commit:
                    reason = "predecessor_project_not_committed"
                elif predecessor["completion_evidence"] != "git:" + commit:
                    reason = "predecessor_terminal_commit_mismatch"
            else:
                tx.cursor.execute(
                    sql.SQL("SELECT * FROM {}.bridge_attempts WHERE work_item_id=%s AND disposition='active'").format(
                        sql.Identifier(tx.schema)
                    )
                    + (sql.SQL(" FOR UPDATE") if lock else sql.SQL("")),
                    (predecessor_id,),
                )
                reviews = tx.cursor.fetchall()
                if len(reviews) != 1 or reviews[0]["head_status"] != "VERIFIED" or not reviews[0]["verified_artifacts"]:
                    reason = "predecessor_review_missing"
                else:
                    review = dict(reviews[0])
                    if review["finalization_failure"]:
                        reason = "predecessor_reverification_required"
                    else:
                        try:
                            self._scope(tx, review, lock=lock)
                        except PostgresKernelError as error:
                            if error.code not in {"scope_changed", "not_found"}:
                                raise
                            reason = "predecessor_scope_changed"
                        else:
                            required_artifacts = {
                                path: blob
                                for path, blob in review["verified_artifacts"].items()
                                if not self._overlap([path], change_paths)
                            }
                            try:
                                actual = self._snapshot(
                                    sorted(required_artifacts), root=self.work_root(parent, create=False)
                                )
                            except PostgresKernelError as error:
                                if error.code not in {
                                    "project_checkout_missing",
                                    "project_checkout_unregistered",
                                    "artifact_snapshot_failed",
                                }:
                                    raise
                                reason = "predecessor_artifacts_unavailable"
                            else:
                                changed_paths = sorted(
                                    path for path, blob in required_artifacts.items() if actual[path] != blob
                                )
                                if changed_paths:
                                    reason = "predecessor_reviewed_bytes_changed"
            results.append(
                {
                    "work_item_id": predecessor_id,
                    "project_id": parent,
                    "required_result": required,
                    "current_status": predecessor["resolution_status"],
                    "satisfied": reason is None,
                    "reason": reason,
                    "changed_paths": changed_paths,
                }
            )
        return {
            "work_item_id": work_item_id,
            "project_id": project_id,
            "ready": all(row["satisfied"] for row in results),
            "predecessors": results,
            "accepted_change_paths": sorted(set(change_paths)),
        }

    def work_item_readiness(self, work_item_id: str) -> dict[str, Any]:
        with self.kernel.transaction(read_only=True) as tx:
            return self._dependency_readiness(tx, work_item_id)

    def _require_work_dependencies(self, tx, work_item_id, **options):
        result = self._dependency_readiness(tx, work_item_id, **options)
        if not result["ready"]:
            _error(
                "work_item_dependencies_unsatisfied",
                "Required work-item results are unavailable; read backlog readiness",
                **result,
            )

    def _claim_readiness(self, tx, attempt, intended_status, *, lock=False):
        if not attempt["work_item_id"]:
            return
        work = _required(tx, "work_items", attempt["work_item_id"], lock=lock)
        if _current_parent(tx, work["id"])["project_id"] != attempt["project_id"]:
            _error("scope_changed", "Current project membership differs from the attempt")
        # Rejection and revision can address changed intent. Approval,
        # implementation and verification must use the accepted proposal scope.
        if intended_status in {"GO", "READY", "VERIFIED"}:
            self._scope(tx, attempt, lock=lock)
        if intended_status in {"NEW", "REVISED", "GO", "READY", "VERIFIED"}:
            _require_project_dependencies(tx, attempt["project_id"], lock=lock)
            self._require_work_dependencies(tx, work["id"], attempt=attempt, lock=lock)

    def claim(self, document: str, request: ClaimRequest) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            binding = self._binding(tx, request.native_context_id)
            self._author(binding, request.intended_status)
            if request.intended_status == "ADVISORY":
                if request.work_item_id is not None:
                    _error("advisory_is_not_work", "An advisory may cite work but does not reserve a work-item attempt")
                work, project, project_id = None, None, None
            else:
                if request.work_item_id is None:
                    _error("work_item_required", "Implementation lifecycle artifacts require one work item")
                work = _required(tx, "work_items", request.work_item_id, lock=True)
                project_id = _current_parent(tx, work["id"])["project_id"]
                project = _required(tx, "projects", project_id)
            attempt = self._attempt(tx, document, lock=True)
            if attempt is None:
                if request.expected_version != 0 or request.intended_status not in THREAD_START_STATUSES:
                    _error("invalid_transition", "A fresh attempt starts with NEW, BLOCKED or ADVISORY")
                if work and (work["resolution_status"] != "open" or project["status"] != "active"):
                    _error("work_not_open", "A new attempt requires open work in an active execution project")
                tx.cursor.execute(
                    sql.SQL(
                        "INSERT INTO {}.bridge_attempts (id,work_item_id,project_id) VALUES (%s,%s,%s) RETURNING *"
                    ).format(sql.Identifier(tx.schema)),
                    (document, work["id"] if work else None, project_id),
                )
                attempt = dict(tx.cursor.fetchone())
            if (
                attempt["work_item_id"] != request.work_item_id
                or attempt["head_version"] != request.expected_version
                or attempt["disposition"] != "active"
            ):
                _error("stale_bridge_head", "Read current canonical attempt state before claiming an artifact")
            allowed = TRANSITIONS[attempt["head_status"]] if attempt["head_status"] else THREAD_START_STATUSES
            if request.intended_status not in allowed:
                _error("invalid_transition", "The intended artifact cannot follow the current bridge status")
            self._claim_readiness(tx, attempt, request.intended_status)
            if request.intended_status == "NEW" and project["authorization"] != "authorized":
                _error("project_not_authorized", "The parent project is not authorized for a NEW proposal")
            if project_id:
                self.work_root(project_id)
            if request.intended_status == "VERIFIED" and attempt["head_status"] == "VERIFIED":
                if not attempt["finalization_failure"]:
                    _error(
                        "verification_not_requested", "Fresh verification requires canonical finalization repair state"
                    )
            head = self._head(tx, attempt)
            predecessor = _hash(head["content"]) if head else None
            tx.cursor.execute(
                sql.SQL(
                    "SELECT *, expires_at>clock_timestamp() AS live FROM {}.work_intent_claims "
                    "WHERE attempt_id=%s FOR UPDATE"
                ).format(sql.Identifier(tx.schema)),
                (document,),
            )
            existing = tx.cursor.fetchone()
            if existing and existing["live"]:
                if (
                    existing["request_id"] == request.request_id
                    and existing["claimant_session_context_id"] == binding["session_context_id"]
                    and existing["intended_status"] == request.intended_status
                    and existing["next_version"] == request.expected_version + 1
                    and existing["predecessor_sha256"] == predecessor
                ):
                    return {
                        **_public({key: value for key, value in existing.items() if key != "live"}),
                        "predecessor": _public(head) if head else None,
                    }
                _error("artifact_already_claimed", "Another request reserves the exact next bridge artifact")
            if request.intended_status == "READY":
                tx.cursor.execute(
                    sql.SQL(
                        "SELECT a.proposal_paths,a.test_targets FROM {}.work_intent_claims c JOIN {}.bridge_attempts a ON a.id=c.attempt_id "
                        "WHERE c.expires_at>clock_timestamp() AND c.intended_status='READY' AND c.attempt_id<>%s"
                    ).format(sql.Identifier(tx.schema), sql.Identifier(tx.schema)),
                    (document,),
                )
                if any(
                    self._overlap(
                        attempt["proposal_paths"] + attempt["test_targets"],
                        row["proposal_paths"] + row["test_targets"],
                    )
                    for row in tx.cursor.fetchall()
                ):
                    _error("artifact_effect_conflict", "An overlapping artifact effect is currently reserved")
            tx.cursor.execute(
                sql.SQL("DELETE FROM {}.work_intent_claims WHERE attempt_id=%s").format(sql.Identifier(tx.schema)),
                (document,),
            )
            tx.cursor.execute(
                sql.SQL(
                    "INSERT INTO {}.work_intent_claims (attempt_id,next_version,intended_status,predecessor_sha256,"
                    "claimant_session_context_id,request_id) VALUES (%s,%s,%s,%s,%s,%s) RETURNING *"
                ).format(sql.Identifier(tx.schema)),
                (
                    document,
                    request.expected_version + 1,
                    request.intended_status,
                    predecessor,
                    binding["session_context_id"],
                    request.request_id,
                ),
            )
            return {**_public(dict(tx.cursor.fetchone())), "predecessor": _public(head) if head else None}

    def _fenced(self, tx: PostgresTransaction, document: str, request: FenceRequest):
        binding = self._binding(tx, request.native_context_id)
        attempt = self._attempt(tx, document, lock=True)
        if not attempt or attempt["disposition"] != "active":
            _error("stale_bridge_head", "No active attempt is available for this effect")
        tx.cursor.execute(
            sql.SQL(
                "SELECT *, expires_at>clock_timestamp() AS live FROM {}.work_intent_claims WHERE attempt_id=%s FOR UPDATE"
            ).format(sql.Identifier(tx.schema)),
            (document,),
        )
        claim = tx.cursor.fetchone()
        if (
            not claim
            or not claim["live"]
            or claim["fence"] != request.fence
            or claim["claimant_session_context_id"] != binding["session_context_id"]
        ):
            _error("stale_artifact_fence", "The exact artifact claim is missing, expired or replaced")
        head = self._head(tx, attempt)
        if claim["next_version"] != attempt["head_version"] + 1 or claim["predecessor_sha256"] != (
            _hash(head["content"]) if head else None
        ):
            _error("stale_bridge_head", "The claimed predecessor is no longer the current exact delivery")
        return binding, attempt, dict(claim)

    def check(self, document: str, request: FenceRequest) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            _, attempt, claim = self._fenced(tx, document, request)
            self._claim_readiness(tx, attempt, claim["intended_status"])
            return {
                "status": "current",
                "claim": _public({key: value for key, value in claim.items() if key != "live"}),
                "target_paths": sorted(set(attempt["proposal_paths"] + attempt["test_targets"]))
                if claim["intended_status"] == "READY"
                else [],
            }

    def release(self, document: str, request: FenceRequest) -> dict[str, Any]:
        with self.kernel.transaction() as tx:
            self._fenced(tx, document, request)
            tx.cursor.execute(
                sql.SQL("DELETE FROM {}.work_intent_claims WHERE attempt_id=%s AND fence=%s").format(
                    sql.Identifier(tx.schema)
                ),
                (document, request.fence),
            )
            return {"status": "released", "document": document, "fence": request.fence}

    def lock_worktrees(self, tx: PostgresTransaction) -> None:
        """Serialize short filesystem effects, never the lifetime of agent work."""
        tx.cursor.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
            ("gtkb-git:" + str(self.project_root.resolve()).casefold(),),
        )

    def open_worktree(self, document: str, request: FenceRequest) -> dict[str, Any]:
        """Materialize current project work into only the receiving context's checkout."""
        with self.kernel.transaction(serializable=False) as tx:
            self.lock_worktrees(tx)
            binding, attempt, claim = self._fenced(tx, document, request)
            self._claim_readiness(tx, attempt, claim["intended_status"], lock=True)
            own_paths = set(attempt["proposal_paths"] + attempt["test_targets"])
            paths = set(own_paths)
            tx.cursor.execute(
                sql.SQL(
                    "SELECT proposal_paths,test_targets FROM {}.bridge_attempts WHERE project_id=%s AND disposition='active'"
                ).format(sql.Identifier(tx.schema)),
                (attempt["project_id"],),
            )
            for row in tx.cursor.fetchall():
                paths.update(row["proposal_paths"] + row["test_targets"])
            source = (
                self.work_root(attempt["project_id"], refresh_base=True) if attempt["project_id"] else self.project_root
            )
            if claim["intended_status"] in {"NEW", "REVISED", "GO", "READY", "VERIFIED"}:
                self._require_work_dependencies(tx, attempt["work_item_id"], attempt=attempt, lock=True)
            head = subprocess.run(
                ["git", "-C", str(source), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            ).stdout.strip()
            try:
                artifacts = self._snapshot(sorted(paths), root=source)
                result = materialize_context_worktree(
                    self.project_root,
                    binding["session_context_id"],
                    expected_head=head,
                    artifacts=artifacts,
                    snapshot=self._snapshot,
                    artifact_source=source,
                )
                result["artifact_preimages"] = {path: artifacts[path] for path in sorted(own_paths)}
                result["loaded_paths"] = sorted(paths)
                return result
            except SessionWorktreeError as error:
                raise PostgresKernelError(error.code, str(error)) from error

    def publish_work(self, document: str, request: PublishWorkRequest) -> dict[str, Any]:
        """Apply only the caller's claimed implementation artifacts, before its report."""
        with self.kernel.transaction(serializable=False) as tx:
            self.lock_worktrees(tx)
            binding, attempt, claim = self._fenced(tx, document, request)
            if claim["intended_status"] != "READY":
                _error(
                    "implementation_claim_required", "Work publication requires the exact implementation-report claim"
                )
            self._scope(tx, attempt, lock=True)
            _require_project_dependencies(tx, attempt["project_id"], lock=True)
            self._require_work_dependencies(tx, attempt["work_item_id"], attempt=attempt, lock=True)
            try:
                artifacts = publish_context_work(
                    self.project_root,
                    binding["session_context_id"],
                    artifact_paths=sorted(set(attempt["proposal_paths"] + attempt["test_targets"])),
                    expected_artifacts=request.expected_artifacts,
                    snapshot=self._snapshot,
                    artifact_destination=self.work_root(attempt["project_id"]),
                    before_effect=lambda: self._fenced(tx, document, request),
                )
            except SessionWorktreeError as error:
                raise PostgresKernelError(error.code, str(error)) from error
            return {"status": "published", "document": document, "artifacts": artifacts}

    def artifacts(self, document: str) -> dict[str, Any]:
        with self.kernel.transaction(read_only=True) as tx:
            attempt = self._attempt(tx, document)
            if not attempt or attempt["disposition"] != "active":
                _error("not_found", "No active attempt has artifacts to review")
            paths = sorted(set(attempt["proposal_paths"] + attempt["test_targets"]))
            return self._snapshot(paths, root=self.work_root(attempt["project_id"])) if paths else {}

    def _snapshot(self, paths: list[str], *, root: Path | None = None) -> dict[str, str | None]:
        """Hash the actual Git-normalized bytes, including explicit deletions."""
        root = (root or self.project_root).resolve()
        result = {}
        for relative in paths:
            path = root / relative
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                _error("artifact_outside_root", "A reviewed artifact escapes the configured project root")
            if not path.exists():
                result[relative] = None
                continue
            if not path.is_file():
                _error("artifact_scope_not_concrete", "Review requires concrete file paths, not directories")
            command = subprocess.run(
                ["git", "-C", str(root), "hash-object", f"--path={relative}", "--", str(path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
            )
            if command.returncode or not re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", command.stdout.strip()):
                _error("artifact_snapshot_failed", "Git could not identify the current artifact bytes")
            result[relative] = command.stdout.strip()
        return result

    @staticmethod
    def _purge(tx: PostgresTransaction, document: str) -> None:
        tx.cursor.execute(
            sql.SQL("DELETE FROM {}.work_intent_claims WHERE attempt_id=%s").format(sql.Identifier(tx.schema)),
            (document,),
        )
        tx.cursor.execute(
            sql.SQL("DELETE FROM {}.bridge_items WHERE attempt_id=%s").format(sql.Identifier(tx.schema)), (document,)
        )
        tx.cursor.execute(
            sql.SQL(
                "UPDATE {}.bridge_attempts SET work_item_version=NULL,proposal_paths='[]',test_targets='[]',"
                "spec_versions='{{}}',proposal_context_id=NULL,go_context_id=NULL,report_context_id=NULL,"
                "verified_artifacts=NULL,finalization_failure=NULL,closed_at=clock_timestamp() WHERE id=%s"
            ).format(sql.Identifier(tx.schema)),
            (document,),
        )

    def deliver(self, document: str, request: DeliverRequest) -> dict[str, Any]:
        message = parse_authored_message(request.content)
        metadata = message["metadata"]
        if metadata["document"] != document:
            _error("invalid_bridge_header", "Document must match the claimed canonical attempt")
        status = message["status"]
        with self.kernel.transaction() as tx:
            binding = self._binding(tx, request.native_context_id)
            self._author(binding, status)
            if metadata["author_session_context_id"] != binding["session_context_id"]:
                _error("author_context_mismatch", "The authored provenance must identify the resolved native context")
            attempt = self._attempt(tx, document, lock=True)
            if attempt is None or attempt["disposition"] != "active":
                _error("attempt_closed", "The attempt is absent or terminal; inspect current work state")
            if status != "ADVISORY" and (
                metadata["work_item"] != attempt["work_item_id"] or metadata["project"] != attempt["project_id"]
            ):
                _error("invalid_bridge_header", "Authored project and work item must match the canonical attempt")
            # A lost acknowledgement is resolved from the exact delivered bytes
            # and fence. Same-context identity alone grants no replay exemption.
            if message["version"] <= attempt["head_version"]:
                tx.cursor.execute(
                    sql.SQL(
                        "SELECT content,delivery_fence FROM {}.bridge_items WHERE attempt_id=%s AND version=%s"
                    ).format(sql.Identifier(tx.schema)),
                    (document, message["version"]),
                )
                prior = tx.cursor.fetchone()
                if prior and prior["content"] == request.content and prior["delivery_fence"] == request.fence:
                    return {"status": "already_delivered", "document": document, "version": message["version"]}
                _error("bridge_version_collision", "The numbered delivery already exists with different bytes or fence")
            binding, attempt, claim = self._fenced(tx, document, request)
            if message["version"] != claim["next_version"] or status != claim["intended_status"]:
                _error("claim_does_not_match_artifact", "The complete artifact must match its exact claimed successor")
            _required(tx, "harnesses", metadata["author_harness_id"])
            if status == "ADVISORY":
                self._publish(
                    tx,
                    document,
                    request,
                    message,
                    binding,
                    claim,
                    {"head_version": message["version"], "head_status": status},
                )
                return {
                    "status": "delivered",
                    "document": document,
                    "version": message["version"],
                    "bridge_status": status,
                    "project_ready_for_commit": False,
                    "project_id": None,
                }
            work = _required(tx, "work_items", attempt["work_item_id"], lock=True)
            project = _required(tx, "projects", attempt["project_id"])
            if _current_parent(tx, work["id"])["project_id"] != project["id"]:
                _error("scope_changed", "Current project membership differs from the attempt")
            updates: dict[str, Any] = {"head_version": message["version"], "head_status": status}
            if status == "NEW" and project["authorization"] != "authorized":
                _error("project_not_authorized", "The parent project is not authorized at NEW proposal filing")
            if status in {"NEW", "REVISED", "GO", "READY", "VERIFIED"}:
                _require_project_dependencies(tx, project["id"])
                self._require_work_dependencies(tx, work["id"], attempt=attempt)
            if status == "BLOCKED":
                if request.mode != "headless":
                    _error(
                        "interactive_owner_decision_required",
                        "Interactive work asks the owner instead of authoring BLOCKED",
                    )
                if (
                    project["authorization"] != "not authorized"
                    or metadata.get("observed_authorization") != project["authorization"]
                ):
                    _error("invalid_blocked_observation", "BLOCKED must report the current not-authorized project")
                try:
                    observed = datetime.fromisoformat(metadata.get("authorization_read_at", ""))
                    if observed.utcoffset() is None or observed > datetime.now(UTC):
                        raise ValueError()
                except ValueError:
                    _error("invalid_blocked_observation", "BLOCKED must identify the observed read time")
            if status in {"NEW", "REVISED"}:
                if message["work_item_version"] != work["version"]:
                    _error(
                        "scope_changed",
                        "The authored work-item version is no longer current; read the changed scope and revise the proposal",
                        id=work["id"],
                        authored_version=message["work_item_version"],
                        current_version=work["version"],
                        recovery_route=f"gt context work-item {work['id']}",
                    )
                _work_evidence(tx, work)
                formals = _work_formal_sources(tx, work, project["id"], additional_ids=list(message["spec_versions"]))
                missing = sorted({spec["id"] for spec in formals} - message["spec_versions"].keys())
                if missing:
                    _error(
                        "incomplete_formal_scope",
                        "The proposal omits linked formal requirements; read current task context and cited sources",
                        ids=missing,
                        recovery_route=f"gt context work-item {work['id']}",
                    )
                specs = {}
                for spec in formals:
                    if spec["status"] != "active":
                        _error("inactive_formal_scope", "A proposal requires active formal authority", id=spec["id"])
                    if spec["version"] != message["spec_versions"][spec["id"]]:
                        _error(
                            "scope_changed",
                            "The authored formal version is no longer current; read the changed requirement and revise the proposal",
                            id=spec["id"],
                            authored_version=message["spec_versions"][spec["id"]],
                            current_version=spec["version"],
                            recovery_route=f"gt context work-item {work['id']}",
                        )
                    specs[spec["id"]] = spec["version"]
                test = _required(tx, "tests", work["source_test_id"])
                if not test["test_file"] or test["test_file"] not in message["test_artifact_targets"]:
                    _error("test_scope_missing", "The proposal must identify the work item's executable test artifact")
                updates.update(
                    work_item_version=work["version"],
                    proposal_paths=Jsonb(message["target_paths"]),
                    test_targets=Jsonb(message["test_artifact_targets"]),
                    spec_versions=Jsonb(specs),
                    proposal_context_id=binding["session_context_id"],
                    go_context_id=None,
                    report_context_id=None,
                )
            if status in {"GO", "READY", "VERIFIED"}:
                self._scope(tx, attempt)
            if status == "GO":
                if (
                    not attempt["proposal_context_id"]
                    or attempt["proposal_context_id"] == binding["session_context_id"]
                ):
                    _error("independent_review_required", "GO requires an independently authored current proposal")
                updates["go_context_id"] = binding["session_context_id"]
            if status == "READY":
                if not attempt["go_context_id"]:
                    _error("implementation_go_required", "An implementation report requires an accepted GO")
                updates["report_context_id"] = binding["session_context_id"]
            ready_to_commit = False
            if status == "VERIFIED":
                if not attempt["report_context_id"] or attempt["report_context_id"] == binding["session_context_id"]:
                    _error("independent_review_required", "Verification requires an independently authored report")
                try:
                    reviewed = parse_json_bytes(metadata.get("verified_artifacts", "").encode("utf-8"))
                except PostgresKernelError:
                    _error("reviewed_artifacts_required", "VERIFIED must identify the exact reviewed Git blob map")
                actual = self._snapshot(
                    sorted(set(attempt["proposal_paths"] + attempt["test_targets"])),
                    root=self.work_root(attempt["project_id"]),
                )
                if not actual or reviewed != actual:
                    _error(
                        "reviewed_bytes_changed",
                        "The submitted reviewed artifact map differs from actual current bytes",
                    )
                updates.update(verified_artifacts=Jsonb(actual), finalization_failure=None)
                result = _write(
                    tx,
                    "work_items",
                    work["id"],
                    {"resolution_status": "verified"},
                    Mutation(
                        expected_version=work["version"],
                        actor=binding["session_context_id"],
                        reason="Independent bridge verification of the current artifact bytes; project commit remains separate",
                    ),
                )
                updates["work_item_version"] = result["version"]
                members = _related(tx, "project_work_item_memberships", project_id=project["id"], status="active")
                ready_to_commit = bool(members) and all(
                    _required(tx, "work_items", member["work_item_id"])["resolution_status"] == "verified"
                    for member in members
                )
            if status == "WITHDRAWN":
                if attempt["go_context_id"]:
                    _error("cannot_withdraw_after_go", "An implemented attempt cannot be withdrawn")
                updates["disposition"] = "withdrawn"
            if status == "SUPERSEDED":
                residual = metadata.get("residual_work_item")
                if not metadata.get("supersession_source") or not residual:
                    _error(
                        "supersession_evidence_required",
                        "Name current canonical supersession evidence and residual work or none",
                    )
                source = None
                for table in ("specifications", "work_items", "projects"):
                    source = tx.get(table, {"id": metadata["supersession_source"]})
                    if source:
                        break
                if source is None:
                    _error(
                        "supersession_source_missing", "Supersession evidence must resolve to current canonical state"
                    )
                if residual != "none":
                    _required(tx, "work_items", residual)
                updates["disposition"] = "superseded"
            self._publish(tx, document, request, message, binding, claim, updates)
            if updates.get("disposition") in {"withdrawn", "superseded"}:
                self._purge(tx, document)
            return {
                "status": "delivered",
                "document": document,
                "version": message["version"],
                "bridge_status": status,
                "project_ready_for_commit": ready_to_commit,
                "project_id": project["id"],
            }

    @staticmethod
    def _publish(tx, document, request, message, binding, claim, updates):
        status = message["status"]
        tx.cursor.execute(
            sql.SQL(
                "INSERT INTO {}.bridge_items (attempt_id,version,status,author_session_context_id,delivery_fence,content) "
                "VALUES (%s,%s,%s,%s,%s,%s)"
            ).format(sql.Identifier(tx.schema)),
            (document, message["version"], status, binding["session_context_id"], claim["fence"], request.content),
        )
        tx.cursor.execute(
            sql.SQL("UPDATE {}.bridge_attempts SET {} WHERE id=%s").format(
                sql.Identifier(tx.schema),
                sql.SQL(",").join(sql.SQL("{}=%s").format(sql.Identifier(key)) for key in updates),
            ),
            [*updates.values(), document],
        )
        tx.cursor.execute(
            sql.SQL("DELETE FROM {}.work_intent_claims WHERE attempt_id=%s AND fence=%s").format(
                sql.Identifier(tx.schema)
            ),
            (document, request.fence),
        )

    def show(self, document: str, *, include_content: bool = False) -> dict[str, Any]:
        with self.kernel.transaction(read_only=True) as tx:
            attempt = self._attempt(tx, document)
            if attempt is None:
                _error("not_found", "Canonical attempt does not exist")
            result = {"attempt": _public(attempt)}
            if include_content and attempt["disposition"] == "active":
                tx.cursor.execute(
                    sql.SQL(
                        "SELECT version,status,author_session_context_id,content,created_at "
                        "FROM {}.bridge_items WHERE attempt_id=%s ORDER BY version"
                    ).format(sql.Identifier(tx.schema)),
                    (document,),
                )
                result["messages"] = [_public(dict(row)) for row in tx.cursor.fetchall()]
            return result

    def queue(self, role: Literal["pb", "lo"]) -> dict[str, Any]:
        """Report eligible work; selection remains the owner's or dispatcher's act."""
        eligible, blocked = [], []
        with self.kernel.transaction(read_only=True) as tx:
            tx.cursor.execute(
                sql.SQL(
                    "SELECT a.*,w.priority FROM {}.bridge_attempts a JOIN {}.work_items w ON w.id=a.work_item_id "
                    "JOIN {}.projects p ON p.id=a.project_id LEFT JOIN {}.work_intent_claims c "
                    "ON c.attempt_id=a.id AND c.expires_at>clock_timestamp() "
                    "WHERE a.disposition='active' AND c.attempt_id IS NULL "
                    'ORDER BY w.priority COLLATE "C" NULLS LAST,a.created_at,a.id'
                ).format(*(sql.Identifier(tx.schema) for _ in range(4)))
            )
            for raw in tx.cursor.fetchall():
                row = dict(raw)
                ordinary = row["head_status"] in (
                    PRIME_ACTIONABLE_STATUSES if role == "pb" else LOYAL_OPPOSITION_ACTIONABLE_STATUSES
                )
                fresh_verification = role == "lo" and row["head_status"] == "VERIFIED" and row["finalization_failure"]
                if ordinary or fresh_verification:
                    readiness = _project_dependency_readiness(tx, row["project_id"], "readiness")
                    work_readiness = self._dependency_readiness(tx, row["work_item_id"], attempt=row)
                    if readiness["ready"] and work_readiness["ready"]:
                        eligible.append(_public(row))
                    else:
                        blocked.append({**_public(row), "readiness": readiness, "work_item_readiness": work_readiness})
            return {"role": role, "eligible": eligible, "blocked": blocked}

    def abandon(self, document: str, request: AbandonRequest) -> dict[str, Any]:
        """Close an unusable attempt from canonical evidence, without a false verdict."""
        with self.kernel.transaction() as tx:
            self._binding(tx, request.native_context_id)
            attempt = self._attempt(tx, document, lock=True)
            if (
                not attempt
                or attempt["disposition"] != "active"
                or attempt["head_version"] != request.expected_version
                or attempt["head_status"] == "VERIFIED"
            ):
                _error(
                    "attempt_not_abandonable", "Read current state; a verified or terminal attempt cannot be abandoned"
                )
            tx.cursor.execute(
                sql.SQL(
                    "SELECT 1 FROM {}.work_intent_claims WHERE attempt_id=%s AND expires_at>clock_timestamp()"
                ).format(sql.Identifier(tx.schema)),
                (document,),
            )
            if tx.cursor.fetchone():
                _error("live_artifact_claim", "An attempt with a live artifact claim cannot be abandoned")
            invalid = False
            try:
                self._head(tx, attempt)
                self._scope(tx, attempt)
            except PostgresKernelError as error:
                if error.code not in {"broken_bridge_chain", "scope_changed", "not_found", "invalid_membership"}:
                    raise
                invalid = True
            if not invalid:
                _error(
                    "attempt_still_valid",
                    "Continue the lawful chain; canonical state does not demonstrate an unusable attempt",
                )
            tx.cursor.execute(
                sql.SQL("UPDATE {}.bridge_attempts SET disposition='abandoned' WHERE id=%s").format(
                    sql.Identifier(tx.schema)
                ),
                (document,),
            )
            self._purge(tx, document)
            return {"document": document, "disposition": "abandoned", "work_item_id": attempt["work_item_id"]}
