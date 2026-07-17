#!/usr/bin/env python3
"""Collect observed evidence for receipt-backed modernization assertions.

The semantic checker deliberately treats a receipt as an observed event.  This
collector is the producer-side contract: it executes an objective-specific
measurement, preserves the raw output, and writes a PASS receipt only after the
measurement succeeds.  Missing live sessions, clean runs, audits, or closure
inputs are BLOCKED prerequisites, never simulated successes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import uuid
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.session.envelope import (  # noqa: E402
    EnvelopeError,
    _validate_worker_role_provenance,
    resolve_worker_role_provenance,
    worker_session_envelope_path,
)

from scripts import check_modernization_release_candidate as release_checker  # noqa: E402
from scripts import check_modernization_scope_semantics as semantic_checker  # noqa: E402

DEFAULT_MANIFEST = PROJECT_ROOT / "config" / "governance" / "modernization-release-candidate.json"
DEFAULT_EVIDENCE_DIR = PROJECT_ROOT / ".gtkb-state" / "modernization-release-candidate" / "semantic-evidence"
_SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{11,127}$")
_FINAL_GROUP = "final"
_PRIMARY_HARNESSES = ("claude", "codex", "cursor", "antigravity")
_HEADLESS_PROVIDERS = ("ollama", "openrouter", "alibaba-cloud-studio")
_BASELINE_BENCHMARK = Path(".gtkb-state/benchmarks/20260704-160641/run.json")
_BASELINE_CORPUS = Path(
    "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HARNESS-EQUIVALENCE-PHASE-3-CORPUS-MANIFEST-2026-07-04.md"
)
_BASELINE_TOKEN_ADVISORY = Path("independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-07-03-18-32.md")
_BASELINE_DISPATCH_ADVISORY = Path(
    "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/"
    "INSIGHTS-2026-07-04-19-08-dispatch-attribute-calibration-advisory.md"
)
_BASELINE_SESSION_HARNESSES = ("claude", "codex", "antigravity")
_BASELINE_DISPATCH_HARNESS_IDS = frozenset({"A", "B", "C", "D", "E", "F"})


class CollectionError(RuntimeError):
    """Base error for deterministic evidence collection."""


class MeasurementBlocked(CollectionError):
    """Raised when genuine external evidence does not exist yet."""


class MeasurementFailed(CollectionError):
    """Raised when an executable measurement runs and fails."""


@dataclass(frozen=True)
class Plan:
    handle_id: str
    receipt_name: str
    group: str
    kind: str
    command_id: str | None = None
    command: tuple[str, ...] = ()
    timeout_seconds: int = 600
    required_assertions: tuple[str, ...] = ()
    harnesses: tuple[str, ...] = ()
    prerequisite: str | None = None

    @property
    def semantic_assertion_id(self) -> str:
        return f"MSA-{self.handle_id}"


@dataclass(frozen=True)
class CollectionResult:
    receipt_name: str
    semantic_assertion_id: str
    group: str
    status: str
    reason: str
    receipt_path: str | None = None
    measurement_path: str | None = None


def _pytest(*nodeids: str) -> tuple[str, ...]:
    return ("{python}", "-m", "pytest", *nodeids, "-q", "--tb=short", "-p", "no:cacheprovider")


PLANS: tuple[Plan, ...] = (
    Plan(
        "MOD-P02",
        "predecessor-reconciliation",
        "foundations",
        "program-reconciliation",
    ),
    Plan("MOD-P06", "program-closure", _FINAL_GROUP, "program-closure"),
    Plan(
        "MOD-AF01",
        "authority-carrier-classification",
        "foundations",
        "pytest",
        "authority-carrier-classification",
        _pytest(
            "platform_tests/scripts/test_modernization_authority_foundations.py::test_frozen_authority_carriers_are_current_stated_and_uniquely_asserted",
            "platform_tests/scripts/test_modernization_authority_foundations.py::test_every_frozen_authority_carrier_is_fully_evaluable",
        ),
        300,
    ),
    Plan(
        "MOD-AD05",
        "artifact-cleanup-batches",
        "repository",
        "artifact-audit",
        required_assertions=("MOD-AD-05", "MOD-AD-09", "MOD-AD-12"),
    ),
    Plan(
        "MOD-AD06",
        "semantic-guidance-cleanup",
        "repository",
        "artifact-audit",
        required_assertions=("MOD-AD-05", "MOD-AD-06", "MOD-AD-07", "MOD-AD-10", "MOD-AD-12"),
    ),
    Plan(
        "MOD-AD08",
        "lifecycle-state-reconciliation",
        "repository",
        "artifact-audit",
        required_assertions=("MOD-AD-02", "MOD-AD-03", "MOD-AD-04", "MOD-AD-08", "MOD-AD-12"),
    ),
    Plan(
        "MOD-AD10",
        "work-item-advisory-deduplication",
        "foundations",
        "program-reconciliation",
    ),
    Plan(
        "MOD-RI01",
        "runtime-interface-inventory",
        "repository",
        "pytest",
        "runtime-interface-inventory",
        _pytest(
            "platform_tests/scripts/test_system_interface_map.py",
            "platform_tests/scripts/test_session_startup_control_map.py",
            "platform_tests/scripts/test_session_continuation_sources_parity.py",
            "platform_tests/scripts/test_modernization_end_to_end_workflow.py",
        ),
        900,
    ),
    Plan("MOD-HP03", "harness-claude-live", "harness-live", "live-harness", harnesses=("claude",)),
    Plan("MOD-HP04", "harness-codex-live", "harness-live", "live-harness", harnesses=("codex",)),
    Plan("MOD-HP05", "harness-cursor-live", "harness-live", "live-harness", harnesses=("cursor",)),
    Plan(
        "MOD-HP06",
        "harness-antigravity-optimized-startup",
        "harness-live",
        "live-harness",
        harnesses=("antigravity",),
    ),
    Plan(
        "MOD-HP07",
        "headless-provider-conformance",
        "harness-live",
        "live-harness",
        harnesses=_HEADLESS_PROVIDERS,
    ),
    Plan(
        "MOD-HP12",
        "cross-harness-confusion-corpus",
        "harness-live",
        "live-harness",
        harnesses=("claude", "codex", "cursor"),
    ),
    Plan("MOD-AS01", "pre-modernization-baseline", "assurance", "pre-baseline"),
    Plan(
        "MOD-AS04",
        "seven-category-scenario-matrix",
        "assurance",
        "pytest",
        "seven-category-scenario-matrix",
        _pytest(
            "platform_tests/scripts/test_modernization_context_manifests.py::test_frozen_context_manifest_contract",
            "platform_tests/scripts/test_modernization_fresh_worker.py::test_fresh_worker_bootstraps_from_only_copied_product_assets",
            "platform_tests/scripts/test_modernization_fresh_worker.py::test_project_context_override_cannot_fall_back_to_packaged_assets",
            "platform_tests/scripts/test_modernization_hard_invariants.py::test_hard_invariant_rejects_stale_or_retired_authority",
            "platform_tests/scripts/test_modernization_hard_invariants.py::test_hard_invariant_rejects_ambiguous_worker_role_authority",
            "platform_tests/scripts/test_modernization_runtime_recovery.py::test_retry_budget_is_bounded_and_exhaustion_quarantines",
        ),
        900,
    ),
    Plan("MOD-AS05", "six-activity-behavior-matrix", "assurance", "activity-matrix"),
    Plan(
        "MOD-AS06",
        "role-harness-session-branch-scenarios",
        "assurance",
        "pytest",
        "role-harness-session-branch-scenarios",
        _pytest(
            "platform_tests/scripts/test_modernization_harness_parity.py::test_headless_worker_authority_is_isolated_by_session_and_harness",
            "platform_tests/scripts/test_modernization_runtime_recovery.py::test_concurrent_attempts_have_exactly_one_owner",
            "platform_tests/scripts/test_modernization_runtime_recovery.py::test_interrupted_attempt_resumes_from_durable_checkpoint",
            "platform_tests/scripts/test_session_role_resolution_table.py::test_assertion4_compaction_resume_falls_back_to_durable",
            "platform_tests/scripts/test_modernization_git_lifecycle.py",
        ),
        1200,
    ),
    Plan(
        "MOD-AS07",
        "confusion-regression-fixtures",
        "assurance",
        "pytest",
        "confusion-regression-fixtures",
        _pytest(
            "platform_tests/scripts/test_modernization_hard_invariants.py",
            "platform_tests/scripts/test_session_role_resolution_table.py::test_malformed_marker_json_treated_as_absent",
            "platform_tests/scripts/test_modernization_fresh_worker.py::test_project_context_override_cannot_fall_back_to_packaged_assets",
        ),
        900,
    ),
    Plan("MOD-AS08", "nonimpairment-orchestrator", "assurance", "clean-run", prerequisite="AT-HARD-INVARIANTS"),
    Plan("MOD-AS09", "modernization-measurements", "assurance", "operational-metrics"),
    Plan(
        "MOD-AS10",
        "shadow-six-activities-primary-harnesses",
        "assurance",
        "shadow-observations",
        harnesses=_PRIMARY_HARNESSES,
    ),
    Plan("MOD-AS11", "activation-thresholds", "assurance", "dependent-receipts"),
    Plan(
        "MOD-AS12",
        "reversible-activation-slices",
        "assurance",
        "clean-run",
        prerequisite="AT-INSTALL-UPGRADE-ROLLBACK,AT-AGENT-RED-PORTABILITY",
    ),
    Plan("MOD-AS13", "operational-observation", "assurance", "pilot-observation"),
    Plan("MOD-AS14", "independent-verification", _FINAL_GROUP, "independent-verification"),
)

PLAN_BY_NAME = {plan.receipt_name: plan for plan in PLANS}
GROUPS = tuple(sorted({plan.group for plan in PLANS}))


def _expected_bindings() -> dict[str, str]:
    return {
        proof.removeprefix("builtin:receipt:"): handle_id
        for handle_id, proofs in semantic_checker.PROOFS.items()
        for proof in proofs
        if proof.startswith("builtin:receipt:")
    }


def validate_plan_coverage() -> list[str]:
    errors: list[str] = []
    expected = _expected_bindings()
    actual = {plan.receipt_name: plan.handle_id for plan in PLANS}
    if len(PLANS) != 26 or len(actual) != 26:
        errors.append("collector must define exactly 26 unique receipt plans")
    if actual != expected:
        errors.append(f"receipt plan coverage mismatch: expected={expected!r}, actual={actual!r}")
    for plan in PLANS:
        if plan.kind == "pytest" and (not plan.command_id or not plan.command):
            errors.append(f"{plan.receipt_name}: pytest plan requires a command id and argv")
    return errors


def _sha256(path: Path) -> str:
    with open(_native_io_path(path), "rb") as stream:
        return hashlib.sha256(stream.read()).hexdigest().upper()


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")


def _native_io_path(path: Path) -> str:
    resolved = str(path.resolve())
    if os.name != "nt" or resolved.startswith("\\\\?\\"):
        return resolved
    if resolved.startswith("\\\\"):
        return "\\\\?\\UNC\\" + resolved[2:]
    return "\\\\?\\" + resolved


def _exclusive_write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as stream:
            stream.write(_json_bytes(payload))
    except FileExistsError as exc:
        raise CollectionError(f"append-only evidence path already exists: {path}") from exc


def _exclusive_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(value)
    except FileExistsError as exc:
        raise CollectionError(f"append-only evidence path already exists: {path}") from exc


def _write_content_addressed_snapshot(path: Path, content: bytes) -> None:
    Path(_native_io_path(path.parent)).mkdir(parents=True, exist_ok=True)
    try:
        with open(_native_io_path(path), "xb") as stream:
            stream.write(content)
    except FileExistsError:
        try:
            with open(_native_io_path(path), "rb") as stream:
                existing = stream.read()
        except OSError as exc:
            raise CollectionError(f"cannot read existing session-envelope snapshot {path}: {exc}") from exc
        if existing != content:
            raise CollectionError(f"conflicting bytes at session-envelope snapshot path: {path}")
    except OSError as exc:
        raise CollectionError(f"cannot write session-envelope snapshot {path}: {exc}") from exc


def _new_issue_id() -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"{timestamp}-{uuid.uuid4().hex[:12]}"


def _relative(project_root: Path, path: Path) -> str:
    resolved_root = project_root.resolve()
    resolved = path.resolve()
    try:
        return resolved.relative_to(resolved_root).as_posix()
    except ValueError as exc:
        raise CollectionError(f"evidence path escapes the project root: {path}") from exc


def _read_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CollectionError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CollectionError(f"JSON root must be an object: {path}")
    return payload


def _git_head(project_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    head = result.stdout.strip()
    if result.returncode != 0 or re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", head) is None:
        raise CollectionError("cannot resolve the current Git HEAD")
    return head


def _registry_rows(project_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    registry = _read_object(project_root / "harness-state" / "harness-registry.json")
    identities = _read_object(project_root / "harness-state" / "harness-identities.json")
    rows = {
        str(row.get("harness_name")): row
        for row in registry.get("harnesses", [])
        if isinstance(row, dict) and isinstance(row.get("harness_name"), str)
    }
    identity_map = {
        str(name): str(record.get("id"))
        for name, record in identities.get("harnesses", {}).items()
        if isinstance(record, dict) and record.get("id")
    }
    return rows, identity_map


def resolve_session_authority(project_root: Path, session_id: str, *, evidence_dir: Path) -> dict[str, Any]:
    if _SESSION_RE.fullmatch(session_id) is None:
        raise CollectionError("a real runtime session context id is required")
    try:
        session = resolve_worker_role_provenance(project_root, current_session_id=session_id)
        envelope_path = worker_session_envelope_path(project_root, str(session["harness_name"]), session_id)
    except EnvelopeError as exc:
        raise CollectionError(f"canonical runtime session provenance is unavailable: {exc}") from exc
    if not envelope_path.is_file():
        raise CollectionError("canonical exact-session envelope must pre-exist before evidence collection")
    try:
        envelope_bytes = envelope_path.read_bytes()
        envelope = json.loads(envelope_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CollectionError(f"canonical exact-session envelope is unreadable: {exc}") from exc
    if not isinstance(envelope, dict):
        raise CollectionError("canonical exact-session envelope must contain a JSON object")
    try:
        captured_session = _validate_worker_role_provenance(
            envelope,
            current_session_id=session_id,
            expected_harness_name=str(session["harness_name"]),
        )
    except EnvelopeError as exc:
        raise CollectionError(f"captured session-envelope provenance is invalid: {exc}") from exc
    if captured_session != session:
        raise CollectionError("captured session-envelope provenance changed during evidence collection")

    resolved_evidence_dir = evidence_dir.resolve()
    _relative(project_root, resolved_evidence_dir)
    envelope_sha256 = hashlib.sha256(envelope_bytes).hexdigest().upper()
    snapshot_path = (
        resolved_evidence_dir
        / "session-envelope-snapshots"
        / str(session["harness_name"])
        / session_id
        / f"{envelope_sha256}.json"
    )
    _relative(project_root, snapshot_path)
    _write_content_addressed_snapshot(snapshot_path, envelope_bytes)
    return {
        "session": session,
        "session_envelope": {
            "path": _relative(project_root, envelope_path),
            "sha256": envelope_sha256,
            "snapshot_path": _relative(project_root, snapshot_path),
        },
    }


def resolve_runtime_provenance(
    project_root: Path,
    *,
    evidence_dir: Path,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    env = dict(environ or os.environ)
    session_id = (
        env.get("GTKB_AUTHOR_SESSION_CONTEXT_ID")
        or env.get("GTKB_BRIDGE_POLLER_RUN_ID")
        or env.get("CODEX_THREAD_ID")
        or ""
    ).strip()
    authority = resolve_session_authority(project_root, session_id, evidence_dir=evidence_dir)
    return {
        "schema_version": semantic_checker.ISSUER_SCHEMA_VERSION,
        "service_id": semantic_checker.COLLECTOR_SERVICE_ID,
        **authority,
    }


class Collector:
    def __init__(
        self,
        *,
        project_root: Path = PROJECT_ROOT,
        manifest: dict[str, Any] | None = None,
        evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        self.project_root = project_root.resolve()
        self.manifest = manifest or semantic_checker.load_manifest(DEFAULT_MANIFEST)
        self.evidence_dir = evidence_dir.resolve()
        _relative(self.project_root, self.evidence_dir)
        self.environ = dict(environ or os.environ)
        self.scope_digest = semantic_checker.scope_digest(self.manifest)
        self.git_head = _git_head(self.project_root)
        self.invocation_id = _new_issue_id()
        try:
            self.issuer: dict[str, Any] | None = resolve_runtime_provenance(
                self.project_root,
                evidence_dir=self.evidence_dir,
                environ=self.environ,
            )
            self.issuer_error: str | None = None
        except CollectionError as exc:
            self.issuer = None
            self.issuer_error = str(exc)
        self._command_cache: dict[str, dict[str, Any]] = {}

    def _command_log_path(self, command_id: str) -> Path:
        return self.evidence_dir / "command-runs" / command_id / self.invocation_id / "output.log"

    def _issue_dir(self, plan: Plan) -> Path:
        return self.evidence_dir / "issues" / plan.receipt_name / self.invocation_id

    def _run_command(self, command_id: str, argv: tuple[str, ...], timeout_seconds: int) -> dict[str, Any]:
        if command_id in self._command_cache:
            return self._command_cache[command_id]
        resolved = [sys.executable if part == "{python}" else part for part in argv]
        before = _git_head(self.project_root)
        temp_key = hashlib.sha256(command_id.encode("utf-8")).hexdigest()[:8]
        temp_root = self.project_root / ".gtkb-state" / "mrc-pytest" / temp_key / self.invocation_id
        temp_root.parent.mkdir(parents=True, exist_ok=True)
        environment = dict(os.environ)
        environment.update(self.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTEST_ADDOPTS"] = f"--basetemp={temp_root.as_posix()}"
        try:
            completed = subprocess.run(
                resolved,
                cwd=self.project_root,
                env=environment,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
            )
            output = (completed.stdout or "") + (completed.stderr or "")
            return_code: int | None = completed.returncode
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            raw = (exc.stdout or "") + (exc.stderr or "")
            output = raw if isinstance(raw, str) else raw.decode("utf-8", errors="replace")
            return_code = None
            timed_out = True
        after = _git_head(self.project_root)
        log_path = self._command_log_path(command_id)
        _exclusive_write_text(log_path, output)
        result = {
            "command_id": command_id,
            "argv": resolved,
            "return_code": return_code,
            "timed_out": timed_out,
            "git_head_before": before,
            "git_head_after": after,
            "output": {
                "path": _relative(self.project_root, log_path),
                "sha256": _sha256(log_path),
                "byte_count": log_path.stat().st_size,
            },
        }
        if timed_out:
            raise MeasurementFailed(f"{command_id} timed out after {timeout_seconds} seconds")
        if return_code != 0:
            raise MeasurementFailed(f"{command_id} exited {return_code}; see {log_path}")
        if before != self.git_head or after != self.git_head:
            raise MeasurementFailed(f"{command_id} did not execute entirely at Git HEAD {self.git_head}")
        self._command_cache[command_id] = result
        return result

    def _artifact_audit(self, plan: Plan) -> dict[str, Any]:
        command = ("{python}", "scripts/check_artifact_decontamination.py", "--json")
        result = self._run_command("artifact-decontamination", command, 300)
        log_path = self.project_root / result["output"]["path"]
        try:
            report = json.loads(log_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise MeasurementFailed(f"artifact audit did not emit JSON: {exc}") from exc
        by_id = {
            row.get("id"): row
            for row in report.get("assertions", [])
            if isinstance(row, dict) and isinstance(row.get("id"), str)
        }
        failed = [
            assertion_id
            for assertion_id in plan.required_assertions
            if by_id.get(assertion_id, {}).get("status") != "PASS"
        ]
        if report.get("status") != "PASS" or failed:
            raise MeasurementFailed(f"artifact audit did not pass required assertions: {failed}")
        return {
            "measurement_kind": "artifact_repository_audit",
            "command": result,
            "required_assertions": {
                assertion_id: by_id[assertion_id].get("evidence") for assertion_id in plan.required_assertions
            },
            "finding_count": len(report.get("audit", {}).get("findings", [])),
        }

    def _program_reconciliation(self, plan: Plan) -> dict[str, Any]:
        root_project = str(self.manifest["program"]["project_id"])
        project_by_family = {str(family["id"]): str(family["project_id"]) for family in self.manifest["scope_families"]}
        project_ids = set(project_by_family.values())
        placeholders = ",".join("?" for _ in project_ids)
        database = self.project_root / "groundtruth.db"
        try:
            connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
            connection.row_factory = sqlite3.Row
            projects = [
                dict(row)
                for row in connection.execute(
                    f"SELECT id, name, status, parent_project_id FROM current_projects "
                    f"WHERE id IN ({placeholders}) ORDER BY id",
                    sorted(project_ids),
                )
            ]
            memberships = [
                dict(row)
                for row in connection.execute(
                    f"SELECT project_id, work_item_id, membership_role, membership_order "
                    f"FROM current_project_work_item_memberships "
                    f"WHERE status = 'active' AND project_id IN ({placeholders}) "
                    f"ORDER BY project_id, membership_order, work_item_id",
                    sorted(project_ids),
                )
            ]
            links = [
                dict(row)
                for row in connection.execute(
                    f"SELECT project_id, artifact_type, artifact_ref, relationship "
                    f"FROM current_project_artifact_links "
                    f"WHERE status = 'active' AND project_id IN ({placeholders}) "
                    f"ORDER BY project_id, artifact_type, artifact_ref",
                    sorted(project_ids),
                )
            ]
        except sqlite3.Error as exc:
            raise MeasurementFailed(f"cannot reconcile modernization program state: {exc}") from exc
        finally:
            if "connection" in locals():
                connection.close()

        project_by_id = {str(row["id"]): row for row in projects}
        member_counts = {project_id: 0 for project_id in project_ids}
        work_item_projects: dict[str, list[str]] = {}
        for row in memberships:
            project_id = str(row["project_id"])
            work_item_id = str(row["work_item_id"])
            member_counts[project_id] += 1
            work_item_projects.setdefault(work_item_id, []).append(project_id)
        duplicate_memberships = {
            work_item_id: sorted(projects)
            for work_item_id, projects in work_item_projects.items()
            if len(projects) != 1
        }
        selected_advisories = [
            row for row in links if row["artifact_type"] == "bridge_thread" and row["relationship"] == "source-advisory"
        ]
        errors: list[str] = []
        if set(project_by_id) != project_ids or any(row["status"] != "active" for row in projects):
            errors.append("the exact eight-project modernization population is not active")
        if project_by_id.get(root_project, {}).get("parent_project_id") is not None:
            errors.append("the modernization root project has an unexpected parent")
        if any(
            project_by_id.get(project_id, {}).get("parent_project_id") != root_project
            for project_id in project_ids - {root_project}
        ):
            errors.append("one or more modernization capability projects has the wrong parent")
        if any(count < 1 for count in member_counts.values()):
            errors.append("one or more modernization projects has no active work-item membership")
        if duplicate_memberships:
            errors.append(f"work items are duplicated across modernization projects: {duplicate_memberships}")
        if len(selected_advisories) != 1:
            errors.append(f"expected one selected source advisory, found {len(selected_advisories)}")
        if errors:
            raise MeasurementFailed("; ".join(errors))
        return {
            "measurement_kind": "modernization_predecessor_work_item_advisory_reconciliation",
            "receipt_name": plan.receipt_name,
            "project_count": len(projects),
            "active_membership_count": len(memberships),
            "member_counts": dict(sorted(member_counts.items())),
            "duplicate_memberships": duplicate_memberships,
            "selected_source_advisories": selected_advisories,
            "project_artifact_links": links,
            "work_item_assignments": memberships,
        }

    def _pytest_measurement(self, plan: Plan) -> dict[str, Any]:
        result = self._run_command(plan.command_id or plan.receipt_name, plan.command, plan.timeout_seconds)
        return {
            "measurement_kind": "executable_acceptance_nodes",
            "command": result,
            "executed_nodeids": [part for part in plan.command if "::" in part or part.endswith(".py")],
        }

    def _activity_matrix(self) -> dict[str, Any]:
        from groundtruth_kb.activity.profiles import CANONICAL_ACTIVITY_ORDER, load_activity_profiles

        profiles = load_activity_profiles()
        observed: dict[str, Any] = {}
        for name in CANONICAL_ACTIVITY_ORDER:
            profile = profiles.get(name)
            if profile is None:
                raise MeasurementFailed(f"missing canonical activity profile: {name}")
            if not profile.skills or not profile.terminology or not profile.history_state.get("sources"):
                raise MeasurementFailed(f"activity profile lacks resources or query routes: {name}")
            if (
                not profile.direction.get("stance")
                or not profile.direction.get("guardrails")
                or not profile.direction.get("manipulates")
            ):
                raise MeasurementFailed(f"activity profile lacks actions, prohibitions, or next-step direction: {name}")
            observed[name] = {
                "headless_eligibility": profile.headless_eligibility,
                "skill_count": len(profile.skills),
                "terminology_count": len(profile.terminology),
                "history_source_count": len(profile.history_state["sources"]),
                "stance": profile.direction["stance"],
                "guardrail_count": len(profile.direction["guardrails"]),
                "manipulated_resource_count": len(profile.direction["manipulates"]),
                "classification": profile.classification,
            }
        if tuple(observed) != CANONICAL_ACTIVITY_ORDER:
            raise MeasurementFailed("six-activity matrix order is not canonical")
        return {"measurement_kind": "six_activity_profile_execution", "activities": observed}

    def _telemetry_files(self) -> list[tuple[Path, dict[str, Any]]]:
        directory = self.project_root / ".gtkb-state" / "bridge-poller" / "dispatch-runs"
        rows: list[tuple[Path, dict[str, Any]]] = []
        for path in sorted(directory.glob("*.telemetry.json")):
            try:
                payload = _read_object(path)
            except CollectionError:
                continue
            if payload.get("schema_id") == "gtkb.shim_dispatch_telemetry.v1":
                rows.append((path, payload))
        return rows

    def _live_harness(self, plan: Plan) -> dict[str, Any]:
        rows, identities = _registry_rows(self.project_root)
        telemetry = self._telemetry_files()
        observed: dict[str, Any] = {}
        for harness_name in plan.harnesses:
            registry_row = rows.get(harness_name)
            if registry_row is None or identities.get(harness_name) != registry_row.get("id"):
                raise MeasurementBlocked(f"{harness_name}: no canonical durable harness registration")
            matches: list[tuple[Path, dict[str, Any], Path, dict[str, Any], dict[str, Any]]] = []
            for telemetry_path, payload in telemetry:
                worker = payload.get("worker", {})
                outcome = payload.get("outcome", {})
                correlation = payload.get("correlation", {})
                if worker.get("harness_name") != harness_name:
                    continue
                if outcome.get("exit_code") != 0 or outcome.get("exit_status") != "succeeded":
                    continue
                session_id = correlation.get("session_context_id")
                if not isinstance(session_id, str) or _SESSION_RE.fullmatch(session_id) is None:
                    continue
                envelope_path = (
                    self.project_root / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json"
                )
                try:
                    envelope = _read_object(envelope_path)
                    authority = resolve_session_authority(
                        self.project_root,
                        session_id,
                        evidence_dir=self.evidence_dir,
                    )
                except CollectionError:
                    continue
                session = authority["session"]
                if (
                    envelope.get("session_id") != session_id
                    or session.get("harness_name") != harness_name
                    or session.get("harness_id") != registry_row.get("id")
                    or session.get("role") != worker.get("role")
                ):
                    continue
                expected_source = _relative(self.project_root, envelope_path)
                if worker.get("role_source_document_id") != expected_source:
                    continue
                matches.append((telemetry_path, payload, envelope_path, envelope, authority))
            if not matches:
                raise MeasurementBlocked(
                    f"{harness_name}: no successful real invocation with a matching canonical session envelope"
                )
            telemetry_path, payload, envelope_path, envelope, authority = matches[-1]
            observed[harness_name] = {
                "harness_id": registry_row.get("id"),
                "registry_status": registry_row.get("status"),
                "session_context_id": envelope.get("session_id"),
                "role": authority["session"]["role"],
                "invocation": {
                    "path": _relative(self.project_root, telemetry_path),
                    "sha256": _sha256(telemetry_path),
                    "exit_status": payload.get("outcome", {}).get("exit_status"),
                },
                "session_authority": authority,
            }
        try:
            parity = self._run_command(
                "harness-parity-live",
                _pytest(
                    "platform_tests/scripts/test_modernization_harness_parity.py::test_active_harnesses_have_required_production_parity",
                    "platform_tests/scripts/test_cross_harness_protocol_parity.py::test_durable_harness_identity_and_role_surfaces_cover_expected_harnesses",
                ),
                600,
            )
        except MeasurementFailed as exc:
            raise MeasurementBlocked(
                f"live invocation exists, but the independent harness-parity prerequisite is blocked: {exc}"
            ) from exc
        return {"measurement_kind": "persisted_live_harness_invocations", "harnesses": observed, "parity": parity}

    def _activity_benchmark(self) -> tuple[dict[str, Any], dict[str, Any]]:
        command = self._run_command(
            "activity-envelope-load",
            ("{python}", "scripts/benchmarks/activity_envelope_load.py", "--json"),
            300,
        )
        log_path = self.project_root / command["output"]["path"]
        try:
            report = json.loads(log_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise MeasurementFailed(f"activity benchmark did not emit JSON: {exc}") from exc
        if report.get("status") not in {"PASS", "WARN"} or len(report.get("activities", {})) != 6:
            raise MeasurementFailed("activity benchmark did not produce a usable six-activity result")
        return command, report

    @staticmethod
    def _started_at(payload: dict[str, Any]) -> datetime | None:
        raw = payload.get("timing", {}).get("started_at")
        return Collector._parse_timestamp(raw)

    @staticmethod
    def _parse_timestamp(raw: object) -> datetime | None:
        if not isinstance(raw, str):
            return None
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed.astimezone(UTC) if parsed.tzinfo else None

    def _pre_baseline(self) -> dict[str, Any]:
        scope_date = str(self.manifest.get("program", {}).get("scope_source", ""))
        match = re.search(r"(20\d{6})", scope_date)
        if match is None:
            raise MeasurementBlocked("the frozen scope source does not define a baseline cutoff date")
        cutoff = datetime.strptime(match.group(1), "%Y%m%d").replace(tzinfo=UTC)

        benchmark_path = self.project_root / _BASELINE_BENCHMARK
        if not benchmark_path.is_file():
            raise MeasurementBlocked(f"historical benchmark is absent: {_BASELINE_BENCHMARK.as_posix()}")
        benchmark = _read_object(benchmark_path)
        if benchmark.get("run_id") != "20260704-160641":
            raise MeasurementFailed("historical benchmark run id does not match its frozen evidence path")
        results = benchmark.get("results")
        if not isinstance(results, list):
            raise MeasurementFailed("historical benchmark results are not a list")
        by_id = {
            str(row.get("benchmark_id")): row
            for row in results
            if isinstance(row, dict) and isinstance(row.get("benchmark_id"), str)
        }
        required_benchmarks = {"harness_observed_scorecard", "harness_role_protocol_smoke"}
        if not required_benchmarks <= by_id.keys():
            raise MeasurementFailed(
                f"historical benchmark is missing required rows: {sorted(required_benchmarks - by_id.keys())}"
            )
        for benchmark_id in sorted(required_benchmarks):
            row = by_id[benchmark_id]
            generated_at = self._parse_timestamp(row.get("generated_at"))
            source_commit = row.get("source_commit")
            if generated_at is None or generated_at >= cutoff:
                raise MeasurementFailed(f"{benchmark_id} is not a pre-cutoff observation")
            if not isinstance(source_commit, str) or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None:
                raise MeasurementFailed(f"{benchmark_id} lacks an exact historical source commit")

        scorecard = by_id["harness_observed_scorecard"]
        dimensions = scorecard.get("dimensions")
        if not isinstance(dimensions, dict):
            raise MeasurementFailed("historical harness scorecard dimensions are absent")
        harness_rows = dimensions.get("harnesses")
        summary = dimensions.get("summary")
        if not isinstance(harness_rows, dict) or not isinstance(summary, dict):
            raise MeasurementFailed("historical harness scorecard is structurally incomplete")
        missing_harnesses = sorted(_BASELINE_DISPATCH_HARNESS_IDS - harness_rows.keys())
        if missing_harnesses:
            raise MeasurementFailed(f"historical harness scorecard lacks primary harness ids: {missing_harnesses}")
        failure_count = summary.get("failure_log_record_count")
        if not isinstance(failure_count, int) or failure_count < 1:
            raise MeasurementFailed("historical harness scorecard has no observed failure records")
        successful_launches = sum(
            int(row.get("successful_exit_count", 0)) for row in harness_rows.values() if isinstance(row, dict)
        )
        if successful_launches < 1:
            raise MeasurementFailed("historical harness scorecard has no observed successful launch")
        latency_samples = {
            harness_id: {
                "count": latency.get("count"),
                "median_seconds": latency.get("median"),
                "p90_seconds": latency.get("p90"),
            }
            for harness_id, row in sorted(harness_rows.items())
            if isinstance(row, dict)
            and isinstance((latency := row.get("verdict_latency_seconds")), dict)
            and int(latency.get("count", 0)) > 0
        }
        if not latency_samples:
            raise MeasurementFailed("historical harness scorecard has no observed verdict latency")

        smoke = by_id["harness_role_protocol_smoke"]
        smoke_dimensions = smoke.get("dimensions")
        if not isinstance(smoke_dimensions, dict):
            raise MeasurementFailed("historical protocol smoke dimensions are absent")
        smoke_passed = smoke_dimensions.get("passed")
        smoke_total = smoke_dimensions.get("total")
        if not isinstance(smoke_passed, int) or smoke_passed < 1 or smoke_passed != smoke_total:
            raise MeasurementFailed("historical protocol smoke did not pass every recorded probe")

        text_evidence: dict[str, dict[str, str]] = {}
        text_contracts = {
            "corpus_manifest": (
                _BASELINE_CORPUS,
                ("Date: 2026-07-04", "Token cost and quality adjudication remain partial."),
            ),
            "token_advisory": (
                _BASELINE_TOKEN_ADVISORY,
                ("Date: 2026-07-03 UTC", "Real token counts at the harness boundary."),
            ),
            "dispatch_advisory": (
                _BASELINE_DISPATCH_ADVISORY,
                ("Date: 2026-07-04", "Observed distribution today"),
            ),
        }
        for name, (relative_path, required_phrases) in text_contracts.items():
            path = self.project_root / relative_path
            if not path.is_file():
                raise MeasurementBlocked(f"historical baseline evidence is absent: {relative_path.as_posix()}")
            text = path.read_text(encoding="utf-8")
            missing_phrases = [phrase for phrase in required_phrases if phrase not in text]
            if missing_phrases:
                raise MeasurementFailed(f"{relative_path.as_posix()} lacks historical anchors: {missing_phrases}")
            text_evidence[name] = {"path": _relative(self.project_root, path), "sha256": _sha256(path)}

        session_samples: list[dict[str, Any]] = []
        for harness_name in _BASELINE_SESSION_HARNESSES:
            archive = self.project_root / "harness-state" / harness_name / "session-envelope-archive"
            candidates: list[tuple[datetime, Path, dict[str, Any]]] = []
            for path in sorted(archive.glob("*.json")):
                row = _read_object(path)
                closed_at = self._parse_timestamp(row.get("closed_at"))
                if (
                    closed_at is not None
                    and closed_at < cutoff
                    and row.get("harness_name") == harness_name
                    and row.get("status") == "closed"
                ):
                    candidates.append((closed_at, path, row))
            if not candidates:
                raise MeasurementBlocked(f"no pre-cutoff closed session envelope exists for {harness_name}")
            closed_at, path, row = max(candidates, key=lambda item: (item[0], item[1].as_posix()))
            topics = [topic for topic in row.get("topics", []) if isinstance(topic, dict)]
            projected_commands = [
                str(command)
                for topic in topics
                for command in topic.get("preload_state", {}).get("commands", [])
                if isinstance(command, str)
            ]
            session_samples.append(
                {
                    "path": _relative(self.project_root, path),
                    "sha256": _sha256(path),
                    "harness": harness_name,
                    "session_id": row.get("session_id"),
                    "opened_at": row.get("opened_at"),
                    "closed_at": closed_at.isoformat(),
                    "topic_count": len(topics),
                    "activity_types": sorted({str(topic.get("type")) for topic in topics if topic.get("type")}),
                    "projected_first_command": projected_commands[0] if projected_commands else None,
                }
            )

        failure_classes = {
            harness_id: sorted(str(name) for name in row.get("failure_classes", {}))
            for harness_id, row in sorted(harness_rows.items())
            if harness_id in _BASELINE_DISPATCH_HARNESS_IDS
            and isinstance(row, dict)
            and isinstance(row.get("failure_classes"), dict)
        }
        return {
            "measurement_kind": "pre_modernization_historical_baseline",
            "cutoff": cutoff.isoformat(),
            "historical_sources": {
                "benchmark": {"path": _relative(self.project_root, benchmark_path), "sha256": _sha256(benchmark_path)},
                **text_evidence,
                "session_envelopes": session_samples,
            },
            "source_commit": scorecard.get("source_commit"),
            "dimensions": {
                "transcripts": {
                    "status": "COMPACT_ONLY",
                    "limitation": "raw transcript archives were not routine cross-harness authority",
                },
                "payloads": {
                    "status": "OBSERVED_COMPACT",
                    "harnesses": sorted(sample["harness"] for sample in session_samples),
                },
                "confusion": {
                    "status": "PARTIAL",
                    "limitation": "Cursor compact-session evidence and provider full-transcript evidence were incomplete",
                },
                "tokens": {
                    "status": "NOT_OBSERVED_REAL",
                    "limitation": "pre-modernization token counts were heuristic or absent, not provider usage accounting",
                },
                "latency": {"status": "OBSERVED", "samples": latency_samples},
                "first_tool_behavior": {
                    "status": "NOT_OBSERVED",
                    "limitation": "session envelopes recorded projected commands, not actual first tool calls",
                    "projected_first_commands": {
                        sample["harness"]: sample["projected_first_command"] for sample in session_samples
                    },
                },
                "failures": {
                    "status": "OBSERVED",
                    "record_count": failure_count,
                    "classes_by_harness": failure_classes,
                },
                "regressions": {
                    "status": "OBSERVED_PROTOCOL_SMOKE",
                    "passed": smoke_passed,
                    "total": smoke_total,
                },
            },
        }

    def _operational_metrics(self) -> dict[str, Any]:
        command, benchmark = self._activity_benchmark()
        rows = self._telemetry_files()
        usable = [row for _, row in rows if isinstance(row.get("timing", {}).get("elapsed_ms"), int)]
        statuses = [str(row.get("outcome", {}).get("exit_status")) for row in usable]
        harness_counts: dict[str, int] = {}
        for row in usable:
            name = str(row.get("worker", {}).get("harness_name"))
            harness_counts[name] = harness_counts.get(name, 0) + 1
        if len(usable) < 2 or "succeeded" not in statuses or "failed" not in statuses:
            raise MeasurementBlocked("operational telemetry lacks repeated success and degradation observations")
        activities = benchmark.get("activities", {})
        if any(row.get("explicit_query_source_count", 0) < 1 for row in activities.values()):
            raise MeasurementFailed("one or more activity lookup routes were not measured")
        if benchmark.get("never_startup", {}).get("missing_required_forbidden_payloads"):
            raise MeasurementFailed("stale-leakage benchmark reports missing never-startup protections")
        return {
            "measurement_kind": "orientation_lookup_route_token_latency_degradation_recurrence",
            "activity_benchmark": command,
            "orientation_activity_count": len(activities),
            "lookup_source_counts": {name: row.get("explicit_query_source_count") for name, row in activities.items()},
            "stale_leakage_issue_codes": [
                issue.get("code") for issue in benchmark.get("issues", []) if "startup" in str(issue.get("code"))
            ],
            "route_classifications": {name: row.get("classification") for name, row in activities.items()},
            "token_measurements": {
                "global": benchmark.get("summary", {}).get("global_surface_token_estimate"),
                "activity_total": benchmark.get("summary", {}).get("activity_auto_payload_token_estimate_total"),
            },
            "latency_ms": [row.get("timing", {}).get("elapsed_ms") for row in usable],
            "degradation_count": statuses.count("failed"),
            "successful_count": statuses.count("succeeded"),
            "recurrence_by_harness": harness_counts,
        }

    def _shadow_observations(self, plan: Plan) -> dict[str, Any]:
        required_activities = {"ops", "deliberation", "build", "test", "spec", "project"}
        observed: dict[str, set[str]] = {name: set() for name in plan.harnesses}
        evidence: list[dict[str, str]] = []
        for path, row in self._telemetry_files():
            worker = row.get("worker", {})
            harness = worker.get("harness_name")
            activity = row.get("activity") or row.get("correlation", {}).get("activity")
            mode = row.get("mode") or row.get("correlation", {}).get("mode")
            if harness in observed and activity in required_activities and mode in {"shadow", "report-only"}:
                observed[str(harness)].add(str(activity))
                evidence.append({"path": _relative(self.project_root, path), "sha256": _sha256(path)})
        incomplete = {
            name: sorted(required_activities - activities)
            for name, activities in observed.items()
            if activities != required_activities
        }
        if incomplete:
            raise MeasurementBlocked(f"shadow/report-only activity observations are incomplete: {incomplete}")
        return {
            "measurement_kind": "shadow_activity_harness_observation",
            "observed": {name: sorted(values) for name, values in observed.items()},
            "invocation_evidence": evidence,
        }

    def _valid_receipt(self, name: str) -> dict[str, Any]:
        plan = PLAN_BY_NAME[name]
        result = semantic_checker._check_receipt(
            name,
            semantic_assertion_id=plan.semantic_assertion_id,
            manifest=self.manifest,
            project_root=self.project_root,
            evidence_dir=self.evidence_dir,
        )
        if result.status != "PASS" or not isinstance(result.evidence, dict):
            raise MeasurementBlocked(f"required receipt {name} is absent or invalid: {result.evidence}")
        return _read_object(Path(str(result.evidence["receipt"])))

    def _dependent_receipts(self) -> dict[str, Any]:
        baseline = self._valid_receipt("pre-modernization-baseline")
        shadow = self._valid_receipt("shadow-six-activities-primary-harnesses")
        command = self._run_command(
            "zero-tolerance-hard-invariants",
            _pytest("platform_tests/scripts/test_modernization_hard_invariants.py"),
            600,
        )
        return {
            "measurement_kind": "baseline_shadow_threshold_calibration",
            "baseline_measurement": baseline["measurement"],
            "shadow_measurement": shadow["measurement"],
            "zero_tolerance_hard_invariants": command,
        }

    def _qualifying_clean_runs(self) -> list[dict[str, Any]]:
        runs = release_checker._qualifying_runs(self.manifest, release_checker.DEFAULT_STATE_DIR)
        return runs.get(self.git_head, [])

    def _clean_run(self, plan: Plan) -> dict[str, Any]:
        required = {item for item in (plan.prerequisite or "").split(",") if item}
        runs = self._qualifying_clean_runs()
        if not runs:
            raise MeasurementBlocked("no independently attested clean acceptance run exists at the current Git HEAD")
        selected = runs[-1]
        by_id = {row.get("test_id"): row for row in selected.get("results", [])}
        missing = sorted(test_id for test_id in required if by_id.get(test_id, {}).get("status") != "pass")
        if missing:
            raise MeasurementBlocked(f"clean run does not contain passing required tests: {missing}")
        run_path = Path(str(selected.get("_path", "")))
        if not run_path.is_file():
            run_path = release_checker.DEFAULT_STATE_DIR / "runs" / f"{selected['run_id']}.json"
        return {
            "measurement_kind": "independently_attested_clean_run_selection",
            "run_id": selected.get("run_id"),
            "run_report": {"path": _relative(self.project_root, run_path), "sha256": _sha256(run_path)},
            "passing_test_ids": sorted(required),
        }

    def _pilot_observation(self) -> dict[str, Any]:
        pilot = semantic_checker.check_git_modernization_pilot(
            manifest=self.manifest,
            project_root=self.project_root,
            evidence_dir=self.evidence_dir,
        )
        if pilot.status != "PASS":
            raise MeasurementBlocked(f"real modernization Git lifecycle pilot is not verified: {pilot.evidence}")
        command = self._run_command(
            "operational-observation-git-lifecycle",
            _pytest("platform_tests/scripts/test_modernization_git_lifecycle.py"),
            900,
        )
        successful = [
            path for path, row in self._telemetry_files() if row.get("outcome", {}).get("exit_status") == "succeeded"
        ]
        if not successful:
            raise MeasurementBlocked("no successful operational harness observation exists")
        return {
            "measurement_kind": "verified_pilot_and_operational_observation",
            "pilot_assertions": pilot.evidence,
            "git_lifecycle": command,
            "successful_invocations": [
                {"path": _relative(self.project_root, path), "sha256": _sha256(path)} for path in successful
            ],
        }

    def _independent_verification(self) -> dict[str, Any]:
        if self.issuer is None or self.issuer["session"].get("role") != "loyal-opposition":
            raise MeasurementBlocked(
                "independent verification must be collected by a canonical Loyal Opposition session"
            )
        status = release_checker.evaluate_status(
            self.manifest,
            project_root=self.project_root,
            state_dir=release_checker.DEFAULT_STATE_DIR,
        )
        non_owner_blockers = [
            blocker for blocker in status["blockers"] if "owner release-candidate acceptance" not in blocker
        ]
        if non_owner_blockers:
            raise MeasurementBlocked("independent verification is incomplete: " + "; ".join(non_owner_blockers))
        audits = release_checker._audit_records(release_checker.DEFAULT_STATE_DIR)
        if not audits:
            raise MeasurementBlocked("independent modernization audit is absent")
        audit = audits[-1]
        audit_path = Path(str(audit.get("_path", "")))
        if not audit_path.is_file():
            raise MeasurementBlocked("latest independent modernization audit path is invalid")
        independence = audit.get("independence", {})
        qualifying_run_ids = set(status.get("qualifying_clean_run_ids", []))
        reports = {
            str(report.get("run_id")): report
            for report in release_checker._run_reports(release_checker.DEFAULT_STATE_DIR)
            if str(report.get("run_id")) in qualifying_run_ids
        }
        producer_sessions = [
            reports[run_id].get("runner", {}).get("session_context_id")
            for run_id in status.get("qualifying_clean_run_ids", [])
            if run_id in reports
        ]
        verifier_session = independence.get("reviewer_session_context_id")
        if (
            independence.get("reviewer_role") != "loyal-opposition"
            or not verifier_session
            or verifier_session != self.issuer["session"].get("session_id")
            or len(producer_sessions) != len(qualifying_run_ids)
            or any(not session or session == verifier_session for session in producer_sessions)
        ):
            raise MeasurementBlocked("independent audit lacks canonical Loyal Opposition provenance")
        producer_authorities: list[dict[str, Any]] = []
        try:
            for session_id in producer_sessions:
                authority = resolve_session_authority(
                    self.project_root,
                    str(session_id),
                    evidence_dir=self.evidence_dir,
                )
                if authority["session"].get("role") != "prime-builder":
                    raise CollectionError(f"producer session {session_id} is not canonically Prime Builder")
                producer_authorities.append(authority)
        except CollectionError as exc:
            raise MeasurementBlocked(f"independent audit producer provenance is invalid: {exc}") from exc
        return {
            "measurement_kind": "independent_audit_and_clean_run_reconciliation",
            "release_status": status,
            "audit": {"path": _relative(self.project_root, audit_path), "sha256": _sha256(audit_path)},
            "producer_session_context_ids": producer_sessions,
            "producer_authorities": producer_authorities,
            "verifier_session_context_id": verifier_session,
            "verifier_role": "loyal-opposition",
        }

    def _program_closure(self) -> dict[str, Any]:
        status = release_checker.evaluate_status(
            self.manifest,
            project_root=self.project_root,
            state_dir=release_checker.DEFAULT_STATE_DIR,
        )
        if not status.get("engineering_ready"):
            raise MeasurementBlocked("program closure is not ready: " + "; ".join(status.get("blockers", [])))
        independent_receipt = self._valid_receipt("independent-verification")
        audits = release_checker._audit_records(release_checker.DEFAULT_STATE_DIR)
        if not audits:
            raise MeasurementBlocked("program closure lacks an independent modernization audit")
        audit_path = Path(str(audits[-1].get("_path", "")))
        if not audit_path.is_file():
            raise MeasurementBlocked("program closure independent audit path is invalid")
        return {
            "measurement_kind": "release_candidate_program_closure",
            "release_status": status,
            "independent_verification_measurement": independent_receipt["measurement"],
            "independent_audit": {"path": _relative(self.project_root, audit_path), "sha256": _sha256(audit_path)},
            "owner_acceptance": "required_external_owner_decision_after_engineering_closure",
        }

    def _measure(self, plan: Plan) -> dict[str, Any]:
        if plan.kind == "program-reconciliation":
            return self._program_reconciliation(plan)
        if plan.kind == "artifact-audit":
            return self._artifact_audit(plan)
        if plan.kind == "pytest":
            return self._pytest_measurement(plan)
        if plan.kind == "activity-matrix":
            return self._activity_matrix()
        if plan.kind == "live-harness":
            return self._live_harness(plan)
        if plan.kind == "pre-baseline":
            return self._pre_baseline()
        if plan.kind == "operational-metrics":
            return self._operational_metrics()
        if plan.kind == "shadow-observations":
            return self._shadow_observations(plan)
        if plan.kind == "dependent-receipts":
            return self._dependent_receipts()
        if plan.kind == "clean-run":
            return self._clean_run(plan)
        if plan.kind == "pilot-observation":
            return self._pilot_observation()
        if plan.kind == "independent-verification":
            return self._independent_verification()
        if plan.kind == "program-closure":
            return self._program_closure()
        raise CollectionError(f"unsupported measurement kind: {plan.kind}")

    def collect(self, plan: Plan) -> CollectionResult:
        if self.issuer is None:
            return CollectionResult(
                plan.receipt_name,
                plan.semantic_assertion_id,
                plan.group,
                "BLOCKED",
                self.issuer_error or "canonical runtime session provenance is unavailable",
            )
        try:
            observed = self._measure(plan)
        except MeasurementBlocked as exc:
            return CollectionResult(
                plan.receipt_name,
                plan.semantic_assertion_id,
                plan.group,
                "BLOCKED",
                str(exc),
            )
        except MeasurementFailed as exc:
            return CollectionResult(
                plan.receipt_name,
                plan.semantic_assertion_id,
                plan.group,
                "FAIL",
                str(exc),
            )
        except CollectionError as exc:
            return CollectionResult(
                plan.receipt_name,
                plan.semantic_assertion_id,
                plan.group,
                "FAIL",
                str(exc),
            )

        issue_dir = self._issue_dir(plan)
        issue_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            issue_dir.mkdir()
        except FileExistsError:
            return CollectionResult(
                plan.receipt_name,
                plan.semantic_assertion_id,
                plan.group,
                "FAIL",
                f"append-only issue path already exists: {issue_dir}",
            )
        measurement = {
            "schema_version": semantic_checker.MEASUREMENT_SCHEMA_VERSION,
            "issue_id": self.invocation_id,
            "semantic_assertion_id": plan.semantic_assertion_id,
            "receipt_name": plan.receipt_name,
            "scope_digest_sha256": self.scope_digest,
            "git_head": self.git_head,
            "issuer": self.issuer,
            "status": "PASS",
            "observed": observed,
        }
        measurement_path = issue_dir / "measurement.json"
        try:
            _exclusive_write_json(measurement_path, measurement)
        except CollectionError as exc:
            return CollectionResult(
                plan.receipt_name,
                plan.semantic_assertion_id,
                plan.group,
                "FAIL",
                str(exc),
            )
        measurement_ref = {
            "path": _relative(self.project_root, measurement_path),
            "sha256": _sha256(measurement_path),
        }
        receipt: dict[str, Any] = {
            "schema_version": semantic_checker.RECEIPT_SCHEMA_VERSION,
            "issue_id": self.invocation_id,
            "semantic_assertion_id": plan.semantic_assertion_id,
            "scope_digest_sha256": self.scope_digest,
            "status": "PASS",
            "issuer": self.issuer,
            "git_head": self.git_head,
            "measurement": measurement_ref,
            "evidence": [measurement_ref],
        }
        if plan.receipt_name == "independent-verification":
            receipt.update(
                {
                    "producer_session_context_ids": observed["producer_session_context_ids"],
                    "verifier_session_context_id": observed["verifier_session_context_id"],
                    "verifier_role": "loyal-opposition",
                }
            )
        receipt_path = issue_dir / "receipt.json"
        try:
            _exclusive_write_json(receipt_path, receipt)
            receipt_ref = {
                "path": _relative(self.project_root, receipt_path),
                "sha256": _sha256(receipt_path),
            }
            issuance = {
                "schema_version": semantic_checker.ISSUANCE_SCHEMA_VERSION,
                "service_id": semantic_checker.COLLECTOR_SERVICE_ID,
                "issue_id": self.invocation_id,
                "receipt_name": plan.receipt_name,
                "semantic_assertion_id": plan.semantic_assertion_id,
                "scope_digest_sha256": self.scope_digest,
                "git_head": self.git_head,
                "status": "ISSUED",
                "issuer": self.issuer,
                "receipt": receipt_ref,
                "measurement": measurement_ref,
            }
            _exclusive_write_json(issue_dir / "issuance.json", issuance)
        except CollectionError as exc:
            return CollectionResult(
                plan.receipt_name,
                plan.semantic_assertion_id,
                plan.group,
                "FAIL",
                str(exc),
                measurement_path=_relative(self.project_root, measurement_path),
            )
        errors = self.validate_receipt(plan)
        if errors:
            return CollectionResult(
                plan.receipt_name,
                plan.semantic_assertion_id,
                plan.group,
                "FAIL",
                "collector produced an invalid receipt: " + "; ".join(errors),
                measurement_path=_relative(self.project_root, measurement_path),
            )
        return CollectionResult(
            plan.receipt_name,
            plan.semantic_assertion_id,
            plan.group,
            "COLLECTED",
            "objective-specific executable measurement passed",
            _relative(self.project_root, receipt_path),
            _relative(self.project_root, measurement_path),
        )

    def validate_receipt(self, plan: Plan) -> list[str]:
        errors, _receipt = semantic_checker._validate_receipt_issue(
            self._issue_dir(plan),
            name=plan.receipt_name,
            semantic_assertion_id=plan.semantic_assertion_id,
            manifest=self.manifest,
            project_root=self.project_root,
            evidence_dir=self.evidence_dir,
        )
        return errors

    def status(self, plans: tuple[Plan, ...] = PLANS) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []
        for plan in plans:
            issue_root = self.evidence_dir / "issues" / plan.receipt_name
            if not any(issue_root.glob("*/issuance.json")):
                rows.append(
                    asdict(
                        CollectionResult(
                            plan.receipt_name,
                            plan.semantic_assertion_id,
                            plan.group,
                            "BLOCKED",
                            "no valid collected receipt exists",
                        )
                    )
                )
                continue
            semantic = semantic_checker._check_receipt(
                plan.receipt_name,
                semantic_assertion_id=plan.semantic_assertion_id,
                manifest=self.manifest,
                project_root=self.project_root,
                evidence_dir=self.evidence_dir,
            )
            valid = semantic.status == "PASS" and isinstance(semantic.evidence, dict)
            receipt_path = str(semantic.evidence.get("receipt")) if valid else None
            rows.append(
                asdict(
                    CollectionResult(
                        plan.receipt_name,
                        plan.semantic_assertion_id,
                        plan.group,
                        "COLLECTED" if valid else "INVALID",
                        "receipt and nested evidence hashes are valid" if valid else str(semantic.evidence),
                        _relative(self.project_root, Path(receipt_path)) if receipt_path else None,
                    )
                )
            )
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["status"]] = counts.get(row["status"], 0) + 1
        return {
            "schema_version": 1,
            "scope_digest_sha256": self.scope_digest,
            "git_head": self.git_head,
            "issuer": self.issuer,
            "counts": counts,
            "results": rows,
        }


def _render(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    counts = payload.get("counts", {})
    print("MODERNIZATION SEMANTIC EVIDENCE: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    for row in payload.get("results", []):
        print(f"- {row['status']} {row['semantic_assertion_id']} {row['receipt_name']}: {row['reason']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    subparsers = parser.add_subparsers(dest="command", required=True)
    group_parser = subparsers.add_parser("group", help="collect one deterministic evidence group")
    group_parser.add_argument("group", choices=GROUPS)
    subparsers.add_parser("all", help="attempt all obtainable receipts and preserve honest blockers")
    subparsers.add_parser("status", help="validate collected receipts without executing measurements")
    args = parser.parse_args(argv)

    coverage_errors = validate_plan_coverage()
    if coverage_errors:
        print("MODERNIZATION SEMANTIC EVIDENCE: FAIL - " + "; ".join(coverage_errors), file=sys.stderr)
        return 2
    try:
        collector = Collector()
    except CollectionError as exc:
        print(f"MODERNIZATION SEMANTIC EVIDENCE: FAIL - {exc}", file=sys.stderr)
        return 2
    if args.command == "status":
        payload = collector.status()
    else:
        selected = PLANS if args.command == "all" else tuple(plan for plan in PLANS if plan.group == args.group)
        results = [asdict(collector.collect(plan)) for plan in selected]
        counts: dict[str, int] = {}
        for row in results:
            counts[row["status"]] = counts.get(row["status"], 0) + 1
        payload = {
            "schema_version": 1,
            "scope_digest_sha256": collector.scope_digest,
            "git_head": collector.git_head,
            "issuer": collector.issuer,
            "counts": counts,
            "results": results,
        }
    _render(payload, as_json=args.as_json)
    return 1 if any(status in payload.get("counts", {}) for status in {"FAIL", "INVALID"}) else 0


if __name__ == "__main__":
    raise SystemExit(main())
