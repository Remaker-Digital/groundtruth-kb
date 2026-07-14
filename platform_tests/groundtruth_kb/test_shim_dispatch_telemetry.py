from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb import shim_dispatch_telemetry as telemetry  # noqa: E402
from groundtruth_kb.cli import main  # noqa: E402
from groundtruth_kb.session.envelope import ensure_worker_session  # noqa: E402


def _worker_document(root: Path, *, session_id: str, role: str = "loyal-opposition") -> None:
    ensure_worker_session(
        root,
        harness_name="openrouter",
        harness_id="F",
        session_id=session_id,
        role=role,
        role_source="dispatch_session_document",
        dispatch_run_id=session_id,
    )


def _bridge(root: Path, bridge_id: str = "telemetry-thread") -> None:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True)
    (bridge_dir / f"{bridge_id}-001.md").write_text(
        "NEW\nWork Item: WI-5173\nSPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001\npython -m pytest sample\n",
        encoding="utf-8",
    )
    (bridge_dir / f"{bridge_id}-002.md").write_text(
        'GO\ntarget_paths: ["one.py", "two.py"]\nSPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001\nruff check one.py\n',
        encoding="utf-8",
    )
    (bridge_dir / f"{bridge_id}-child-999.md").write_text(
        "VERIFIED\nWork Item: WI-9999\nSPEC-UNRELATED-999\n",
        encoding="utf-8",
    )


def _observer(root: Path, dispatch_id: str) -> telemetry.DispatchTelemetryObserver:
    _worker_document(root, session_id=dispatch_id)
    return telemetry.create_dispatch_telemetry_observer(
        root,
        harness_id="F",
        harness_name="openrouter",
        provider="openrouter",
        model_id="provider/model-v1",
        model_version="v1",
        turn_budget=8,
        environ={
            telemetry.DISPATCH_ID_ENV_VAR: dispatch_id,
            telemetry.SESSION_ID_ENV_VAR: dispatch_id,
            telemetry.PRIMARY_BRIDGE_ID_ENV_VAR: "telemetry-thread",
            # Deliberately conflicting dispatch metadata must never become role authority.
            "GTKB_DISPATCH_ROLE": "prime-builder",
        },
    )


def test_envelope_is_atomic_document_authoritative_and_privacy_bounded(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _bridge(root)
    dispatch_id = "dispatch-telemetry-one"
    observer = _observer(root, dispatch_id)

    observer.record_turn(
        1,
        ["Read", "Bash"],
        provider_response={
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 4,
                "total_tokens": 4,
                "prompt_tokens_details": {"cached_tokens": 0},
                "cache_write_tokens": 0,
            },
            "cost": {"amount": 0, "currency": "USD"},
            "messages": "owner prompt must not persist",
            "api_key": "credential-must-not-persist",
        },
    )
    observer.record_turn(
        2,
        [],
        provider_response={
            "usage": {
                "prompt_tokens": 1,
                "completion_tokens": 2,
                "total_tokens": 3,
                "prompt_tokens_details": {"cached_tokens": 0},
                "cache_write_tokens": 0,
            },
            "cost": {"amount": 0, "currency": "USD"},
            "tool_arguments": {"secret": "must-not-persist"},
        },
    )
    result = observer.finish(stop_reason="final_response")

    assert result.written is True
    path = telemetry.telemetry_path(root, dispatch_id)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_id"] == telemetry.SCHEMA_ID
    assert payload["worker"]["role"] == "loyal-opposition"
    assert payload["worker"]["role_source_document_id"].endswith(f"{dispatch_id}.json")
    assert payload["budget"] == {"turn_budget": 8, "turns_used": 2}
    assert payload["turns"] == [{"index": 1, "tool_names": ["Read", "Bash"]}, {"index": 2, "tool_names": []}]
    assert payload["tool_calls"] == {"total": 2, "by_name": {"Bash": 1, "Read": 1}}
    assert payload["usage"] == {
        "coverage": "complete",
        "input_tokens": 1,
        "output_tokens": 6,
        "total_tokens": 7,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
    }
    assert payload["cost"] == {"amount": 0, "currency": "USD", "source": "provider_reported"}
    assert payload["thread_complexity"] == {
        "bridge_version_count": 2,
        "target_path_count": 2,
        "linked_spec_count": 1,
        "verification_command_count": 2,
    }
    serialized = path.read_text(encoding="utf-8")
    for prohibited in ("owner prompt", "credential-must-not-persist", "must-not-persist", "api_key", "messages"):
        assert prohibited not in serialized

    # A second writer for the same dispatch atomically replaces the current
    # record; the run directory never accumulates competing current records.
    replacement = _observer(root, dispatch_id)
    replacement.finish(stop_reason="final_response")
    assert list(path.parent.glob(f"{dispatch_id}.telemetry.json")) == [path]


