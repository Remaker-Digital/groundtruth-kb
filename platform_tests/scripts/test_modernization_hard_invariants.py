"""Objective fail-closed acceptance tests for modernization hard invariants."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = REPO_ROOT / "groundtruth-kb" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.context.freshness import evaluate_extract  # noqa: E402
from groundtruth_kb.context.manifest import (  # noqa: E402
    ContextManifestError,
    assemble_context_manifest,
)
from groundtruth_kb.governance.project_authorization_operation_time import (  # noqa: E402
    evaluate_envelope,
    load_operation_taxonomy,
)
from groundtruth_kb.session.envelope import (  # noqa: E402
    EnvelopeError,
    ensure_worker_session,
    resolve_worker_role_provenance,
)

NOW = datetime(2026, 7, 13, tzinfo=UTC)


def _freshness_record() -> dict[str, object]:
    return {
        "source_id": "GOV-HARD-INVARIANT-FIXTURE",
        "source_path": "groundtruth.db:current_specifications",
        "authority_class": "stated",
        "source_version_or_hash": "v1",
        "churn_class": "low",
        "generated_at": NOW.isoformat(),
        "ttl_seconds": 120,
        "bounded_usage_context": "hard-invariant-acceptance",
        "live_query_route": "gt spec show GOV-HARD-INVARIANT-FIXTURE",
        "recovery_route": "gt spec show GOV-HARD-INVARIANT-FIXTURE",
        "embedded_content": {"status": "specified"},
    }


def _authorization(*, allowed: list[str] | None = None) -> dict[str, object]:
    return {
        "id": "PAUTH-HARD-INVARIANT-FIXTURE",
        "version": 1,
        "project_id": "PROJECT-HARD-INVARIANT-FIXTURE",
        "status": "active",
        "owner_decision_deliberation_id": "DELIB-HARD-INVARIANT-FIXTURE",
        "expires_at": "2026-08-01T00:00:00Z",
        "supersedes": None,
        "superseded_by": None,
        "allowed_mutation_classes": allowed or ["source", "test"],
        "forbidden_operations": [],
        "included_work_item_ids": ["WI-HARD-INVARIANT-FIXTURE"],
        "excluded_work_item_ids": [],
        "included_spec_ids": ["SPEC-HARD-INVARIANT-FIXTURE"],
        "excluded_spec_ids": [],
    }


def _write_harness_state(project_root: Path) -> None:
    state = project_root / "harness-state"
    state.mkdir(parents=True)
    identities = {
        "schema_version": 1,
        "harnesses": {
            "codex": {"id": "A"},
            "claude": {"id": "B"},
        },
    }
    registry = {
        "schema_version": 1,
        "harnesses": [
            {"id": "A", "harness_name": "codex", "role": ["prime-builder"]},
            {"id": "B", "harness_name": "claude", "role": ["loyal-opposition"]},
        ],
    }
    (state / "harness-identities.json").write_text(json.dumps(identities), encoding="utf-8")
    (state / "harness-registry.json").write_text(json.dumps(registry), encoding="utf-8")


def test_hard_invariant_rejects_stale_or_retired_authority() -> None:
    current = evaluate_extract(_freshness_record(), now=NOW)
    assert current["eligible_as_current"] is True

    expired = {
        **_freshness_record(),
        "generated_at": (NOW - timedelta(seconds=121)).isoformat(),
    }
    expired_result = evaluate_extract(expired, now=NOW)
    retired_result = evaluate_extract({**_freshness_record(), "source_path": "bridge/INDEX.md"}, now=NOW)

    assert expired_result["eligible_as_current"] is False
    assert expired_result["status"] == "recovery_required"
    assert "expired" in expired_result["reasons"]
    assert retired_result["eligible_as_current"] is False
    assert "retired-authority" in retired_result["reasons"]


def test_hard_invariant_rejects_an_unauthorized_protected_operation() -> None:
    taxonomy = load_operation_taxonomy(REPO_ROOT)
    allowed = evaluate_envelope(
        _authorization(),
        requested_operation="protected_mutation",
        target_paths=["scripts/authorized.py", "platform_tests/scripts/test_authorized.py"],
        decision_time=NOW,
        taxonomy=taxonomy,
    )
    denied = evaluate_envelope(
        _authorization(allowed=["bridge", "metadata"]),
        requested_operation="protected_mutation",
        target_paths=["scripts/unauthorized.py"],
        decision_time=NOW,
        taxonomy=taxonomy,
    )

    assert allowed.allowed is True
    assert denied.allowed is False
    assert denied.reason_code == "target_mutation_class_not_allowed"
    assert denied.classified_targets[0].mutation_class == "source"


def test_hard_invariant_rejects_ambiguous_worker_role_authority(tmp_path: Path) -> None:
    _write_harness_state(tmp_path)
    session_id = "shared-session-id"
    ensure_worker_session(
        tmp_path,
        harness_name="codex",
        session_id=session_id,
        role="prime-builder",
        role_source="dispatcher_composition",
        dispatch_run_id="run-codex",
    )
    ensure_worker_session(
        tmp_path,
        harness_name="claude",
        session_id=session_id,
        role="loyal-opposition",
        role_source="dispatcher_composition",
        dispatch_run_id="run-claude",
    )

    codex = resolve_worker_role_provenance(tmp_path, current_session_id=session_id, harness_name="codex")
    assert codex["role"] == "prime-builder"
    with pytest.raises(EnvelopeError, match="ambiguous across session envelopes"):
        resolve_worker_role_provenance(tmp_path, current_session_id=session_id)


def test_hard_invariant_rejects_incomplete_or_expired_context(tmp_path: Path) -> None:
    complete = assemble_context_manifest(
        activity="build",
        role="Prime Builder",
        generated_at=NOW,
        evaluated_at=NOW,
    )
    assert complete["active_activity"] == "build"
    assert complete["role_bootstrap"]["cannot_alter_role"] is True

    registry_text = (REPO_ROOT / "config" / "registry" / "context-manifests.toml").read_text(encoding="utf-8")
    missing_source_registry = tmp_path / "missing-source.toml"
    missing_source_registry.write_text(
        registry_text.replace(
            'source_path = "config/governance/canonical-terms-sync.toml"',
            'source_path = "config/governance/does-not-exist.toml"',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ContextManifestError, match="source is missing; recovery="):
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=NOW,
            registry_path=missing_source_registry,
        )
    with pytest.raises(ContextManifestError, match="expired.*recovery="):
        assemble_context_manifest(
            activity="build",
            role="Prime Builder",
            generated_at=NOW,
            evaluated_at=NOW + timedelta(seconds=121),
        )
