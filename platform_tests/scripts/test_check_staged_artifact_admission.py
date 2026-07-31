"""Coverage for the staged-artifact admission gate (WI-5699).

The gate answers the question no other sweep check asks: may this file be here
at all? Each test pins one admission basis or one fail-safe behavior.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = PROJECT_ROOT / "scripts" / "check_staged_artifact_admission.py"

_spec = importlib.util.spec_from_file_location("check_staged_artifact_admission", MODULE_PATH)
assert _spec and _spec.loader
admission = importlib.util.module_from_spec(_spec)
sys.modules["check_staged_artifact_admission"] = admission
_spec.loader.exec_module(admission)


CONFIG = """
schema_version = 1

[[rules]]
id = "root-scratch"
glob = "_*.py"
root_only = true
reason = "root session scratch"

[[rules]]
id = "runtime-state"
glob = ".gtkb-state/**"
root_only = false
reason = "runtime state"
"""

PROPOSAL = """NEW
Document: fixture-thread
Version: 001
target_paths: ["src/declared.py", "platform_tests/test_declared.py"]
"""

VERDICT = """GO
Document: fixture-thread
Version: 002
Responds to: bridge/fixture-thread-001.md
"""


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "fixture-thread-001.md").write_text(PROPOSAL, encoding="utf-8")
    # A verdict carries no target_paths; it must contribute nothing and raise nothing.
    (tmp_path / "bridge" / "fixture-thread-002.md").write_text(VERDICT, encoding="utf-8")
    config_dir = tmp_path / "config" / "governance"
    config_dir.mkdir(parents=True)
    (config_dir / "staging-admission.toml").write_text(CONFIG, encoding="utf-8")
    return tmp_path


def classify(workspace: Path, *paths: str) -> admission.AdmissionReport:
    return admission.evaluate(workspace, paths=list(paths))


# --- the four admission buckets ---------------------------------------------


def test_declared_target_path_is_authorized(workspace: Path) -> None:
    report = classify(workspace, "src/declared.py")
    assert report.authorized == {"src/declared.py": "fixture-thread-001.md"}
    assert report.unresolved == []


def test_config_excluded_path_reports_matching_rule(workspace: Path) -> None:
    report = classify(workspace, "_debug_scratch.py")
    assert report.excluded == {"_debug_scratch.py": "root-scratch"}
    assert report.unresolved == []


def test_directory_glob_exclusion_matches_nested_paths(workspace: Path) -> None:
    report = classify(workspace, ".gtkb-state/ops/run.json")
    assert report.excluded == {".gtkb-state/ops/run.json": "runtime-state"}


def test_unregistered_addition_is_unresolved(workspace: Path) -> None:
    """The finding this gate exists to produce.

    Reproduces the 2026-07-31 sweep: a harness transcript with no bridge
    target_paths coverage, no registry record, and no exclusion rule.
    """
    report = classify(workspace, "harness-test-transcripts/glm52-r3.json")
    assert report.unresolved == ["harness-test-transcripts/glm52-r3.json"]
    assert report.authorized == {}
    assert report.excluded == {}


# --- scoping and fail-safe behavior -----------------------------------------


def test_root_only_rule_does_not_match_nested_paths(workspace: Path) -> None:
    """`root_only` scratch rules must not excuse a nested file of the same shape."""
    report = classify(workspace, "src/_helper.py")
    assert report.excluded == {}
    assert report.unresolved == ["src/_helper.py"]


def test_verdict_without_target_paths_contributes_no_authorization(workspace: Path) -> None:
    """A verdict file carries no target_paths; that is normal, not an error."""
    report = classify(workspace, "src/undeclared.py")
    assert report.unresolved == ["src/undeclared.py"]
    assert not any("fixture-thread-002" in error for error in report.errors)


def test_missing_exclusion_config_fails_safe(tmp_path: Path) -> None:
    """Without config, nothing is excused and the gap is surfaced."""
    (tmp_path / "bridge").mkdir()
    report = admission.evaluate(tmp_path, paths=["_debug_scratch.py"])
    assert report.unresolved == ["_debug_scratch.py"]
    assert any("exclusion config missing" in error for error in report.errors)


def test_rule_missing_reason_is_rejected_not_applied(tmp_path: Path) -> None:
    """A rule without a reason must not silently excuse paths."""
    (tmp_path / "bridge").mkdir()
    config_dir = tmp_path / "config" / "governance"
    config_dir.mkdir(parents=True)
    (config_dir / "staging-admission.toml").write_text(
        'schema_version = 1\n\n[[rules]]\nid = "no-reason"\nglob = "_*.py"\n',
        encoding="utf-8",
    )
    report = admission.evaluate(tmp_path, paths=["_x.py"])
    assert report.unresolved == ["_x.py"]
    assert any("missing id, glob, or reason" in error for error in report.errors)


def test_empty_addition_set_is_clean(workspace: Path) -> None:
    report = classify(workspace)
    assert report.to_dict() == {
        "authorized": {},
        "errors": [],
        "excluded": {},
        "registered": {},
        "unresolved": [],
    }


# --- determinism and advisory posture ---------------------------------------


def test_output_is_order_independent(workspace: Path) -> None:
    forward = classify(workspace, "src/declared.py", "_debug_scratch.py", "zz/unknown.txt")
    reverse = classify(workspace, "zz/unknown.txt", "_debug_scratch.py", "src/declared.py")
    assert forward.to_dict() == reverse.to_dict()


def test_render_is_stable_for_identical_input(workspace: Path) -> None:
    first = admission.render(classify(workspace, "src/declared.py", "zz/unknown.txt"))
    second = admission.render(classify(workspace, "zz/unknown.txt", "src/declared.py"))
    assert first == second


def test_phase_one_always_exits_zero_even_with_unresolved(workspace: Path) -> None:
    """Phase 1 is advisory: it reports and never blocks."""
    exit_code = admission.main(["--project-root", str(workspace), "--path", "harness-test-transcripts/glm52-r3.json"])
    assert exit_code == 0


def test_json_mode_exits_zero_and_emits_all_buckets(workspace: Path, capsys: pytest.CaptureFixture[str]) -> None:
    import json as json_module

    exit_code = admission.main(["--project-root", str(workspace), "--json", "--path", "zz/unknown.txt"])
    assert exit_code == 0
    payload = json_module.loads(capsys.readouterr().out)
    assert set(payload) == {"authorized", "errors", "excluded", "registered", "unresolved"}
    assert payload["unresolved"] == ["zz/unknown.txt"]


# --- reuse invariant ---------------------------------------------------------


def test_reuses_canonical_surfaces_without_reimplementing_them() -> None:
    """No second target_paths parser and no second registry reader."""
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "from implementation_authorization import extract_target_paths" in source
    assert "from controlled_artifact_paths import classify_controlled_artifact" in source
    assert "def extract_target_paths(" not in source, "must not reimplement the parser"
    assert "def classify_controlled_artifact(" not in source, "must not reimplement the registry reader"
