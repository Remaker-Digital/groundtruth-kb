"""Codex conformance uses the neutral baseline and its own native projection."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

from scripts import check_harness_parity as parity

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def tree(tmp_path):
    for rel in (parity.ENGINE, "scripts/harness_projection/profiles.toml", "scripts/codex_hook_adapter.py"):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, target)
    base = tmp_path / parity.BASELINE
    (base / "skills/inspect-work").mkdir(parents=True)
    (base / "skills/inspect-work/SKILL.md").write_text(
        "---\nname: inspect-work\ndescription: Inspect current work.\n---\nUse the CLI.\n", encoding="utf-8"
    )
    (base / "hooks").mkdir()
    (base / "hooks/manifest.toml").write_text(
        "schema_version = 1\n"
        '[[hook]]\nevent = "pre_tool_use"\nintents = ["file_write", "shell_exec"]\n'
        'script = "implementation_start_gate.py"\nscript_root = "project_scripts"\nblocking = true\ntimeout_seconds = 5\n'
        '[[hook]]\nevent = "session_start"\nintents = ["all"]\n'
        'script = "startup.py"\nblocking = false\ntimeout_seconds = 60\n',
        encoding="utf-8",
    )
    for name in ("implementation_start_gate.py", "startup.py"):
        target = tmp_path / "scripts" / name if name == "implementation_start_gate.py" else base / "hooks" / name
        target.write_text("print('{}')\n", encoding="utf-8")
    plan = parity._load_projector(tmp_path).build_plan("codex")
    assert not plan.gaps, plan.gaps
    for rel, content in plan.writes.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return tmp_path


def report(root, *, installed=True):
    return parity.check_harness_parity(root, harness="codex", installed=installed)


def issues(result):
    return result["issues"] + result["harnesses"].get("codex", {}).get("issues", [])


def test_codex_derivation_has_no_peer_configuration_dependency(monkeypatch):
    original = Path.open
    peers = {".claude", ".agent", ".cursor", ".goose", ".api-harness", "harness-state", ".gtkb-state"}

    def guarded(path, *args, **kwargs):
        assert not peers.intersection(path.parts), f"Peer or retired authority accessed: {path}"
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    result = report(ROOT, installed=False)
    assert result["status"] == "pass", result
    assert result["operational_readiness"] == "not_evaluated"


def test_codex_current_projection_passes_without_role_or_identity_files(tree):
    result = report(tree)
    assert result["status"] == "pass", result
    assert {p.name for p in tree.iterdir()} == {"scripts", parity.BASELINE, ".codex"}
    assert result["operational_readiness"] == "not_evaluated"


def test_codex_conformance_cli_reports_installed_drift_and_preserves_bytes(tree, capsys):
    argv = ["--project-root", str(tree), "--harness", "codex", "--json"]
    assert parity.main(argv) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "pass"
    path = tree / ".codex/hooks.json"
    path.write_text('{"hooks": {}}', encoding="utf-8")
    before = path.read_bytes()
    assert parity.main(argv) == 1
    result = json.loads(capsys.readouterr().out)
    assert any(i["code"] == "changed_output" and i["path"] == ".codex/hooks.json" for i in issues(result))
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "damage", ["missing", "invalid_json", "disabled", "missing_route", "wrong_matcher", "duplicate"]
)
def test_codex_missing_or_changed_registration_is_not_qualified(tree, damage):
    path = tree / ".codex/hooks.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    if damage == "missing":
        path.unlink()
    elif damage == "invalid_json":
        path.write_text("{", encoding="utf-8")
    else:
        if damage == "disabled":
            value["disableAllHooks"] = True
        elif damage == "missing_route":
            value["hooks"]["PreToolUse"] = []
        elif damage == "wrong_matcher":
            value["hooks"]["PreToolUse"][0]["matcher"] = "Read"
        else:
            value["hooks"]["PreToolUse"] *= 2
        path.write_text(json.dumps(value), encoding="utf-8")
    before = path.read_bytes() if path.exists() else None
    result = report(tree)
    assert result["status"] == "fail", result
    assert any(i["code"] in {"missing_output", "changed_output"} for i in issues(result))
    assert (path.read_bytes() if path.exists() else None) == before


def test_codex_bridge_gate_is_registered_once_for_each_native_effect_tool(tree):
    value = json.loads((tree / ".codex/hooks.json").read_text(encoding="utf-8"))
    groups = value["hooks"]["PreToolUse"]
    for tool in ("Bash", "apply_patch"):
        commands = [h["command"] for g in groups if re.fullmatch(g["matcher"], tool) for h in g["hooks"]]
        assert sum("implementation_start_gate.py" in c for c in commands) == 1
    assert not any(re.fullmatch(g["matcher"], "Read") for g in groups)
    # Registration is checked here; effect refusal is exercised by native subprocess tests.


def test_codex_startup_registration_retains_timeout_headroom(tree):
    value = json.loads((tree / ".codex/hooks.json").read_text(encoding="utf-8"))
    handlers = [h for group in value["hooks"]["SessionStart"] for h in group["hooks"]]
    assert len(handlers) == 1
    assert handlers[0]["timeout"] >= 60
    assert "startup.py" in handlers[0]["command"]


def test_codex_stop_and_startup_are_explicit_native_events():
    plan = parity._load_projector(ROOT).build_plan("codex")
    assert not plan.gaps
    value = json.loads(plan.writes[".codex/hooks.json"])
    assert set(value["hooks"]) == {"PreToolUse", "PostToolUse", "Stop"}
    assert all(not g.get("matcher") for g in value["hooks"]["Stop"])
    commands = [h["command"] for groups in value["hooks"].values() for g in groups for h in g["hooks"]]
    assert not any("auto_finalize_sweep.py" in c or "cross_harness_bridge_trigger.py" in c for c in commands)
    assert not any(name in c for c in commands for name in ("owner-decision-tracker", "owner-decision-capture"))
