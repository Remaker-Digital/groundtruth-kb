"""Tests for scripts/proposal_target_paths_coverage_preflight.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "proposal_target_paths_coverage_preflight.py"


def _load_module():
    import sys

    spec = importlib.util.spec_from_file_location("proposal_target_paths_coverage_preflight", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["proposal_target_paths_coverage_preflight"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def module():
    return _load_module()


def _write_proposal(tmp_path: Path, target_paths: list[str], commands: str) -> Path:
    proposal = tmp_path / "proposal.md"
    proposal.write_text(
        f"NEW\n\ntarget_paths: {target_paths!r}\n".replace("'", '"')
        + "\n## Spec-Derived Verification Plan\n\n"
        + commands
        + "\n",
        encoding="utf-8",
    )
    return proposal


def test_flags_pytest_path_missing_from_target_paths(module, tmp_path) -> None:
    proposal = _write_proposal(
        tmp_path,
        ["scripts/example.py"],
        "    .venv/Scripts/python.exe -m pytest platform_tests/scripts/test_example.py -q",
    )

    result, exit_code = module.run_preflight(tmp_path, content_file=str(proposal))

    assert exit_code == module.EXIT_OK
    assert result["uncovered_verification_paths"] == ["platform_tests/scripts/test_example.py"]
    assert result["verdict"] == "gaps"


def test_flags_generator_outputs_missing_from_target_paths(module, tmp_path) -> None:
    proposal = _write_proposal(
        tmp_path,
        ["scripts/generate_codex_skill_adapters.py"],
        "    python scripts/generate_codex_skill_adapters.py --check --update-registry",
    )

    result, _exit_code = module.run_preflight(tmp_path, content_file=str(proposal))

    assert result["uncovered_generator_paths"] == [
        ".codex/skills/**",
        ".codex/skills/MANIFEST.json",
        "config/agent-control/harness-capability-registry.toml",
    ]


def test_generator_output_covered_by_recursive_glob(module, tmp_path) -> None:
    proposal = _write_proposal(
        tmp_path,
        [
            "scripts/generate_codex_skill_adapters.py",
            ".codex/skills/**",
            "config/agent-control/harness-capability-registry.toml",
        ],
        "    python scripts/generate_codex_skill_adapters.py --check --update-registry",
    )

    result, _exit_code = module.run_preflight(tmp_path, content_file=str(proposal))

    assert ".codex/skills/**" not in result["uncovered_generator_paths"]
    assert ".codex/skills/MANIFEST.json" not in result["uncovered_generator_paths"]
    assert result["uncovered_generator_paths"] == []


def test_escaped_path_reported_out_of_root_not_coerced(module, tmp_path) -> None:
    proposal = _write_proposal(
        tmp_path,
        ["platform_tests/scripts/test_example.py"],
        "    .venv/Scripts/python.exe -m pytest ../evil.py -q",
    )

    result, _exit_code = module.run_preflight(tmp_path, content_file=str(proposal))

    assert result["out_of_root"]
    assert result["out_of_root"][0]["path"] == "../evil.py"
    assert result["uncovered_verification_paths"] == []


def test_default_exit_is_advisory_zero_even_with_uncovered(module, tmp_path) -> None:
    proposal = _write_proposal(
        tmp_path,
        ["scripts/example.py"],
        "    pytest platform_tests/scripts/test_missing.py",
    )

    result, exit_code = module.run_preflight(tmp_path, content_file=str(proposal), strict=False)

    assert result["verdict"] == "gaps"
    assert exit_code == module.EXIT_OK


def test_strict_flag_exits_nonzero_on_uncovered(module, tmp_path) -> None:
    proposal = _write_proposal(
        tmp_path,
        ["scripts/example.py"],
        "    pytest platform_tests/scripts/test_missing.py",
    )

    result, exit_code = module.run_preflight(tmp_path, content_file=str(proposal), strict=True)

    assert result["verdict"] == "gaps"
    assert exit_code == module.EXIT_STRICT_GAPS


def test_fully_scoped_proposal_reports_no_gaps(module, tmp_path) -> None:
    proposal = _write_proposal(
        tmp_path,
        [
            "scripts/proposal_target_paths_coverage_preflight.py",
            "platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py",
        ],
        (
            "    .venv/Scripts/python.exe -m pytest "
            "platform_tests/scripts/test_proposal_target_paths_coverage_preflight.py -q"
        ),
    )

    result, exit_code = module.run_preflight(tmp_path, content_file=str(proposal), strict=True)

    assert exit_code == module.EXIT_OK
    assert result["verdict"] == "clean"
    assert result["uncovered_verification_paths"] == []
    assert result["uncovered_generator_paths"] == []
    assert result["out_of_root"] == []
