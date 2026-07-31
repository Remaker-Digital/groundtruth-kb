"""Spec-derived governance checks for Alibaba Cloud Studio harness H."""

from __future__ import annotations

import json
import sys
import tomllib
from importlib import import_module
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

_check_alibaba_cloud_studio_harness = import_module("groundtruth_kb.project.doctor")._check_alibaba_cloud_studio_harness


CANONICAL_TOOLS = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]


def _write_clean_harness_fixture(root: Path) -> None:
    (root / "harness-state").mkdir(parents=True, exist_ok=True)
    (root / "harness-state" / "harness-identities.json").write_text(
        json.dumps({"schema_version": 1, "harnesses": {"alibaba-cloud-studio": {"id": "H"}}}),
        encoding="utf-8",
    )
    registry = {
        "schema_version": 1,
        "harnesses": [
            {
                "id": "H",
                "harness_name": "alibaba-cloud-studio",
                "harness_type": "claude",
                "status": "active",
                "role": ["loyal-opposition"],
                "can_receive_dispatch": False,
                "invocation_surfaces": {
                    "headless": {
                        "argv": [
                            "groundtruth-kb/.venv/Scripts/python.exe",
                            "scripts/alibaba_cloud_studio_harness.py",
                            "--prompt",
                            "{{PROMPT}}",
                            "--skill",
                            "bridge-review",
                            "--model",
                            "alibaba-deepseek-v4-pro",
                        ]
                    }
                },
            },
            {
                "id": "G",
                "harness_name": "goose",
                "harness_type": "goose-desktop",
                "status": "suspended",
                "role": ["loyal-opposition"],
                "can_receive_dispatch": False,
                "invocation_surfaces": {},
            },
        ],
    }
    (root / "harness-state" / "harness-registry.json").write_text(json.dumps(registry), encoding="utf-8")

    (root / "config" / "agent-control").mkdir(parents=True, exist_ok=True)
    (root / "config" / "agent-control" / "harness-capability-registry.toml").write_text(
        "\n".join(
            [
                "[harnesses.alibaba-cloud-studio]",
                "bridge_compliance_gate_respect = true",
                "root_boundary_respect = true",
                "author_metadata_env_var_setting = true",
                "destructive_gate_delegation = true",
                'advertised_tool_subset = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]',
                "tool_guard_adapter_fail_closed = true",
                'dialect = "anthropic-messages"',
                'hook_tier = "native-full-hooks"',
                'auth_style = "authorization-bearer"',
                'auth_env_key = "ALIBABA_API_KEY"',
                'endpoint_env_key = "ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT"',
                'provider_routing_key = "alibaba-cloud-studio"',
                'activity_envelope_projection_mode = "compact-provider"',
                'compact_result_envelope_mode = "compact-provider"',
                'compact_session_envelope_mode = "compact-provider"',
                "full_transcript_archive_required = false",
                "",
            ]
        ),
        encoding="utf-8",
    )

    (root / ".api-harness").mkdir(parents=True, exist_ok=True)
    (root / ".api-harness" / "routing.toml").write_text(
        "\n".join(
            [
                "schema_version = 1",
                "",
                "[models.alibaba-deepseek-v4-pro]",
                'model_id = "deepseek-v4-pro"',
                'provider = "alibaba-cloud-studio"',
                "tool_calling_supported = true",
                'allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]',
                "",
                "[routing.alibaba-cloud-studio]",
                'default_model = "alibaba-deepseek-v4-pro"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "alibaba_cloud_studio_harness.py").write_text(
        "API_KEY_ENV = 'ALIBABA_API_KEY'\nENDPOINT_ENV = 'ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT'\n",
        encoding="utf-8",
    )


def test_alibaba_capability_floor_and_routing_are_provider_specific() -> None:
    capability_path = PROJECT_ROOT / "config" / "agent-control" / "harness-capability-registry.toml"
    routing_path = PROJECT_ROOT / ".api-harness" / "routing.toml"
    capabilities = tomllib.loads(capability_path.read_text(encoding="utf-8"))
    routing = tomllib.loads(routing_path.read_text(encoding="utf-8"))

    h_caps = capabilities["harnesses"]["alibaba-cloud-studio"]
    assert all(
        h_caps[name] is True
        for name in (
            "bridge_compliance_gate_respect",
            "root_boundary_respect",
            "author_metadata_env_var_setting",
            "destructive_gate_delegation",
            "tool_guard_adapter_fail_closed",
        )
    )
    assert h_caps["advertised_tool_subset"] == CANONICAL_TOOLS
    assert h_caps["dialect"] == "anthropic-messages"
    assert h_caps["hook_tier"] == "native-full-hooks"
    assert h_caps["auth_style"] == "authorization-bearer"
    assert h_caps["auth_env_key"] == "ALIBABA_API_KEY"
    assert h_caps["endpoint_env_key"] == "ALIBABA_ANTHROPIC_COMPATIBLE_ENDPOINT"
    assert h_caps["activity_envelope_projection_mode"] == "compact-provider"

    model = routing["models"]["alibaba-deepseek-v4-pro"]
    assert model["provider"] == "alibaba-cloud-studio"
    assert model["tool_calling_supported"] is True
    assert model["allowed_tools"] == CANONICAL_TOOLS
    assert routing["routing"]["alibaba-cloud-studio"]["default_model"] == "alibaba-deepseek-v4-pro"
    assert routing["models"]["deepseek-v4-pro"]["provider"] == "openrouter"


def test_doctor_accepts_clean_h_fixture_without_credentials(tmp_path: Path) -> None:
    _write_clean_harness_fixture(tmp_path)

    result = _check_alibaba_cloud_studio_harness(tmp_path)

    assert result.status == "pass", result.message
    assert "identity" in result.message.lower()
    assert "Goose retirement" in result.message


def test_doctor_accepts_enabled_h_after_governed_live_proof(tmp_path: Path) -> None:
    _write_clean_harness_fixture(tmp_path)
    registry_path = tmp_path / "harness-state" / "harness-registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["harnesses"][0]["can_receive_dispatch"] = True
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    result = _check_alibaba_cloud_studio_harness(tmp_path)

    assert result.status == "pass", result.message


def test_doctor_rejects_dispatchable_goose_fixture(tmp_path: Path) -> None:
    _write_clean_harness_fixture(tmp_path)
    registry_path = tmp_path / "harness-state" / "harness-registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["harnesses"][1]["can_receive_dispatch"] = True
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    result = _check_alibaba_cloud_studio_harness(tmp_path)

    assert result.status == "warning"
    assert "Goose G remains dispatchable" in result.message
