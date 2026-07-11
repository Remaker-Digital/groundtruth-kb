from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.harness_diagnostic import MAX_RECENT_RECORDS, SCHEMA_ID, diagnose_harness  # noqa: E402
from groundtruth_kb.session.envelope import ensure_worker_session  # noqa: E402


def _project(root: Path, *, with_document: bool = True) -> None:
    state = root / "harness-state"
    state.mkdir(parents=True)
    (state / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"codex": {"id": "A"}}}),
        encoding="utf-8",
    )
    (state / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["prime-builder"],
                        "can_receive_dispatch": True,
                        "can_fire_events": False,
                        "invocation_surfaces": {
                            "headless": {"argv": ["codex", "exec", "--model", "gpt-test", "{{PROMPT}}"]},
                            "interactive": {"argv": ["codex"]},
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    if with_document:
        ensure_worker_session(
            root,
            harness_name="codex",
            harness_id="A",
            session_id="diagnostic-session",
            role="loyal-opposition",
            role_source="test_document",
            dispatch_run_id=None,
        )


def _telemetry(root: Path, index: int, *, partial: bool = False) -> None:
    directory = root / ".gtkb-state" / "bridge-poller" / "dispatch-runs"
    directory.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_id": "gtkb.shim_dispatch_telemetry.v1",
        "correlation": {
            "dispatch_id": f"dispatch-{index}",
            "run_id": f"dispatch-{index}",
            "bridge_document_id": "diagnostic-thread",
            "related_work_item_ids": ["WI-5179"],
            "session_context_id": "diagnostic-session",
        },
        "worker": {
            "harness_id": "A",
            "harness_name": "codex",
            "provider": "openai",
            "model_id": "test-model",
            "model_version": "v1",
            "role": "prime-builder",
        },
        "timing": {"started_at": "2026-07-11T00:00:00Z", "completed_at": None, "elapsed_ms": None},
        "budget": {"turn_budget": 8, "turns_used": None if partial else 2},
        "turns": [{"index": 1, "tool_names": ["Read"]}],
        "tool_calls": {"total": None if partial else 1, "by_name": {"Read": 1}},
        "outcome": {"stop_reason": "external_termination", "exit_status": "partial", "exit_code": None},
        "usage": {
            "coverage": "unavailable" if partial else "complete",
            "input_tokens": None if partial else 0,
            "output_tokens": None if partial else 4,
            "total_tokens": None if partial else 4,
            "cache_read_tokens": None,
            "cache_write_tokens": None,
        },
        "cost": {"amount": None, "currency": None, "source": None},
        "prompt": "must not persist",
        "tool_arguments": {"credential": "must not persist"},
        "provider_body": {"secret": "must not persist"},
    }
    (directory / f"dispatch-{index}.telemetry.json").write_text(json.dumps(payload), encoding="utf-8")


def test_diagnostic_role_comes_from_document_and_is_privacy_bounded(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _project(root)
    _telemetry(root, 1)

    result = diagnose_harness(root, "A")
    serialized = json.dumps(result, sort_keys=True)

    assert result["schema_id"] == SCHEMA_ID
    assert result["role"]["role"] == "loyal-opposition"
    assert result["role"]["source"] == "worker_session_document"
    assert result["harness"]["configuration_fingerprint"]
    assert result["harness"]["provider_identity"] == "codex"
    assert result["harness"]["model_identity"] == "gpt-test"
    assert result["correlation"]["run_id"] == "dispatch-1"
    assert result["parity"] == {
        "status": "implemented",
        "contract": SCHEMA_ID,
        "coverage_inventory": "active_harness_registry",
        "waiver": None,
    }
    assert result["provider_health"]["coverage"] == "not_requested"
    assert result["recent_runs"][0]["usage"]["input_tokens"] == 0
    assert "must not persist" not in serialized
    assert "tool_arguments" not in serialized
    assert "provider_body" not in serialized


def test_diagnostic_missing_document_and_partial_telemetry_remain_available(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _project(root, with_document=False)
    _telemetry(root, 1, partial=True)

    result = diagnose_harness(root, "A")

    assert result["status"] == "ok"
    assert result["role"]["role"] is None
    assert result["role"]["reason"] == "worker_session_document_missing"
    assert result["recent_runs"][0]["budget"]["turns_used"] is None
    assert result["recent_runs"][0]["usage"]["coverage"] == "unavailable"


def test_diagnostic_bounds_recent_events_to_fifty(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _project(root)
    for index in range(MAX_RECENT_RECORDS + 7):
        _telemetry(root, index)

    result = diagnose_harness(root, "A")

    assert len(result["recent_runs"]) == MAX_RECENT_RECORDS
    assert result["recent_runs_bounds"] == {
        "record_limit": MAX_RECENT_RECORDS,
        "records_returned": MAX_RECENT_RECORDS,
    }


def test_unknown_harness_returns_structured_error(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _project(root)

    result = diagnose_harness(root, "Z")

    assert result["status"] == "error"
    assert result["errors"] == ["harness_not_registered"]


def test_live_active_registry_is_the_diagnostic_coverage_inventory() -> None:
    registry = json.loads((REPO_ROOT / "harness-state" / "harness-registry.json").read_text(encoding="utf-8"))
    active_ids = [row["id"] for row in registry["harnesses"] if row["status"] == "active"]

    assert active_ids
    for harness_id in active_ids:
        result = diagnose_harness(REPO_ROOT, harness_id)
        assert result["schema_id"] == SCHEMA_ID
        assert result["parity"] == {
            "status": "implemented",
            "contract": SCHEMA_ID,
            "coverage_inventory": "active_harness_registry",
            "waiver": None,
        }
