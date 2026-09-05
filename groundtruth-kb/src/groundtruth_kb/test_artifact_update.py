"""Governed CAS/idempotent update service for canonical TEST artifacts.

The service is the sole ordinary TEST mutation route.
Callers provide the exact execution project, work item, approved bridge chain,
session context, expected TEST version, and an idempotency key.  The service
revalidates those facts at the protected effect boundary and commits the TEST
version, durable replay receipt, and pipeline event in one SQLite transaction.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.db import (
    WORK_ITEM_TERMINAL_RESOLUTION_STATUSES,
    KnowledgeDB,
    _validate_application_scope,
)
from groundtruth_kb.project.lifecycle import PROJECT_DEPENDENCY_KIND_REGISTRY

REQUEST_SCHEMA_VERSION = 1
_TEST_TYPES = frozenset({"assertion", "e2e", "integration", "manual", "unit"})
_RESULT_TYPES = frozenset({"blocked", "error", "fail", "pass", "skipped"})
_MUTABLE_FIELDS = (
    "title",
    "spec_id",
    "test_type",
    "test_file",
    "test_class",
    "test_function",
    "description",
    "expected_outcome",
    "last_result",
    "last_executed_at",
    "application_scope",
)
_REQUIRED_FIELDS = frozenset({"title", "spec_id", "test_type", "expected_outcome"})
_VERSIONED_BRIDGE_RE = re.compile(r"^(?P<slug>[a-z0-9][a-z0-9-]*)-(?P<version>\d{3})\.md$")


class TestArtifactUpdateError(RuntimeError):
    """Raised only for caller/programming errors outside a typed service result."""


@dataclass(frozen=True)
class TestArtifactUpdateRequest:
    test_id: str
    expected_version: int
    idempotency_key: str
    project_id: str
    work_item_id: str
    bridge_slug: str
    actor_session_context_id: str
    changed_by: str
    change_reason: str
    updates: dict[str, Any] = field(default_factory=dict)
    execution_evidence: dict[str, str] | None = None
    dry_run: bool = False


@dataclass(frozen=True)
class TestArtifactUpdateResult:
    status: str
    test_id: str
    expected_version: int
    applied: bool = False
    replayed: bool = False
    reason_code: str | None = None
    recovery: str | None = None
    request_digest: str | None = None
    postimage_digest: str | None = None
    postimage: dict[str, Any] | None = None
    row: dict[str, Any] | None = None
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "test_id": self.test_id,
            "expected_version": self.expected_version,
            "applied": self.applied,
            "replayed": self.replayed,
            "reason_code": self.reason_code,
            "recovery": self.recovery,
            "request_digest": self.request_digest,
            "postimage_digest": self.postimage_digest,
            "postimage": self.postimage,
            "row": self.row,
            "evidence": self.evidence,
        }


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalized_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None


def _json_string_list(raw: Any) -> list[str]:
    if raw in (None, ""):
        return []
    parsed = raw if isinstance(raw, list) else json.loads(str(raw))
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("expected JSON list of strings")
    return parsed


def _execution_definition_digest(postimage: dict[str, Any]) -> str:
    material = {
        name: postimage.get(name)
        for name in (
            "application_scope",
            "expected_outcome",
            "spec_id",
            "test_class",
            "test_file",
            "test_function",
            "test_type",
        )
    }
    return _sha256_text(_canonical_json(material))


def _metadata_value(content: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", content)
    return match.group(1).strip() if match else None


def _bridge_version(path: Path, slug: str) -> int | None:
    match = _VERSIONED_BRIDGE_RE.fullmatch(path.name)
    if match is None or match.group("slug") != slug:
        return None
    return int(match.group("version"))


def _latest_bridge_file(project_root: Path, slug: str) -> Path:
    bridge_dir = project_root / "bridge"
    versions = [
        (version, path)
        for path in bridge_dir.glob(f"{slug}-*.md")
        if (version := _bridge_version(path, slug)) is not None
    ]
    if not versions:
        raise TestArtifactUpdateError(f"no bridge chain exists for {slug}")
    return max(versions, key=lambda item: item[0])[1]


def _resolve_bridge_lineage(project_root: Path, request: TestArtifactUpdateRequest) -> dict[str, Any]:
    latest = _latest_bridge_file(project_root, request.bridge_slug)
    go_bytes = latest.read_bytes()
    go_text = go_bytes.decode("utf-8-sig")
    go_lines = go_text.splitlines()
    if not go_lines or go_lines[0].strip() != "GO":
        raise TestArtifactUpdateError(f"current bridge status is not GO: {latest.relative_to(project_root)}")
    if _metadata_value(go_text, "Document") != request.bridge_slug:
        raise TestArtifactUpdateError("current GO Document does not match requested bridge slug")
    if _metadata_value(go_text, "Work Item") != request.work_item_id:
        raise TestArtifactUpdateError("current GO work item does not match request")
    if _metadata_value(go_text, "Project") != request.project_id:
        raise TestArtifactUpdateError("current GO project does not match request")

    responds_to = _metadata_value(go_text, "Responds to")
    if not responds_to or "`" in responds_to:
        raise TestArtifactUpdateError("current GO has no exact unquoted proposal predecessor")
    proposal_rel = responds_to.replace("\\", "/")
    proposal = (project_root / proposal_rel).resolve()
    if not proposal.is_relative_to(project_root.resolve()) or not proposal.is_file():
        raise TestArtifactUpdateError("current GO proposal predecessor is outside the project or missing")
    proposal_text = proposal.read_text(encoding="utf-8-sig")
    proposal_lines = proposal_text.splitlines()
    if not proposal_lines or proposal_lines[0].strip() not in {"NEW", "REVISED"}:
        raise TestArtifactUpdateError("GO predecessor is not an implementation proposal")
    if _metadata_value(proposal_text, "Document") != request.bridge_slug:
        raise TestArtifactUpdateError("proposal Document does not match requested bridge slug")
    if _metadata_value(proposal_text, "Work Item") != request.work_item_id:
        raise TestArtifactUpdateError("proposal work item does not match request")
    if _metadata_value(proposal_text, "Project") != request.project_id:
        raise TestArtifactUpdateError("proposal project does not match request")
    raw_targets = _metadata_value(proposal_text, "test_artifact_targets")
    if raw_targets is None:
        raise TestArtifactUpdateError("proposal omits typed test_artifact_targets")
    try:
        targets = json.loads(raw_targets)
    except json.JSONDecodeError as exc:
        raise TestArtifactUpdateError("proposal test_artifact_targets is invalid JSON") from exc
    if not isinstance(targets, list) or not all(isinstance(item, str) and item.strip() for item in targets):
        raise TestArtifactUpdateError("proposal test_artifact_targets must be a JSON list of exact TEST ids")
    if "*" in targets or request.test_id not in targets:
        raise TestArtifactUpdateError(f"proposal target scope does not include exact TEST id {request.test_id}")

    return {
        "go_file": latest.relative_to(project_root).as_posix(),
        "go_sha256": hashlib.sha256(go_bytes).hexdigest(),
        "proposal_file": proposal.relative_to(project_root).as_posix(),
        "test_artifact_targets": targets,
    }


def _build_postimage(current: dict[str, Any], request: TestArtifactUpdateRequest) -> dict[str, Any]:
    unknown = sorted(set(request.updates) - set(_MUTABLE_FIELDS))
    if unknown:
        raise TestArtifactUpdateError("unsupported TEST field(s): " + ", ".join(unknown))
    postimage = {name: current.get(name) for name in _MUTABLE_FIELDS}
    for name, value in request.updates.items():
        if isinstance(value, str):
            value = _normalized_text(value)
            if name in _REQUIRED_FIELDS:
                value = value.strip()
        postimage[name] = value
    definition_fields = {
        "application_scope",
        "expected_outcome",
        "spec_id",
        "test_class",
        "test_file",
        "test_function",
        "test_type",
    }
    if any(name in request.updates and postimage[name] != current.get(name) for name in definition_fields):
        postimage["last_result"] = None
        postimage["last_executed_at"] = None
    for name in _REQUIRED_FIELDS:
        value = postimage[name]
        if not isinstance(value, str) or not value.strip():
            raise TestArtifactUpdateError(f"{name} must be a non-empty string")
    if postimage["test_type"] not in _TEST_TYPES:
        raise TestArtifactUpdateError("test_type must be one of: " + ", ".join(sorted(_TEST_TYPES)))
    if postimage["last_result"] is not None and postimage["last_result"] not in _RESULT_TYPES:
        raise TestArtifactUpdateError("last_result must be null or one of: " + ", ".join(sorted(_RESULT_TYPES)))
    if postimage["last_result"] == "pass":
        evidence = request.execution_evidence
        if not isinstance(evidence, dict):
            raise TestArtifactUpdateError("last_result=pass requires exact execution evidence")
        evidence_sha256 = str(evidence.get("sha256") or "")
        evidence_executed_at = str(evidence.get("executed_at") or "")
        if not re.fullmatch(r"[0-9a-f]{64}", evidence_sha256) or _parse_utc(evidence_executed_at) is None:
            raise TestArtifactUpdateError("execution evidence requires lowercase sha256 and UTC executed_at")
        if evidence_sha256 != _execution_definition_digest(postimage):
            raise TestArtifactUpdateError("execution evidence sha256 does not match the exact TEST definition")
        if postimage["last_executed_at"] != evidence_executed_at:
            raise TestArtifactUpdateError("last_executed_at must exactly match execution evidence")
    postimage["application_scope"] = _validate_application_scope(postimage["application_scope"])
    postimage.update(
        {
            "id": request.test_id,
            "version": request.expected_version + 1,
            "changed_by": request.changed_by.strip(),
            "change_reason": _normalized_text(request.change_reason.strip()),
        }
    )
    if not postimage["changed_by"] or not postimage["change_reason"]:
        raise TestArtifactUpdateError("changed_by and change_reason must be non-empty")
    return postimage


def _postimage_digest(postimage: dict[str, Any]) -> str:
    return _sha256_text(_canonical_json(postimage))


def _request_digest(
    request: TestArtifactUpdateRequest,
    postimage_digest: str,
    lineage: dict[str, Any],
) -> str:
    material = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "operation": "test_artifact_update",
        "test_id": request.test_id,
        "expected_version": request.expected_version,
        "postimage_digest": postimage_digest,
        "project_id": request.project_id,
        "work_item_id": request.work_item_id,
        "bridge_slug": request.bridge_slug,
        "go_file": lineage["go_file"],
        "go_sha256": lineage["go_sha256"],
        "actor_session_context_id": request.actor_session_context_id,
        "changed_by": request.changed_by,
        "change_reason": _normalized_text(request.change_reason),
        "execution_evidence": request.execution_evidence,
    }
    return _sha256_text(_canonical_json(material))


def _denied(request: TestArtifactUpdateRequest, code: str, detail: str, **evidence: Any) -> TestArtifactUpdateResult:
    return TestArtifactUpdateResult(
        status="denied",
        test_id=request.test_id,
        expected_version=request.expected_version,
        reason_code=code,
        recovery=detail,
        evidence=evidence,
    )


def _validate_replay(
    conn: sqlite3.Connection,
    request: TestArtifactUpdateRequest,
    receipt: dict[str, Any],
    request_digest: str,
) -> TestArtifactUpdateResult:
    if receipt["request_schema_version"] != REQUEST_SCHEMA_VERSION:
        return TestArtifactUpdateResult(
            status="recovery_required",
            test_id=request.test_id,
            expected_version=request.expected_version,
            reason_code="receipt_schema_unsupported",
            recovery="Use a reader that supports the stored receipt schema; do not append a replacement version.",
        )
    if receipt["request_digest"] != request_digest:
        return _denied(
            request,
            "idempotency_conflict",
            "Use a fresh idempotency key for a materially different request.",
            stored_request_digest=receipt["request_digest"],
            supplied_request_digest=request_digest,
        )
    try:
        payload = json.loads(receipt["result_payload_json"])
    except (TypeError, json.JSONDecodeError):
        payload = None
    if not isinstance(payload, dict) or _sha256_text(_canonical_json(payload)) != receipt["result_receipt_digest"]:
        return TestArtifactUpdateResult(
            status="recovery_required",
            test_id=request.test_id,
            expected_version=request.expected_version,
            reason_code="receipt_corrupt",
            recovery="Inspect the durable receipt and bound TEST version; do not retry with another key.",
        )
    row = payload.get("row")
    postimage = payload.get("postimage")
    replay_evidence = payload.get("evidence")
    canonical = _exact_test_version(conn, receipt["test_id"], receipt["result_test_version"])
    if (
        not isinstance(row, dict)
        or not isinstance(postimage, dict)
        or not isinstance(replay_evidence, dict)
        or canonical is None
        or row != canonical
        or row.get("id") != receipt["test_id"]
        or row.get("version") != receipt["result_test_version"]
        or payload.get("postimage_digest") != receipt["result_postimage_digest"]
        or _postimage_digest(postimage) != receipt["result_postimage_digest"]
        or any(canonical.get(key) != value for key, value in postimage.items())
    ):
        return TestArtifactUpdateResult(
            status="recovery_required",
            test_id=request.test_id,
            expected_version=request.expected_version,
            reason_code="receipt_result_mismatch",
            recovery="Inspect the receipt and exact historical TEST row; do not append a replacement version.",
        )
    return TestArtifactUpdateResult(
        status="replay",
        test_id=request.test_id,
        expected_version=request.expected_version,
        replayed=True,
        request_digest=request_digest,
        postimage_digest=receipt["result_postimage_digest"],
        postimage=postimage,
        row=row,
        evidence={
            **replay_evidence,
            "result_test_version": receipt["result_test_version"],
        },
    )


def _validate_db_authority(
    conn: sqlite3.Connection,
    request: TestArtifactUpdateRequest,
    postimage: dict[str, Any],
    *,
    now: datetime,
) -> dict[str, Any]:
    project = conn.execute(
        "SELECT id, version, status FROM current_projects WHERE id = ?",
        (request.project_id,),
    ).fetchone()
    if project is None or project["status"] != "active":
        raise TestArtifactUpdateError("exact_execution_project_missing_or_inactive")
    work_item = conn.execute(
        "SELECT id, version, resolution_status FROM current_work_items WHERE id = ?",
        (request.work_item_id,),
    ).fetchone()
    if work_item is None:
        raise TestArtifactUpdateError("exact_work_item_missing")
    if work_item["resolution_status"] in WORK_ITEM_TERMINAL_RESOLUTION_STATUSES:
        raise TestArtifactUpdateError("exact_work_item_terminal")

    memberships = conn.execute(
        """SELECT * FROM current_project_work_item_memberships
           WHERE work_item_id = ? AND status = 'active'""",
        (request.work_item_id,),
    ).fetchall()
    if len(memberships) != 1 or memberships[0]["project_id"] != request.project_id:
        raise TestArtifactUpdateError("exact_project_membership_missing_or_ambiguous")

    # Authorization gates dispatch, not this protected effect. Exact project
    # membership above supplies the work-item scope used at operation time.
    spec_id = str(postimage["spec_id"])

    dependencies = conn.execute(
        """SELECT d.*, p.status AS prerequisite_status
           FROM current_project_dependencies d
           LEFT JOIN current_projects p ON p.id = d.prerequisite_project_id
           WHERE d.dependent_project_id = ?
             AND d.status = 'active'
             AND d.affected_gate = 'readiness'""",
        (request.project_id,),
    ).fetchall()
    for dependency in dependencies:
        dependency_id = str(dependency["id"])
        dependency_kind = str(dependency["dependency_kind"] or "").strip()
        definition = PROJECT_DEPENDENCY_KIND_REGISTRY.get(dependency_kind)
        if not isinstance(definition, dict):
            raise TestArtifactUpdateError(f"project_dependency_kind_unsupported:{dependency_id}:readiness")
        required_state = str(dependency["required_prerequisite_state"] or "").strip()
        satisfying_states_by_required = definition.get("satisfying_states")
        if not isinstance(satisfying_states_by_required, dict):
            raise TestArtifactUpdateError(f"project_dependency_kind_unsupported:{dependency_id}:readiness")
        satisfying_states = satisfying_states_by_required.get(required_state)
        if not isinstance(satisfying_states, (list, tuple)) or not satisfying_states:
            raise TestArtifactUpdateError(f"project_dependency_required_state_unsupported:{dependency_id}:readiness")
        prerequisite_status = str(dependency["prerequisite_status"] or "").strip()
        if prerequisite_status not in satisfying_states:
            raise TestArtifactUpdateError(f"project_dependency_unsatisfied:{dependency_id}:readiness")

    formal = conn.execute("SELECT id, version, status FROM current_specifications WHERE id = ?", (spec_id,)).fetchone()
    if formal is None or formal["status"] != "active":
        raise TestArtifactUpdateError("applicable_formal_authority_missing_or_inactive")

    claim = conn.execute("SELECT * FROM work_intent_claims WHERE thread_slug = ?", (request.bridge_slug,)).fetchone()
    if claim is None:
        raise TestArtifactUpdateError("matching_live_work_intent_claim_missing")
    claim = dict(claim)
    if (
        claim.get("claim_kind") != "go_implementation"
        or claim.get("acting_role") != "prime-builder"
        or not str(claim.get("session_envelope_id") or "").strip()
        or not str(claim.get("acting_role_attestation") or "").strip()
        or claim.get("session_id") != request.actor_session_context_id
        or claim.get("project_id") != request.project_id
        or claim.get("work_item_id") != request.work_item_id
    ):
        raise TestArtifactUpdateError("matching_live_work_intent_claim_mismatch")
    acquired_at = _parse_utc(claim.get("acquired_at"))
    if acquired_at is None or acquired_at > now:
        raise TestArtifactUpdateError("matching_live_work_intent_claim_acquisition_invalid")
    expiries = [
        value
        for value in (
            _parse_utc(claim.get("ttl_expires_at")),
            _parse_utc(claim.get("implementation_grace_expires_at")),
        )
        if value is not None
    ]
    if not expiries:
        raise TestArtifactUpdateError("matching_live_work_intent_claim_expiry_missing")
    expiry = min(expiries)
    if now >= expiry:
        raise TestArtifactUpdateError("matching_live_work_intent_claim_expired")
    return {
        "project_version": project["version"],
        "work_item_version": work_item["version"],
        "membership_id": memberships[0]["id"],
        "formal_source_id": formal["id"],
        "formal_source_version": formal["version"],
        "claim_acquired_at": claim["acquired_at"],
    }


def _receipt(conn: sqlite3.Connection, key: str) -> dict[str, Any] | None:
    return _row_dict(
        conn.execute("SELECT * FROM test_artifact_update_requests WHERE idempotency_key = ?", (key,)).fetchone()
    )


def _exact_test_version(
    conn: sqlite3.Connection,
    test_id: str,
    version: int,
) -> dict[str, Any] | None:
    return _row_dict(
        conn.execute(
            "SELECT * FROM tests WHERE id = ? AND version = ?",
            (test_id, version),
        ).fetchone()
    )


def _replay_from_receipt(
    conn: sqlite3.Connection,
    request: TestArtifactUpdateRequest,
    receipt: dict[str, Any],
) -> TestArtifactUpdateResult:
    base = _exact_test_version(conn, request.test_id, request.expected_version)
    if base is None:
        return TestArtifactUpdateResult(
            status="recovery_required",
            test_id=request.test_id,
            expected_version=request.expected_version,
            reason_code="receipt_base_version_missing",
            recovery="Restore or inspect the exact historical TEST base version; do not append a replacement version.",
        )
    try:
        postimage = _build_postimage(base, request)
    except (TestArtifactUpdateError, ValueError) as exc:
        return _denied(request, "validation_failed", str(exc))
    lineage = {
        "go_file": receipt["go_file"],
        "go_sha256": receipt["go_sha256"],
    }
    request_digest = _request_digest(request, _postimage_digest(postimage), lineage)
    return _validate_replay(conn, request, receipt, request_digest)


def update_test_artifact(
    db: KnowledgeDB,
    request: TestArtifactUpdateRequest,
    *,
    project_root: Path,
) -> TestArtifactUpdateResult:
    """Inspect or apply one governed TEST update with durable exact replay."""

    if not request.test_id.strip() or request.expected_version < 1 or not request.idempotency_key.strip():
        return _denied(
            request,
            "invalid_request",
            "TEST id, positive expected version, and idempotency key are required.",
        )
    conn = db._get_conn()
    existing = _receipt(conn, request.idempotency_key)
    if existing is not None:
        return _replay_from_receipt(conn, request, existing)
    current = _row_dict(conn.execute("SELECT * FROM current_tests WHERE id = ?", (request.test_id,)).fetchone())
    if current is None:
        return _denied(request, "test_not_found", f"Create {request.test_id} through the governed create path first.")
    base = _exact_test_version(conn, request.test_id, request.expected_version)
    if base is None or int(current["version"]) != request.expected_version:
        return _denied(
            request,
            "stale_expected_version",
            "Re-read the current TEST and construct a fresh request with a fresh idempotency key.",
            current_version=current["version"],
        )
    try:
        postimage = _build_postimage(base, request)
        lineage = _resolve_bridge_lineage(project_root.resolve(), request)
    except (OSError, TestArtifactUpdateError, ValueError) as exc:
        return _denied(request, "validation_failed", str(exc))
    postimage_digest = _postimage_digest(postimage)
    request_digest = _request_digest(request, postimage_digest, lineage)

    if request.dry_run:
        try:
            authority = _validate_db_authority(conn, request, postimage, now=datetime.now(UTC))
        except TestArtifactUpdateError as exc:
            return _denied(request, str(exc), "Restore the named live predicate, then re-inspect the request.")
        return TestArtifactUpdateResult(
            status="dry_run",
            test_id=request.test_id,
            expected_version=request.expected_version,
            request_digest=request_digest,
            postimage_digest=postimage_digest,
            postimage=postimage,
            evidence={
                "request_schema_version": REQUEST_SCHEMA_VERSION,
                "idempotency_collision": False,
                **lineage,
                **authority,
            },
        )

    try:
        conn.execute("BEGIN IMMEDIATE")
        existing = _receipt(conn, request.idempotency_key)
        if existing is not None:
            result = _replay_from_receipt(conn, request, existing)
            conn.rollback()
            return result
        current = _row_dict(conn.execute("SELECT * FROM current_tests WHERE id = ?", (request.test_id,)).fetchone())
        if current is None:
            conn.rollback()
            return _denied(request, "test_not_found", "The TEST disappeared before the protected effect.")
        if int(current["version"]) != request.expected_version:
            conn.rollback()
            return _denied(
                request,
                "stale_expected_version",
                "Re-read current state and use a fresh key; no effect was committed.",
                current_version=current["version"],
            )
        postimage = _build_postimage(current, request)
        postimage_digest = _postimage_digest(postimage)
        lineage = _resolve_bridge_lineage(project_root.resolve(), request)
        request_digest = _request_digest(request, postimage_digest, lineage)
        authority = _validate_db_authority(conn, request, postimage, now=datetime.now(UTC))

        if postimage["last_result"] == "pass" and db._gate_registry is not None:
            db._gate_registry.run_pre_test_pass(
                request.test_id,
                postimage["spec_id"],
                postimage["test_file"],
                {
                    "test_type": postimage["test_type"],
                    "test_file": postimage["test_file"],
                    "spec_id": postimage["spec_id"],
                },
            )
        changed_at = _now_iso()
        conn.execute(
            """INSERT INTO tests
               (id, version, title, spec_id, test_type, test_file, test_class,
                test_function, description, expected_outcome, last_result,
                last_executed_at, application_scope, changed_by, changed_at, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                postimage["id"],
                postimage["version"],
                postimage["title"],
                postimage["spec_id"],
                postimage["test_type"],
                postimage["test_file"],
                postimage["test_class"],
                postimage["test_function"],
                postimage["description"],
                postimage["expected_outcome"],
                postimage["last_result"],
                postimage["last_executed_at"],
                postimage["application_scope"],
                postimage["changed_by"],
                changed_at,
                postimage["change_reason"],
            ),
        )
        db._record_event(
            conn,
            "test_artifact_updated",
            request.changed_by,
            artifact_id=request.test_id,
            artifact_type="test",
            artifact_version=postimage["version"],
            metadata={
                "bridge_slug": request.bridge_slug,
                "work_item_id": request.work_item_id,
                "request_digest": request_digest,
                "postimage_digest": postimage_digest,
            },
        )
        row = _row_dict(
            conn.execute(
                "SELECT * FROM tests WHERE id = ? AND version = ?",
                (request.test_id, postimage["version"]),
            ).fetchone()
        )
        if row is None or _postimage_digest({key: row[key] for key in postimage}) != postimage_digest:
            raise TestArtifactUpdateError("canonical_readback_mismatch")
        payload = {
            "row": row,
            "postimage": postimage,
            "request_digest": request_digest,
            "postimage_digest": postimage_digest,
            "evidence": {
                "request_schema_version": REQUEST_SCHEMA_VERSION,
                "idempotency_collision": False,
                **lineage,
                **authority,
                "execution_evidence": request.execution_evidence,
            },
        }
        payload_json = _canonical_json(payload)
        receipt_digest = _sha256_text(payload_json)
        conn.execute(
            """INSERT INTO test_artifact_update_requests
               (idempotency_key, request_schema_version, request_digest, test_id,
                expected_test_version, result_test_version, result_postimage_digest,
                result_payload_json, result_receipt_digest, project_id, work_item_id,
                bridge_slug, go_file, go_sha256, actor_session_context_id, created_at,
                changed_by, change_reason)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                request.idempotency_key,
                REQUEST_SCHEMA_VERSION,
                request_digest,
                request.test_id,
                request.expected_version,
                postimage["version"],
                postimage_digest,
                payload_json,
                receipt_digest,
                request.project_id,
                request.work_item_id,
                request.bridge_slug,
                lineage["go_file"],
                lineage["go_sha256"],
                request.actor_session_context_id,
                changed_at,
                request.changed_by,
                request.change_reason,
            ),
        )
        persisted = _receipt(conn, request.idempotency_key)
        if persisted is None or persisted["result_receipt_digest"] != receipt_digest:
            raise TestArtifactUpdateError("durable_receipt_readback_mismatch")
        conn.commit()
    except TestArtifactUpdateError as exc:
        conn.rollback()
        reason_code = str(exc).split(":", 1)[0]
        return _denied(request, reason_code, f"No effect committed: {exc}")
    except Exception as exc:
        conn.rollback()
        return _denied(request, "protected_effect_failed", f"No effect committed: {exc}")

    exact = _row_dict(
        conn.execute(
            "SELECT * FROM tests WHERE id = ? AND version = ?",
            (request.test_id, postimage["version"]),
        ).fetchone()
    )
    if exact is None or _postimage_digest({key: exact[key] for key in postimage}) != postimage_digest:
        return TestArtifactUpdateResult(
            status="recovery_required",
            test_id=request.test_id,
            expected_version=request.expected_version,
            reason_code="post_commit_readback_mismatch",
            recovery="Inspect the committed TEST version and durable receipt; do not retry with another key.",
            request_digest=request_digest,
            postimage_digest=postimage_digest,
        )
    return TestArtifactUpdateResult(
        status="applied",
        test_id=request.test_id,
        expected_version=request.expected_version,
        applied=True,
        request_digest=request_digest,
        postimage_digest=postimage_digest,
        postimage=postimage,
        row=exact,
        evidence={
            "request_schema_version": REQUEST_SCHEMA_VERSION,
            "idempotency_collision": False,
            **lineage,
            **authority,
        },
    )


def update_test_artifact_for_maintenance(
    db: KnowledgeDB,
    *,
    project_root: Path,
    project_id: str,
    work_item_id: str,
    bridge_slug: str,
    actor_session_context_id: str,
    test_id: str,
    changed_by: str,
    change_reason: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    """Apply one maintenance-script update through the governed service.

    The deterministic key binds the approved chain, exact preimage version,
    actor, reason, and normalized update payload. Re-running the same script
    action therefore returns the durable replay instead of appending a second
    TEST version.
    """

    current = db.get_test(test_id)
    if current is None:
        raise TestArtifactUpdateError(f"Test {test_id} not found")
    key_material = {
        "actor_session_context_id": actor_session_context_id,
        "bridge_slug": bridge_slug,
        "change_reason": change_reason,
        "changed_by": changed_by,
        "expected_version": current["version"],
        "project_id": project_id,
        "test_id": test_id,
        "updates": updates,
        "work_item_id": work_item_id,
    }
    request = TestArtifactUpdateRequest(
        test_id=test_id,
        expected_version=int(current["version"]),
        idempotency_key=f"maintenance:{bridge_slug}:{_sha256_text(_canonical_json(key_material))}",
        project_id=project_id,
        work_item_id=work_item_id,
        bridge_slug=bridge_slug,
        actor_session_context_id=actor_session_context_id,
        changed_by=changed_by,
        change_reason=change_reason,
        updates=updates,
    )
    result = update_test_artifact(db, request, project_root=project_root)
    if result.status not in {"applied", "replay"} or result.row is None:
        detail = result.reason_code or result.status
        recovery = f"; {result.recovery}" if result.recovery else ""
        raise TestArtifactUpdateError(f"governed TEST update refused: {detail}{recovery}")
    return result.row


__all__ = [
    "REQUEST_SCHEMA_VERSION",
    "TestArtifactUpdateError",
    "TestArtifactUpdateRequest",
    "TestArtifactUpdateResult",
    "update_test_artifact",
    "update_test_artifact_for_maintenance",
]
