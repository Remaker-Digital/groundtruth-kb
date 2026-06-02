"""Tests for the bridge protected narrative-artifact write helper."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".claude" / "skills" / "bridge" / "helpers" / "protected_write.py"
CHECKER_PATH = REPO_ROOT / "scripts" / "check_narrative_artifact_evidence.py"
SKILL_PATH = REPO_ROOT / ".claude" / "skills" / "bridge" / "SKILL.md"


def _load_helper_module():
    spec = importlib.util.spec_from_file_location("bridge_protected_write_helper_under_test", HELPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["bridge_protected_write_helper_under_test"] = module
    spec.loader.exec_module(module)
    return module


def _load_checker_module():
    spec = importlib.util.spec_from_file_location("check_narrative_artifact_evidence_under_test", CHECKER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_narrative_artifact_evidence_under_test"] = module
    spec.loader.exec_module(module)
    return module


def _make_project(tmp_path: Path) -> Path:
    config_target = tmp_path / "config" / "governance" / "narrative-artifact-approval.toml"
    config_target.parent.mkdir(parents=True)
    config_target.write_text(
        (REPO_ROOT / "config" / "governance" / "narrative-artifact-approval.toml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    return tmp_path


def _packet(target_path: str, content: str, **overrides) -> dict:
    packet = {
        "artifact_type": "narrative_artifact",
        "artifact_id": "test-protected-write",
        "action": "update",
        "target_path": target_path,
        "source_ref": "bridge/gtkb-bridge-skill-protected-write-helper-004.md",
        "full_content": content,
        "full_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "Owner approved this protected write in the transcript.",
        "changed_by": "codex/A",
        "change_reason": "protected write helper test fixture",
    }
    packet.update(overrides)
    return packet


def _write_packet(root: Path, packet: dict, *, filename: str = "2026-06-02-test-protected-write.json") -> Path:
    packet_dir = root / ".groundtruth" / "formal-artifact-approvals"
    packet_dir.mkdir(parents=True, exist_ok=True)
    path = packet_dir / filename
    path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _write_content_file(root: Path, content: str) -> Path:
    path = root / "content.txt"
    path.write_text(content, encoding="utf-8", newline="")
    return path


def _run_helper(root: Path, target: str, content_file: Path, packet_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(HELPER_PATH),
            "--project-root",
            str(root),
            "--target",
            target,
            "--content-file",
            str(content_file),
            "--packet",
            str(packet_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def test_helper_writes_with_valid_packet(tmp_path):
    root = _make_project(tmp_path)
    target = ".claude/rules/example.md"
    content = "approved narrative content\n"
    packet_path = _write_packet(root, _packet(target, content))
    content_file = _write_content_file(root, content)

    result = _run_helper(root, target, content_file, packet_path)

    assert result.returncode == 0, result.stderr
    assert (root / target).read_text(encoding="utf-8") == content
    checker = _load_checker_module()
    assert checker.evaluate(root, paths=[target])["status"] == "pass"


def test_helper_rejects_hash_mismatch(tmp_path):
    root = _make_project(tmp_path)
    target = ".claude/rules/example.md"
    content = "approved narrative content\n"
    packet_path = _write_packet(root, _packet(target, "different content\n"))
    content_file = _write_content_file(root, content)

    result = _run_helper(root, target, content_file, packet_path)

    assert result.returncode == 1
    assert "failed validation" in result.stderr
    assert not (root / target).exists()


def test_helper_rejects_invalid_packet(tmp_path):
    root = _make_project(tmp_path)
    target = "AGENTS.md"
    content = "agent instructions\n"
    invalid_packet = _packet(target, content, artifact_type="deliberation")
    packet_path = _write_packet(root, invalid_packet)
    content_file = _write_content_file(root, content)

    result = _run_helper(root, target, content_file, packet_path)

    assert result.returncode == 1
    assert "DCL-ARTIFACT-APPROVAL-HOOK-001" in result.stderr
    assert not (root / target).exists()


def test_helper_rejects_unprotected_target(tmp_path):
    root = _make_project(tmp_path)
    target = "notes/example.txt"
    content = "plain note\n"
    packet_path = _write_packet(root, _packet(target, content))
    content_file = _write_content_file(root, content)

    result = _run_helper(root, target, content_file, packet_path)

    assert result.returncode == 1
    assert "not a protected narrative artifact" in result.stderr
    assert not (root / target).exists()


def test_helper_lf_normalizes_content(tmp_path):
    root = _make_project(tmp_path)
    target = ".claude/rules/example.md"
    authored_content = "line one\r\nline two\r\n"
    normalized_content = "line one\nline two\n"
    packet_path = _write_packet(root, _packet(target, normalized_content))
    content_file = _write_content_file(root, authored_content)

    result = _run_helper(root, target, content_file, packet_path)

    assert result.returncode == 0, result.stderr
    written = (root / target).read_bytes()
    assert written == normalized_content.encode("utf-8")
    assert hashlib.sha256(written).hexdigest() == _packet(target, normalized_content)["full_content_sha256"]


def test_helper_surfaces_evidence_checker_finding(tmp_path):
    root = _make_project(tmp_path)
    target = ".claude/rules/example.md"
    content = "approved narrative content\n"
    external_packet = tmp_path / "outside-packet.json"
    external_packet.write_text(json.dumps(_packet(target, content)), encoding="utf-8")
    content_file = _write_content_file(root, content)

    result = _run_helper(root, target, content_file, external_packet)

    assert result.returncode == 1
    assert "FAIL narrative-artifact evidence" in result.stderr
    assert "no matching approval packet" in result.stderr
    assert (root / target).read_text(encoding="utf-8") == content


def test_skill_md_references_helper():
    skill_text = SKILL_PATH.read_text(encoding="utf-8")

    assert "Protected-file Writes" in skill_text
    assert ".claude/skills/bridge/helpers/protected_write.py" in skill_text
    assert "Layer-C universal-floor evidence path" in skill_text
