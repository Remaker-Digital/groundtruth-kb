"""The existing projection diagnostic replaces the obsolete vendor-pair check.

All fixtures begin as complete projector output. Corruptions below are explicit
disposable negative canaries, never manual changes to installed projections.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from groundtruth_kb.project.doctor import _check_harness_projection_conformance

pytestmark = pytest.mark.timeout(300)


@pytest.fixture
def projected(tmp_path, generated_harness_root):
    root = tmp_path / "candidate"
    shutil.copytree(generated_harness_root, root)
    return root


def groups(root, relative):
    path = root / relative
    document = json.loads(path.read_text(encoding="utf-8"))
    hits = [row for row in document["hooks"]["PreToolUse"] if "sot-read-discipline.py" in json.dumps(row)]
    assert len(hits) == 1
    return path, document, hits[0]


def test_clean_passes(projected: Path):
    result = _check_harness_projection_conformance(projected)
    assert result.status == "pass", result.message
    assert "actual hook invocation remains separate qualification" in result.message


def test_missing_canonical_hook_warns(projected: Path):
    (projected / ".harness-baseline-configuration/hooks/sot-read-discipline.py").unlink()
    result = _check_harness_projection_conformance(projected)
    assert result.status == "fail", result.message


def test_missing_codex_adapter_warns(projected: Path):
    (projected / "scripts/codex_hook_adapter.py").unlink()
    result = _check_harness_projection_conformance(projected)
    assert result.status == "fail" and "codex" in result.message


def test_claude_matcher_missing_glob_warns(projected: Path):
    path, data, entry = groups(projected, ".claude/settings.json")
    entry["matcher"] = entry["matcher"].replace("Glob", "")
    path.write_text(json.dumps(data), encoding="utf-8")
    result = _check_harness_projection_conformance(projected)
    assert result.status == "fail" and "claude" in result.message


def test_codex_false_green_read_matcher_fails(projected: Path):
    path, data, entry = groups(projected, ".codex/hooks.json")
    entry["matcher"] = "Read|Grep|Glob"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = _check_harness_projection_conformance(projected)
    assert result.status == "fail" and "codex" in result.message


def test_codex_missing_bash_warns(projected: Path):
    path, data, entry = groups(projected, ".codex/hooks.json")
    # A basename in an unrelated command cannot prove the intended hook runs.
    entry["hooks"][0]["command"] = "echo sot-read-discipline.py"
    path.write_text(json.dumps(data), encoding="utf-8")
    result = _check_harness_projection_conformance(projected)
    assert result.status == "fail" and "codex" in result.message


def test_missing_settings_files_warns(projected: Path):
    (projected / ".claude/settings.json").unlink()
    (projected / ".codex/hooks.json").unlink()
    result = _check_harness_projection_conformance(projected)
    assert result.status == "fail" and "claude" in result.message and "codex" in result.message
