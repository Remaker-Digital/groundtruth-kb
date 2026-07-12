from __future__ import annotations

import importlib.util
import json
import sys
import tomllib
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


def _write_fixture(root: Path, *, with_waiver: bool = False, waiver_text: str | None = None) -> None:
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
                    {
                        "id": "H",
                        "harness_name": "alibaba-cloud-studio",
                        "harness_type": "claude",
                        "status": "active",
                        "role": ["loyal-opposition"],
                        "can_receive_dispatch": False,
                        "can_fire_events": False,
                        "invocation_surfaces": {
                            "headless": {
                                "argv": [
                                    "python.exe",
                                    "scripts/alibaba_cloud_studio_harness.py",
                                    "--prompt",
                                    "{{PROMPT}}",
                                ]
                            }
                        },
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

[harnesses.alibaba-cloud-studio]
routing_schema_version = 1
skill_adapter_generation_supported = true
skill_adapter_manifest = ".api-harness/skills/MANIFEST.json"
""".lstrip(),
        encoding="utf-8",
    )
    (root / ".codex" / "skills" / "MANIFEST.json").write_text('{"adapters": []}', encoding="utf-8")
    (root / ".api-harness" / "skills" / "bridge").mkdir(parents=True)
    (root / ".api-harness" / "skills" / "MANIFEST.json").write_text('{"adapters": []}', encoding="utf-8")
    (root / ".codex" / "hooks.json").write_text("{}", encoding="utf-8")
    (root / "scripts" / "check_codex_harness.py").write_text("# fixture\n", encoding="utf-8")
    (root / "scripts" / "alibaba_cloud_studio_harness.py").write_text("# governed adapter\n", encoding="utf-8")
    (root / "scripts" / "dispatcher_runtime.py").write_text(
        "import subprocess\ncreationflags = subprocess.CREATE_NO_WINDOW\n",
        encoding="utf-8",
    )

    waiver = waiver_text or ""
    if with_waiver and waiver_text is None:
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


def test_alibaba_h_runtime_surfaces_and_receive_capability_are_recognized(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(tmp_path)

    report = module.evaluate(tmp_path)
    cells = {cell["dimension"]: cell for cell in report["cells"] if cell["harness"] == "alibaba-cloud-studio"}

    for dimension in (
        "skill_projection",
        "hook_projection",
        "bridge_write_path",
        "readiness_probe",
        "provider_settings",
        "no_window_launch",
        "dispatcher_receive",
    ):
        assert cells[dimension]["status"] == "supported"
    assert "current_eligibility=False" in cells["dispatcher_receive"]["details"]
    assert "receive_capable=True" in cells["dispatcher_receive"]["details"]


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


def test_malformed_active_waiver_fails_closed_and_does_not_waive_gap(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(
        tmp_path,
        waiver_text="""
[[waivers]]
id = "WAIVER-OPENROUTER-DISPATCH"
harness = "openrouter"
dimension = "dispatcher_receive"
reason_class = "unsupported_reason"
rationale = "Fixture attempts to waive OpenRouter dispatch receive support."
evidence = "fixture"
review_trigger = "fixture review"
evaluator_behavior = "waive"
status = "active"
""",
    )

    report = module.evaluate(tmp_path)

    invalid = [cell for cell in report["cells"] if cell["status"] == "invalid_waiver"]
    target = [
        cell
        for cell in report["cells"]
        if cell["harness"] == "openrouter" and cell["dimension"] == "dispatcher_receive"
    ]
    assert invalid
    assert "invalid reason_class" in invalid[0]["details"]
    assert "missing required field 'owner_decision'" in invalid[0]["details"]
    assert target[0]["status"] == "needs_adapter"
    assert target[0]["waiver_id"] is None
    assert report["summary"]["invalid_waiver_count"] == 1


def test_retired_waiver_does_not_suppress_matching_gap(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(
        tmp_path,
        waiver_text="""
[[waivers]]
id = "WAIVER-OPENROUTER-DISPATCH"
harness = "openrouter"
dimension = "dispatcher_receive"
reason_class = "deliberate_deferral"
rationale = "Fixture retired waiver."
owner_decision = "DELIB-TEST"
evidence = "fixture"
review_trigger = "fixture review"
evaluator_behavior = "waive"
status = "retired"
""",
    )

    report = module.evaluate(tmp_path)

    target = [
        cell
        for cell in report["cells"]
        if cell["harness"] == "openrouter" and cell["dimension"] == "dispatcher_receive"
    ]
    assert target[0]["status"] == "needs_adapter"
    assert target[0]["waiver_id"] is None
    assert any(
        item["harness"] == "openrouter" and item["dimension"] == "dispatcher_receive"
        for item in report["candidate_work_items"]
    )
    assert report["summary"]["retired_waiver_count"] == 1


def test_wildcard_waiver_marks_matching_dimension_gaps_waived(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(
        tmp_path,
        waiver_text="""
[[waivers]]
id = "WAIVER-NO-WINDOW-WILDCARD"
harness = "*"
dimension = "no_window_launch"
reason_class = "owner_accepted_risk"
rationale = "Fixture accepts no-window evidence gaps for this slice."
owner_decision = "DELIB-TEST"
evidence = "fixture"
review_trigger = "fixture review"
evaluator_behavior = "waive"
status = "active"
""",
    )

    report = module.evaluate(tmp_path)

    no_window_cells = [cell for cell in report["cells"] if cell["dimension"] == "no_window_launch"]
    assert no_window_cells
    assert all(cell["status"] in {"supported", "waived"} for cell in no_window_cells)
    waived = [cell for cell in no_window_cells if cell["status"] == "waived"]
    assert waived
    assert all(cell["waiver_id"] == "WAIVER-NO-WINDOW-WILDCARD" for cell in waived)
    assert report["summary"]["active_waiver_count"] == 1


def test_no_window_dimension_accepts_explicit_wrapper_evidence(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(tmp_path)
    (tmp_path / "scripts" / "dispatcher_runtime.py").write_text(
        "import subprocess\ncreationflags = subprocess.CREATE_NO_WINDOW\n",
        encoding="utf-8",
    )

    report = module.evaluate(tmp_path)

    target = [
        cell for cell in report["cells"] if cell["harness"] == "codex" and cell["dimension"] == "no_window_launch"
    ]
    assert target[0]["status"] == "supported"
    assert "scripts/dispatcher_runtime.py" in target[0]["evidence"]


def test_cli_writes_json_and_markdown_outputs(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(tmp_path)
    json_output = tmp_path / ".gtkb-state" / "harness-parity" / "phase2-latest.json"
    markdown_output = tmp_path / ".gtkb-state" / "harness-parity" / "phase2-latest.md"

    assert module.main(["--project-root", str(tmp_path), "--format", "json", "--output", str(json_output)]) == 0
    assert module.main(["--project-root", str(tmp_path), "--format", "markdown", "--output", str(markdown_output)]) == 0

    payload = json.loads(json_output.read_text(encoding="utf-8"))
    assert payload["metadata"]["work_item_id"] == "WI-4899"
    assert payload["metadata"]["evaluator_work_item_id"] == "WI-4900"
    assert payload["metadata"]["waiver_registry_work_item_id"] == "WI-4901"
    markdown = markdown_output.read_text(encoding="utf-8")
    assert "# Harness Parity Phase 2 Codex Baseline Matrix" in markdown
    assert "Waiver registry work item: WI-4901" in markdown


def test_markdown_links_each_unwaived_gap_to_candidate(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(tmp_path)

    report = module.evaluate(tmp_path)
    markdown = module.format_markdown(report)

    for candidate in report["candidate_work_items"]:
        assert f"Candidate: {candidate['title']}" in markdown


def test_strict_mode_fails_on_unwaived_release_blocking_gap(tmp_path: Path) -> None:
    module = _load_module()
    _write_fixture(tmp_path)

    assert module.main(["--project-root", str(tmp_path), "--strict"]) == 1


def test_wi4926_provider_readiness_contract_is_documented_and_registered() -> None:
    docs = (REPO_ROOT / "docs" / "harness-parity-phase-2.md").read_text(encoding="utf-8")
    matrix = (REPO_ROOT / "docs" / "harness-parity-phase-2-matrix.md").read_text(encoding="utf-8")
    registry = tomllib.loads(
        (REPO_ROOT / "config" / "agent-control" / "harness-capability-registry.toml").read_text(encoding="utf-8")
    )

    assert "WI-4926 Provider Readiness Contract" in docs
    assert "OPENROUTER_API_KEY" in docs
    assert "Missing `OPENROUTER_API_KEY` is configuration failure" in docs
    assert "WI-4926 Provider Readiness Contract" in matrix
    assert "WAIVER-P2-OLLAMA-EVENT-SOURCE" in matrix
    assert "do not waive provider" in matrix

    ollama = registry["harnesses"]["ollama"]
    openrouter = registry["harnesses"]["openrouter"]
    assert ollama["provider_readiness_contract"] == "local-inventory-live-dispatch"
    assert ollama["provider_readiness_default_test_mode"] == "mocked-routing-and-inventory"
    assert "configured_model_not_advertised" in ollama["provider_readiness_failure_classes"]
    assert openrouter["provider_readiness_contract"] == "env-local-credential-live-dispatch"
    assert openrouter["provider_readiness_default_test_mode"] == "mocked-credential-and-provider-responses"
    assert "missing_credential" in openrouter["provider_readiness_failure_classes"]
