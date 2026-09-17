"""Read-only native harness metadata and explicitly selected context diagnostics.

Registry declarations are not measurements of an installed harness. This local
report makes no provider request and cannot qualify host behavior or parity.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from groundtruth_kb.authority_client import AuthorityClient, AuthorityClientError
from groundtruth_kb.config import GTConfig, GTConfigError

SCHEMA_ID = "gtkb.harness_diagnostic.v1"
SCHEMA_VERSION = 1
MAX_RECENT_RECORDS = 50


def _field(source: str | None = None, *, reason: str | None = None) -> dict[str, Any]:
    return {
        "status": "observed" if source else "unavailable",
        "coverage": "canonical_record" if source else "unavailable",
        "freshness": "current_read" if source else None,
        "source": source,
        "unavailable_reason": reason,
    }


def _error(harness_id: str, code: str) -> dict[str, Any]:
    # Never copy arbitrary service bodies, details or exception text into reports.
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "status": "error",
        "errors": [code],
        "harness": {"harness_id": harness_id},
    }


def collect_harness_diagnostic(
    client: AuthorityClient, harness_id: str, *, native_context_id: str | None = None
) -> dict[str, Any]:
    """Read the selected installation and optional exact immutable binding."""
    if not harness_id or harness_id != harness_id.strip():
        raise ValueError("harness_id must be non-empty and exact")
    if native_context_id is not None and (not native_context_id or native_context_id != native_context_id.strip()):
        raise ValueError("native_context_id must be non-empty and exact")
    path = f"/v1/harnesses/{quote(harness_id, safe='')}"
    try:
        record = client.request("GET", path)
    except AuthorityClientError as error:
        code = "harness_not_registered" if error.code == "not_found" else "harness_authority_unavailable"
        return _error(harness_id, code)
    if not isinstance(record, dict) or record.get("id") != harness_id:
        return _error(harness_id, "invalid_harness_response")

    binding = None
    binding_reason: str | None = "native_context_not_selected"
    if native_context_id is not None:
        try:
            binding = client.request("GET", "/v1/sessions/binding", query={"native_context_id": native_context_id})
        except AuthorityClientError as error:
            binding_reason = (
                "no_session_binding" if error.code == "no_session_binding" else "session_authority_unavailable"
            )
        else:
            if (
                not isinstance(binding, dict)
                or binding.get("native_context_id") != native_context_id
                or binding.get("role") not in {"prime-builder", "loyal-opposition"}
                or not isinstance(binding.get("session_context_id"), str)
                or not binding["session_context_id"]
                or binding.get("subject") != "gtkb"
            ):
                binding = None
                binding_reason = "invalid_session_response"
            else:
                binding_reason = None

    # Exclude invocation argv, environment, arbitrary nested values and
    # configuration file contents, even from the metadata fingerprint.
    metadata = {key: record.get(key) for key in ("id", "harness_name", "harness_type", "status", "capabilities_ref")}
    fingerprint = hashlib.sha256(
        json.dumps(metadata, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    role_field = _field("native_session_binding" if binding else None, reason=binding_reason)
    lifecycle = record.get("status")
    return {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "partial",
        "errors": [] if lifecycle == "active" else ["harness_not_active"],
        "harness": {
            "harness_id": harness_id,
            "harness_name": metadata["harness_name"],
            "harness_type": metadata["harness_type"],
            "record_version": record.get("version"),
            "lifecycle_status": lifecycle,
            "capabilities": {"declared_reference": metadata["capabilities_ref"], "observed": None},
            "provider_identity": None,
            "model_identity": None,
            "configuration_fingerprint": fingerprint,
            "configuration_fingerprint_scope": "canonical_installation_metadata_only",
        },
        "role": {
            **role_field,
            "role": binding["role"] if binding else None,
            "native_context_id": native_context_id,
            "session_context_id": binding["session_context_id"] if binding else None,
            "scope": "explicitly_selected_context; no_harness_association_asserted",
        },
        "correlation": {
            "session_id": binding["session_context_id"] if binding else None,
            "dispatch_id": None,
            "run_id": None,
            "bridge_document_id": None,
            "claim_id": None,
        },
        "checks": {
            "session_binding": role_field,
            "role_provenance": role_field,
            **{
                key: _field(reason="actual_host_behavior_not_measured")
                for key in ("guard", "hooks", "tool_surface", "adapter_readiness")
            },
        },
        "provider_health": {"mode": "local", **_field(reason="provider_request_not_performed")},
        "recent_runs": [],
        "recent_runs_bounds": {"record_limit": MAX_RECENT_RECORDS, "records_returned": 0},
        "measurements": {
            key: None
            for key in (
                "elapsed_ms",
                "turns_used",
                "tool_calls",
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "cache_read_tokens",
                "cache_write_tokens",
                "cost",
                "failure_class",
            )
        },
        "parity": {
            "status": "unqualified",
            "contract": SCHEMA_ID,
            "coverage_inventory": "canonical_harness_records",
            "unavailable_reason": "local_metadata_does_not_establish_behavioral_parity",
        },
        "field_status": {
            "identity": _field("canonical_harness_record"),
            "configuration_fingerprint": _field("canonical_harness_record"),
            "capabilities": _field(reason="capability_reference_is_a_declaration"),
            "provider_identity": _field(reason="runtime_identity_not_measured"),
            "model_identity": _field(reason="runtime_identity_not_measured"),
            "role": role_field,
            "correlation": _field(reason="only_explicit_session_binding_is_available"),
            "telemetry": _field(reason="current_run_evidence_source_unavailable"),
            "provider_health": _field(reason="provider_request_not_performed"),
        },
    }


def diagnose_harness(project_root: Path, harness_id: str, *, native_context_id: str | None = None) -> dict[str, Any]:
    """Use the selected root's native authority; never discover a different root."""
    try:
        config = GTConfig.load(config_path=project_root.resolve() / "groundtruth.toml", discover=False)
    except FileNotFoundError:
        return _error(harness_id, "native_authority_not_configured")
    except (OSError, GTConfigError, ValueError):
        return _error(harness_id, "native_authority_configuration_invalid")
    if not config.authority_url:
        return _error(harness_id, "native_authority_not_configured")
    return collect_harness_diagnostic(
        AuthorityClient(config.authority_url), harness_id, native_context_id=native_context_id
    )


__all__ = ["MAX_RECENT_RECORDS", "SCHEMA_ID", "SCHEMA_VERSION", "collect_harness_diagnostic", "diagnose_harness"]
