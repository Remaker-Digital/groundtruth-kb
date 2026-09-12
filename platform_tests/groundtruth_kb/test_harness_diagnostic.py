from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.harness_diagnostic import SCHEMA_ID, diagnose_harness  # noqa: E402


def _project(root: Path) -> None:
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
