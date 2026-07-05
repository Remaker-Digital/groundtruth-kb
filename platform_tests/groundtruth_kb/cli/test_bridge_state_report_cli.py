from __future__ import annotations

import json
import sys
from pathlib import Path

from click.testing import CliRunner

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.cli import main  # noqa: E402


def _project(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "project"
    root.mkdir()
    config = root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "./groundtruth.db"\nproject_root = "."\n', encoding="utf-8")

    dispatcher_dir = root / "config" / "dispatcher"
    dispatcher_dir.mkdir(parents=True)
    (dispatcher_dir / "rules.toml").write_text(
        """
schema_version = 1
selection_order = ["reviewer_precedence", "harness_id"]

[budget]
enabled = false

[budget.harnesses.A]
model = "gpt-5.5"

[budget.harnesses.D]
model = "deepseek-v4-pro-cloud"

[harnesses.A]
max_items = 1

[harnesses.D]
max_items = 2

rules = []
""".lstrip(),
        encoding="utf-8",
    )

    harness_dir = root / "harness-state"
    harness_dir.mkdir()
    (harness_dir / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "test",
                "harnesses": [
                    {
                        "id": "A",
                        "harness_name": "codex",
                        "harness_type": "codex",
                        "status": "active",
                        "role": ["prime-builder"],
                        "can_fire_events": False,
                        "can_receive_dispatch": True,
                        "event_driven_hooks": False,
                        "dispatch_cost": 60,
                        "dispatch_quality": 90,
                        "dispatch_availability": 90,
                        "dispatch_max_items": 1,
                        "reviewer_precedence": 20,
                        "invocation_surfaces": {
                            "headless": {
                                "argv": [
                                    "codex",
                                    "exec",
                                    "--model",
                                    "gpt-5.5",
                                    "-c",
                                    'approval_policy="never"',
                                    "-c",
                                    'model_reasoning_effort="xhigh"',
                                ]
                            }
                        },
                    },
                    {
                        "id": "D",
                        "harness_name": "ollama",
                        "harness_type": "ollama",
                        "status": "active",
                        "role": ["loyal-opposition"],
                        "can_fire_events": False,
                        "can_receive_dispatch": True,
                        "event_driven_hooks": False,
                        "dispatch_cost": 25,
                        "dispatch_quality": 92,
                        "dispatch_availability": 95,
                        "dispatch_max_items": 2,
                        "reviewer_precedence": 10,
                        "invocation_surfaces": {
                            "headless": {
                                "argv": [
                                    "groundtruth-kb/.venv/Scripts/python.exe",
                                    "scripts/ollama_harness.py",
                                    "-p",
                                    "{{PROMPT}}",
                                    "--skill",
                                    "bridge-review",
                                    "--model",
                                    "deepseek-v4-pro-cloud",
                                ]
                            }
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    bridge_dir = root / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "alpha-001.md").write_text("NEW\n\n# Alpha proposal\n", encoding="utf-8")
    (bridge_dir / "alpha-002.md").write_text("GO\n\n# Alpha approved\n", encoding="utf-8")
    (bridge_dir / "alpha-child-003.md").write_text("REVISED\n\n# Prefix sibling\n", encoding="utf-8")
    (bridge_dir / "gamma-001.md").write_text("NEW\n\n# Gamma proposal\n", encoding="utf-8")
    (bridge_dir / "closed-001.md").write_text("VERIFIED\n\n# Closed thread\n", encoding="utf-8")
    (bridge_dir / "alpha-draft.md").write_text("NO-GO\n\n# Non-canonical draft\n", encoding="utf-8")

    state_dir = root / ".gtkb-state" / "bridge-poller"
    state_dir.mkdir(parents=True)
    (state_dir / "dispatch-state.json").write_text(
        json.dumps({"schema_version": 1, "updated_at": "2026-07-04T00:00:00Z", "recipients": {}}),
        encoding="utf-8",
    )

    return root, config


def test_bridge_state_report_json_uses_exact_threads_and_harness_model_config(tmp_path: Path) -> None:
    _root, config = _project(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["bridge"]["total_thread_count"] == 4
    threads = {row["slug"]: row for row in payload["bridge"]["threads"]}
    assert threads["alpha"]["latest_status"] == "GO"
    assert threads["alpha"]["latest_path"] == "bridge/alpha-002.md"
    assert "alpha-draft" not in threads
    assert [row["slug"] for row in payload["bridge"]["lo_actionable"]] == ["alpha-child", "gamma"]
    assert {row["status"]: row["count"] for row in payload["bridge"]["status_mix"]} == {
        "GO": 1,
        "NEW": 1,
        "REVISED": 1,
        "VERIFIED": 1,
    }
    assert payload["dispatcher"]["health"] == "PASS"
    assert payload["dispatcher"]["selected"] == {"loyal-opposition": ["D"], "prime-builder": ["A"]}

    harnesses = {row["id"]: row for row in payload["harnesses"]["rows"]}
    assert harnesses["A"]["model_config"] == "gpt-5.5; reasoning=xhigh; approval_policy=never"
    assert harnesses["D"]["model_config"] == "deepseek-v4-pro-cloud; skill=bridge-review"
    assert harnesses["A"]["events"] == "no"
    assert harnesses["D"]["dispatchable"] == "yes"


def test_bridge_state_report_markdown_is_three_owner_tables(tmp_path: Path) -> None:
    _root, config = _project(tmp_path)

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--markdown"])

    assert result.exit_code == 0, result.output
    assert "| Status | Count |" in result.output
    assert "| Aspect | Value |" in result.output
    assert "| ID | Harness | Model / Config | Role | Active | Dispatchable | Events |" in result.output
    assert "| LO_ACTIONABLE_LATEST_NEW_REVISED | 2: alpha-child" in result.output
    assert sum(1 for line in result.output.splitlines() if line.startswith("| ---")) == 3


def test_bridge_state_report_is_read_only_for_state_inputs(tmp_path: Path) -> None:
    root, config = _project(tmp_path)
    tracked = [
        root / "bridge" / "alpha-001.md",
        root / "bridge" / "alpha-002.md",
        root / "config" / "dispatcher" / "rules.toml",
        root / "harness-state" / "harness-registry.json",
        root / ".gtkb-state" / "bridge-poller" / "dispatch-state.json",
    ]
    before = {path: path.read_bytes() for path in tracked}

    result = CliRunner().invoke(main, ["--config", str(config), "bridge", "state-report", "--json"])

    assert result.exit_code == 0, result.output
    assert {path: path.read_bytes() for path in tracked} == before
