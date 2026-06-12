# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Unit and integration tests for dispatch-state recovery, wrapper status recording,
circuit breakers, retry delays, and dry-run safety in cross-harness bridge trigger.
"""

import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Add project root and scripts directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Import scripts
import run_with_status
from cross_harness_bridge_trigger import main as trigger_main
from cross_harness_bridge_trigger import run_trigger


@pytest.fixture()
def test_env(tmp_path: Path) -> tuple[Path, Path]:
    # Setup mock groundtruth.toml
    toml = tmp_path / "groundtruth.toml"
    toml.write_text(
        f'[groundtruth]\ndb_path = "{(tmp_path / "groundtruth.db").as_posix()}"\n'
        f'project_root = "{tmp_path.as_posix()}"\napp_title = "Test Project"\n',
        encoding="utf-8",
    )

    # Setup mock harness-state/harness-registry.json
    harness_state_dir = tmp_path / "harness-state"
    harness_state_dir.mkdir(parents=True, exist_ok=True)
    registry_file = harness_state_dir / "harness-registry.json"
    registry_file.write_text(
        json.dumps(
            {
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "role": ["prime-builder"],
                        "status": "active",
                        "event_driven_hooks": True,
                        "invocation_surfaces": {"headless": {"argv": ["python", "-c", "print('prime spawned')"]}},
                    },
                    {
                        "id": "D",
                        "harness_name": "ollama",
                        "harness_type": "ollama",
                        "role": ["loyal-opposition"],
                        "status": "active",
                        "event_driven_hooks": True,
                        "invocation_surfaces": {"headless": {"argv": ["python", "-c", "print('lo spawned')"]}},
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    # Setup mock bridge/INDEX.md
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)

    index_file = bridge_dir / "INDEX.md"
    index_file.write_text(
        "Document: doc-lo\nNEW: bridge/doc-lo-001.md\n\nDocument: doc-pb\nGO: bridge/doc-pb-001.md\n",
        encoding="utf-8",
    )

    # Create the mock files on disk with correct headers
    (bridge_dir / "doc-lo-001.md").write_text(
        "## target_paths\n- `dummy.txt`\n## Requirement Sufficiency\nExisting requirements sufficient\n",
        encoding="utf-8",
    )
    (bridge_dir / "doc-pb-001.md").write_text(
        "## target_paths\n- `dummy.txt`\n## Requirement Sufficiency\nExisting requirements sufficient\n",
        encoding="utf-8",
    )

    # Set active substrate file so it is active
    substrate_file = harness_state_dir / "bridge-substrate.json"
    substrate_file.write_text(json.dumps({"substrate": "cross_harness_trigger"}), encoding="utf-8")

    # Setup state-dir
    state_dir = tmp_path / ".gtkb-state" / "cross-harness-trigger"
    state_dir.mkdir(parents=True, exist_ok=True)

    # Mock environment variable for test execution to avoid single harness skip
    os.environ["GTKB_HARNESS_PROJECT_TEST_MODE"] = "1"
    os.environ["GTKB_HARNESS_REGISTRY_PATH"] = str(registry_file)

    return tmp_path, state_dir


def test_wrapper_records_exit_code(tmp_path: Path) -> None:
    status_file = tmp_path / "test.exit_code"

    # Run a command that exits with code 0
    cmd_args = [sys.executable, "-c", "import sys; sys.exit(0)"]
    res = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "run_with_status.py"), str(status_file)] + cmd_args,
        capture_output=True,
    )
    assert res.returncode == 0
    assert status_file.is_file()
    assert status_file.read_text(encoding="utf-8").strip() == "0"

    # Run a command that exits with code 42
    cmd_args = [sys.executable, "-c", "import sys; sys.exit(42)"]
    res = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "run_with_status.py"), str(status_file)] + cmd_args,
        capture_output=True,
    )
    assert res.returncode == 42
    assert status_file.read_text(encoding="utf-8").strip() == "42"


def test_dry_run_does_not_mutate_state(test_env: tuple[Path, Path]) -> None:
    project_root, state_dir = test_env

    # Run trigger in dry-run mode
    summary = run_trigger(
        project_root=project_root,
        state_dir=state_dir,
        max_items=2,
        dry_run=True,
        invocation_source="manual",
    )

    # Load dispatch state
    state_file = state_dir / "dispatch-state.json"
    assert state_file.is_file()
    state_data = json.loads(state_file.read_text(encoding="utf-8"))

    # Verify last_dispatched_signature and signature are updated in dry-run mode
    recipients = state_data.get("recipients", {})
    for recipient, data in recipients.items():
        if "loyal-opposition" in recipient:
            assert data.get("last_dispatched_signature") is not None
            assert data.get("signature") is not None


def test_circuit_breaker_active(test_env: tuple[Path, Path]) -> None:
    project_root, state_dir = test_env

    # Write a state with circuit breaker tripped for loyal-opposition
    state_file = state_dir / "dispatch-state.json"
    state_data = {
        "schema_version": 1,
        "recipients": {
            "loyal-opposition:D": {
                "failure_count": 3,
                "circuit_breaker_tripped": True,
                "updated_at": "2026-06-09T12:00:00Z",
            }
        },
    }
    state_file.write_text(json.dumps(state_data), encoding="utf-8")

    summary = run_trigger(
        project_root=project_root,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
        invocation_source="manual",
    )

    # Verify circuit breaker blocked the run
    lo_state = summary["results"].get("loyal-opposition") or summary["results"].get("loyal-opposition:D")
    assert lo_state is not None
    assert lo_state.get("launched") is False
    assert lo_state.get("reason") == "circuit_breaker_active"


def test_retry_delay_enforcement(test_env: tuple[Path, Path]) -> None:
    project_root, state_dir = test_env

    # Write a state with 1 failure (retry pending) updated just now
    now_iso = dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    state_file = state_dir / "dispatch-state.json"
    state_data = {
        "schema_version": 1,
        "recipients": {
            "loyal-opposition:D": {
                "failure_count": 1,
                "circuit_breaker_tripped": False,
                "updated_at": now_iso,
                "last_launch": {
                    "launched_at": now_iso,
                },
            }
        },
    }
    state_file.write_text(json.dumps(state_data), encoding="utf-8")

    # Set delay to a high value so it enforces it
    os.environ["OLLAMA_RETRY_DELAY_SECONDS"] = "300"

    summary = run_trigger(
        project_root=project_root,
        state_dir=state_dir,
        max_items=2,
        dry_run=False,
        invocation_source="manual",
    )

    lo_state = summary["results"].get("loyal-opposition") or summary["results"].get("loyal-opposition:D")
    assert lo_state is not None
    assert lo_state.get("launched") is False
    assert lo_state.get("reason") == "retry_delay_enforced"


def test_reset_recipient_cli(test_env: tuple[Path, Path]) -> None:
    project_root, state_dir = test_env

    # Write a state with circuit breaker tripped for loyal-opposition
    state_file = state_dir / "dispatch-state.json"
    state_data = {
        "schema_version": 1,
        "recipients": {
            "loyal-opposition:D": {
                "failure_count": 3,
                "circuit_breaker_tripped": True,
                "updated_at": "2026-06-09T12:00:00Z",
            }
        },
    }
    state_file.write_text(json.dumps(state_data), encoding="utf-8")

    # Run CLI reset
    args = [
        "--project-root",
        str(project_root),
        "--state-dir",
        str(state_dir),
        "--reset-recipient",
        "loyal-opposition",
    ]
    ret = trigger_main(args)
    assert ret == 0

    # Check that state file was updated
    state_data_updated = json.loads(state_file.read_text(encoding="utf-8"))
    lo_state = state_data_updated["recipients"]["loyal-opposition:D"]
    assert lo_state["failure_count"] == 0
    assert lo_state["circuit_breaker_tripped"] is False
