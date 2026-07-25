#!/usr/bin/env python3
"""Validate and execute the frozen GT-KB modernization acceptance contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.session.envelope import (  # noqa: E402
    EnvelopeError,
    _validate_worker_role_provenance,
    resolve_worker_role_provenance,
)

DEFAULT_MANIFEST = PROJECT_ROOT / "config" / "governance" / "modernization-release-candidate.json"
DEFAULT_STATE_DIR = PROJECT_ROOT / ".gtkb-state" / "modernization-release-candidate"
_DIGEST_FIELD = "frozen_scope_digest_sha256"
_RESOLVED_FINDING_STATUSES = {"closed", "accepted", "deferred", "backlogged"}
_AUDIT_FINDING_STATUSES = _RESOLVED_FINDING_STATUSES | {"open"}
_AUDIT_FINDING_SEVERITIES = {"P0", "P1", "P2", "P3"}
_RUN_SCHEMA_VERSION = 4
_RUNNER_ID = "scripts/check_modernization_release_candidate.py"
_RUNNER_VERSION = 4
_ATTESTATION_SCHEMA_VERSION = 2
_ATTESTER_ID = "scripts/check_modernization_release_candidate.py:attest-run"
_ACTOR_RECEIPT_SCHEMA_VERSION = 2
_ACTOR_ISSUER_ID = "scripts/check_modernization_release_candidate.py:actor-receipt"
_AUDIT_SCHEMA_VERSION = 5
_AUDIT_ISSUER_ID = "scripts/check_modernization_release_candidate.py:record-audit"
_SHA256_RE = re.compile(r"^[0-9A-F]{64}$")
_GIT_HEAD_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
_RUN_ID_RE = re.compile(r"^\d{8}T\d{6}\.\d{6}Z-[0-9A-F]{12}$")
_EMPTY_SHA256 = hashlib.sha256(b"").hexdigest().upper()


class ManifestError(RuntimeError):
    """Raised when the frozen acceptance contract is malformed or changed."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"missing JSON artifact: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"malformed JSON artifact {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ManifestError(f"JSON artifact root must be an object: {path}")
    return payload


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    return _read_json(path)


