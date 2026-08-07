"""Recoverable production composition for one approved modernization change.

The ``rehearse`` command executes the real workflow services in an isolated Git
repository. It is intentionally suitable for acceptance and operator rehearsal:
all bridge artifacts go through canonical writers, protected mutation goes
through PAUTH and the implementation-start gate, and recovery is durable.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from groundtruth_kb.context.manifest import assemble_context_manifest, canonical_manifest_bytes
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.git_lifecycle import GitLifecycleService, deterministic_work_branch
from groundtruth_kb.runtime_recovery import ClaimOutcome, RecoveryStore
from groundtruth_kb.session import envelope as session_envelope

PROJECT_ID = "PROJECT-E2E-001"
# Rehearsal-only synthetic specification identity, used exclusively inside the
# disposable isolated rehearsal database. It is NOT production authority.
REHEARSAL_SPEC_ID = "SPEC-E2E-001"
# Production release-candidate authority: the exact canonical governance
# specifications the workflow may cite as production authority. These resolve
# through the canonical platform MemBase, never the disposable rehearsal DB.
WORKFLOW_AUTHORITY_SPEC_IDS = ("GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",)
WORK_ITEM_ID = "WI-9001"
PAUTH_ID = "PAUTH-E2E-001"
DELIBERATION_ID = "DELIB-E2E-OWNER-001"
BRIDGE_SLUG = "modernization-e2e"
TARGET_PATH = "scripts/e2e_sample.py"
TARGET_CONTENT = b"RESULT = 'verified'\n"
PREPARED_SCHEMA_VERSION = 2
REVIEW_RECEIPT_SCHEMA_VERSION = 1
RESULT_SCHEMA_VERSION = 2
INTERRUPTED_EXIT = 75
TRUSTED_WORKER_ROLE_SOURCES = frozenset(
    {
        "dispatcher_composition",
        "interactive_transcript_explicit",
        "owner_init_keyword",
        "session_resolver_fallback",
        "transcript_init_keyword",
    }
)
INTERACTIVE_ROLE_SOURCES = frozenset(
    {
        "interactive_transcript_explicit",
        "owner_init_keyword",
        "transcript_init_keyword",
    }
)


class ModernizationWorkflowError(RuntimeError):
    """Raised when the composed modernization workflow cannot proceed safely."""


@dataclass(frozen=True)
class WorkflowActor:
    """Identity resolved from one runtime-issued canonical session envelope."""

    role: str
    session_id: str
    harness_id: str
    harness_name: str
    envelope_path: Path
    envelope_sha256: str
    role_resolution_source: str

    def __post_init__(self) -> None:
        if self.role not in {"prime-builder", "loyal-opposition"}:
            raise ModernizationWorkflowError(f"unsupported workflow actor role: {self.role}")
        if not all(
            value.strip()
            for value in (
                self.session_id,
                self.harness_id,
                self.harness_name,
                self.envelope_sha256,
                self.role_resolution_source,
            )
        ):
            raise ModernizationWorkflowError("workflow actor requires complete runtime-issued identity evidence")


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _sha256_file(path: Path) -> str:
    try:
        return _sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise ModernizationWorkflowError(f"bound workflow artifact is unreadable: {path}") from exc


def _receipt_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(value)
    payload.pop("receipt_sha256", None)
    return payload


def _receipt_sha256(value: Mapping[str, Any]) -> str:
    return _sha256_bytes(_canonical_json(_receipt_payload(value)).encode("ascii"))


def _write_receipt(path: Path, value: Mapping[str, Any]) -> dict[str, Any]:
    payload = _receipt_payload(value)
    payload["receipt_sha256"] = _receipt_sha256(payload)
    _atomic_write(path, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return payload


def _read_receipt(path: Path, *, receipt_kind: str) -> dict[str, Any]:
    receipt = _read_json(path)
    if receipt.get("schema_version") != REVIEW_RECEIPT_SCHEMA_VERSION:
        raise ModernizationWorkflowError(f"{receipt_kind} receipt has an unsupported schema")
    if receipt.get("receipt_kind") != receipt_kind:
        raise ModernizationWorkflowError(f"expected {receipt_kind} receipt; got {receipt.get('receipt_kind')!r}")
    recorded = receipt.get("receipt_sha256")
    if not isinstance(recorded, str) or recorded != _receipt_sha256(receipt):
        raise ModernizationWorkflowError(f"{receipt_kind} receipt digest does not match its content")
    return receipt


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ModernizationWorkflowError(f"cannot load production helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _resolve_platform_helper(platform_root: Path, *relative_candidates: str) -> Path:
    """Resolve a governed skill-helper path, preferring the canonical gtkb-
    prefixed location and falling back to the pre-rename name for backward
    compatibility (WI-5651 skill-rename path canonicalization)."""
    for relative in relative_candidates:
        candidate = platform_root / relative
        if candidate.is_file():
            return candidate
    return platform_root / relative_candidates[0]


def _run_git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        reason = (result.stderr or result.stdout).strip()
        raise ModernizationWorkflowError(f"git {' '.join(args)} failed: {reason}")
    return result.stdout.strip()


def _git_blob_sha256(root: Path, commit_sha: str, relative_path: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "show", f"{commit_sha}:{relative_path}"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        reason = result.stderr.decode("utf-8", errors="replace").strip()
        raise ModernizationWorkflowError(f"commit does not contain bound target {relative_path}: {reason}")
    return _sha256_bytes(result.stdout)


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.modernization.tmp")
    temporary.write_bytes(content)
    os.replace(temporary, path)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ModernizationWorkflowError(f"workflow state is unreadable: {path}") from exc
    if not isinstance(value, dict):
        raise ModernizationWorkflowError(f"workflow state is not an object: {path}")
    return value


def _validate_actor_authority(root: Path, actor: WorkflowActor, *, authority_label: str) -> None:
    identities = _read_json(root / "harness-state" / "harness-identities.json")
    identity_rows = identities.get("harnesses")
    if not isinstance(identity_rows, dict):
        raise ModernizationWorkflowError(f"{authority_label} harness identity authority is malformed")
    identity = identity_rows.get(actor.harness_name)
    if not isinstance(identity, dict) or identity.get("id") != actor.harness_id:
        raise ModernizationWorkflowError(
            f"runtime session identity is not bound by {authority_label} harness identity authority"
        )
    duplicate_names = [
        name
        for name, record in identity_rows.items()
        if name != actor.harness_name and isinstance(record, dict) and record.get("id") == actor.harness_id
    ]
    if duplicate_names:
        raise ModernizationWorkflowError(f"{authority_label} harness identity authority contains a duplicate id")

    registry = _read_json(root / "harness-state" / "harness-registry.json")
    role_rows = registry.get("harnesses")
    if not isinstance(role_rows, list):
        raise ModernizationWorkflowError(f"{authority_label} harness role authority is malformed")
    matches = [
        row
        for row in role_rows
        if isinstance(row, dict) and row.get("id") == actor.harness_id and row.get("harness_name") == actor.harness_name
    ]
    if len(matches) != 1:
        raise ModernizationWorkflowError(
            f"runtime session identity is not uniquely bound by {authority_label} harness role authority"
        )
    role_record = matches[0]
    if role_record.get("status") != "active":
        raise ModernizationWorkflowError(f"runtime harness is not active in {authority_label} harness role authority")

    # Interactive role authority is issued by the canonical session envelope.
    # The registry still authenticates the durable harness identity, but its
    # dispatcher/default role must not override an explicit transcript role.
    if actor.role_resolution_source in INTERACTIVE_ROLE_SOURCES:
        return

    roles = role_record.get("role")
    if isinstance(roles, str):
        roles = [roles]
    if not isinstance(roles, list) or actor.role not in roles:
        raise ModernizationWorkflowError(
            f"runtime session role is not active in {authority_label} harness role authority"
        )


def _resolve_workflow_actor(
    workspace: Path,
    platform_root: Path,
    *,
    session_id: str,
    required_role: str,
) -> WorkflowActor:
    try:
        provenance = session_envelope.resolve_worker_role_provenance(
            workspace,
            current_session_id=session_id,
        )
    except (session_envelope.EnvelopeError, OSError, ValueError) as exc:
        raise ModernizationWorkflowError(
            f"workflow requires a pre-existing runtime-issued session envelope: {exc}"
        ) from exc

    role = str(provenance.get("role") or "")
    harness_id = str(provenance.get("harness_id") or "")
    harness_name = str(provenance.get("harness_name") or "")
    role_source = str(provenance.get("role_resolution_source") or "")
    if role != required_role:
        raise ModernizationWorkflowError(
            f"workflow operation requires {required_role} runtime authority; session resolves to {role!r}"
        )
    if role_source not in TRUSTED_WORKER_ROLE_SOURCES:
        raise ModernizationWorkflowError("session envelope was not issued by a recognized runtime role resolver")

    envelope_path = session_envelope.worker_session_envelope_path(workspace, harness_name, session_id).resolve()
    if not envelope_path.is_file():
        raise ModernizationWorkflowError("workflow requires an exact authoritative per-session envelope document")
    envelope = _read_json(envelope_path)
    if any(
        envelope.get(field) != expected
        for field, expected in (
            ("session_id", session_id),
            ("harness_id", harness_id),
            ("harness_name", harness_name),
            ("role", role),
            ("role_resolved", role),
            ("status", "open"),
        )
    ):
        raise ModernizationWorkflowError("runtime session envelope conflicts with its authoritative provenance")

    actor = WorkflowActor(
        role=role,
        session_id=session_id,
        harness_id=harness_id,
        harness_name=harness_name,
        envelope_path=envelope_path,
        envelope_sha256=_sha256_file(envelope_path),
        role_resolution_source=role_source,
    )
    _validate_actor_authority(workspace, actor, authority_label="workspace")
    _validate_actor_authority(platform_root, actor, authority_label="platform")
    return actor


def _author_metadata(*, role: str, harness_id: str, harness_name: str, session_id: str) -> dict[str, str]:
    return {
        "author_identity": f"{role}/{harness_name}",
        "author_harness_id": harness_id,
        "author_session_context_id": session_id,
        "author_model": "modernization-acceptance",
        "author_model_version": "1",
        "author_model_configuration": "deterministic-rehearsal",
        "author_metadata_source": "modernization-workflow",
    }


@contextmanager
def _author_environment(metadata: Mapping[str, str], *, harness_name: str) -> Iterator[None]:
    names = {
        "GTKB_AUTHOR_IDENTITY": metadata["author_identity"],
        "GTKB_AUTHOR_HARNESS_ID": metadata["author_harness_id"],
        "GTKB_AUTHOR_SESSION_CONTEXT_ID": metadata["author_session_context_id"],
        "GTKB_AUTHOR_MODEL": metadata["author_model"],
        "GTKB_AUTHOR_MODEL_VERSION": metadata["author_model_version"],
        "GTKB_AUTHOR_MODEL_CONFIGURATION": metadata["author_model_configuration"],
        "GTKB_AUTHOR_METADATA_SOURCE": metadata["author_metadata_source"],
        "GTKB_HARNESS_NAME": harness_name,
        "GTKB_SESSION_ID": metadata["author_session_context_id"],
    }
    previous = {name: os.environ.get(name) for name in names}
    os.environ.update(names)
    try:
        yield
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


@contextmanager
def _work_intent_environment(names: tuple[str, ...], session_id: str) -> Iterator[None]:
    previous = {name: os.environ.get(name) for name in names}
    for name in names:
        os.environ.pop(name, None)
    os.environ["GTKB_SESSION_ID"] = session_id
    try:
        yield
    finally:
        for name in names:
            value = previous[name]
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


class ModernizationWorkflow:
    """Compose one approved change through the production modernization services."""

    def __init__(
        self,
        workspace: Path,
        platform_root: Path,
        *,
        actor: WorkflowActor,
        operation_id: str = "modernization-e2e-operation-001",
        lease_seconds: int = 30,
    ) -> None:
        self.workspace = workspace.resolve()
        self.platform_root = platform_root.resolve()
        self.actor = actor
        self.operation_id = operation_id
        self.lease_seconds = lease_seconds
        if not (self.platform_root / "groundtruth-kb" / "src" / "groundtruth_kb").is_dir():
            raise ModernizationWorkflowError(f"platform root is not a GT-KB checkout: {self.platform_root}")
        if str(self.platform_root) not in sys.path:
            sys.path.insert(0, str(self.platform_root))

        from scripts import gtkb_bridge_writer, implementation_authorization, implementation_start_gate
        from scripts.bridge_author_metadata import ensure_author_metadata, extract_author_metadata

        self.authorization = implementation_authorization
        self.start_gate = implementation_start_gate
        self.bridge_writer = gtkb_bridge_writer
        self.ensure_author_metadata = ensure_author_metadata
        self.extract_author_metadata = extract_author_metadata
        self.proposal_helper = _load_module(
            _resolve_platform_helper(
                self.platform_root,
                ".claude/skills/gtkb-bridge-propose/helpers/write_bridge.py",
            ),
            "gtkb_modernization_proposal_helper",
        )
        self.report_helper = _load_module(
            _resolve_platform_helper(
                self.platform_root,
                ".claude/skills/gtkb-bridge/helpers/impl_report_bridge.py",
            ),
            "gtkb_modernization_report_helper",
        )
        self.verify_helper = _load_module(
            _resolve_platform_helper(
                self.platform_root,
                ".claude/skills/gtkb-verify/helpers/write_verdict.py",
            ),
            "gtkb_modernization_verify_helper",
        )
        self.applicability_helper = _load_module(
            self.platform_root / "scripts/bridge_applicability_preflight.py",
            "gtkb_modernization_applicability_helper",
        )
        self.rc_checker = _load_module(
            self.platform_root / "scripts/check_modernization_release_candidate.py",
            "gtkb_modernization_rc_checker",
        )

    @property
    def state_dir(self) -> Path:
        return self.workspace / ".gtkb-state" / "modernization-workflow"

    @property
    def prepared_path(self) -> Path:
        return self.state_dir / "prepared.json"

    @property
    def proposal_request_path(self) -> Path:
        return self.state_dir / "proposal-review-request.json"

    @property
    def go_receipt_path(self) -> Path:
        return self.state_dir / "go-review-receipt.json"

    @property
    def verification_request_path(self) -> Path:
        return self.state_dir / "verification-review-request.json"

    @property
    def verification_receipt_path(self) -> Path:
        return self.state_dir / "verification-review-receipt.json"

    @property
    def result_path(self) -> Path:
        return self.state_dir / "result.json"

    @property
    def recovery_db(self) -> Path:
        return self.state_dir / "runtime-recovery.db"

    @property
    def target(self) -> Path:
        return self.workspace / TARGET_PATH

    @property
    def bridge_dir(self) -> Path:
        return self.workspace / "bridge"

    @property
    def work_branch(self) -> str:
        return deterministic_work_branch(WORK_ITEM_ID, "Implement approved end-to-end behavior")

    @property
    def actor_metadata(self) -> dict[str, str]:
        return _author_metadata(
            role=self.actor.role,
            harness_id=self.actor.harness_id,
            harness_name=self.actor.harness_name,
            session_id=self.actor.session_id,
        )

    def _require_role(self, role: str) -> None:
        if self.actor.role != role:
            raise ModernizationWorkflowError(f"workflow operation requires {role}; invocation is {self.actor.role}")

    def _initialize_repository(self) -> None:
        if (self.workspace / ".git").exists():
            raise ModernizationWorkflowError("unprepared rehearsal workspace already contains a Git repository")
        self.workspace.mkdir(parents=True, exist_ok=True)
        _run_git(self.workspace, "init", "-b", "main")
        _run_git(self.workspace, "config", "user.email", "modernization-rehearsal@invalid.local")
        _run_git(self.workspace, "config", "user.name", "GT-KB Modernization Rehearsal")
        _atomic_write(self.workspace / "README.md", b"# GT-KB modernization rehearsal\n")
        _run_git(self.workspace, "add", "README.md")
        _run_git(self.workspace, "commit", "-m", "chore: initialize modernization rehearsal")
        _run_git(self.workspace, "switch", "-c", "project/project-e2e")
        _run_git(self.workspace, "switch", "-c", self.work_branch)

    def _validate_actor_session(self) -> dict[str, Any]:
        if _sha256_file(self.actor.envelope_path) != self.actor.envelope_sha256:
            raise ModernizationWorkflowError("runtime session envelope changed after workflow authentication")
        resolved = _resolve_workflow_actor(
            self.workspace,
            self.platform_root,
            session_id=self.actor.session_id,
            required_role=self.actor.role,
        )
        if resolved != self.actor:
            raise ModernizationWorkflowError("runtime session authority changed after workflow authentication")
        return _read_json(self.actor.envelope_path)

    def _seed_selection(self) -> None:
        taxonomy_source = self.platform_root / "config/governance/project-authorization-operation-taxonomy.toml"
        taxonomy_target = self.workspace / "config/governance" / taxonomy_source.name
        taxonomy_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(taxonomy_source, taxonomy_target)
        db = KnowledgeDB(self.workspace / "groundtruth.db")
        try:
            db.insert_spec(
                id=REHEARSAL_SPEC_ID,
                title="Approved end-to-end behavior",
                description="One bounded source change must traverse the production modernization workflow.",
                status="verified",
                changed_by="modernization-owner",
                change_reason="initialize deterministic modernization rehearsal",
                source_paths=[TARGET_PATH],
                testability="automatable",
            )
            db.insert_project(
                "End-to-end modernization rehearsal",
                "modernization-owner",
                "initialize deterministic modernization rehearsal",
                id=PROJECT_ID,
                status="active",
            )
            db.insert_work_item(
                WORK_ITEM_ID,
                "Implement approved end-to-end behavior",
                "new",
                "platform",
                "open",
                "modernization-owner",
                "initialize deterministic modernization rehearsal",
                source_spec_id=REHEARSAL_SPEC_ID,
                stage="backlogged",
                approval_state="approved",
            )
            db.link_project_work_item(
                PROJECT_ID,
                WORK_ITEM_ID,
                "modernization-owner",
                "select approved modernization work",
            )
            db.insert_deliberation(
                DELIBERATION_ID,
                "owner_conversation",
                "Authorize the bounded modernization rehearsal",
                "Owner-approved acceptance scope permits one isolated source mutation.",
                "The authority is valid only inside this disposable rehearsal repository.",
                "modernization-owner",
                "record isolated acceptance authority",
                outcome="owner_decision",
            )
        finally:
            db.close()

    def _consume_actor_session(self) -> dict[str, Any]:
        session = self._validate_actor_session()
        result = {
            "session_status": session["status"],
            "session_id": self.actor.session_id,
            "harness_id": self.actor.harness_id,
            "harness_name": self.actor.harness_name,
            "role": self.actor.role,
            "role_resolution_source": self.actor.role_resolution_source,
            "session_envelope_sha256": self.actor.envelope_sha256,
        }
        if self.actor.role == "prime-builder":
            context = assemble_context_manifest(
                activity="build",
                role="Prime Builder",
                registry_path=self.platform_root / "config/registry/context-manifests.toml",
                project_root=self.platform_root,
            )
            context_path = self.state_dir / "context-manifest.json"
            _atomic_write(context_path, canonical_manifest_bytes(context) + b"\n")
            result.update(
                {
                    "active_activity": context["active_activity"],
                    "context_manifest_sha256": _sha256_bytes(canonical_manifest_bytes(context)),
                    "build_route": session_envelope.ROUTE_TARGETS["build"],
                }
            )
        return result

    def _selection_snapshot(self) -> dict[str, Any]:
        db = KnowledgeDB(self.workspace / "groundtruth.db")
        try:
            return {
                "project_selected": db.get_project(PROJECT_ID) is not None,
                "spec_selected": db.get_spec(REHEARSAL_SPEC_ID) is not None,
                "work_item_selected": db.get_work_item(WORK_ITEM_ID) is not None,
            }
        finally:
            db.close()

    def _mutation_payload(self) -> dict[str, Any]:
        patch = f"*** Begin Patch\n*** Add File: {TARGET_PATH}\n+RESULT = 'verified'\n*** End Patch\n"
        return {
            "cwd": str(self.workspace),
            "session_id": self.actor.session_id,
            "tool_name": "apply_patch",
            "tool_input": {"patch": patch},
        }

    def _prove_missing_authority_denial(self) -> dict[str, Any]:
        try:
            self.authorization.validate_targets(
                self.workspace,
                [TARGET_PATH],
                session_id=self.actor.session_id,
            )
        except self.authorization.AuthorizationError as exc:
            authorization_reason = str(exc)
        else:
            raise ModernizationWorkflowError("protected mutation unexpectedly resolved without authority")
        gate_result = self.start_gate.gate_decision(self._mutation_payload())
        if gate_result.get("decision") != "block":
            raise ModernizationWorkflowError("implementation-start gate did not deny missing authority")
        if self.target.exists():
            raise ModernizationWorkflowError("missing-authority probe created the protected target")
        return {
            "authorization_denied": True,
            "authorization_reason": authorization_reason,
            "start_gate_denied": True,
            "start_gate_reason": gate_result.get("reason", ""),
        }

    def _seed_project_authorization(self) -> None:
        db = KnowledgeDB(self.workspace / "groundtruth.db")
        try:
            db.insert_project_authorization(
                PROJECT_ID,
                "Bounded modernization rehearsal",
                DELIBERATION_ID,
                "One protected source target for the selected work item.",
                "modernization-owner",
                "authorize deterministic operation-time rehearsal",
                id=PAUTH_ID,
                status="active",
                allowed_mutation_classes=["source"],
                forbidden_operations=[],
                included_work_item_ids=[WORK_ITEM_ID],
                included_spec_ids=[REHEARSAL_SPEC_ID],
            )
        finally:
            db.close()

    @property
    def applicability_config(self) -> Path:
        return self.platform_root / "config/governance/spec-applicability.toml"

    def _pending_applicability_packet(self, content: str, *, draft_name: str) -> dict[str, Any]:
        draft = self.state_dir / "applicability-drafts" / draft_name
        _atomic_write(draft, content.encode("utf-8"))
        return self.applicability_helper.build_packet(
            bridge_id=BRIDGE_SLUG,
            bridge_dir=self.bridge_dir,
            config_path=self.applicability_config,
            db_path=self.workspace / "groundtruth.db",
            content_file=draft,
        )

    def _operative_applicability_packet(self) -> dict[str, Any]:
        packet = self.applicability_helper.build_packet(
            bridge_id=BRIDGE_SLUG,
            bridge_dir=self.bridge_dir,
            config_path=self.applicability_config,
            db_path=self.workspace / "groundtruth.db",
        )
        if packet["missing_required_specs"]:
            raise ModernizationWorkflowError(
                "operative bridge artifact lacks required specifications: "
                + ", ".join(packet["missing_required_specs"])
            )
        return packet

    def _proposal_body(self, spec_links: tuple[str, ...] = (REHEARSAL_SPEC_ID,)) -> str:
        return "\n".join(
            [
                "NEW",
                "",
                "# GT-KB Modernization End-To-End Proposal",
                "",
                "bridge_kind: prime_proposal",
                f"Document: {BRIDGE_SLUG}",
                "Version: 001 (NEW)",
                f"Project: {PROJECT_ID}",
                f"Work Item: {WORK_ITEM_ID}",
                f"Project Authorization: {PAUTH_ID}",
                f'target_paths: ["{TARGET_PATH}"]',
                "",
                "## Specification Links",
                "",
                *(f"- `{spec_id}`" for spec_id in spec_links),
                "",
                "## Requirement Sufficiency",
                "",
                "Existing approved requirements are sufficient for this bounded source mutation.",
                "",
                "## Prior Deliberations",
                "",
                f"- `{DELIBERATION_ID}` - owner authorization for this isolated rehearsal.",
                "",
                "## Specification-Derived Verification Plan",
                "",
                "| Test ID | Requirement | Verification |",
                "| --- | --- | --- |",
                f"| E2E-A1 | {REHEARSAL_SPEC_ID} | Verify exact content, recovery, and independent verdict. |",
                "",
                "## Acceptance Criteria",
                "",
                "- [ ] Missing authority is denied.",
                "- [ ] Authorized mutation is recovered exactly once.",
                "- [ ] A distinct session independently verifies the result.",
                "",
            ]
        )

    def _closed_proposal_body(self) -> tuple[str, tuple[str, ...]]:
        spec_links = {REHEARSAL_SPEC_ID}
        for _ in range(3):
            body = self._proposal_body(tuple(sorted(spec_links)))
            packet = self._pending_applicability_packet(body, draft_name="proposal.md")
            missing = set(packet["missing_required_specs"])
            if not missing:
                return body, tuple(sorted(spec_links))
            spec_links.update(missing)
        raise ModernizationWorkflowError("proposal applicability did not converge")

    def _workspace_artifact(self, value: object, *, label: str) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise ModernizationWorkflowError(f"{label} path is missing")
        target = (self.workspace / value).resolve()
        try:
            target.relative_to(self.workspace)
        except ValueError as exc:
            raise ModernizationWorkflowError(f"{label} path escapes the rehearsal workspace") from exc
        if not target.is_file():
            raise ModernizationWorkflowError(f"{label} path does not exist: {target}")
        return target

    def _input_artifact(self, path: Path, *, label: str) -> Path:
        target = path.resolve()
        try:
            target.relative_to(self.workspace)
        except ValueError as exc:
            raise ModernizationWorkflowError(f"{label} must be an in-workspace artifact") from exc
        if not target.is_file():
            raise ModernizationWorkflowError(f"{label} does not exist: {target}")
        return target

    def _validate_reviewer_authority(self, receipt: Mapping[str, Any]) -> None:
        reviewer_session = receipt.get("reviewer_session_id")
        if not isinstance(reviewer_session, str) or not reviewer_session.strip():
            raise ModernizationWorkflowError("review receipt lacks a concrete reviewer session id")
        reviewer_id = receipt.get("reviewer_harness_id")
        reviewer_name = receipt.get("reviewer_harness_name")
        reviewer_actor = _resolve_workflow_actor(
            self.workspace,
            self.platform_root,
            session_id=reviewer_session,
            required_role="loyal-opposition",
        )
        if reviewer_actor.harness_id != reviewer_id or reviewer_actor.harness_name != reviewer_name:
            raise ModernizationWorkflowError("review receipt reviewer conflicts with runtime session authority")

    def _publish_proposal(self) -> dict[str, Any]:
        proposal_body, applicable_specs = self._closed_proposal_body()
        proposal = self.proposal_helper.propose_bridge_codex_non_bypass(
            BRIDGE_SLUG,
            proposal_body,
            bridge_dir=self.bridge_dir,
            pre_populate_prior_deliberations=False,
            pre_populate_log_path=False,
            author_metadata=self.actor_metadata,
        )
        proposal_packet = self._operative_applicability_packet()
        return {
            "proposal": proposal.relative_to(self.workspace).as_posix(),
            "proposal_sha256": _sha256_file(proposal),
            "applicable_specs": list(applicable_specs),
            "proposal_preflight_packet_hash": proposal_packet["packet_hash"],
        }

    def prepare_prime(self) -> dict[str, Any]:
        self._require_role("prime-builder")
        if self.prepared_path.is_file():
            prepared = _read_json(self.prepared_path)
            if prepared.get("schema_version") != PREPARED_SCHEMA_VERSION:
                raise ModernizationWorkflowError("prepared workflow state has an unsupported schema")
            if prepared.get("prime_actor") != self.actor_metadata:
                raise ModernizationWorkflowError("prepared workflow belongs to a different Prime Builder invocation")
            return {
                "schema_version": RESULT_SCHEMA_VERSION,
                "status": "awaiting_go_review",
                "proposal_review_request": self.proposal_request_path.relative_to(self.workspace).as_posix(),
                "proposal_review_request_sha256": _sha256_file(self.proposal_request_path),
                "proposal": prepared["proposal"],
            }

        self._initialize_repository()
        self._validate_actor_session()
        self._seed_selection()
        session = self._consume_actor_session()
        selection = self._selection_snapshot()
        missing_authority = self._prove_missing_authority_denial()
        self._seed_project_authorization()
        proposal = self._publish_proposal()
        prepared = {
            "schema_version": PREPARED_SCHEMA_VERSION,
            "workspace": str(self.workspace),
            "prime_actor": self.actor_metadata,
            "session": session,
            "selection": selection,
            "missing_authority": missing_authority,
            "proposal": proposal,
        }
        _atomic_write(self.prepared_path, (json.dumps(prepared, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        request = _write_receipt(
            self.proposal_request_path,
            {
                "schema_version": REVIEW_RECEIPT_SCHEMA_VERSION,
                "receipt_kind": "proposal_review_request",
                "status": "PENDING",
                "proposal_path": proposal["proposal"],
                "proposal_sha256": proposal["proposal_sha256"],
                "prime_session_id": self.actor.session_id,
                "prime_harness_id": self.actor.harness_id,
                "project_id": PROJECT_ID,
                "work_item_id": WORK_ITEM_ID,
                "pauth_id": PAUTH_ID,
                "target_path": TARGET_PATH,
            },
        )
        return {
            "schema_version": RESULT_SCHEMA_VERSION,
            "status": "awaiting_go_review",
            "proposal": proposal,
            "proposal_review_request": self.proposal_request_path.relative_to(self.workspace).as_posix(),
            "proposal_review_request_sha256": request["receipt_sha256"],
            "selection": selection,
            "missing_authority": missing_authority,
            "session": session,
        }

    def review_proposal(self, request_path: Path) -> dict[str, Any]:
        self._require_role("loyal-opposition")
        reviewer_session = self._consume_actor_session()
        request_path = self._input_artifact(request_path, label="proposal review request")
        request = _read_receipt(request_path, receipt_kind="proposal_review_request")
        prime_session_id = request.get("prime_session_id")
        if prime_session_id == self.actor.session_id:
            raise ModernizationWorkflowError("Loyal Opposition GO review must use a distinct session identity")
        proposal = self._workspace_artifact(request.get("proposal_path"), label="proposal")
        if request.get("proposal_sha256") != _sha256_file(proposal):
            raise ModernizationWorkflowError("proposal review request does not match the exact proposal bytes")
        proposal_metadata = self.extract_author_metadata(proposal.read_text(encoding="utf-8"))
        if proposal_metadata.get("author_session_context_id") != prime_session_id:
            raise ModernizationWorkflowError("proposal author session does not match the review request")
        if proposal.read_text(encoding="utf-8").split(maxsplit=1)[0] != "NEW":
            raise ModernizationWorkflowError("GO review request does not identify a NEW proposal")

        proposal_packet = self._operative_applicability_packet()
        go_body = "\n".join(
            [
                "GO",
                "",
                "# Loyal Opposition Review",
                "",
                "bridge_kind: lo_verdict",
                f"Document: {BRIDGE_SLUG}",
                "Version: 002 (GO)",
                f"Responds to: bridge/{BRIDGE_SLUG}-001.md",
                "",
                "Independent review confirms the exact target, PAUTH scope, and objective acceptance plan.",
                "",
            ]
        ) + self.applicability_helper.format_markdown(proposal_packet)
        go = self.bridge_writer.write_bridge_file(
            BRIDGE_SLUG,
            2,
            go_body,
            self.workspace,
            author_metadata=self.actor_metadata,
        )
        receipt = _write_receipt(
            self.go_receipt_path,
            {
                "schema_version": REVIEW_RECEIPT_SCHEMA_VERSION,
                "receipt_kind": "go_review",
                "status": "GO",
                "proposal_request_path": request_path.relative_to(self.workspace).as_posix(),
                "proposal_request_sha256": _sha256_file(request_path),
                "proposal_path": proposal.relative_to(self.workspace).as_posix(),
                "proposal_sha256": _sha256_file(proposal),
                "go_path": go.relative_to(self.workspace).as_posix(),
                "go_sha256": _sha256_file(go),
                "prime_session_id": prime_session_id,
                "reviewer_session_id": self.actor.session_id,
                "reviewer_harness_id": self.actor.harness_id,
                "reviewer_harness_name": self.actor.harness_name,
                "reviewer_role": self.actor.role,
                "applicability_packet_hash": proposal_packet["packet_hash"],
            },
        )
        return {
            "schema_version": RESULT_SCHEMA_VERSION,
            "status": "go_reviewed",
            "go_review_receipt": self.go_receipt_path.relative_to(self.workspace).as_posix(),
            "go_review_receipt_sha256": receipt["receipt_sha256"],
            "proposal_path": receipt["proposal_path"],
            "go_path": receipt["go_path"],
            "reviewer_session": reviewer_session,
        }

    def _consume_go_receipt(self, receipt_path: Path, prepared: Mapping[str, Any]) -> dict[str, Any]:
        receipt_path = self._input_artifact(receipt_path, label="GO review receipt")
        receipt = _read_receipt(receipt_path, receipt_kind="go_review")
        if receipt.get("status") != "GO" or receipt.get("reviewer_role") != "loyal-opposition":
            raise ModernizationWorkflowError("implementation requires a Loyal Opposition GO receipt")
        self._validate_reviewer_authority(receipt)
        prime_actor = prepared.get("prime_actor")
        if not isinstance(prime_actor, dict):
            raise ModernizationWorkflowError("prepared workflow lacks Prime Builder provenance")
        if receipt.get("prime_session_id") != prime_actor.get("author_session_context_id"):
            raise ModernizationWorkflowError("GO receipt is not bound to the preparing Prime Builder session")
        if receipt.get("reviewer_session_id") == receipt.get("prime_session_id"):
            raise ModernizationWorkflowError("GO receipt reviewer session is not independent")
        proposal = prepared.get("proposal")
        if not isinstance(proposal, dict):
            raise ModernizationWorkflowError("prepared workflow lacks proposal evidence")
        proposal_path = self._workspace_artifact(receipt.get("proposal_path"), label="GO-bound proposal")
        if receipt.get("proposal_path") != proposal.get("proposal"):
            raise ModernizationWorkflowError("GO receipt identifies a different proposal path")
        expected_proposal_hash = proposal.get("proposal_sha256")
        if (
            receipt.get("proposal_sha256") != expected_proposal_hash
            or _sha256_file(proposal_path) != expected_proposal_hash
        ):
            raise ModernizationWorkflowError("GO receipt identifies different proposal bytes")
        go_path = self._workspace_artifact(receipt.get("go_path"), label="GO verdict")
        if _sha256_file(go_path) != receipt.get("go_sha256"):
            raise ModernizationWorkflowError("GO receipt does not match the exact GO verdict bytes")
        go_metadata = self.extract_author_metadata(go_path.read_text(encoding="utf-8"))
        if go_metadata.get("author_session_context_id") != receipt.get("reviewer_session_id") or go_metadata.get(
            "author_harness_id"
        ) != receipt.get("reviewer_harness_id"):
            raise ModernizationWorkflowError("GO verdict author session does not match the review receipt")
        if go_path.read_text(encoding="utf-8").split(maxsplit=1)[0] != "GO":
            raise ModernizationWorkflowError("GO review receipt does not identify a GO verdict")
        return receipt

    def _activate_start_authority(self) -> dict[str, Any]:
        packet = self.authorization.create_authorization_packet(
            self.workspace,
            BRIDGE_SLUG,
            session_id=self.actor.session_id,
        )
        acquired = self.authorization.bridge_work_intent_registry.acquire(
            BRIDGE_SLUG,
            self.actor.session_id,
            project_root=self.workspace,
        )
        if not acquired:
            raise ModernizationWorkflowError("Prime Builder could not acquire the bridge work-intent claim")
        started = self.authorization.finalize_implementation_start_packet(
            self.workspace,
            packet,
            session_id=self.actor.session_id,
        )
        self.authorization.write_started_packets(self.workspace, [started])
        if not isinstance(started.get("project_authorization"), dict):
            raise ModernizationWorkflowError("implementation-start packet is not PAUTH-backed")
        return {
            "bridge_id": started["bridge_id"],
            "packet_hash": started["packet_hash"],
            "project_authorization_id": started["project_authorization"]["id"],
            "implementation_start_session": started["implementation_start"]["session_id"],
        }

    def _bind_git_lifecycle(self) -> dict[str, Any]:
        service = GitLifecycleService(
            self.workspace,
            state_dir=self.state_dir / "git-lifecycle",
            dispatcher_state_dir=self.state_dir / "dispatcher",
        )
        result = service.bind_work_item(
            work_item_id=WORK_ITEM_ID,
            title="Implement approved end-to-end behavior",
            project_branch="project/project-e2e",
            scope_paths=(TARGET_PATH,),
            required_checks=("E2E-A1",),
        )
        return result.to_dict()

    def _authorize_and_apply_mutation(self) -> bool:
        with _work_intent_environment(
            self.authorization.gtkb_session_id.BRIDGE_WORK_INTENT_ORDER,
            self.actor.session_id,
        ):
            resolution = self.authorization.validate_targets(
                self.workspace,
                [TARGET_PATH],
                session_id=self.actor.session_id,
            )
            packet = resolution.get("packet")
            if not isinstance(packet, dict):
                raise ModernizationWorkflowError("protected mutation did not resolve a concrete start packet")
            if not isinstance(packet.get("project_authorization"), dict):
                raise ModernizationWorkflowError("protected mutation requires a current PAUTH-backed packet")
            decision = self.start_gate.gate_decision(self._mutation_payload())
        if decision:
            raise ModernizationWorkflowError(f"implementation-start gate denied authorized mutation: {decision}")
        if self.target.exists():
            if self.target.read_bytes() != TARGET_CONTENT:
                raise ModernizationWorkflowError("protected target exists with content outside the immutable request")
            return False
        _atomic_write(self.target, TARGET_CONTENT)
        return True

    def _preserve_implementation(self) -> str:
        service = GitLifecycleService(
            self.workspace,
            state_dir=self.state_dir / "git-lifecycle",
            dispatcher_state_dir=self.state_dir / "dispatcher",
        )
        registry = service.state.load_registry()
        binding = registry["bindings"].get(WORK_ITEM_ID)
        if not isinstance(binding, dict):
            raise ModernizationWorkflowError("Git lifecycle binding disappeared")
        lifecycle_state = binding.get("lifecycle_state")
        if lifecycle_state == "preserved":
            commit = binding.get("preserved_commit")
            if not isinstance(commit, str):
                raise ModernizationWorkflowError("preserved Git lifecycle binding lacks a commit")
            return commit
        if lifecycle_state != "active":
            raise ModernizationWorkflowError(f"unexpected Git lifecycle state: {lifecycle_state}")
        result = service.preserve_scoped_changes(
            work_item_id=WORK_ITEM_ID,
            message="feat: implement modernization end-to-end rehearsal",
            operation_id="modernization-e2e-preserve-001",
            wait_seconds=5,
        )
        if result.commit_sha is None:
            raise ModernizationWorkflowError("Git lifecycle preservation did not return a commit")
        return result.commit_sha

    def _run_objective_verification(
        self,
        *,
        receipt_path: Path,
        implementation_commit: str,
        report_sha256: str,
    ) -> dict[str, Any]:
        verification_dir = self.state_dir / "verification"
        test_path = verification_dir / "test_approved_change.py"
        if receipt_path.is_file():
            receipt = _read_receipt(receipt_path, receipt_kind="objective_verification")
            expected = {
                "status": "PASS",
                "actor_role": self.actor.role,
                "actor_session_id": self.actor.session_id,
                "implementation_commit": implementation_commit,
                "report_sha256": report_sha256,
                "target_sha256": _sha256_bytes(self.target.read_bytes()),
            }
            if any(receipt.get(key) != value for key, value in expected.items()):
                raise ModernizationWorkflowError("cached objective verification has different provenance or bindings")
            return receipt
        test_content = (
            "from pathlib import Path\n\n"
            "ROOT = Path(__file__).resolve().parents[3]\n\n"
            "def test_approved_change_has_exact_authorized_bytes():\n"
            f"    assert (ROOT / {TARGET_PATH!r}).read_bytes() == {TARGET_CONTENT!r}\n"
        ).encode()
        _atomic_write(test_path, test_content)
        relative_test = test_path.relative_to(self.workspace).as_posix()
        command = [sys.executable, "-m", "pytest", relative_test, "-q", "--tb=short"]
        completed = subprocess.run(
            command,
            cwd=self.workspace,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        output = completed.stdout + completed.stderr
        if completed.returncode != 0:
            raise ModernizationWorkflowError(f"objective verification failed: {output[-2000:]}")
        receipt = {
            "schema_version": REVIEW_RECEIPT_SCHEMA_VERSION,
            "receipt_kind": "objective_verification",
            "status": "PASS",
            "actor_role": self.actor.role,
            "actor_session_id": self.actor.session_id,
            "actor_harness_id": self.actor.harness_id,
            "implementation_commit": implementation_commit,
            "report_sha256": report_sha256,
            "command": ["python", "-m", "pytest", relative_test, "-q", "--tb=short"],
            "return_code": completed.returncode,
            "output_sha256": _sha256_bytes(output.encode("utf-8")),
            "target_sha256": _sha256_bytes(self.target.read_bytes()),
        }
        return _write_receipt(receipt_path, receipt)

    def _implementation_report_body(
        self,
        commit_sha: str,
        spec_links: tuple[str, ...],
        verification: Mapping[str, Any],
    ) -> str:
        return "\n".join(
            [
                "NEW",
                "",
                "# GT-KB Modernization End-To-End Implementation Report",
                "",
                "bridge_kind: implementation_report",
                f"Document: {BRIDGE_SLUG}",
                "Version: 003 (NEW; post-implementation report)",
                f"Responds to GO: bridge/{BRIDGE_SLUG}-002.md",
                f"Approved proposal: bridge/{BRIDGE_SLUG}-001.md",
                f"Project: {PROJECT_ID}",
                f"Work Item: {WORK_ITEM_ID}",
                f"Project Authorization: {PAUTH_ID}",
                "Recommended commit type: feat:",
                "",
                "## Implementation Claim",
                "",
                "The production workflow applied and preserved the exact authorized source mutation.",
                "",
                "## Specification Links",
                "",
                *(f"- `{spec_id}`" for spec_id in spec_links),
                "",
                "## Owner Decisions / Input",
                "",
                "No additional owner decision is required for the frozen rehearsal scope.",
                "",
                "## Prior Deliberations",
                "",
                f"- `{DELIBERATION_ID}` - bounded owner authorization.",
                "",
                "## Specification-Derived Verification Plan",
                "",
                "| Spec | Executed evidence |",
                "| --- | --- |",
                f"| {REHEARSAL_SPEC_ID} | Exact target bytes and preserved commit {commit_sha}. |",
                "",
                "## Commands Run",
                "",
                f"- `{' '.join(verification['command'])}` - PASS.",
                "",
                "## Observed Results",
                "",
                f"- E2E-A1 PASS: `{TARGET_PATH}` has SHA-256 `{_sha256_bytes(TARGET_CONTENT)}`.",
                "",
                "## Files Changed",
                "",
                f"- `{TARGET_PATH}`",
                "",
                "## Recommended Commit Type",
                "",
                "- `feat:` for the bounded production behavior.",
                "",
                "## Acceptance Criteria Status",
                "",
                "- [x] Missing authority denied.",
                "- [x] Authorized mutation preserved exactly once.",
                "- [x] Independent verification requested.",
                "",
                "## Risk And Rollback",
                "",
                "Reset the disposable repository to the project branch; no live project state is affected.",
                "",
                "## Loyal Opposition Asks",
                "",
                "1. Verify the exact target bytes and distinct-session provenance.",
                "",
            ]
        )

    def _file_report(
        self,
        commit_sha: str,
        initial_spec_links: tuple[str, ...],
        verification: Mapping[str, Any],
    ) -> Path:
        path = self.bridge_dir / f"{BRIDGE_SLUG}-003.md"
        if path.is_file():
            return path
        spec_links = set(initial_spec_links)
        for _ in range(3):
            content = self._implementation_report_body(
                commit_sha,
                tuple(sorted(spec_links)),
                verification,
            )
            packet = self._pending_applicability_packet(content, draft_name="implementation-report.md")
            missing = set(packet["missing_required_specs"])
            if not missing:
                break
            spec_links.update(missing)
        else:
            raise ModernizationWorkflowError("implementation-report applicability did not converge")
        with _author_environment(self.actor_metadata, harness_name=self.actor.harness_name):
            return self.report_helper.file_report(
                BRIDGE_SLUG,
                content=content,
                bridge_dir=self.bridge_dir,
            )

    def _verified_body(
        self,
        report_path: Path,
        commit_sha: str,
        spec_links: tuple[str, ...],
        verification: Mapping[str, Any],
    ) -> str:
        return "\n".join(
            [
                "VERIFIED",
                "",
                "# Independent Modernization Verification",
                "",
                "bridge_kind: lo_verdict",
                f"Document: {BRIDGE_SLUG}",
                "Version: 004 (VERIFIED)",
                f"Responds to: {report_path.relative_to(self.workspace).as_posix()}",
                "Recommended commit type: feat:",
                "",
                "## Verification Claim",
                "",
                "A distinct Loyal Opposition session verified the exact authorized result.",
                "",
                "## Specification Links",
                "",
                *(f"- `{spec_id}`" for spec_id in spec_links),
                "",
                "## Spec-to-Test Mapping",
                "",
                "| Spec | Test | Executed | Result |",
                "| --- | --- | --- | --- |",
                f"| {REHEARSAL_SPEC_ID} | E2E-A1 | yes | PASS at subject commit {commit_sha} |",
                "",
                "## Commands Executed",
                "",
                f"- `{' '.join(verification['command'])}` - PASS; output SHA-256 `{verification['output_sha256']}`.",
                "- Compared implementation-report author and verifier session envelopes; they are distinct.",
                "",
                "## Findings",
                "",
                "- No finding for the bounded rehearsal scope.",
                "",
            ]
        )

    def _publish_verified(
        self,
        report_path: Path,
        commit_sha: str,
        verification: Mapping[str, Any],
    ) -> tuple[Path, str]:
        target = self.bridge_dir / f"{BRIDGE_SLUG}-004.md"
        if target.is_file():
            return target, _run_git(self.workspace, "rev-parse", "HEAD")
        report_packet = self._operative_applicability_packet()
        body = self.ensure_author_metadata(
            self._verified_body(
                report_path,
                commit_sha,
                tuple(report_packet["cited_specs"]),
                verification,
            )
            + self.applicability_helper.format_markdown(report_packet),
            project_root=self.workspace,
            explicit=self.actor_metadata,
        )
        include_paths = [
            TARGET_PATH,
            f"bridge/{BRIDGE_SLUG}-001.md",
            f"bridge/{BRIDGE_SLUG}-002.md",
            report_path.relative_to(self.workspace).as_posix(),
        ]
        with _author_environment(self.actor_metadata, harness_name=self.actor.harness_name):
            finalization = self.verify_helper.finalize_verified_commit(
                BRIDGE_SLUG,
                body,
                include_paths=include_paths,
                commit_message="test: finalize independent modernization verification",
                project_root=self.workspace,
                pre_populate=False,
                db=False,
                log_path=False,
            )
        return self.workspace / finalization.verdict_path, finalization.commit_sha

    def _write_verification_request(
        self,
        *,
        prepared: Mapping[str, Any],
        go_receipt_path: Path,
        go_receipt: Mapping[str, Any],
        report_path: Path,
        implementation_commit: str,
        implementation_check: Mapping[str, Any],
    ) -> dict[str, Any]:
        proposal = prepared.get("proposal")
        if not isinstance(proposal, dict):
            raise ModernizationWorkflowError("prepared workflow lacks proposal evidence")
        request = _write_receipt(
            self.verification_request_path,
            {
                "schema_version": REVIEW_RECEIPT_SCHEMA_VERSION,
                "receipt_kind": "verification_review_request",
                "status": "PENDING",
                "prime_session_id": self.actor.session_id,
                "prime_harness_id": self.actor.harness_id,
                "proposal_path": proposal["proposal"],
                "proposal_sha256": proposal["proposal_sha256"],
                "go_receipt_path": go_receipt_path.resolve().relative_to(self.workspace).as_posix(),
                "go_receipt_sha256": _sha256_file(go_receipt_path.resolve()),
                "go_path": go_receipt["go_path"],
                "go_sha256": go_receipt["go_sha256"],
                "report_path": report_path.relative_to(self.workspace).as_posix(),
                "report_sha256": _sha256_file(report_path),
                "implementation_commit": implementation_commit,
                "implementation_check_path": (self.state_dir / "verification" / "prime-implementation-check.json")
                .relative_to(self.workspace)
                .as_posix(),
                "implementation_check_sha256": _sha256_file(
                    self.state_dir / "verification" / "prime-implementation-check.json"
                ),
                "implementation_check_receipt_sha256": implementation_check["receipt_sha256"],
                "implementation_check_output_sha256": implementation_check["output_sha256"],
                "target_path": TARGET_PATH,
                "target_sha256": _sha256_bytes(TARGET_CONTENT),
            },
        )
        return request

    def review_implementation(self, request_path: Path) -> dict[str, Any]:
        self._require_role("loyal-opposition")
        reviewer_session = self._consume_actor_session()
        request_path = self._input_artifact(request_path, label="verification review request")
        request = _read_receipt(request_path, receipt_kind="verification_review_request")
        if request.get("prime_session_id") == self.actor.session_id:
            raise ModernizationWorkflowError("independent verification must use a distinct session identity")
        if self.verification_receipt_path.is_file():
            existing = _read_receipt(self.verification_receipt_path, receipt_kind="verification_review")
            if (
                existing.get("verification_request_sha256") != _sha256_file(request_path)
                or existing.get("reviewer_session_id") != self.actor.session_id
            ):
                raise ModernizationWorkflowError("existing verification receipt belongs to another request or reviewer")
            return {
                "schema_version": RESULT_SCHEMA_VERSION,
                "status": "independently_verified_existing",
                "verification_review_receipt": self.verification_receipt_path.relative_to(self.workspace).as_posix(),
                "verification_review_receipt_sha256": existing["receipt_sha256"],
                "verdict_path": existing["verdict_path"],
                "verification_commit": existing["verification_commit"],
                "reviewer_session": reviewer_session,
            }

        proposal_path = self._workspace_artifact(request.get("proposal_path"), label="verification-bound proposal")
        go_receipt_path = self._workspace_artifact(
            request.get("go_receipt_path"), label="verification-bound GO receipt"
        )
        go_path = self._workspace_artifact(request.get("go_path"), label="verification-bound GO")
        report_path = self._workspace_artifact(request.get("report_path"), label="implementation report")
        implementation_check_path = self._workspace_artifact(
            request.get("implementation_check_path"), label="Prime Builder implementation check"
        )
        exact_bindings = (
            (proposal_path, request.get("proposal_sha256"), "proposal"),
            (go_receipt_path, request.get("go_receipt_sha256"), "GO receipt"),
            (go_path, request.get("go_sha256"), "GO verdict"),
            (report_path, request.get("report_sha256"), "implementation report"),
            (
                implementation_check_path,
                request.get("implementation_check_sha256"),
                "Prime Builder implementation check",
            ),
        )
        for path, expected_hash, label in exact_bindings:
            if _sha256_file(path) != expected_hash:
                raise ModernizationWorkflowError(f"verification request {label} digest does not match exact bytes")
        go_receipt = _read_receipt(go_receipt_path, receipt_kind="go_review")
        self._validate_reviewer_authority(go_receipt)
        if (
            go_receipt.get("status") != "GO"
            or go_receipt.get("proposal_path") != request.get("proposal_path")
            or go_receipt.get("proposal_sha256") != request.get("proposal_sha256")
            or go_receipt.get("go_path") != request.get("go_path")
            or go_receipt.get("go_sha256") != request.get("go_sha256")
            or go_receipt.get("prime_session_id") != request.get("prime_session_id")
        ):
            raise ModernizationWorkflowError("verification request is not bound to the operative GO review")
        implementation_check = _read_receipt(implementation_check_path, receipt_kind="objective_verification")
        if (
            implementation_check.get("actor_role") != "prime-builder"
            or implementation_check.get("actor_session_id") != request.get("prime_session_id")
            or implementation_check.get("implementation_commit") != request.get("implementation_commit")
            or implementation_check.get("receipt_sha256") != request.get("implementation_check_receipt_sha256")
        ):
            raise ModernizationWorkflowError("Prime Builder implementation check has invalid provenance or bindings")
        report_metadata = self.extract_author_metadata(report_path.read_text(encoding="utf-8"))
        if report_metadata.get("author_session_context_id") != request.get("prime_session_id"):
            raise ModernizationWorkflowError("implementation report author does not match its review request")
        commit_sha = request.get("implementation_commit")
        if not isinstance(commit_sha, str) or _run_git(self.workspace, "rev-parse", commit_sha) != commit_sha:
            raise ModernizationWorkflowError("verification request implementation commit is not exact")
        if _git_blob_sha256(self.workspace, commit_sha, TARGET_PATH) != request.get("target_sha256"):
            raise ModernizationWorkflowError("implementation commit does not contain the exact requested target bytes")
        if _sha256_bytes(self.target.read_bytes()) != request.get("target_sha256"):
            raise ModernizationWorkflowError("working target differs from the review subject commit")

        clean_run_path = self.state_dir / "verification" / f"lo-clean-run-{self.actor.session_id}.json"
        clean_run = self._run_objective_verification(
            receipt_path=clean_run_path,
            implementation_commit=commit_sha,
            report_sha256=str(request["report_sha256"]),
        )
        verdict, verification_commit = self._publish_verified(report_path, commit_sha, clean_run)
        receipt = _write_receipt(
            self.verification_receipt_path,
            {
                "schema_version": REVIEW_RECEIPT_SCHEMA_VERSION,
                "receipt_kind": "verification_review",
                "status": "VERIFIED",
                "verification_request_path": request_path.relative_to(self.workspace).as_posix(),
                "verification_request_sha256": _sha256_file(request_path),
                "proposal_path": request["proposal_path"],
                "proposal_sha256": request["proposal_sha256"],
                "report_path": request["report_path"],
                "report_sha256": request["report_sha256"],
                "implementation_commit": commit_sha,
                "clean_run_path": clean_run_path.relative_to(self.workspace).as_posix(),
                "clean_run_sha256": _sha256_file(clean_run_path),
                "clean_run_output_sha256": clean_run["output_sha256"],
                "verdict_path": verdict.relative_to(self.workspace).as_posix(),
                "verdict_sha256": _sha256_file(verdict),
                "verification_commit": verification_commit,
                "prime_session_id": request["prime_session_id"],
                "reviewer_session_id": self.actor.session_id,
                "reviewer_harness_id": self.actor.harness_id,
                "reviewer_harness_name": self.actor.harness_name,
                "reviewer_role": self.actor.role,
            },
        )
        return {
            "schema_version": RESULT_SCHEMA_VERSION,
            "status": "independently_verified",
            "verification_review_receipt": self.verification_receipt_path.relative_to(self.workspace).as_posix(),
            "verification_review_receipt_sha256": receipt["receipt_sha256"],
            "verdict_path": receipt["verdict_path"],
            "verification_commit": receipt["verification_commit"],
            "reviewer_session": reviewer_session,
        }

    def _consume_verification_receipt(
        self,
        receipt_path: Path,
        execution: Mapping[str, Any],
    ) -> dict[str, Any]:
        receipt_path = self._input_artifact(receipt_path, label="verification review receipt")
        receipt = _read_receipt(receipt_path, receipt_kind="verification_review")
        if receipt.get("status") != "VERIFIED" or receipt.get("reviewer_role") != "loyal-opposition":
            raise ModernizationWorkflowError("finalization requires a Loyal Opposition VERIFIED receipt")
        self._validate_reviewer_authority(receipt)
        if receipt.get("prime_session_id") != self.actor.session_id:
            raise ModernizationWorkflowError("verification receipt is not bound to this Prime Builder session")
        if receipt.get("reviewer_session_id") == self.actor.session_id:
            raise ModernizationWorkflowError("verification receipt reviewer session is not independent")
        if receipt.get("implementation_commit") != execution.get("implementation_commit"):
            raise ModernizationWorkflowError("verification receipt identifies a different implementation commit")
        request_path = self._workspace_artifact(
            receipt.get("verification_request_path"), label="verification review request"
        )
        if request_path != self.verification_request_path.resolve():
            raise ModernizationWorkflowError("verification receipt identifies a non-canonical review request")
        if _sha256_file(request_path) != receipt.get("verification_request_sha256"):
            raise ModernizationWorkflowError("verification receipt does not match the exact review request")
        request = _read_receipt(request_path, receipt_kind="verification_review_request")
        for key in ("proposal_path", "proposal_sha256", "report_path", "report_sha256", "implementation_commit"):
            if receipt.get(key) != request.get(key):
                raise ModernizationWorkflowError(f"verification receipt changed the request binding: {key}")
        report_path = self._workspace_artifact(receipt.get("report_path"), label="verified implementation report")
        clean_run_path = self._workspace_artifact(receipt.get("clean_run_path"), label="independent clean run")
        verdict_path = self._workspace_artifact(receipt.get("verdict_path"), label="VERIFIED verdict")
        if _sha256_file(report_path) != receipt.get("report_sha256"):
            raise ModernizationWorkflowError("verified report bytes do not match the receipt")
        if _sha256_file(clean_run_path) != receipt.get("clean_run_sha256"):
            raise ModernizationWorkflowError("independent clean-run bytes do not match the receipt")
        clean_run = _read_receipt(clean_run_path, receipt_kind="objective_verification")
        if (
            clean_run.get("status") != "PASS"
            or clean_run.get("actor_role") != "loyal-opposition"
            or clean_run.get("actor_session_id") != receipt.get("reviewer_session_id")
            or clean_run.get("implementation_commit") != execution.get("implementation_commit")
            or clean_run.get("report_sha256") != receipt.get("report_sha256")
            or clean_run.get("output_sha256") != receipt.get("clean_run_output_sha256")
            or clean_run.get("target_sha256") != _sha256_bytes(TARGET_CONTENT)
        ):
            raise ModernizationWorkflowError("independent clean run has invalid provenance or subject bindings")
        if _sha256_file(verdict_path) != receipt.get("verdict_sha256"):
            raise ModernizationWorkflowError("VERIFIED verdict bytes do not match the receipt")
        verdict_metadata = self.extract_author_metadata(verdict_path.read_text(encoding="utf-8"))
        if verdict_metadata.get("author_session_context_id") != receipt.get(
            "reviewer_session_id"
        ) or verdict_metadata.get("author_harness_id") != receipt.get("reviewer_harness_id"):
            raise ModernizationWorkflowError("VERIFIED verdict author does not match the review receipt")
        verification_commit = receipt.get("verification_commit")
        if (
            not isinstance(verification_commit, str)
            or _run_git(self.workspace, "rev-parse", "HEAD") != verification_commit
        ):
            raise ModernizationWorkflowError("workspace HEAD is not the receipt-bound verification commit")
        _run_git(
            self.workspace, "merge-base", "--is-ancestor", str(execution["implementation_commit"]), verification_commit
        )
        return receipt

    def _candidate_assessment(self) -> dict[str, Any]:
        manifest_path = self.platform_root / "config/governance/modernization-release-candidate.json"
        manifest = self.rc_checker.load_manifest(manifest_path)
        assessment = self.rc_checker.evaluate_status(
            manifest,
            project_root=self.platform_root,
            state_dir=self.workspace / ".gtkb-state" / "release-candidate-assessment",
        )
        acceptance = next(item for item in manifest["acceptance_tests"] if item["id"] == "AT-END-TO-END-WORKFLOW")
        # WI-5553 Slice C: bind production authority. The manifest row must
        # declare exactly the canonical authority set and every ID must resolve
        # through the canonical platform MemBase (not the disposable rehearsal DB).
        declared = list(acceptance.get("spec_ids") or [])
        authority_set = tuple(sorted(declared))
        if authority_set != tuple(sorted(WORKFLOW_AUTHORITY_SPEC_IDS)):
            raise ModernizationWorkflowError(
                "release-candidate workflow authority mismatch: "
                f"manifest declared {declared!r}, expected {WORKFLOW_AUTHORITY_SPEC_IDS!r}"
            )
        resolved_authority = []
        try:
            canonical_db = KnowledgeDB(str(self.platform_root / "groundtruth.db"))
            for spec_id in WORKFLOW_AUTHORITY_SPEC_IDS:
                resolved_authority.append(
                    {
                        "spec_id": spec_id,
                        "resolved": canonical_db.get_spec(spec_id) is not None,
                    }
                )
        except Exception as exc:  # noqa: BLE001 - fail closed on lookup failure
            raise ModernizationWorkflowError(
                f"release-candidate authority could not be resolved canonically: {exc}"
            ) from exc
        if not all(record["resolved"] for record in resolved_authority):
            raise ModernizationWorkflowError(
                "release-candidate workflow authority does not resolve in canonical MemBase: "
                + ", ".join(record["spec_id"] for record in resolved_authority if not record["resolved"])
            )
        return {
            "scope_digest_sha256": assessment["scope_digest_sha256"],
            "manifest_valid": not self.rc_checker.validate_manifest(
                manifest,
                project_root=self.platform_root,
                require_test_paths=True,
            ),
            "workflow_acceptance_test_id": acceptance["id"],
            "ready": assessment["ready"],
            "blockers": assessment["blockers"],
            "production_deployment_separate": manifest["program"]["production_deployment_separate"],
            "workflow_authority_spec_ids": list(WORKFLOW_AUTHORITY_SPEC_IDS),
            "workflow_authority_resolution": resolved_authority,
        }

    def _release_claim(self) -> None:
        holder = self.authorization.bridge_work_intent_registry.current_holder(
            BRIDGE_SLUG,
            project_root=self.workspace,
        )
        if holder is not None:
            self.authorization.bridge_work_intent_registry.release(
                BRIDGE_SLUG,
                self.actor.session_id,
                project_root=self.workspace,
            )

    def _load_prepared_for_prime(self) -> dict[str, Any]:
        if not self.prepared_path.is_file():
            raise ModernizationWorkflowError("run prime-prepare before executing the rehearsal")
        prepared = _read_json(self.prepared_path)
        if prepared.get("schema_version") != PREPARED_SCHEMA_VERSION:
            raise ModernizationWorkflowError("prepared workflow state has an unsupported schema")
        if prepared.get("prime_actor") != self.actor_metadata:
            raise ModernizationWorkflowError("rehearsal execution must use the preparing Prime Builder identity")
        return prepared

    def _finalize_execution(
        self,
        *,
        prepared: Mapping[str, Any],
        execution: Mapping[str, Any],
        verification_receipt_path: Path,
        store: RecoveryStore,
    ) -> dict[str, Any]:
        verification_receipt = self._consume_verification_receipt(verification_receipt_path, execution)
        assessment = self._candidate_assessment()
        self._release_claim()
        result = {
            **dict(execution),
            "schema_version": RESULT_SCHEMA_VERSION,
            "status": "completed",
            "author_session": self.actor.session_id,
            "verifier_session": verification_receipt["reviewer_session_id"],
            "verdict_path": verification_receipt["verdict_path"],
            "verification_commit": verification_receipt["verification_commit"],
            "verification_receipt_sha256": verification_receipt["receipt_sha256"],
            "independent_clean_run_sha256": verification_receipt["clean_run_sha256"],
            "context": prepared["session"],
            "selection": prepared["selection"],
            "missing_authority": prepared["missing_authority"],
            "start_authority": prepared["start_authority"],
            "candidate_assessment": assessment,
            "event_count": len(store.events(self.operation_id)),
            "recovery_status": "completed",
        }
        result.pop("verification_review_request", None)
        result.pop("verification_review_request_sha256", None)
        _atomic_write(self.result_path, (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        return result

    def execute(
        self,
        *,
        go_receipt_path: Path,
        verification_receipt_path: Path | None = None,
        interrupt_after_authorized_mutation: bool = False,
    ) -> tuple[int, dict[str, Any]]:
        self._require_role("prime-builder")
        prepared = self._load_prepared_for_prime()
        self._consume_actor_session()
        go_receipt_path = go_receipt_path.resolve()
        go_receipt = self._consume_go_receipt(go_receipt_path, prepared)
        if "start_authority" not in prepared:
            prepared["start_authority"] = self._activate_start_authority()
            prepared["git_binding"] = self._bind_git_lifecycle()
            prepared["go_review_receipt_path"] = go_receipt_path.relative_to(self.workspace).as_posix()
            prepared["go_review_receipt_sha256"] = _sha256_file(go_receipt_path)
            _atomic_write(
                self.prepared_path,
                (json.dumps(prepared, indent=2, sort_keys=True) + "\n").encode("utf-8"),
            )
        elif prepared.get("go_review_receipt_path") != go_receipt_path.relative_to(
            self.workspace
        ).as_posix() or prepared.get("go_review_receipt_sha256") != _sha256_file(go_receipt_path):
            raise ModernizationWorkflowError("rehearsal resume supplied a different GO receipt")

        fingerprint = _sha256_bytes(
            _canonical_json(
                {
                    "project_id": PROJECT_ID,
                    "spec_id": REHEARSAL_SPEC_ID,
                    "work_item_id": WORK_ITEM_ID,
                    "pauth_id": PAUTH_ID,
                    "target_path": TARGET_PATH,
                    "target_sha256": _sha256_bytes(TARGET_CONTENT),
                    "prime_session_id": self.actor.session_id,
                    "go_receipt_sha256": go_receipt["receipt_sha256"],
                }
            ).encode("ascii")
        )
        store = RecoveryStore(self.recovery_db)
        if self.result_path.is_file():
            result = _read_json(self.result_path)
            if verification_receipt_path is None:
                raise ModernizationWorkflowError("completed replay requires the bound verification receipt")
            receipt = self._consume_verification_receipt(verification_receipt_path, result)
            if result.get("verification_receipt_sha256") != receipt.get("receipt_sha256"):
                raise ModernizationWorkflowError("completed result is bound to a different verification receipt")
            result.update(
                {
                    "status": "completed_existing",
                    "replayed_completed_result": True,
                    "event_count": len(store.events(self.operation_id)),
                }
            )
            return 0, result

        decision = store.claim(
            self.operation_id,
            operation_kind="modernization-approved-change",
            input_fingerprint=fingerprint,
            owner_id=f"process-{os.getpid()}",
            max_attempts=3,
            lease_seconds=self.lease_seconds,
        )
        if decision.outcome == ClaimOutcome.COMPLETED:
            execution = dict(decision.operation.result or {})
            if verification_receipt_path is None:
                execution["event_count"] = len(store.events(self.operation_id))
                return 0, execution
            return 0, self._finalize_execution(
                prepared=prepared,
                execution=execution,
                verification_receipt_path=verification_receipt_path.resolve(),
                store=store,
            )
        if decision.outcome != ClaimOutcome.ACQUIRED or decision.claim is None:
            return 73, {
                "schema_version": RESULT_SCHEMA_VERSION,
                "status": decision.outcome.value,
                "operation_id": self.operation_id,
                "recovery": store.observe(self.operation_id).recommended_action,
            }

        claim = decision.claim
        try:
            checkpoint = decision.operation.checkpoint or {}
            if checkpoint.get("stage") not in {
                "mutation_applied",
                "implementation_preserved",
            }:
                checkpoint = {
                    "stage": "mutation_prepared",
                    "mutation_effect_count": 0,
                    "target_sha256": _sha256_bytes(TARGET_CONTENT),
                }
                store.checkpoint(claim, checkpoint)
                wrote_mutation = self._authorize_and_apply_mutation()
                if interrupt_after_authorized_mutation:
                    store.fail(
                        claim,
                        "injected interruption after authorized mutation",
                        retryable=True,
                        retry_delay_seconds=0,
                    )
                    return INTERRUPTED_EXIT, {
                        "schema_version": RESULT_SCHEMA_VERSION,
                        "status": "interrupted",
                        "operation_id": self.operation_id,
                        "interruption_boundary": "authorized-mutation-before-checkpoint",
                        "missing_authority": prepared["missing_authority"],
                        "mutation_written": wrote_mutation,
                        "target_sha256": _sha256_bytes(self.target.read_bytes()),
                        "attempt_count": decision.operation.attempt_count,
                        "event_count": len(store.events(self.operation_id)),
                    }
                checkpoint = {
                    "stage": "mutation_applied",
                    "mutation_effect_count": 1,
                    "mutation_reused_existing": not wrote_mutation,
                    "target_sha256": _sha256_bytes(self.target.read_bytes()),
                }
                store.checkpoint(claim, checkpoint)

            commit_sha = str(checkpoint.get("implementation_commit") or "")
            if checkpoint.get("stage") == "mutation_applied" or not commit_sha:
                commit_sha = self._preserve_implementation()
                checkpoint = {
                    **checkpoint,
                    "stage": "implementation_preserved",
                    "implementation_commit": commit_sha,
                }
                store.checkpoint(claim, checkpoint)

            implementation_check_path = self.state_dir / "verification" / "prime-implementation-check.json"
            verification = self._run_objective_verification(
                receipt_path=implementation_check_path,
                implementation_commit=commit_sha,
                report_sha256="",
            )
            report = self._file_report(
                commit_sha,
                tuple(prepared["proposal"]["applicable_specs"]),
                verification,
            )
            verification_request = self._write_verification_request(
                prepared=prepared,
                go_receipt_path=go_receipt_path,
                go_receipt=go_receipt,
                report_path=report,
                implementation_commit=commit_sha,
                implementation_check=verification,
            )
            checkpoint = {
                **checkpoint,
                "stage": "implementation_reported",
                "report_path": report.relative_to(self.workspace).as_posix(),
                "verification_review_request": self.verification_request_path.relative_to(self.workspace).as_posix(),
                "verification_review_request_sha256": verification_request["receipt_sha256"],
            }
            store.checkpoint(claim, checkpoint)
            execution = {
                "schema_version": RESULT_SCHEMA_VERSION,
                "status": "awaiting_independent_verification",
                "operation_id": self.operation_id,
                "attempt_count": claim.attempt_number,
                "mutation_effect_count": checkpoint["mutation_effect_count"],
                "mutation_reused_existing": checkpoint.get("mutation_reused_existing", False),
                "target_path": TARGET_PATH,
                "target_sha256": _sha256_bytes(self.target.read_bytes()),
                "implementation_commit": commit_sha,
                "author_session": self.actor.session_id,
                "report_path": checkpoint["report_path"],
                "implementation_check_sha256": verification["receipt_sha256"],
                "verification_review_request": checkpoint["verification_review_request"],
                "verification_review_request_sha256": checkpoint["verification_review_request_sha256"],
            }
            completed = store.complete(claim, execution)
            execution["event_count"] = len(store.events(self.operation_id))
            execution["recovery_status"] = completed.status.value
            return 0, execution
        except Exception as exc:
            with suppress(Exception):
                store.fail(claim, str(exc), retryable=True)
            raise


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_actor_arguments(command: argparse.ArgumentParser) -> None:
        command.add_argument("--workspace", type=Path, required=True)
        command.add_argument("--platform-root", type=Path, required=True)
        command.add_argument("--session-id", required=True)

    prepare = subparsers.add_parser("prime-prepare", help="Prepare a proposal for external GO review.")
    add_actor_arguments(prepare)

    go_review = subparsers.add_parser("lo-review", help="Independently review one exact proposal and issue GO.")
    add_actor_arguments(go_review)
    go_review.add_argument("--request", type=Path, required=True)

    rehearse = subparsers.add_parser(
        "rehearse", help="Run, resume, or finalize the Prime Builder portion of the production rehearsal."
    )
    add_actor_arguments(rehearse)
    rehearse.add_argument("--operation-id", default="modernization-e2e-operation-001")
    rehearse.add_argument("--lease-seconds", type=int, default=30)
    rehearse.add_argument("--go-receipt", type=Path, required=True)
    rehearse.add_argument("--verification-receipt", type=Path)
    rehearse.add_argument(
        "--interrupt-after",
        choices=("authorized-mutation",),
        help="Inject a process boundary after the protected effect and before its durable checkpoint.",
    )

    verify = subparsers.add_parser(
        "lo-verify", help="Independently verify one exact implementation report and issue VERIFIED."
    )
    add_actor_arguments(verify)
    verify.add_argument("--request", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        role = "prime-builder" if args.command in {"prime-prepare", "rehearse"} else "loyal-opposition"
        workspace = args.workspace.resolve()
        platform_root = args.platform_root.resolve()
        workflow = ModernizationWorkflow(
            workspace,
            platform_root,
            actor=_resolve_workflow_actor(
                workspace,
                platform_root,
                session_id=args.session_id,
                required_role=role,
            ),
            operation_id=getattr(args, "operation_id", "modernization-e2e-operation-001"),
            lease_seconds=getattr(args, "lease_seconds", 30),
        )
        if args.command == "prime-prepare":
            code, payload = 0, workflow.prepare_prime()
        elif args.command == "lo-review":
            code, payload = 0, workflow.review_proposal(args.request)
        elif args.command == "lo-verify":
            code, payload = 0, workflow.review_implementation(args.request)
        else:
            code, payload = workflow.execute(
                go_receipt_path=args.go_receipt,
                verification_receipt_path=args.verification_receipt,
                interrupt_after_authorized_mutation=args.interrupt_after == "authorized-mutation",
            )
    except Exception as exc:
        code = 1
        payload = {
            "schema_version": RESULT_SCHEMA_VERSION,
            "status": "error",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
