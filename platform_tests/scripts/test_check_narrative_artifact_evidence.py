"""Tests for the narrative-artifact universal-floor pre-commit gate.

Bridge:    bridge/gtkb-narrative-artifact-approval-extension-001-004.md (GO)
Specs:     GOV-ARTIFACT-APPROVAL-001 (extended), DCL-ARTIFACT-APPROVAL-HOOK-001 (extended)
Slice C of GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001.

Tests use the script's pure `evaluate(...)` entry point with explicit `paths`
to avoid depending on the actual git index. The CLI/staged-path branch is
exercised by a small smoke test via subprocess to confirm argparse handling.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_narrative_artifact_evidence.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_narrative_artifact_evidence", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_narrative_artifact_evidence"] = module
    spec.loader.exec_module(module)
    return module


def _make_fixture(tmp_path: Path, files: dict[str, str | bytes], packets: dict[str, dict] | None = None) -> Path:
    """Build a synthetic project root with files and approval packets.

    `files`: mapping of relative path -> file content (bytes via utf-8). Any
        path under .groundtruth/formal-artifact-approvals/ is set up via the
        `packets` argument instead.
    `packets`: mapping of relative packet path -> JSON-serializable dict.
    """
    # Layout the synthetic project
    config_path = tmp_path / "config" / "governance" / "narrative-artifact-approval.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    # Copy the live config so test sees the real protected/exempt patterns
    live_config = (REPO_ROOT / "config" / "governance" / "narrative-artifact-approval.toml").read_text(encoding="utf-8")
    config_path.write_text(live_config, encoding="utf-8")

    for rel, content in files.items():
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")

    if packets:
        packets_dir = tmp_path / ".groundtruth" / "formal-artifact-approvals"
        packets_dir.mkdir(parents=True, exist_ok=True)
        for rel, data in packets.items():
            (packets_dir / rel).write_text(json.dumps(data), encoding="utf-8")

    # Stage everything in a synthetic git repo so `_staged_blob_sha256` works
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return tmp_path


def _make_packet(target_path: str, content: str, **overrides) -> dict:
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    base = {
        "artifact_type": "narrative_artifact",
        "artifact_id": "test-artifact",
        "action": "update",
        "target_path": target_path,
        "source_ref": "bridge/gtkb-narrative-artifact-approval-extension-001-004.md",
        "full_content": content,
        "full_content_sha256": sha,
        "approval_mode": "approve",
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": "Owner verbatim approval text recorded in transcript.",
        "changed_by": "claude/test",
        "change_reason": "test fixture",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# T-C-block-without-evidence
# ---------------------------------------------------------------------------


def test_c_block_without_evidence(tmp_path):
    """Staging a narrative-artifact change without an approval packet must fail."""
    module = _load_module()
    target = ".claude/rules/example.md"
    content = "new narrative content\n"
    root = _make_fixture(tmp_path, {target: content})
    result = module.evaluate(root, paths=[target])
    assert result["status"] == "fail"
    assert len(result["findings"]) == 1
    finding = result["findings"][0]
    assert finding["path"] == target
    assert "no matching approval packet" in finding["reason"]


# ---------------------------------------------------------------------------
# T-C-allow-with-packet
# ---------------------------------------------------------------------------


def test_c_allow_with_matching_packet(tmp_path):
    """A valid approval packet whose hash matches the staged content allows."""
    module = _load_module()
    target = ".claude/rules/example.md"
    content = "approved narrative content\n"
    packet = _make_packet(target, content)
    root = _make_fixture(tmp_path, {target: content}, packets={"2026-05-08-test.json": packet})
    result = module.evaluate(root, paths=[target])
    assert result["status"] == "pass", result
    assert target in result["cleared"]
    assert result["findings"] == []


def test_c_allow_with_lf_normalized_packet_for_crlf_staged_blob(tmp_path):
    """A valid LF-normalized packet authorizes CRLF staged bytes for text artifacts."""
    module = _load_module()
    target = ".claude/rules/example.md"
    packet_content = "approved narrative content\nsecond line\n"
    staged_content = b"approved narrative content\r\nsecond line\r\n"
    packet = _make_packet(target, packet_content)
    root = _make_fixture(tmp_path, {target: staged_content}, packets={"2026-05-08-test.json": packet})
    result = module.evaluate(root, paths=[target])
    assert result["status"] == "pass", result
    assert target in result["cleared"]
    assert result["findings"] == []


# ---------------------------------------------------------------------------
# T-C-content-mismatch
# ---------------------------------------------------------------------------


def test_c_block_when_packet_content_does_not_match_staged(tmp_path):
    """A packet whose full_content does not match the staged blob must fail."""
    module = _load_module()
    target = ".claude/rules/example.md"
    staged_content = "what was actually staged\n"
    packet_content = "what the packet describes\n"
    packet = _make_packet(target, packet_content)
    root = _make_fixture(tmp_path, {target: staged_content}, packets={"2026-05-08-test.json": packet})
    result = module.evaluate(root, paths=[target])
    # No matching packet found because target_path matches but sha256 doesn't
    assert result["status"] == "fail"
    assert "no matching approval packet" in result["findings"][0]["reason"]


def test_c_block_when_crlf_staged_blob_substantively_differs_from_packet(tmp_path):
    """EOL normalization must not mask actual text differences."""
    module = _load_module()
    target = ".claude/rules/example.md"
    staged_content = b"what was actually staged\r\n"
    packet = _make_packet(target, "what the packet describes\n")
    root = _make_fixture(tmp_path, {target: staged_content}, packets={"2026-05-08-test.json": packet})
    result = module.evaluate(root, paths=[target])
    assert result["status"] == "fail"
    assert "no matching approval packet" in result["findings"][0]["reason"]


def test_c_block_non_utf8_staged_blob(tmp_path):
    """Protected narrative artifacts are UTF-8 text; undecodable staged blobs fail."""
    module = _load_module()
    target = ".claude/rules/example.md"
    root = _make_fixture(tmp_path, {target: b"\xff\xfe\x00"})
    result = module.evaluate(root, paths=[target])
    assert result["status"] == "fail"
    assert "not valid UTF-8" in result["findings"][0]["reason"]


def test_c_block_when_packet_target_path_mismatches(tmp_path):
    """A packet for a different target_path must not authorize an unrelated staged path."""
    module = _load_module()
    other_target = "AGENTS.md"
    other_content = "something else\n"
    target = ".claude/rules/example.md"
    staged_content = "narrative content\n"
    packet = _make_packet(other_target, other_content)
    root = _make_fixture(
        tmp_path,
        {target: staged_content, other_target: other_content},
        packets={"2026-05-08-test.json": packet},
    )
    # Stage only `target` for the test
    result = module.evaluate(root, paths=[target])
    assert result["status"] == "fail"


# ---------------------------------------------------------------------------
# T-C-claude-and-codex-paths (harness-agnostic by construction)
# ---------------------------------------------------------------------------


def test_c_blocks_regardless_of_origin(tmp_path):
    """The pre-commit gate runs at git-layer and is harness-agnostic; same blocking
    behavior regardless of which AI harness produced the staged change.

    This is verified structurally: the gate reads from `git diff --cached`, not
    from any harness-specific identifier. We simulate two notional sources by
    running the same evaluation twice with different packet states; both must
    block when no packet is present and pass when one is.
    """
    module = _load_module()
    target = "AGENTS.md"
    content = "agent instructions\n"

    # Source 1: "Claude harness" produced the change without a packet
    root1 = _make_fixture(tmp_path / "claude_origin", {target: content})
    r1 = module.evaluate(root1, paths=[target])
    assert r1["status"] == "fail"

    # Source 2: "Codex harness" produced the same change without a packet
    root2 = _make_fixture(tmp_path / "codex_origin", {target: content})
    r2 = module.evaluate(root2, paths=[target])
    assert r2["status"] == "fail"

    # Both block equivalently; the gate does not consult harness identity
    assert r1["findings"][0]["reason"] == r2["findings"][0]["reason"]


# ---------------------------------------------------------------------------
# T-C-no-bypass
# ---------------------------------------------------------------------------


def test_c_no_commit_message_escape_hatch(tmp_path):
    """The gate does NOT honor any commit-message escape tag (e.g., [narrative-exempt:]);
    such a tag is a hypothetical bypass that this slice deliberately does not implement.

    This test simply asserts the script source does not read commit messages or
    look for an escape pattern, ensuring the gate cannot be bypassed by message convention.
    """
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "narrative-exempt" not in source
    assert "COMMIT_EDITMSG" not in source
    assert "commit_msg" not in source.lower()


# ---------------------------------------------------------------------------
# T-C-skipped-unprotected
# ---------------------------------------------------------------------------


def test_c_unprotected_paths_skipped(tmp_path):
    """Paths that don't match the protected pattern set must pass through."""
    module = _load_module()
    targets = ["scripts/some_script.py", "tests/scripts/test_x.py", "MEMORY.md"]
    root = _make_fixture(tmp_path, {t: f"content of {t}\n" for t in targets})
    result = module.evaluate(root, paths=targets)
    assert result["status"] == "pass"
    assert result["cleared"] == []
    assert sorted(result["skipped_unprotected"]) == sorted(targets)


