"""Spec-derived tests for the WI-4801 legacy harness-language scanner."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _PROJECT_ROOT / "scripts" / "check_legacy_harness_language.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_legacy_harness_language", _SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_legacy_harness_language"] = module
    spec.loader.exec_module(module)
    return module


def _write_text(root: Path, rel_path: str, text: str) -> Path:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_detects_legacy_reviewer_harness_phrases(tmp_path: Path) -> None:
    check = _load_module()
    path = _write_text(
        tmp_path,
        ".claude/rules/file-bridge-protocol.md",
        "The Codex reviewer harness owns this bridge check.\n",
    )

    findings = check.scan_text(tmp_path, path, path.read_text(encoding="utf-8"))

    assert findings
    assert {finding.pattern_family for finding in findings} >= {
        "reviewer_harness_language",
        "harness_role_coupling",
    }
    assert all(finding.classification == "STRIP" for finding in findings)


def test_excludes_bridge_audit_and_runtime_state(tmp_path: Path) -> None:
    check = _load_module()
    bridge_path = _write_text(tmp_path, "bridge/example-001.md", "Codex reviewer harness\n")
    runtime_path = _write_text(tmp_path, ".gtkb-state/state.md", "Codex reviewer harness\n")
    memory_path = _write_text(tmp_path, "memory/MEMORY.md", "Codex reviewer harness\n")

    assert check.classify_path(tmp_path, bridge_path).classification == "EXCLUDED"
    assert check.classify_path(tmp_path, runtime_path).classification == "EXCLUDED"
    assert check.classify_path(tmp_path, memory_path).classification == "EXCLUDED"
    assert check.evaluate(tmp_path)["summary"]["matches"] == 0


def test_classifies_keep_strip_quarantine(tmp_path: Path) -> None:
    check = _load_module()
    strip_path = _write_text(tmp_path, ".claude/rules/role.md", "Codex as reviewer for this surface.\n")
    keep_path = _write_text(
        tmp_path,
        "platform_tests/scripts/test_fixture.py",
        'def test_fixture():\n    assert "Codex as reviewer" == "Codex as reviewer"\n',
    )
    quarantine_path = _write_text(
        tmp_path,
        ".codex/skills/bridge/SKILL.md",
        "<!-- GTKB-CODEX-SKILL-ADAPTER\nGenerated: true\n-->\nCodex as reviewer.\n",
    )

    strip = check.scan_text(tmp_path, strip_path, strip_path.read_text(encoding="utf-8"))
    keep = check.scan_text(tmp_path, keep_path, keep_path.read_text(encoding="utf-8"))
    quarantine = check.scan_text(tmp_path, quarantine_path, quarantine_path.read_text(encoding="utf-8"))

    assert {finding.classification for finding in strip} == {"STRIP"}
    assert {finding.classification for finding in keep} == {"KEEP"}
    assert {finding.classification for finding in quarantine} == {"QUARANTINE"}


def test_rejects_out_of_root_paths(tmp_path: Path) -> None:
    check = _load_module()
    outside = tmp_path.parent / "outside.md"

    with pytest.raises(ValueError, match="outside project root"):
        check.relative_to_root(tmp_path, outside)


def test_json_and_text_outputs_are_stable(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    check = _load_module()
    _write_text(tmp_path, "AGENTS.md", "Claude and Codex are hard-coded reviewer harnesses.\n")

    assert check.main(["--project-root", str(tmp_path), "--json"]) == 0
    json_output = capsys.readouterr().out
    payload = json.loads(json_output)
    assert payload["status"] == "advisory"
    assert payload["summary"]["matches"] >= 1
    assert {"path", "line", "column", "classification", "pattern_id"} <= set(payload["findings"][0])

    assert check.main(["--project-root", str(tmp_path)]) == 0
    text_output = capsys.readouterr().out
    assert "[ADVISORY] legacy harness-language scan" in text_output
    assert "AGENTS.md:1:" in text_output


def test_live_root_smoke_is_read_only() -> None:
    check = _load_module()
    before = {path.as_posix() for path in _PROJECT_ROOT.glob("scripts/check_legacy_harness_language.py")}

    result = check.evaluate(_PROJECT_ROOT)

    assert result["status"] in {"advisory", "pass"}
    assert {"files_scanned", "matches", "by_classification"} <= set(result["summary"])
    after = {path.as_posix() for path in _PROJECT_ROOT.glob("scripts/check_legacy_harness_language.py")}
    assert after == before