def scope_digest(manifest: dict[str, Any]) -> str:
    payload = copy.deepcopy(manifest)
    program = payload.get("program")
    if isinstance(program, dict):
        program.pop(_DIGEST_FIELD, None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper()


def _report_digest(report: dict[str, Any]) -> str:
    payload = {key: value for key, value in report.items() if key not in {"_path", "report_sha256"}}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper()


def _attestation_digest(attestation: dict[str, Any]) -> str:
    payload = {key: value for key, value in attestation.items() if key not in {"_path", "attestation_sha256"}}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper()


def _record_digest(record: dict[str, Any], digest_field: str) -> str:
    payload = {key: value for key, value in record.items() if key not in {"_path", digest_field}}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper()


def _safe_relative_path(value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value.replace("\\", "/"):
        return None
    return path


def _parse_utc_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(UTC)


def _require_nonempty_string(value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")


def _expanded_handles(family: dict[str, Any]) -> list[str]:
    first = family.get("first")
    last = family.get("last")
    width = family.get("width")
    prefix = family.get("handle_prefix")
    if not all(isinstance(value, int) for value in (first, last, width)) or not isinstance(prefix, str):
        return []
    if first < 1 or last < first or width < 1:
        return []
    return [f"{prefix}{value:0{width}d}" for value in range(first, last + 1)]


def validate_manifest(
    manifest: dict[str, Any],
    *,
    project_root: Path = PROJECT_ROOT,
    require_test_paths: bool = False,
) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    program = manifest.get("program")
    if not isinstance(program, dict):
        return errors + ["program must be an object"]
    for field in ("id", "project_id", "title", "scope_source", "new_finding_default", "scope_change_authority"):
        _require_nonempty_string(program.get(field), f"program.{field}", errors)
    if program.get("scope_source_version") != 1:
        errors.append("program.scope_source_version must be 1")
    if program.get("expected_handle_count") != 94:
        errors.append("program.expected_handle_count must be 94")
    if program.get("required_clean_passes") != 2:
        errors.append("program.required_clean_passes must be 2")
    clean_run_max_age_hours = program.get("clean_run_max_age_hours")
    if not isinstance(clean_run_max_age_hours, int) or clean_run_max_age_hours < 1:
        errors.append("program.clean_run_max_age_hours must be a positive integer")
    if program.get("blocking_severities") != ["P0", "P1", "P2"]:
        errors.append("program.blocking_severities must be exactly P0, P1, P2")
    if program.get("new_finding_default") != "post_modernization_backlog":
        errors.append("program.new_finding_default must be post_modernization_backlog")
    if program.get("scope_change_authority") != "owner_only":
        errors.append("program.scope_change_authority must be owner_only")
    if program.get("owner_acceptance_required") is not True:
        errors.append("program.owner_acceptance_required must be true")
    if program.get("production_deployment_separate") is not True:
        errors.append("program.production_deployment_separate must be true")

    recorded_digest = program.get(_DIGEST_FIELD)
    calculated_digest = scope_digest(manifest)
    if recorded_digest != calculated_digest:
        errors.append(f"program.{_DIGEST_FIELD} mismatch: expected {calculated_digest}, found {recorded_digest!r}")

    families = manifest.get("scope_families")
    if not isinstance(families, list) or not families:
        errors.append("scope_families must be a non-empty array")
        families = []
    family_ids: list[str] = []
    handles: list[str] = []
    handle_to_family: dict[str, str] = {}
    for index, family in enumerate(families):
        if not isinstance(family, dict):
            errors.append(f"scope_families[{index}] must be an object")
            continue
        family_id = family.get("id")
        _require_nonempty_string(family_id, f"scope_families[{index}].id", errors)
        _require_nonempty_string(family.get("project_id"), f"scope_families[{index}].project_id", errors)
        expanded = _expanded_handles(family)
        if not expanded:
            errors.append(f"scope_families[{index}] has an invalid handle range")
        if isinstance(family_id, str):
            family_ids.append(family_id)
            handle_to_family.update({handle: family_id for handle in expanded})
        handles.extend(expanded)
    duplicate_families = sorted(item for item, count in Counter(family_ids).items() if count > 1)
    duplicate_handles = sorted(item for item, count in Counter(handles).items() if count > 1)
    if duplicate_families:
        errors.append("duplicate scope family ids: " + ", ".join(duplicate_families))
    if duplicate_handles:
        errors.append("duplicate scope handles: " + ", ".join(duplicate_handles))
    if len(handles) != program.get("expected_handle_count"):
        errors.append(f"expanded scope contains {len(handles)} handles, expected 94")

    tests = manifest.get("acceptance_tests")
    if not isinstance(tests, list) or not tests:
        errors.append("acceptance_tests must be a non-empty array")
        tests = []
    test_ids: list[str] = []
    for index, test in enumerate(tests):
        if not isinstance(test, dict):
            errors.append(f"acceptance_tests[{index}] must be an object")
            continue
        test_id = test.get("id")
        _require_nonempty_string(test_id, f"acceptance_tests[{index}].id", errors)
        if isinstance(test_id, str):
            test_ids.append(test_id)
        command = test.get("command")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(token, str) and token for token in command)
        ):
            errors.append(f"acceptance_tests[{index}].command must be a non-empty string array")
        elif command[0] != "{python}":
            errors.append(f"acceptance_tests[{index}].command must use {{python}} as its executable")
        required_paths = test.get("required_paths")
        if not isinstance(required_paths, list) or not required_paths:
            errors.append(f"acceptance_tests[{index}].required_paths must be a non-empty array")
            required_paths = []
        for relative in required_paths:
            safe_path = _safe_relative_path(relative)
            if safe_path is None:
                errors.append(f"acceptance_tests[{index}] has unsafe required path: {relative!r}")
                continue
            if require_test_paths and not (project_root / safe_path).is_file():
                errors.append(f"acceptance test path is missing: {relative}")
        timeout = test.get("timeout_seconds")
        if not isinstance(timeout, int) or timeout < 1:
            errors.append(f"acceptance_tests[{index}].timeout_seconds must be a positive integer")
    duplicate_tests = sorted(item for item, count in Counter(test_ids).items() if count > 1)
    if duplicate_tests:
        errors.append("duplicate acceptance test ids: " + ", ".join(duplicate_tests))

    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        errors.append("capabilities must be a non-empty array")
        capabilities = []
    capability_ids: list[str] = []
    mapped_families: list[str] = []
    referenced_test_ids: set[str] = set()
    family_acceptance_ids: dict[str, set[str]] = {}
    for index, capability in enumerate(capabilities):
        if not isinstance(capability, dict):
            errors.append(f"capabilities[{index}] must be an object")
            continue
        capability_id = capability.get("id")
        family_id = capability.get("scope_family")
        _require_nonempty_string(capability_id, f"capabilities[{index}].id", errors)
        _require_nonempty_string(capability.get("objective"), f"capabilities[{index}].objective", errors)
        if isinstance(capability_id, str):
            capability_ids.append(capability_id)
        if not isinstance(family_id, str) or family_id not in family_ids:
            errors.append(f"capabilities[{index}].scope_family is unknown: {family_id!r}")
        else:
            mapped_families.append(family_id)
        acceptance_ids = capability.get("acceptance_test_ids")
        if not isinstance(acceptance_ids, list) or not acceptance_ids:
            errors.append(f"capabilities[{index}].acceptance_test_ids must be non-empty")
            continue
        for test_id in acceptance_ids:
            if test_id not in test_ids:
                errors.append(f"capabilities[{index}] references unknown acceptance test: {test_id!r}")
            elif isinstance(test_id, str):
                referenced_test_ids.add(test_id)
                if isinstance(family_id, str):
                    family_acceptance_ids.setdefault(family_id, set()).add(test_id)
    duplicate_capabilities = sorted(item for item, count in Counter(capability_ids).items() if count > 1)
    if duplicate_capabilities:
        errors.append("duplicate capability ids: " + ", ".join(duplicate_capabilities))
    if Counter(mapped_families) != Counter(family_ids):
        errors.append("capabilities must map every scope family exactly once")
    unreferenced_tests = sorted(set(test_ids) - referenced_test_ids)
    if unreferenced_tests:
        errors.append("acceptance tests are not mapped to a capability: " + ", ".join(unreferenced_tests))

    handle_records = manifest.get("scope_handles")
    if not isinstance(handle_records, list) or not handle_records:
        errors.append("scope_handles must be a non-empty array")
        handle_records = []
    record_ids: list[str] = []
    for index, record in enumerate(handle_records):
        if not isinstance(record, dict):
            errors.append(f"scope_handles[{index}] must be an object")
            continue
        handle_id = record.get("id")
        family_id = record.get("scope_family")
        _require_nonempty_string(handle_id, f"scope_handles[{index}].id", errors)
        _require_nonempty_string(record.get("objective"), f"scope_handles[{index}].objective", errors)
        if isinstance(handle_id, str):
            record_ids.append(handle_id)
            expected_family = handle_to_family.get(handle_id)
            if expected_family is None:
                errors.append(f"scope_handles[{index}] references unknown handle: {handle_id!r}")
            elif family_id != expected_family:
                errors.append(f"scope_handles[{index}].scope_family must be {expected_family!r} for {handle_id}")
        evidence_paths = record.get("implementation_evidence_paths")
        if not isinstance(evidence_paths, list) or not evidence_paths:
            errors.append(f"scope_handles[{index}].implementation_evidence_paths must be non-empty")
            evidence_paths = []
        if len(evidence_paths) != len(set(item for item in evidence_paths if isinstance(item, str))):
            errors.append(f"scope_handles[{index}] has duplicate implementation evidence paths")
        for relative in evidence_paths:
            safe_path = _safe_relative_path(relative)
            if safe_path is None:
                errors.append(f"scope_handles[{index}] has unsafe implementation evidence path: {relative!r}")
                continue
            if require_test_paths and not (project_root / safe_path).is_file():
                errors.append(f"implementation evidence path is missing: {relative}")
        acceptance_ids = record.get("acceptance_test_ids")
        if not isinstance(acceptance_ids, list) or not acceptance_ids:
            errors.append(f"scope_handles[{index}].acceptance_test_ids must be non-empty")
            acceptance_ids = []
        if len(acceptance_ids) != len(set(item for item in acceptance_ids if isinstance(item, str))):
            errors.append(f"scope_handles[{index}] has duplicate acceptance test ids")
        allowed_ids = family_acceptance_ids.get(family_id, set())
        for test_id in acceptance_ids:
            if test_id not in test_ids:
                errors.append(f"scope_handles[{index}] references unknown acceptance test: {test_id!r}")
            elif test_id not in allowed_ids:
                errors.append(
                    f"scope_handles[{index}] acceptance test {test_id!r} is not mapped to family {family_id!r}"
                )
    duplicate_record_ids = sorted(item for item, count in Counter(record_ids).items() if count > 1)
    if duplicate_record_ids:
        errors.append("duplicate scope handle records: " + ", ".join(duplicate_record_ids))
    missing_records = sorted(set(handles) - set(record_ids))
    if missing_records:
        errors.append("scope handles lack explicit records: " + ", ".join(missing_records))
    unexpected_records = sorted(set(record_ids) - set(handles))
    if unexpected_records:
        errors.append("scope handle records are outside the frozen scope: " + ", ".join(unexpected_records))
    if record_ids != handles:
        errors.append("scope_handles must preserve the canonical frozen handle order exactly")
    return errors


def _git_output(project_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=project_root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if result.returncode != 0:
        raise ManifestError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _active_session_id() -> str:
    session_id = (os.environ.get("GTKB_AUTHOR_SESSION_CONTEXT_ID") or "").strip()
    try:
        uuid.UUID(session_id)
    except (ValueError, AttributeError) as exc:
        raise ManifestError("operation requires a runtime-issued active session UUID") from exc
    return session_id


def _write_actor_envelope_snapshot(
    state_dir: Path,
    *,
    session_id: str,
    envelope_sha256: str,
    envelope_bytes: bytes,
) -> str:
    relative = Path("actor-envelopes") / f"{session_id}.json"
    path = state_dir / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(envelope_bytes)
    except FileExistsError:
        if path.read_bytes() != envelope_bytes:
            raise ManifestError(f"actor session-envelope snapshot conflicts with existing evidence: {path}")
    return relative.as_posix()


def _issue_actor_receipt(
    manifest: dict[str, Any],
    *,
    expected_role: str,
    git_head: str,
    project_root: Path,
    state_dir: Path,
) -> dict[str, Any]:
    session_id = _active_session_id()
    try:
        provenance = resolve_worker_role_provenance(project_root, current_session_id=session_id)
    except EnvelopeError as exc:
        raise ManifestError("active session lacks canonical runtime-issued role provenance") from exc
    if provenance.get("role") != expected_role:
        raise ManifestError(f"operation requires an active {expected_role} session")
    harness_name = provenance.get("harness_name")
    harness_id = provenance.get("harness_id")
    if not isinstance(harness_name, str) or not harness_name or not isinstance(harness_id, str) or not harness_id:
        raise ManifestError("canonical actor provenance lacks durable harness identity")
    envelope_path = (
        project_root / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json"
    ).resolve()
    try:
        envelope_relative = envelope_path.relative_to(project_root.resolve()).as_posix()
        envelope_bytes = envelope_path.read_bytes()
    except (ValueError, OSError) as exc:
        raise ManifestError("canonical session envelope is absent from the repository") from exc
    actor = {
        "session_context_id": session_id,
        "harness_id": harness_id,
        "harness_name": harness_name,
        "role": expected_role,
        "role_resolution_source": provenance.get("role_resolution_source"),
    }
    if not isinstance(actor["role_resolution_source"], str) or not actor["role_resolution_source"]:
        raise ManifestError("canonical actor provenance lacks a role-resolution source")
    envelope_sha256 = hashlib.sha256(envelope_bytes).hexdigest().upper()
    snapshot_relative = _write_actor_envelope_snapshot(
        state_dir,
        session_id=session_id,
        envelope_sha256=envelope_sha256,
        envelope_bytes=envelope_bytes,
    )
    receipt = {
        "schema_version": _ACTOR_RECEIPT_SCHEMA_VERSION,
        "issuer": _ACTOR_ISSUER_ID,
        "issued_at": datetime.now(UTC).isoformat(),
        "scope_digest_sha256": scope_digest(manifest),
        "git_head": git_head,
        "actor": actor,
        "session_envelope": {
            "path": envelope_relative,
            "sha256": envelope_sha256,
            "snapshot_path": snapshot_relative,
        },
    }
    receipt["actor_receipt_sha256"] = _record_digest(receipt, "actor_receipt_sha256")
    path = state_dir / "actors" / f"{session_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(receipt, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except FileExistsError:
        existing = _read_json(path)
        existing["_path"] = str(path)
        errors = _validate_actor_receipt(
            manifest,
            existing,
            state_dir,
            expected_role=expected_role,
            expected_git_head=git_head,
        )
        if errors:
            raise ManifestError("existing actor receipt conflicts with the active session: " + "; ".join(errors))
        if existing.get("actor") != actor or existing.get("session_envelope") != receipt["session_envelope"]:
            raise ManifestError("existing actor receipt conflicts with current canonical session provenance")
        return existing
    receipt["_path"] = str(path)
    return receipt


def _require_active_dispatch_context(
    project_root: Path,
    *,
    session_id: str,
    expected_role: str,
) -> dict[str, Any]:
    try:
        provenance = resolve_worker_role_provenance(project_root, current_session_id=session_id)
    except EnvelopeError as exc:
        raise ManifestError("independent review requires canonical dispatcher-issued role provenance") from exc
    dispatch_run_id = provenance.get("dispatch_run_id")
    if provenance.get("role") != expected_role:
        raise ManifestError(f"independent review requires an active {expected_role} dispatcher session")
    if provenance.get("role_resolution_source") != "dispatcher_composition" or not dispatch_run_id:
        raise ManifestError("independent review requires dispatcher_composition role authority")
    if os.environ.get("GTKB_BRIDGE_POLLER_RUN_ID") != dispatch_run_id:
        raise ManifestError("independent review dispatch environment does not bind the session envelope")
    return provenance


def _actor_receipt(state_dir: Path, reference: object) -> dict[str, Any] | None:
    if not isinstance(reference, dict) or set(reference) != {"path", "sha256"}:
        return None
    relative = _safe_relative_path(reference.get("path"))
    if relative is None or relative.parts[:1] != ("actors",):
        return None
    path = state_dir / relative
    try:
        receipt = _read_json(path)
    except ManifestError:
        return None
    receipt["_path"] = str(path)
    if receipt.get("actor_receipt_sha256") != reference.get("sha256"):
        return None
    return receipt


def _validate_actor_receipt(
    manifest: dict[str, Any],
    receipt: dict[str, Any] | None,
    state_dir: Path,
    *,
    expected_role: str,
    expected_git_head: str,
) -> list[str]:
    if receipt is None:
        return ["canonical actor receipt is missing"]
    errors: list[str] = []
    path_value = receipt.get("_path")
    path = Path(path_value) if isinstance(path_value, str) else None
    actor = receipt.get("actor")
    session_id = actor.get("session_context_id") if isinstance(actor, dict) else None
    expected_path = (state_dir / "actors" / f"{session_id}.json").resolve()
    if path is None or path.resolve() != expected_path:
        errors.append("actor receipt path does not bind its session")
    if receipt.get("schema_version") != _ACTOR_RECEIPT_SCHEMA_VERSION or receipt.get("issuer") != _ACTOR_ISSUER_ID:
        errors.append("actor receipt issuer or schema is not canonical")
    if receipt.get("scope_digest_sha256") != scope_digest(manifest):
        errors.append("actor receipt does not bind the frozen scope")
    if receipt.get("git_head") != expected_git_head:
        errors.append("actor receipt does not bind the candidate Git HEAD")
    if not isinstance(actor, dict) or set(actor) != {
        "session_context_id",
        "harness_id",
        "harness_name",
        "role",
        "role_resolution_source",
    }:
        errors.append("actor receipt identity is incomplete")
    else:
        try:
            uuid.UUID(str(actor.get("session_context_id")))
        except (ValueError, AttributeError):
            errors.append("actor receipt session is not a runtime UUID")
        if actor.get("role") != expected_role:
            errors.append(f"actor receipt role is not {expected_role}")
        for field in ("harness_id", "harness_name", "role_resolution_source"):
            if not isinstance(actor.get(field), str) or not actor[field].strip():
                errors.append(f"actor receipt {field} is missing")
    envelope = receipt.get("session_envelope")
    if not isinstance(envelope, dict) or set(envelope) != {"path", "sha256", "snapshot_path"}:
        errors.append("actor receipt session-envelope evidence is incomplete")
    else:
        envelope_relative = _safe_relative_path(envelope.get("path"))
        envelope_sha256 = envelope.get("sha256")
        snapshot_relative = _safe_relative_path(envelope.get("snapshot_path"))
        expected_envelope_relative = None
        if isinstance(actor, dict):
            expected_envelope_relative = (
                Path("harness-state")
                / str(actor.get("harness_name"))
                / "session-envelopes"
                / f"{actor.get('session_context_id')}.json"
            )
        if envelope_relative is None or envelope_relative != expected_envelope_relative:
            errors.append("actor receipt session-envelope path is not the exact canonical session path")
        if _SHA256_RE.fullmatch(str(envelope_sha256)) is None:
            errors.append("actor receipt session-envelope hash is invalid")
        expected_snapshot_relative = Path("actor-envelopes") / f"{session_id}.json"
        if snapshot_relative is None or snapshot_relative != expected_snapshot_relative:
            errors.append("actor receipt session-envelope snapshot path is invalid")
        else:
            snapshot_path = state_dir / snapshot_relative
            try:
                snapshot_bytes = snapshot_path.read_bytes()
                snapshot_payload = json.loads(snapshot_bytes.decode("utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                errors.append("actor receipt session-envelope snapshot is missing or malformed")
            else:
                snapshot_sha256 = hashlib.sha256(snapshot_bytes).hexdigest().upper()
                if snapshot_sha256 != envelope_sha256:
                    errors.append("actor receipt session-envelope snapshot hash is invalid")
                if not isinstance(snapshot_payload, dict):
                    errors.append("actor receipt session-envelope snapshot root is invalid")
                elif isinstance(actor, dict):
                    try:
                        snapshot_provenance = _validate_worker_role_provenance(
                            snapshot_payload,
                            current_session_id=str(session_id),
                            expected_harness_name=str(actor.get("harness_name")),
                        )
                    except EnvelopeError:
                        errors.append("actor receipt session-envelope snapshot lacks canonical role provenance")
                    else:
                        for field in (
                            "session_context_id",
                            "harness_id",
                            "harness_name",
                            "role",
                            "role_resolution_source",
                        ):
                            provenance_field = "session_id" if field == "session_context_id" else field
                            if actor.get(field) != snapshot_provenance.get(provenance_field):
                                errors.append(f"actor receipt {field} conflicts with its session-envelope snapshot")
    issued_at = _parse_utc_timestamp(receipt.get("issued_at"))
    if issued_at is None:
        errors.append("actor receipt timestamp is invalid")
    recorded = receipt.get("actor_receipt_sha256")
    if recorded != _record_digest(receipt, "actor_receipt_sha256") or _SHA256_RE.fullmatch(str(recorded)) is None:
        errors.append("actor receipt digest is invalid")
    return errors


def _run_reports(state_dir: Path) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for path in sorted((state_dir / "runs").glob("*.json")):
        try:
            payload = _read_json(path)
        except ManifestError:
            continue
        payload["_path"] = str(path)
        reports.append(payload)
    return reports


def _run_attestation(state_dir: Path, run_id: str) -> dict[str, Any] | None:
    path = state_dir / "attestations" / f"{run_id}.json"
    try:
        payload = _read_json(path)
    except ManifestError:
        return None
    payload["_path"] = str(path)
    return payload


def _expected_command(test: dict[str, Any], python_executable: str) -> list[str]:
    return [python_executable if token == "{python}" else token for token in test["command"]]


def _validate_run_report(
    manifest: dict[str, Any],
    report: dict[str, Any],
    state_dir: Path,
    *,
    now: datetime,
) -> list[str]:
    errors: list[str] = []
    path_value = report.get("_path")
    report_path = Path(path_value) if isinstance(path_value, str) else None
    run_id = report.get("run_id")
    if report.get("schema_version") != _RUN_SCHEMA_VERSION:
        errors.append("run schema version is not the current runner schema")
    if not isinstance(run_id, str) or _RUN_ID_RE.fullmatch(run_id) is None:
        errors.append("run_id is not runner-generated")
    if (
        report_path is None
        or report_path.parent.resolve() != (state_dir / "runs").resolve()
        or not isinstance(run_id, str)
        or report_path.stem != run_id
    ):
        errors.append("run report path does not bind its run_id")

    runner = report.get("runner")
    if not isinstance(runner, dict) or set(runner) != {
        "id",
        "version",
        "python_executable",
        "session_context_id",
        "actor_receipt",
    }:
        errors.append("runner provenance is incomplete")
        python_executable = ""
        actor_reference = None
    else:
        python_executable = runner.get("python_executable")
        actor_reference = runner.get("actor_receipt")
        if runner.get("id") != _RUNNER_ID or runner.get("version") != _RUNNER_VERSION:
            errors.append("runner provenance is not canonical")
        if not isinstance(python_executable, str) or not python_executable or not Path(python_executable).is_absolute():
            errors.append("runner python_executable must be an absolute path")
            python_executable = ""
        session_context_id = runner.get("session_context_id")
        if not isinstance(session_context_id, str) or len(session_context_id.strip()) < 12:
            errors.append("runner session_context_id is missing or synthetic")

    if report.get("scope_digest_sha256") != scope_digest(manifest):
        errors.append("run does not bind the frozen scope")
    runner_actor_receipt: dict[str, Any] | None = None
    git_head = report.get("git_head")
    if not isinstance(git_head, str) or _GIT_HEAD_RE.fullmatch(git_head) is None:
        errors.append("run git_head is not a complete Git object ID")
    else:
        actor_receipt = _actor_receipt(state_dir, actor_reference)
        runner_actor_receipt = actor_receipt
        actor_errors = _validate_actor_receipt(
            manifest,
            actor_receipt,
            state_dir,
            expected_role="prime-builder",
            expected_git_head=git_head,
        )
        errors.extend(f"runner {error}" for error in actor_errors)
        if actor_receipt is not None and isinstance(runner, dict):
            actor = actor_receipt.get("actor", {})
            if runner.get("session_context_id") != actor.get("session_context_id"):
                errors.append("runner session does not bind its canonical actor receipt")
    if report.get("git_head_after") != git_head:
        errors.append("candidate Git HEAD changed during the run")
    if report.get("clean_state_before") is not True or report.get("git_status_before_sha256") != _EMPTY_SHA256:
        errors.append("run lacks canonical clean-state-before evidence")
    if report.get("clean_state_after") is not True or report.get("git_status_after_sha256") != _EMPTY_SHA256:
        errors.append("run lacks canonical clean-state-after evidence")
    if report.get("complete") is not True or report.get("status") != "pass":
        errors.append("run is not complete and passing")

    started = _parse_utc_timestamp(report.get("started_at"))
    completed = _parse_utc_timestamp(report.get("completed_at"))
    if started is None or completed is None or completed < started:
        errors.append("run timestamps are missing, non-UTC, or out of order")
    else:
        actor_issued_at = _parse_utc_timestamp(
            runner_actor_receipt.get("issued_at") if runner_actor_receipt is not None else None
        )
        if actor_issued_at is None or actor_issued_at > started:
            errors.append("runner actor receipt was not issued before the clean run")
        if completed > now + timedelta(minutes=5):
            errors.append("run completion timestamp is in the future")
        max_age = timedelta(hours=manifest["program"]["clean_run_max_age_hours"])
        if now - completed > max_age:
            errors.append("run evidence is stale")

    results = report.get("results")
    expected_tests = manifest["acceptance_tests"]
    if not isinstance(results, list) or len(results) != len(expected_tests):
        errors.append("run result set is incomplete")
        results = []
    observed_ids = [item.get("test_id") for item in results if isinstance(item, dict)]
    expected_ids = [item["id"] for item in expected_tests]
    if observed_ids != expected_ids:
        errors.append("run results do not preserve the complete acceptance-test order")
    if len(observed_ids) != len(set(observed_ids)):
        errors.append("run results contain duplicate acceptance-test IDs")

    for index, test in enumerate(expected_tests):
        if index >= len(results) or not isinstance(results[index], dict):
            continue
        result = results[index]
        prefix = f"run result {test['id']}"
        if result.get("command") != _expected_command(test, python_executable):
            errors.append(f"{prefix} command does not match the frozen command")
        if result.get("status") != "pass" or result.get("return_code") != 0:
            errors.append(f"{prefix} is not a successful process result")
        if result.get("git_head_before") != git_head or result.get("git_head_after") != git_head:
            errors.append(f"{prefix} did not execute entirely at the candidate Git HEAD")
        if result.get("clean_state_before") is not True or result.get("clean_state_after") is not True:
            errors.append(f"{prefix} did not execute entirely from clean Git state")
        if (
            result.get("git_status_before_sha256") != _EMPTY_SHA256
            or result.get("git_status_after_sha256") != _EMPTY_SHA256
        ):
            errors.append(f"{prefix} clean-state hashes are not canonical")
        elapsed = result.get("elapsed_seconds")
        if not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool) or elapsed < 0:
            errors.append(f"{prefix} elapsed_seconds is invalid")
        result_started = _parse_utc_timestamp(result.get("started_at"))
        result_completed = _parse_utc_timestamp(result.get("completed_at"))
        if (
            result_started is None
            or result_completed is None
            or result_completed < result_started
            or started is None
            or completed is None
            or result_started < started
            or result_completed > completed
        ):
            errors.append(f"{prefix} timestamps are missing or outside the run interval")
        elif isinstance(elapsed, (int, float)) and not isinstance(elapsed, bool):
            wall_elapsed = (result_completed - result_started).total_seconds()
            if abs(wall_elapsed - elapsed) > 5:
                errors.append(f"{prefix} elapsed evidence conflicts with its timestamps")

        evidence = result.get("evidence")
        if not isinstance(evidence, dict) or set(evidence) != {"path", "sha256", "byte_count", "output_tail"}:
            errors.append(f"{prefix} output evidence is incomplete")
            continue
        expected_relative = f"runs/{run_id}/{index:02d}-{test['id']}.log"
        relative = _safe_relative_path(evidence.get("path"))
        if relative is None or relative.as_posix() != expected_relative:
            errors.append(f"{prefix} output evidence path is not runner-bound")
            continue
        evidence_path = state_dir / relative
        try:
            output_bytes = evidence_path.read_bytes()
        except OSError:
            errors.append(f"{prefix} output evidence file is missing")
            continue
        output_hash = hashlib.sha256(output_bytes).hexdigest().upper()
        if evidence.get("sha256") != output_hash or _SHA256_RE.fullmatch(str(evidence.get("sha256"))) is None:
            errors.append(f"{prefix} output evidence hash is invalid")
        if evidence.get("byte_count") != len(output_bytes):
            errors.append(f"{prefix} output evidence byte count is invalid")
        output_text = output_bytes.decode("utf-8", errors="replace")
        if evidence.get("output_tail") != output_text[-4000:]:
            errors.append(f"{prefix} output evidence tail is invalid")

    recorded_report_digest = report.get("report_sha256")
    if recorded_report_digest != _report_digest(report) or _SHA256_RE.fullmatch(str(recorded_report_digest)) is None:
        errors.append("run report digest is invalid")
    return errors


def _validate_run_attestation(
    manifest: dict[str, Any],
    report: dict[str, Any],
    attestation: dict[str, Any] | None,
    state_dir: Path,
    *,
    now: datetime,
) -> list[str]:
    if attestation is None:
        return ["run lacks an independently issued execution receipt"]
    errors: list[str] = []
    run_id = report.get("run_id")
    path_value = attestation.get("_path")
    path = Path(path_value) if isinstance(path_value, str) else None
    expected_path = (state_dir / "attestations" / f"{run_id}.json").resolve()
    if path is None or path.resolve() != expected_path:
        errors.append("execution receipt path does not bind its run_id")
    if attestation.get("schema_version") != _ATTESTATION_SCHEMA_VERSION:
        errors.append("execution receipt schema version is invalid")
    if attestation.get("issuer") != _ATTESTER_ID:
        errors.append("execution receipt issuer is not canonical")
    if attestation.get("run_id") != run_id:
        errors.append("execution receipt does not bind the run_id")
    if attestation.get("run_report_sha256") != report.get("report_sha256"):
        errors.append("execution receipt does not bind the exact run report")
    if attestation.get("scope_digest_sha256") != scope_digest(manifest):
        errors.append("execution receipt does not bind the frozen scope")
    if attestation.get("git_head") != report.get("git_head"):
        errors.append("execution receipt does not bind the candidate Git HEAD")
    expected_logs = [item.get("evidence", {}).get("sha256") for item in report.get("results", [])]
    if attestation.get("output_log_sha256s") != expected_logs:
        errors.append("execution receipt does not bind the complete output evidence")
    reviewer = attestation.get("reviewer")
    runner = report.get("runner") if isinstance(report.get("runner"), dict) else {}
    reviewer_actor_receipt: dict[str, Any] | None = None
    if not isinstance(reviewer, dict) or set(reviewer) != {
        "session_context_id",
        "harness_id",
        "harness_name",
        "role",
        "actor_receipt",
    }:
        errors.append("execution receipt reviewer identity is missing")
    else:
        reviewer_session = reviewer.get("session_context_id")
        if reviewer.get("role") != "loyal-opposition":
            errors.append("execution receipt was not issued by Loyal Opposition")
        if not isinstance(reviewer_session, str) or len(reviewer_session.strip()) < 12:
            errors.append("execution receipt reviewer session is missing or synthetic")
        if reviewer_session == runner.get("session_context_id"):
            errors.append("execution receipt reviewer is not independent of the runner")
        actor_receipt = _actor_receipt(state_dir, reviewer.get("actor_receipt"))
        reviewer_actor_receipt = actor_receipt
        actor_errors = _validate_actor_receipt(
            manifest,
            actor_receipt,
            state_dir,
            expected_role="loyal-opposition",
            expected_git_head=str(report.get("git_head") or ""),
        )
        errors.extend(f"execution receipt reviewer {error}" for error in actor_errors)
        if actor_receipt is not None:
            actor = actor_receipt.get("actor", {})
            for field in ("session_context_id", "harness_id", "harness_name", "role"):
                if reviewer.get(field) != actor.get(field):
                    errors.append(f"execution receipt reviewer {field} conflicts with its actor receipt")
    issued_at = _parse_utc_timestamp(attestation.get("issued_at"))
    completed_at = _parse_utc_timestamp(report.get("completed_at"))
    if issued_at is None or completed_at is None or issued_at < completed_at or issued_at > now + timedelta(minutes=5):
        errors.append("execution receipt timestamp is invalid")
    else:
        actor_issued_at = _parse_utc_timestamp(
            reviewer_actor_receipt.get("issued_at") if reviewer_actor_receipt is not None else None
        )
        if actor_issued_at is None or actor_issued_at > issued_at:
            errors.append("execution receipt actor authority was not issued before attestation")
    recorded_digest = attestation.get("attestation_sha256")
    if recorded_digest != _attestation_digest(attestation) or _SHA256_RE.fullmatch(str(recorded_digest)) is None:
        errors.append("execution receipt digest is invalid")
    return errors


def _qualifying_runs(
    manifest: dict[str, Any],
    state_dir: Path,
    *,
    now: datetime | None = None,
) -> dict[str, list[dict[str, Any]]]:
    evaluated_at = now or datetime.now(UTC)
    candidates = [
        report
        for report in _run_reports(state_dir)
        if not _validate_run_report(manifest, report, state_dir, now=evaluated_at)
        and not _validate_run_attestation(
            manifest,
            report,
            _run_attestation(state_dir, str(report.get("run_id", ""))),
            state_dir,
            now=evaluated_at,
        )
    ]
    candidates.sort(key=lambda report: (str(report["started_at"]), str(report["run_id"])))
    by_head: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_run_ids: set[str] = set()
    seen_report_digests: set[str] = set()
    last_completion_by_head: dict[str, datetime] = {}
    for report in candidates:
        run_id = report["run_id"]
        report_digest = report["report_sha256"]
        head = report["git_head"]
        started = _parse_utc_timestamp(report["started_at"])
        completed = _parse_utc_timestamp(report["completed_at"])
        if run_id in seen_run_ids or report_digest in seen_report_digests or started is None or completed is None:
            continue
        if head in last_completion_by_head and started < last_completion_by_head[head]:
            continue
        seen_run_ids.add(run_id)
        seen_report_digests.add(report_digest)
        last_completion_by_head[head] = completed
        by_head[head].append(report)
    return by_head


def _audit_records(state_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted((state_dir / "audits").glob("*.json")):
        if re.fullmatch(r"\d{6}\.json", path.name) is None:
            raise ManifestError(f"independent audit has a noncanonical filename: {path}")
        record = _read_json(path)
        if record.get("sequence") != int(path.stem):
            raise ManifestError(f"independent audit sequence does not match its path: {path}")
        record["_path"] = str(path)
        records.append(record)
    return records


def _latest_audit(state_dir: Path) -> dict[str, Any] | None:
    records = _audit_records(state_dir)
    return records[-1] if records else None


def _validate_audit_findings(findings: object) -> list[str]:
    if not isinstance(findings, list):
        return ["independent modernization audit findings must be an array"]
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"independent modernization audit finding {index} is malformed")
            continue
        finding_id = finding.get("id")
        severity = finding.get("severity")
        status = finding.get("status")
        if not isinstance(finding_id, str) or not finding_id or finding_id != finding_id.strip():
            errors.append(f"independent modernization audit finding {index} has an invalid id")
        elif finding_id in seen_ids:
            errors.append(f"independent modernization audit has duplicate finding id: {finding_id}")
        else:
            seen_ids.add(finding_id)
        if severity not in _AUDIT_FINDING_SEVERITIES:
            errors.append(
                f"independent modernization audit finding {finding_id or index} has invalid severity: {severity}"
            )
        if status not in _AUDIT_FINDING_STATUSES:
            errors.append(f"independent modernization audit finding {finding_id or index} has invalid status: {status}")
            continue
        if status == "closed":
            _require_nonempty_string(
                finding.get("resolution"),
                f"independent modernization audit finding {finding_id or index} resolution",
                errors,
            )
            _require_nonempty_string(
                finding.get("verification"),
                f"independent modernization audit finding {finding_id or index} verification",
                errors,
            )
        elif status in {"accepted", "deferred", "backlogged"}:
            _require_nonempty_string(
                finding.get("disposition"),
                f"independent modernization audit finding {finding_id or index} disposition",
                errors,
            )
        if status != "open":
            evidence_refs = finding.get("evidence_refs")
            if not isinstance(evidence_refs, list) or not evidence_refs:
                errors.append(
                    f"independent modernization audit finding {finding_id or index} evidence_refs must be non-empty"
                )
            else:
                for evidence_index, evidence_ref in enumerate(evidence_refs):
                    if _safe_relative_path(evidence_ref) is None:
                        errors.append(
                            "independent modernization audit finding "
                            f"{finding_id or index} evidence_refs[{evidence_index}] is not a project-relative path"
                        )
    return errors


def _validate_audit_chain(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    previous: dict[str, Any] | None = None
    for record in records:
        sequence = record.get("sequence")
        digest = record.get("audit_sha256")
        if record.get("schema_version") != _AUDIT_SCHEMA_VERSION:
            errors.append(f"independent modernization audit {sequence} schema version is invalid")
        if digest != _record_digest(record, "audit_sha256") or _SHA256_RE.fullmatch(str(digest)) is None:
            errors.append(f"independent modernization audit {sequence} digest is invalid")
        expected_predecessor = previous.get("audit_sha256") if previous is not None else None
        if record.get("predecessor_audit_sha256") != expected_predecessor:
            errors.append(f"independent modernization audit {sequence} predecessor binding is invalid")

        issued_at = _parse_utc_timestamp(record.get("issued_at"))
        previous_issued_at = _parse_utc_timestamp(previous.get("issued_at")) if previous is not None else None
        if issued_at is None:
            errors.append(f"independent modernization audit {sequence} timestamp is invalid")
        elif previous is not None and (previous_issued_at is None or issued_at <= previous_issued_at):
            errors.append(f"independent modernization audit {sequence} timestamp is not monotonic")

        findings = record.get("findings")
        errors.extend(_validate_audit_findings(findings))
        if previous is not None and isinstance(findings, list):
            previous_findings = {
                item.get("id"): item
                for item in previous.get("findings", [])
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            current_findings = {
                item.get("id"): item for item in findings if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            for finding_id, prior_finding in previous_findings.items():
                current = current_findings.get(finding_id)
                if current is None:
                    errors.append(f"independent modernization audit {sequence} omits predecessor finding: {finding_id}")
                elif current.get("severity") != prior_finding.get("severity"):
                    errors.append(
                        f"independent modernization audit {sequence} changes predecessor finding severity: {finding_id}"
                    )
        previous = record
    return errors


def evaluate_status(
    manifest: dict[str, Any],
    *,
    project_root: Path = PROJECT_ROOT,
    state_dir: Path = DEFAULT_STATE_DIR,
) -> dict[str, Any]:
    structural_errors = validate_manifest(manifest, project_root=project_root, require_test_paths=True)
    blockers = list(structural_errors)
    required_passes = manifest["program"].get("required_clean_passes", 2)
    try:
        current_status = _git_output(project_root, "status", "--porcelain=v1", "--untracked-files=all")
        current_head = _git_output(project_root, "rev-parse", "HEAD")
    except ManifestError as exc:
        blockers.append(str(exc))
        current_status = "unavailable"
        current_head = None
    current_clean = current_status == ""
    if not current_clean:
        blockers.append("release-candidate status requires the current Git worktree to be entirely clean")
    runs_by_head = _qualifying_runs(manifest, state_dir) if not structural_errors else {}
    current_runs = runs_by_head.get(current_head, []) if current_head is not None and current_clean else []
    if len(current_runs) < required_passes:
        blockers.append(
            f"need {required_passes} complete independently attested clean passing runs at current Git HEAD; "
            f"found {len(current_runs)}"
        )
    candidate_head = current_head if len(current_runs) >= required_passes else None
    candidate_runs = current_runs[:required_passes] if candidate_head is not None else []
    candidate_run_ids = [item["run_id"] for item in candidate_runs]
    candidate_run_digests = [item["report_sha256"] for item in candidate_runs]

    digest = scope_digest(manifest)
    audit: dict[str, Any] | None = None
    try:
        audit_records = _audit_records(state_dir)
        blockers.extend(_validate_audit_chain(audit_records))
        audit = audit_records[-1] if audit_records else None
    except ManifestError as exc:
        blockers.append(str(exc))
    if audit is None:
        blockers.append(f"independent modernization audit is missing: {state_dir / 'audits' / '*.json'}")
    else:
        if audit is not None:
            audit_path_value = audit.get("_path")
            audit_path = Path(audit_path_value) if isinstance(audit_path_value, str) else None
            audit_sequence = audit.get("sequence")
            if (
                not isinstance(audit_sequence, int)
                or audit_sequence < 1
                or audit_path is None
                or audit_path.resolve() != (state_dir / "audits" / f"{audit_sequence:06d}.json").resolve()
            ):
                blockers.append("independent modernization audit sequence or path is invalid")
            if (
                audit.get("schema_version") != _AUDIT_SCHEMA_VERSION
                or audit.get("issuer") != _AUDIT_ISSUER_ID
                or audit.get("scope_digest_sha256") != digest
            ):
                blockers.append("independent modernization audit does not bind the frozen scope")
            recorded_audit_digest = audit.get("audit_sha256")
            if (
                recorded_audit_digest != _record_digest(audit, "audit_sha256")
                or _SHA256_RE.fullmatch(str(recorded_audit_digest)) is None
            ):
                blockers.append("independent modernization audit digest is invalid")
            issued_at = _parse_utc_timestamp(audit.get("issued_at"))
            if issued_at is None or issued_at > datetime.now(UTC) + timedelta(minutes=5):
                blockers.append("independent modernization audit timestamp is invalid")
            if candidate_head is None or audit.get("git_head") != candidate_head:
                blockers.append("independent modernization audit does not bind the twice-passing Git HEAD")
            if audit.get("clean_run_report_sha256s") != candidate_run_digests:
                blockers.append("independent modernization audit does not bind the qualifying clean-run evidence")
            attestation_records = [_run_attestation(state_dir, item["run_id"]) for item in candidate_runs]
            expected_attestations = [item["attestation_sha256"] for item in attestation_records if item is not None]
            if audit.get("attestation_receipt_sha256s") != expected_attestations:
                blockers.append("independent modernization audit does not bind execution receipts")
            evidence_times = [_parse_utc_timestamp(item.get("completed_at")) for item in candidate_runs] + [
                _parse_utc_timestamp(item.get("issued_at")) for item in attestation_records if item is not None
            ]
            if issued_at is not None and (
                any(item is None for item in evidence_times)
                or any(item is not None and issued_at < item for item in evidence_times)
            ):
                blockers.append("independent modernization audit predates its clean-run or attestation evidence")
            independence = audit.get("independence")
            if not isinstance(independence, dict) or independence.get("independently_reviewed") is not True:
                blockers.append("independent modernization audit lacks independent-review evidence")
            else:
                reviewer_session = independence.get("reviewer_session_context_id")
                runner_sessions = [item.get("runner", {}).get("session_context_id") for item in candidate_runs]
                attester_sessions = [
                    item.get("reviewer", {}).get("session_context_id")
                    for item in attestation_records
                    if item is not None
                ]
                if independence.get("reviewer_role") != "loyal-opposition":
                    blockers.append("independent modernization audit reviewer is not Loyal Opposition")
                try:
                    uuid.UUID(str(reviewer_session))
                except (ValueError, AttributeError):
                    blockers.append("independent modernization audit reviewer session is missing or synthetic")
                if reviewer_session in runner_sessions + attester_sessions:
                    blockers.append("independent modernization audit session is not distinct from run actors")
                if independence.get("runner_session_context_ids") != runner_sessions:
                    blockers.append("independent modernization audit does not bind clean-run session identities")
                if independence.get("attester_session_context_ids") != attester_sessions:
                    blockers.append("independent modernization audit does not bind attester session identities")
                actor_receipt = _actor_receipt(state_dir, independence.get("reviewer_actor_receipt"))
                actor_errors = _validate_actor_receipt(
                    manifest,
                    actor_receipt,
                    state_dir,
                    expected_role="loyal-opposition",
                    expected_git_head=str(candidate_head or ""),
                )
                blockers.extend(f"independent modernization audit reviewer {error}" for error in actor_errors)
                if actor_receipt is not None:
                    actor = actor_receipt.get("actor", {})
                    if (
                        independence.get("reviewer_session_context_id") != actor.get("session_context_id")
                        or independence.get("reviewer_harness_id") != actor.get("harness_id")
                        or independence.get("reviewer_harness_name") != actor.get("harness_name")
                    ):
                        blockers.append("independent modernization audit reviewer conflicts with actor receipt")
                    actor_issued_at = _parse_utc_timestamp(actor_receipt.get("issued_at"))
                    if issued_at is None or actor_issued_at is None or actor_issued_at > issued_at:
                        blockers.append("independent modernization audit actor authority was issued after the audit")
            findings = audit.get("findings")
            finding_errors = _validate_audit_findings(findings)
            blockers.extend(finding_errors)
            if not finding_errors and isinstance(findings, list):
                for finding in findings:
                    severity = finding.get("severity")
                    status = finding.get("status")
                    finding_id = finding.get("id")
                    if severity in {"P0", "P1", "P2"} and status != "closed":
                        blockers.append(f"blocking finding is not closed: {finding_id} ({severity}, {status})")
                    elif severity not in {"P0", "P1", "P2"} and status not in _RESOLVED_FINDING_STATUSES:
                        blockers.append(f"remaining finding lacks disposition: {finding_id} ({status})")

    engineering_ready = not blockers
    return {
        "schema_version": 1,
        "program_id": manifest["program"].get("id"),
        "scope_digest_sha256": digest,
        "scope_handle_count": sum(len(_expanded_handles(item)) for item in manifest.get("scope_families", [])),
        "capability_count": len(manifest.get("capabilities", [])),
        "acceptance_test_count": len(manifest.get("acceptance_tests", [])),
        "qualifying_git_head": candidate_head,
        "current_git_head": current_head,
        "current_git_clean": current_clean,
        "qualifying_clean_passes": len(current_runs),
        "qualifying_clean_run_ids": candidate_run_ids,
        "qualifying_clean_run_report_sha256s": candidate_run_digests,
        "required_clean_passes": required_passes,
        "engineering_ready": engineering_ready,
        "owner_acceptance_required": engineering_ready,
        "ready": engineering_ready,
        "blockers": blockers,
    }


def run_clean_acceptance(
    manifest: dict[str, Any],
    *,
    project_root: Path = PROJECT_ROOT,
    state_dir: Path = DEFAULT_STATE_DIR,
) -> tuple[Path, dict[str, Any]]:
    errors = validate_manifest(manifest, project_root=project_root, require_test_paths=True)
    if errors:
        raise ManifestError("; ".join(errors))
    dirty_before = _git_output(project_root, "status", "--porcelain=v1", "--untracked-files=all")
    if dirty_before:
        raise ManifestError("clean acceptance run requires an entirely clean Git worktree")
    git_head = _git_output(project_root, "rev-parse", "HEAD")
    actor_receipt = _issue_actor_receipt(
        manifest,
        expected_role="prime-builder",
        git_head=git_head,
        project_root=project_root,
        state_dir=state_dir,
    )
    actor = actor_receipt["actor"]
    actor_path = Path(str(actor_receipt["_path"])).resolve().relative_to(state_dir.resolve()).as_posix()
    started = datetime.now(UTC)
    run_id = f"{started.strftime('%Y%m%dT%H%M%S.%fZ')}-{uuid.uuid4().hex[:12].upper()}"
    evidence_dir = state_dir / "runs" / run_id
    try:
        evidence_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise ManifestError(f"clean acceptance run ID collision: {run_id}") from exc
    results: list[dict[str, Any]] = []
    for index, test in enumerate(manifest["acceptance_tests"]):
        command = _expected_command(test, sys.executable)
        command_status_before = _git_output(project_root, "status", "--porcelain=v1", "--untracked-files=all")
        command_head_before = _git_output(project_root, "rev-parse", "HEAD")
        if command_status_before or command_head_before != git_head:
            raise ManifestError(f"acceptance command {test['id']} did not start at the clean candidate Git HEAD")
        result_started = datetime.now(UTC)
        command_started = time.monotonic()
        try:
            completed = subprocess.run(
                command,
                cwd=project_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf-8",
                errors="replace",
                timeout=test["timeout_seconds"],
            )
            output = completed.stdout or ""
            return_code: int | None = completed.returncode
            status = "pass" if completed.returncode == 0 else "fail"
        except subprocess.TimeoutExpired as exc:
            output_value = exc.stdout or ""
            output = output_value if isinstance(output_value, str) else output_value.decode("utf-8", errors="replace")
            return_code = None
            status = "timeout"
        result_completed = datetime.now(UTC)
        command_status_after = _git_output(project_root, "status", "--porcelain=v1", "--untracked-files=all")
        command_head_after = _git_output(project_root, "rev-parse", "HEAD")
        if command_status_after or command_head_after != git_head:
            raise ManifestError(f"acceptance command {test['id']} did not finish at the clean candidate Git HEAD")
        output_bytes = output.encode("utf-8")
        evidence_relative = Path("runs") / run_id / f"{index:02d}-{test['id']}.log"
        evidence_path = state_dir / evidence_relative
        evidence_path.write_bytes(output_bytes)
        results.append(
            {
                "test_id": test["id"],
                "command": command,
                "status": status,
                "return_code": return_code,
                "elapsed_seconds": round(time.monotonic() - command_started, 3),
                "started_at": result_started.isoformat(),
                "completed_at": result_completed.isoformat(),
                "git_head_before": command_head_before,
                "git_head_after": command_head_after,
                "clean_state_before": command_status_before == "",
                "clean_state_after": command_status_after == "",
                "git_status_before_sha256": hashlib.sha256(command_status_before.encode("utf-8")).hexdigest().upper(),
                "git_status_after_sha256": hashlib.sha256(command_status_after.encode("utf-8")).hexdigest().upper(),
                "evidence": {
                    "path": evidence_relative.as_posix(),
                    "sha256": hashlib.sha256(output_bytes).hexdigest().upper(),
                    "byte_count": len(output_bytes),
                    "output_tail": output[-4000:],
                },
            }
        )

    dirty_after = _git_output(project_root, "status", "--porcelain=v1", "--untracked-files=all")
    git_head_after = _git_output(project_root, "rev-parse", "HEAD")
    completed_at = datetime.now(UTC)
    clean_after = not dirty_after
    report = {
        "schema_version": _RUN_SCHEMA_VERSION,
        "runner": {
            "id": _RUNNER_ID,
            "version": _RUNNER_VERSION,
            "python_executable": sys.executable,
            "session_context_id": actor["session_context_id"],
            "actor_receipt": {
                "path": actor_path,
                "sha256": actor_receipt["actor_receipt_sha256"],
            },
        },
        "run_id": run_id,
        "scope_digest_sha256": scope_digest(manifest),
        "git_head": git_head,
        "git_head_after": git_head_after,
        "started_at": started.isoformat(),
        "completed_at": completed_at.isoformat(),
        "clean_state_before": True,
        "git_status_before_sha256": hashlib.sha256(dirty_before.encode("utf-8")).hexdigest().upper(),
        "clean_state_after": clean_after,
        "git_status_after_sha256": hashlib.sha256(dirty_after.encode("utf-8")).hexdigest().upper(),
        "complete": True,
        "status": (
            "pass"
            if clean_after and git_head_after == git_head and all(item["status"] == "pass" for item in results)
            else "fail"
        ),
        "results": results,
    }
    report["report_sha256"] = _report_digest(report)
    runs_dir = state_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    report_path = runs_dir / f"{report['run_id']}.json"
    if report_path.exists():
        raise ManifestError(f"clean acceptance run ID collision: {report['run_id']}")
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path, report


def attest_clean_run(
    manifest: dict[str, Any],
    *,
    run_id: str,
    state_dir: Path = DEFAULT_STATE_DIR,
    project_root: Path = PROJECT_ROOT,
) -> tuple[Path, dict[str, Any]]:
    reports = {str(item.get("run_id")): item for item in _run_reports(state_dir)}
    report = reports.get(run_id)
    if report is None:
        raise ManifestError(f"clean-run report does not exist: {run_id}")
    errors = _validate_run_report(manifest, report, state_dir, now=datetime.now(UTC))
    if errors:
        raise ManifestError("cannot attest invalid clean run: " + "; ".join(errors))
    _require_active_dispatch_context(
        project_root,
        session_id=_active_session_id(),
        expected_role="loyal-opposition",
    )
    actor_receipt = _issue_actor_receipt(
        manifest,
        expected_role="loyal-opposition",
        git_head=str(report["git_head"]),
        project_root=project_root,
        state_dir=state_dir,
    )
    actor = actor_receipt["actor"]
    reviewer_session = str(actor["session_context_id"])
    runner_session = str(report["runner"]["session_context_id"])
    if reviewer_session == runner_session:
        raise ManifestError("attest-run requires a session distinct from the clean-run session")
    current_status = _git_output(project_root, "status", "--porcelain=v1", "--untracked-files=all")
    current_head = _git_output(project_root, "rev-parse", "HEAD")
    if current_status or current_head != report["git_head"]:
        raise ManifestError("attest-run requires the clean worktree at the report Git HEAD")
    now = datetime.now(UTC)
    actor_path = Path(str(actor_receipt["_path"])).resolve().relative_to(state_dir.resolve()).as_posix()
    attestation = {
        "schema_version": _ATTESTATION_SCHEMA_VERSION,
        "issuer": _ATTESTER_ID,
        "issued_at": now.isoformat(),
        "run_id": run_id,
        "run_report_sha256": report["report_sha256"],
        "scope_digest_sha256": scope_digest(manifest),
        "git_head": report["git_head"],
        "output_log_sha256s": [item["evidence"]["sha256"] for item in report["results"]],
        "reviewer": {
            "session_context_id": reviewer_session,
            "harness_id": actor["harness_id"],
            "harness_name": actor["harness_name"],
            "role": "loyal-opposition",
            "actor_receipt": {
                "path": actor_path,
                "sha256": actor_receipt["actor_receipt_sha256"],
            },
        },
        "runner_session_context_id": runner_session,
    }
    attestation["attestation_sha256"] = _attestation_digest(attestation)
    path = state_dir / "attestations" / f"{run_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(attestation, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except FileExistsError as exc:
        raise ManifestError(f"execution receipt already exists: {path}") from exc
    return path, attestation


def issue_independent_audit(
    manifest: dict[str, Any],
    *,
    findings: list[dict[str, Any]],
    state_dir: Path = DEFAULT_STATE_DIR,
    project_root: Path = PROJECT_ROOT,
) -> tuple[Path, dict[str, Any]]:
    finding_errors = _validate_audit_findings(findings)
    if finding_errors:
        raise ManifestError("; ".join(finding_errors))
    current_status = _git_output(project_root, "status", "--porcelain=v1", "--untracked-files=all")
    current_head = _git_output(project_root, "rev-parse", "HEAD")
    if current_status:
        raise ManifestError("independent audit requires the clean candidate worktree")
    qualifying = _qualifying_runs(manifest, state_dir).get(current_head, [])
    required = int(manifest["program"].get("required_clean_passes", 2))
    if len(qualifying) < required:
        raise ManifestError("independent audit requires the complete twice-clean acceptance evidence")
    runs = qualifying[:required]
    _require_active_dispatch_context(
        project_root,
        session_id=_active_session_id(),
        expected_role="loyal-opposition",
    )
    actor_receipt = _issue_actor_receipt(
        manifest,
        expected_role="loyal-opposition",
        git_head=current_head,
        project_root=project_root,
        state_dir=state_dir,
    )
    actor = actor_receipt["actor"]
    reviewer_session = str(actor["session_context_id"])
    runner_sessions = [str(item["runner"]["session_context_id"]) for item in runs]
    attestations = [_run_attestation(state_dir, str(item["run_id"])) for item in runs]
    if any(item is None for item in attestations):
        raise ManifestError("independent audit requires every clean-run execution receipt")
    attestation_sessions = [str(item["reviewer"]["session_context_id"]) for item in attestations if item]
    if reviewer_session in set(runner_sessions + attestation_sessions):
        raise ManifestError("independent audit requires a session distinct from runners and run attesters")
    prior_audits = _audit_records(state_dir)
    chain_errors = _validate_audit_chain(prior_audits)
    if chain_errors:
        raise ManifestError("; ".join(chain_errors))
    if prior_audits:
        previous_findings = {
            item["id"]: item
            for item in prior_audits[-1].get("findings", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        current_findings = {
            item["id"]: item for item in findings if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        for finding_id, prior_finding in previous_findings.items():
            current = current_findings.get(finding_id)
            if current is None:
                raise ManifestError(f"successor audit omits predecessor finding: {finding_id}")
            if current.get("severity") != prior_finding.get("severity"):
                raise ManifestError(f"successor audit changes predecessor finding severity: {finding_id}")
    sequence = int(prior_audits[-1]["sequence"]) + 1 if prior_audits else 1
    issued_at = datetime.now(UTC)
    if prior_audits:
        previous_issued_at = _parse_utc_timestamp(prior_audits[-1].get("issued_at"))
        if previous_issued_at is None:
            raise ManifestError("predecessor audit timestamp is invalid")
        if issued_at <= previous_issued_at:
            issued_at = previous_issued_at + timedelta(microseconds=1)
    actor_path = Path(str(actor_receipt["_path"])).resolve().relative_to(state_dir.resolve()).as_posix()
    audit = {
        "schema_version": _AUDIT_SCHEMA_VERSION,
        "issuer": _AUDIT_ISSUER_ID,
        "sequence": sequence,
        "issued_at": issued_at.isoformat(),
        "predecessor_audit_sha256": prior_audits[-1]["audit_sha256"] if prior_audits else None,
        "scope_digest_sha256": scope_digest(manifest),
        "git_head": current_head,
        "clean_run_report_sha256s": [item["report_sha256"] for item in runs],
        "attestation_receipt_sha256s": [item["attestation_sha256"] for item in attestations if item],
        "independence": {
            "independently_reviewed": True,
            "reviewer_role": "loyal-opposition",
            "reviewer_session_context_id": reviewer_session,
            "reviewer_harness_id": actor["harness_id"],
            "reviewer_harness_name": actor["harness_name"],
            "reviewer_actor_receipt": {
                "path": actor_path,
                "sha256": actor_receipt["actor_receipt_sha256"],
            },
            "runner_session_context_ids": runner_sessions,
            "attester_session_context_ids": attestation_sessions,
        },
        "findings": findings,
    }
    audit["audit_sha256"] = _record_digest(audit, "audit_sha256")
    path = state_dir / "audits" / f"{sequence:06d}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(audit, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except FileExistsError as exc:
        raise ManifestError(f"independent audit sequence collision: {path}") from exc
    return path, audit


def expected_owner_acceptance_reply(manifest: dict[str, Any], *, git_head: str, audit_sha256: str) -> str:
    return (
        "ACCEPT MODERNIZATION RELEASE CANDIDATE "
        f"{git_head} {scope_digest(manifest)} {audit_sha256}; PRODUCTION DEPLOYMENT NOT AUTHORIZED"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate the frozen contract")
    validate_parser.add_argument("--require-test-paths", action="store_true")
    validate_parser.add_argument("--json", action="store_true", dest="as_json")
    status_parser = subparsers.add_parser("status", help="report release-candidate completion status")
    status_parser.add_argument("--json", action="store_true", dest="as_json")
    subparsers.add_parser("digest", help="print the calculated frozen-scope digest")
    subparsers.add_parser("run-clean", help="run and record all acceptance tests from a clean Git state")
    attest_parser = subparsers.add_parser("attest-run", help="independently attest one clean-run report")
    attest_parser.add_argument("--run-id", required=True)
    audit_parser = subparsers.add_parser("record-audit", help="record an independently issued audit")
    audit_parser.add_argument("--findings-file", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.manifest.resolve() != DEFAULT_MANIFEST.resolve():
            raise ManifestError("--manifest must resolve to the canonical in-root modernization contract")
        if args.state_dir.resolve() != DEFAULT_STATE_DIR.resolve():
            raise ManifestError("--state-dir must resolve to the canonical in-root release-candidate state directory")
        manifest = load_manifest(args.manifest)
        if args.command == "digest":
            print(scope_digest(manifest))
            return 0
        if args.command == "validate":
            errors = validate_manifest(
                manifest,
                project_root=PROJECT_ROOT,
                require_test_paths=args.require_test_paths,
            )
            if errors:
                raise ManifestError("; ".join(errors))
            capability_count = len(manifest["capabilities"])
            handle_count = manifest["program"]["expected_handle_count"]
            if args.as_json:
                # Deterministic validation evidence only: the frozen scope digest
                # plus the inventory counts just validated. No runtime receipt,
                # timestamp, or release evidence is emitted here.
                print(
                    json.dumps(
                        {
                            "capability_count": capability_count,
                            "handle_count": handle_count,
                            "require_test_paths": args.require_test_paths,
                            "result": "PASS",
                            "scope_digest": scope_digest(manifest),
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )
            else:
                print(
                    f"PASS modernization acceptance manifest ({capability_count} capabilities, {handle_count} handles)"
                )
            return 0
        if args.command == "status":
            status = evaluate_status(manifest, project_root=PROJECT_ROOT, state_dir=args.state_dir)
            if args.as_json:
                print(json.dumps(status, indent=2, sort_keys=True))
            else:
                verdict = "READY FOR OWNER ACCEPTANCE" if status["ready"] else "NOT READY"
                print(f"MODERNIZATION RELEASE CANDIDATE ENGINEERING EVIDENCE: {verdict}")
                for blocker in status["blockers"]:
                    print(f"- {blocker}")
            return 0 if status["ready"] else 1
        if args.command == "attest-run":
            receipt_path, _receipt = attest_clean_run(
                manifest,
                run_id=args.run_id,
                project_root=PROJECT_ROOT,
                state_dir=args.state_dir,
            )
            print(f"ATTESTED acceptance run: {receipt_path}")
            return 0
        if args.command == "record-audit":
            findings_path = args.findings_file.resolve()
            try:
                findings_path.relative_to(PROJECT_ROOT.resolve())
            except ValueError as exc:
                raise ManifestError("audit findings file must be inside the project root") from exc
            findings_payload = _read_json(findings_path)
            audit_path, _audit = issue_independent_audit(
                manifest,
                findings=findings_payload.get("findings"),
                project_root=PROJECT_ROOT,
                state_dir=args.state_dir,
            )
            print(f"RECORDED independent audit: {audit_path}")
            return 0
        report_path, report = run_clean_acceptance(
            manifest,
            project_root=PROJECT_ROOT,
            state_dir=args.state_dir,
        )
        print(f"{report['status'].upper()} acceptance run: {report_path}")
        return 0 if report["status"] == "pass" else 1
    except ManifestError as exc:
        print(f"MODERNIZATION RELEASE CANDIDATE: FAIL - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