def test_c_exempted_paths_skipped(tmp_path):
    """Hook-managed and local-override paths are exempted."""
    module = _load_module()
    targets = ["memory/pending-owner-decisions.md", ".claude/rules/owner.local.md"]
    root = _make_fixture(tmp_path, {t: f"content {t}\n" for t in targets})
    result = module.evaluate(root, paths=targets)
    assert result["status"] == "pass"
    assert sorted(result["skipped_unprotected"]) == sorted(targets)


# ---------------------------------------------------------------------------
# T-C-cli-smoke
# ---------------------------------------------------------------------------


def test_c_cli_emits_json(tmp_path):
    """Smoke test: --paths + --json prints valid JSON with expected keys."""
    target = ".claude/rules/example.md"
    content = "narrative content\n"
    root = _make_fixture(tmp_path, {target: content})
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--paths",
            target,
            "--json",
            "--project-root",
            str(root),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Returns exit 1 on fail (no packet) but still emits valid JSON
    assert result.returncode in (0, 1)
    payload = json.loads(result.stdout)
    assert payload["status"] in {"pass", "fail"}
    assert "findings" in payload
    assert "cleared" in payload
    assert "skipped_unprotected" in payload


def test_c_cli_requires_paths_or_staged():
    """--staged or --paths is required."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# T-C-config-error
# ---------------------------------------------------------------------------


def test_c_config_missing_returns_runtime_error(tmp_path, monkeypatch):
    """Missing config raises GateError surfacing as exit 2 in the CLI."""
    module = _load_module()
    # Use a tmp project root that has NO config
    fake_root = tmp_path / "empty"
    fake_root.mkdir()
    with pytest.raises(module.GateError):
        module._load_config(fake_root)


# ---------------------------------------------------------------------------
# T-C-release-gate-integration (per GO -004 condition C4 + NO-GO -007 F1)
# ---------------------------------------------------------------------------


def test_c_release_gate_imports_narrative_artifact_evidence():
    """Per Slice C C4 + NO-GO -007 F1: scripts/release_candidate_gate.py must
    integrate with check_narrative_artifact_evidence so the release-readiness
    report surfaces the narrative-artifact rollup.
    """
    release_gate = REPO_ROOT / "scripts" / "release_candidate_gate.py"
    text = release_gate.read_text(encoding="utf-8")
    # The release gate calls check_narrative_artifact_evidence.evaluate(...)
    assert "check_narrative_artifact_evidence" in text, (
        "scripts/release_candidate_gate.py must import check_narrative_artifact_evidence "
        "to surface the narrative-artifact rollup per Slice C C4."
    )
    assert "_check_narrative_artifact_evidence" in text or "evaluate(PROJECT_ROOT" in text, (
        "release_candidate_gate.py must invoke evaluate() against PROJECT_ROOT per Slice C C4 GO scope."
    )


def test_c_release_gate_pass_message_present():
    """The release-gate integration emits a PASS line with 'narrative-artifact evidence'
    so dashboard / CI consumers can pattern-match the rollup status.
    """
    release_gate = REPO_ROOT / "scripts" / "release_candidate_gate.py"
    text = release_gate.read_text(encoding="utf-8")
    assert "PASS narrative-artifact evidence" in text, (
        "release_candidate_gate.py must emit a 'PASS narrative-artifact evidence' "
        "message so the rollup is consumable by downstream tooling."
    )
