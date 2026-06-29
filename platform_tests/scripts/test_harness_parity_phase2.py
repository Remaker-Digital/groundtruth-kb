from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "harness_parity_phase2.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("harness_parity_phase2", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["harness_parity_phase2"] = module
    spec.loader.exec_module(module)
    return module


def _write_fixture(root: Path, *, with_waiver: bool = False) -> None:
    (root / "harness-state").mkdir(parents=True)
    (root / "config" / "dispatcher").mkdir(parents=True)
    (root / "config" / "agent-control").mkdir(parents=True)
    (root / "config" / "harness-parity").mkdir(parents=True)
    (root / ".codex" / "skills").mkdir(parents=True)
    (root / ".codex" / "gtkb-hooks").mkdir(parents=True)
    (root / ".codex" / "skills" / "bridge" / "helpers").mkdir(parents=True)
    (root / "scripts").mkdir(parents=True)

    (root / "harness-state" / "harness-registry.json").write_text(
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
                        "can_fire_events": True,
                        "invocation_surfaces": {"headless": {"argv": ["codex", "exec", "{{PROMPT}}"]}},
                    },
                    {
                        "id": "F",
                        "harness_name": "openrouter",
                        "harness_type": "openrouter",
                        "status": "active",
                        "role": ["loyal-opposition"],
                        "can_receive_dispatch": False,
                        "can_fire_events": False,
                        "invocation_surfaces": {},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "config" / "dispatcher" / "rules.toml").write_text(
        """
schema_version = 1

[[rules]]
id = "bridge-prime-builder-default"
required_roles = ["prime-builder"]
statuses = ["GO", "NO-GO"]

[[rules]]
id = "bridge-loyal-opposition-default"
required_roles = ["loyal-opposition"]
statuses = ["NEW", "REVISED"]
""".lstrip(),
        encoding="utf-8",
    )
    (root / "config" / "agent-control" / "harness-capability-registry.toml").write_text(
        """
schema_version = 1
registry_id = "test"
purpose = "test"

[harnesses.openrouter]
routing_schema_version = 1
skill_adapter_generation_supported = true
skill_adapter_manifest = ".api-harness/skills/MANIFEST.json"
""".lstrip(),
        encoding="utf-8",
    )
    (root / ".codex" / "skills" / "MANIFEST.json").write_text('{"adapters": []}', encoding="utf-8")
    (root / ".codex" / "hooks.json").write_text("{}", encoding="utf-8")
    (root / "scripts" / "check_codex_harness.py").write_text("# fixture\n", encoding="utf-8")

    waiver = ""
    if with_waiver:
        waiver = """
[[waivers]]
id = "WAIVER-OPENROUTER-DISPATCH"
harness = "openrouter"
dimension = "dispatcher_receive"
reason_class = "deliberate_deferral"
rationale = "Fixture defers OpenRouter dispatch receive support."
owner_decision = "DELIB-TEST"
evidence = "fixture"
review_trigger = "fixture review"
evaluator_behavior = "waive"
status = "active"
"""
    (root / "config" / "harness-parity" / "phase2-waivers.toml").write_text(
        (
            """
schema_version = 1
registry_id = "test-waivers"
purpose = "test"
""".lstrip()
            + waiver
        ),
        encoding="utf-8",
    )


def test_report_includes_candidate_work_items_for_unwaived_gaps(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(tmp_path)

    report = module.evaluate(tmp_path)

    assert report["overall_status"] == "FAIL"
    assert any(item["harness"] == "openrouter" for item in report["candidate_work_items"])
    assert all("gt backlog add" in item["suggested_command"] for item in report["candidate_work_items"])


def test_active_typed_waiver_marks_matching_gap_waived(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(tmp_path, with_waiver=True)

    report = module.evaluate(tmp_path)

    waived = [
        cell
        for cell in report["cells"]
        if cell["harness"] == "openrouter" and cell["dimension"] == "dispatcher_receive"
    ]
    assert waived[0]["status"] == "waived"
    assert waived[0]["waiver_id"] == "WAIVER-OPENROUTER-DISPATCH"


def test_cli_writes_json_and_markdown_outputs(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(tmp_path)
    json_output = tmp_path / ".gtkb-state" / "harness-parity" / "phase2-latest.json"
    markdown_output = tmp_path / ".gtkb-state" / "harness-parity" / "phase2-latest.md"

    assert module.main(["--project-root", str(tmp_path), "--format", "json", "--output", str(json_output)]) == 0
    assert module.main(["--project-root", str(tmp_path), "--format", "markdown", "--output", str(markdown_output)]) == 0

    assert json.loads(json_output.read_text(encoding="utf-8"))["metadata"]["work_item_id"] == "WI-4900"
    assert "# Harness Parity Phase 2 Baseline" in markdown_output.read_text(encoding="utf-8")


def test_strict_mode_fails_on_unwaived_release_blocking_gap(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(tmp_path)

    assert module.main(["--project-root", str(tmp_path), "--strict"]) == 1
