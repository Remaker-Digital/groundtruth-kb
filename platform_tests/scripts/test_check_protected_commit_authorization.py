"""Tests for the protected commit authorization pre-commit gate."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_protected_commit_authorization.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_protected_commit_authorization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_protected_commit_authorization"] = module
    spec.loader.exec_module(module)
    return module


def _packet(root: Path, bridge_id: str) -> None:
    packet_dir = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    packet_dir.mkdir(parents=True, exist_ok=True)
    (packet_dir / f"{bridge_id}.json").write_text(json.dumps({"bridge_id": bridge_id}), encoding="utf-8")


def test_blocks_protected_path_without_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "fail"
    assert result["findings"][0]["path"] == "scripts/foo.py"


def test_dot_prefixed_protected_surfaces_are_blocked_without_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    paths = [
        ".claude/hooks/h.py",
        ".codex/gtkb-hooks/h.py",
        ".github/workflows/ci.yml",
        ".claude/settings.json",
        ".codex/hooks.json",
    ]
    result = module.evaluate(tmp_path, paths=paths)

    assert result["status"] == "fail"
    assert {finding["path"] for finding in result["findings"]} == set(paths)


def test_live_go_packet_allows_protected_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "list_named_packets",
        lambda root: [
            {
                "bridge_id": "gtkb-example",
                "path": ".gtkb-state/implementation-authorizations/by-bridge/gtkb-example.json",
                "valid": True,
                "target_path_globs": ["scripts/foo.py"],
                "error": None,
            }
        ],
    )

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "pass"
    assert result["cleared"][0]["evidence"] == "live_go_packet"


def test_terminal_verified_thread_allows_without_live_packet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / "gtkb-example-001.md").write_text('NEW\n\ntarget_paths: ["scripts/foo.py"]\n', encoding="utf-8")
    _packet(tmp_path, "gtkb-example")
    monkeypatch.setattr(
        module,
        "list_named_packets",
        lambda root: [
            {
                "bridge_id": "gtkb-example",
                "path": ".gtkb-state/implementation-authorizations/by-bridge/gtkb-example.json",
                "valid": False,
                "target_path_globs": ["scripts/foo.py"],
                "error": "expired",
            }
        ],
    )
    monkeypatch.setattr(
        module,
        "bridge_entry",
        lambda root, bridge_id: SimpleNamespace(
            latest_status="VERIFIED",
            versions=[
                ("VERIFIED", "bridge/gtkb-example-003.md"),
                ("GO", "bridge/gtkb-example-002.md"),
                ("NEW", "bridge/gtkb-example-001.md"),
            ],
        ),
    )

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "pass"
    assert result["cleared"][0]["evidence"] == "terminal_verified_bridge_thread"


def test_routine_paths_short_circuit_before_packet_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()

    def fail_if_called(root):
        raise AssertionError("routine paths must not read implementation packets")

    monkeypatch.setattr(module, "list_named_packets", fail_if_called)

    result = module.evaluate(
        tmp_path,
        paths=[
            "memory/MEMORY.md",
            "docs/guide.md",
            "bridge/thread-001.md",
            ".gtkb-state/state.json",
            "independent-progress-assessments/report.md",
        ],
    )

    assert result["status"] == "pass"
    assert result["protected_paths"] == []


def test_verified_bridge_file_without_finalization_evidence_blocks(tmp_path: Path) -> None:
    module = _load_module()
    bridge_file = tmp_path / "bridge" / "gtkb-example-004.md"
    bridge_file.parent.mkdir()
    bridge_file.write_text(
        """VERIFIED

# Verdict

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest fixture` | yes | PASS |
""",
        encoding="utf-8",
    )

    result = module.evaluate(tmp_path, paths=["bridge/gtkb-example-004.md"])

    assert result["status"] == "fail"
    assert "Commit Finalization Evidence" in result["findings"][0]["reason"]


def test_verified_bridge_file_with_finalization_evidence_passes(tmp_path: Path) -> None:
    module = _load_module()
    bridge_file = tmp_path / "bridge" / "gtkb-example-004.md"
    bridge_file.parent.mkdir()
    bridge_file.write_text(
        """VERIFIED

# Verdict

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`
- Same-transaction path set:
- `scripts/foo.py`
- `bridge/gtkb-example-003.md`
- `bridge/gtkb-example-004.md`
""",
        encoding="utf-8",
    )

    result = module.evaluate(tmp_path, paths=["bridge/gtkb-example-004.md"])

    assert result["status"] == "pass"
    assert result["findings"] == []


def test_corrupt_packet_blocks_protected_path_when_no_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "list_named_packets",
        lambda root: [
            {
                "path": ".gtkb-state/implementation-authorizations/by-bridge/bad.json",
                "bridge_id": None,
                "valid": False,
                "target_path_globs": [],
                "error": "corrupt or unreadable",
            }
        ],
    )

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "fail"
    assert "evidence_errors" in result["findings"][0]


def test_groundtruth_db_and_githooks_are_protected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["groundtruth.db", ".githooks/pre-commit"])

    assert result["status"] == "fail"
    assert {finding["path"] for finding in result["findings"]} == {"groundtruth.db", ".githooks/pre-commit"}


def test_json_shape_for_cli_paths(tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    exit_code = module.main(["--project-root", str(tmp_path), "--paths", "scripts/foo.py", "--json"])
    parsed = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert parsed["status"] == "fail"
    assert parsed["protected_paths"] == ["scripts/foo.py"]