def test_governed_verdict_tool_is_counted_without_serializing_payload(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _bridge(root)
    dispatch_id = "dispatch-governed-verdict-tool"
    observer = _observer(root, dispatch_id)

    observer.record_turn(
        1,
        [
            "Read",
            "Write",
            "Edit",
            "Grep",
            "Glob",
            "Bash",
            "PublishBridgeVerdict",
            "PublishBridgeVerdict",
            "UnknownTool",
        ],
        provider_response={
            "tool_arguments": {
                "path": "/sensitive/review.md",
                "content": "PRIVATE_VERDICT_BODY",
            },
            "messages": "PROMPT_TEXT_SENTINEL",
            "provider_body": "PROVIDER_BODY_SENTINEL",
            "environment_value": "ENV_VALUE_SENTINEL",
        },
    )
    observer.finish(stop_reason="verdict_emitted")

    path = telemetry.telemetry_path(root, dispatch_id)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_id"] == telemetry.SCHEMA_ID
    assert payload["turns"] == [
        {
            "index": 1,
            "tool_names": [
                "Read",
                "Write",
                "Edit",
                "Grep",
                "Glob",
                "Bash",
                "PublishBridgeVerdict",
                "PublishBridgeVerdict",
            ],
        }
    ]
    assert payload["tool_calls"] == {
        "total": 8,
        "by_name": {
            "Bash": 1,
            "Edit": 1,
            "Glob": 1,
            "Grep": 1,
            "PublishBridgeVerdict": 2,
            "Read": 1,
            "Write": 1,
        },
    }
    serialized = path.read_text(encoding="utf-8")
    for prohibited in (
        "UnknownTool",
        "/sensitive/review.md",
        "PRIVATE_VERDICT_BODY",
        "PROMPT_TEXT_SENTINEL",
        "PROVIDER_BODY_SENTINEL",
        "ENV_VALUE_SENTINEL",
    ):
        assert prohibited not in serialized


def test_missing_role_document_is_never_filled_from_dispatch_intent(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    observer = telemetry.create_dispatch_telemetry_observer(
        root,
        harness_id="F",
        harness_name="openrouter",
        provider="openrouter",
        model_id="provider/model-v1",
        model_version="v1",
        turn_budget=3,
        environ={
            telemetry.DISPATCH_ID_ENV_VAR: "dispatch-missing-document",
            telemetry.SESSION_ID_ENV_VAR: "dispatch-missing-document",
            "GTKB_DISPATCH_ROLE": "prime-builder",
        },
    )
    observer.record_turn(1, [], provider_response={})
    observer.finish(stop_reason="final_response")

    payload = json.loads(telemetry.telemetry_path(root, "dispatch-missing-document").read_text(encoding="utf-8"))
    assert payload["worker"]["role"] is None
    assert payload["worker"]["role_source_document_id"] is None
    assert payload["outcome"]["stop_reason"] == "role_document_invalid"
    assert payload["usage"] == {
        "coverage": "unavailable",
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
        "cache_read_tokens": None,
        "cache_write_tokens": None,
    }
    assert payload["cost"] == {"amount": None, "currency": None, "source": None}


@pytest.mark.parametrize(
    "stop_reason",
    sorted(telemetry.STOP_REASONS - {"role_document_invalid"}),
)
def test_every_non_role_document_stop_reason_serializes_as_a_bounded_code(
    tmp_path: Path,
    stop_reason: str,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    dispatch_id = f"dispatch-stop-{stop_reason}"
    observer = _observer(root, dispatch_id)

    observer.finish(stop_reason=stop_reason)

    payload = json.loads(telemetry.telemetry_path(root, dispatch_id).read_text(encoding="utf-8"))
    assert payload["outcome"]["stop_reason"] == stop_reason
    assert "disk full" not in telemetry.telemetry_path(root, dispatch_id).read_text(encoding="utf-8")


def test_reconciliation_creates_partial_and_query_is_bounded_to_successful_reviews(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _bridge(root)
    dispatch_id = "dispatch-successful-review"
    observer = _observer(root, dispatch_id)
    observer.record_turn(1, [], provider_response={"usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}})
    observer.finish(stop_reason="final_response")
    telemetry.reconcile_dispatch_telemetry(
        root,
        dispatch_id,
        launched_at="2026-07-10T10:00:00Z",
        completed_at="2026-07-10T10:00:01Z",
        elapsed_ms=1000,
        exit_code=0,
        exit_status="succeeded",
        stop_reason="verdict_emitted",
        bridge_status="VERIFIED",
        bridge_document_id="telemetry-thread",
    )
    partial = telemetry.reconcile_dispatch_telemetry(
        root,
        "dispatch-external-termination",
        exit_code=4294967295,
        exit_status="external_termination",
        stop_reason="external_termination",
        bridge_document_id="telemetry-thread",
    )
    assert partial.written is True
    partial_payload = json.loads(
        telemetry.telemetry_path(root, "dispatch-external-termination").read_text(encoding="utf-8")
    )
    assert partial_payload["usage"]["coverage"] == "unavailable"
    assert partial_payload["usage"]["input_tokens"] is None
    assert partial_payload["outcome"]["exit_code"] == 4294967295

    payload = telemetry.query_dispatch_telemetry(root, group_by="role", limit=2)
    assert payload["successful_reconciled_review_count"] == 1
    assert payload["distribution"] == [{"value": "loyal-opposition", "count": 1}]
    assert payload["bounds"]["record_limit"] == 2
    complexity_filtered = telemetry.query_dispatch_telemetry(
        root,
        group_by="target_path_count",
        complexity="target_path_count",
        complexity_value=2,
        limit=2,
    )
    assert complexity_filtered["distribution"] == [{"value": "2", "count": 1}]


def test_reconciliation_preserves_worker_failure_reason_when_dispatcher_falls_back_to_process_error(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _bridge(root)
    dispatch_id = "dispatch-provider-loop"
    observer = _observer(root, dispatch_id)
    observer.finish(stop_reason="no_progress_loop")

    result = telemetry.reconcile_dispatch_telemetry(
        root,
        dispatch_id,
        launched_at="2026-07-14T10:00:00Z",
        completed_at="2026-07-14T10:00:05Z",
        elapsed_ms=5000,
        exit_code=1,
        exit_status="failed",
        stop_reason="process_error",
        bridge_document_id="telemetry-thread",
    )

    assert result.written is True
    payload = json.loads(telemetry.telemetry_path(root, dispatch_id).read_text(encoding="utf-8"))
    assert payload["outcome"]["stop_reason"] == "no_progress_loop"
    assert payload["outcome"]["exit_code"] == 1
    assert payload["outcome"]["exit_status"] == "failed"
    assert payload["timing"]["elapsed_ms"] == 5000


def test_telemetry_write_failure_is_bounded_and_nonfatal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _worker_document(root, session_id="dispatch-write-failure")
    observer = _observer(root, "dispatch-write-failure")

    def fail_write(_path: Path, _payload: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(telemetry, "_atomic_write_json", fail_write)
    result = observer.finish(stop_reason="final_response")

    assert result == telemetry.TelemetryWriteResult(
        written=False,
        path=telemetry.telemetry_path(root, "dispatch-write-failure"),
        diagnostic="telemetry_write_failed",
    )
    assert observer.diagnostic == "telemetry_write_failed"


def test_harness_telemetry_cli_exposes_read_only_distribution(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _bridge(root)
    dispatch_id = "dispatch-cli-review"
    observer = _observer(root, dispatch_id)
    observer.record_turn(1, [], provider_response={})
    observer.finish(stop_reason="final_response")
    telemetry.reconcile_dispatch_telemetry(
        root,
        dispatch_id,
        exit_code=0,
        exit_status="succeeded",
        stop_reason="verdict_emitted",
        bridge_status="GO",
        bridge_document_id="telemetry-thread",
    )
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")

    result = CliRunner().invoke(
        main, ["--config", str(config), "harness", "telemetry", "--group-by", "harness", "--json"]
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema_id"] == telemetry.QUERY_SCHEMA_ID
    assert payload["distribution"] == [{"count": 1, "value": "openrouter"}]


def test_read_dispatch_telemetry_records_is_filtered_newest_first_and_bounded(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()

    for index in range(55):
        dispatch_id = f"dispatch-{index:02d}"
        observer = _observer(root, dispatch_id)
        observer.finish(stop_reason="final_response")
        path = telemetry.telemetry_path(root, dispatch_id)
        path.touch()

    other = telemetry.create_dispatch_telemetry_observer(
        root,
        harness_id="A",
        harness_name="codex",
        provider="openai",
        model_id="gpt-test",
        model_version="test",
        turn_budget=1,
        environ={telemetry.DISPATCH_ID_ENV_VAR: "dispatch-other"},
    )
    other.finish(stop_reason="role_document_invalid")

    records = telemetry.read_dispatch_telemetry_records(
        root,
        harness_id="F",
        harness_name="openrouter",
        limit=100,
    )

    assert len(records) == 50
    assert all(record["worker"]["harness_id"] == "F" for record in records)
    assert records[0]["correlation"]["dispatch_id"] == "dispatch-54"
