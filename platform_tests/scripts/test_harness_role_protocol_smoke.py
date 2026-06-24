"""Focused tests for the harness role/protocol smoke benchmark."""

from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path

from scripts.benchmarks import cli, harness_role_protocol_smoke

WINDOW_START = "2026-01-01T00:00:00+00:00"
WINDOW_END = "2026-06-24T00:00:00+00:00"


def _write(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _fixture_root(tmp_path: Path) -> Path:
    _write(
        tmp_path,
        "harness-state/harness-registry.json",
        json.dumps(
            {
                "harnesses": [
                    {"id": "A", "role": ["prime-builder"]},
                    {"id": "B", "role": ["loyal-opposition"]},
                ]
            }
        ),
    )
    _write(
        tmp_path,
        ".claude/rules/file-bridge-protocol.md",
        "NEW REVISED GO NO-GO VERIFIED Prime Builder Loyal Opposition "
        "implementation_authorization.py begin work-intent claim",
    )
    _write(
        tmp_path,
        "scripts/implementation_authorization.py",
        "target_paths Requirement Sufficiency Project Authorization latest_status GO work-intent",
    )
    _write(
        tmp_path,
        ".claude/rules/project-root-boundary.md",
        "E:\\GT-KB No GT-KB artifact protected",
    )
    _write(
        tmp_path,
        ".claude/rules/codex-review-gate.md",
        "No implementation without Loyal Opposition implementation-start protected",
    )
    _write(
        tmp_path,
        "AGENTS.md",
        "GOV-SESSION-ROLE-AUTHORITY-001 DCL-SESSION-ROLE-RESOLUTION-001 transcript-defined durable role",
    )
    _write(
        tmp_path,
        ".claude/rules/prime-builder-role.md",
        "GOV-SESSION-ROLE-AUTHORITY-001 DCL-SESSION-ROLE-RESOLUTION-001 transcript-defined durable role",
    )
    _write(
        tmp_path,
        ".claude/rules/operating-role.md",
        "GOV-SESSION-ROLE-AUTHORITY-001 DCL-SESSION-ROLE-RESOLUTION-001 transcript-defined durable role",
    )
    _write(
        tmp_path,
        "scripts/benchmarks/harness_quality_manifest.py",
        "direct_mutation_refusal cli_first_operation no_durable_role_assignment_change "
        "no_live_bridge_backlog_spec_challenge_mutation no_dispatcher_ranking_or_eligibility_enforcement "
        "no_external_service_side_effects",
    )
    return tmp_path


def test_full_fixture_scores_one_and_reports_dimensions(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)

    result = harness_role_protocol_smoke.run(WINDOW_START, WINDOW_END, root)

    assert result.benchmark_id == "harness_role_protocol_smoke"
    assert result.value == 1.0
    assert result.dimensions["passed"] == result.dimensions["total"] == 6
    assert set(result.dimensions["probes"]) == {
        "role_adoption",
        "bridge_protocol_compliance",
        "implementation_start_safety",
        "protected_mutation_boundary",
        "role_authority_citation",
        "direct_mutation_refusal",
    }
    for probe in result.dimensions["probes"].values():
        assert probe["passed"] is True
        assert probe["missing"] == []


def test_missing_role_and_manifest_anchors_reduce_score(tmp_path: Path) -> None:
    root = _fixture_root(tmp_path)
    _write(
        root,
        "harness-state/harness-registry.json",
        json.dumps({"harnesses": [{"id": "A", "role": ["prime-builder"]}]}),
    )
    _write(
        root,
        "scripts/benchmarks/harness_quality_manifest.py",
        "direct_mutation_refusal cli_first_operation",
    )

    result = harness_role_protocol_smoke.run(WINDOW_START, WINDOW_END, root)

    assert result.value == 0.6667
    probes = result.dimensions["probes"]
    assert probes["role_adoption"]["passed"] is False
    assert probes["role_adoption"]["missing"] == ["loyal-opposition"]
    assert probes["direct_mutation_refusal"]["passed"] is False
    assert "no_durable_role_assignment_change" in probes["direct_mutation_refusal"]["missing"]


def test_missing_project_root_surfaces_are_safe(tmp_path: Path) -> None:
    result = harness_role_protocol_smoke.run(WINDOW_START, WINDOW_END, tmp_path)

    assert result.value == 0.0
    assert result.dimensions["passed"] == 0
    assert not (tmp_path / ".gtkb-state").exists()
    assert not (tmp_path / "groundtruth.db").exists()


def test_benchmark_module_is_registered_and_importable() -> None:
    assert "harness_role_protocol_smoke" in cli.BENCHMARK_MODULES
    mod = importlib.import_module("scripts.benchmarks.harness_role_protocol_smoke")
    assert callable(getattr(mod, "run", None))


def test_module_has_no_write_or_database_mutation_calls() -> None:
    source = Path(harness_role_protocol_smoke.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_attr_calls = {
        "commit",
        "execute",
        "executemany",
        "executescript",
        "mkdir",
        "open",
        "replace",
        "unlink",
        "write_bytes",
        "write_text",
    }
    forbidden_sql = ("insert ", "update ", "delete ", "replace ", "drop ", "create table", "alter ")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in forbidden_attr_calls, f"write call {node.func.attr}"
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            low = node.value.lower()
            for verb in forbidden_sql:
                assert verb not in low, f"write SQL fragment {verb!r} in literal"
