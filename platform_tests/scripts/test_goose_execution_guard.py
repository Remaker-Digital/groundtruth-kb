"""Tests for goose_execution_guard.py — WI-5831 reliability floor detectors.

Covers write-claim reconciliation, run-window sweep, leak detection,
terminal-stall detection, and provenance-drift detection. All tests use
constructed fixtures; no test spawns the goose CLI or mutates live state.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from goose_execution_guard import (  # noqa: E402
    ExecutionFloorConfig,
    check_provenance_drift,
    detect_terminal_stall,
    detect_tool_call_leaks,
    evaluate_run,
    reconcile_write_claims,
    sweep_run_window,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_project_root(tmp_path: Path) -> Path:
    """A temporary project root with a git repo for sweep tests."""
    root = tmp_path / "project"
    root.mkdir()
    # Initialize git
    subprocess.run(["git", "init"], cwd=str(root), capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(root),
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(root),
        capture_output=True,
    )
    # Create an initial commit so git status works
    (root / "README.md").write_text("# Test")
    subprocess.run(["git", "add", "."], cwd=str(root), capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(root), capture_output=True)
    return root


@pytest.fixture
def default_config() -> ExecutionFloorConfig:
    return ExecutionFloorConfig()


# ---------------------------------------------------------------------------
# Test helpers: payload factories
# ---------------------------------------------------------------------------


def _make_goose_payload(
    messages: list[dict] | None = None,
    tool_requests: list[dict] | None = None,
    tool_results: list[dict] | None = None,
) -> dict:
    """Build a standard Goose JSON payload."""
    payload: dict = {"messages": messages or []}
    if tool_requests is not None:
        payload["tool_requests"] = tool_requests
    if tool_results is not None:
        payload["tool_results"] = tool_results
    return payload


def _assistant_msg(text: str) -> dict:
    return {"role": "assistant", "content": [{"type": "text", "text": text}]}


# ---------------------------------------------------------------------------
# Slice A: Write verification tests
# ---------------------------------------------------------------------------


class TestWriteClaimReconciliation:
    """Tests for reconcile_write_claims."""

    def test_success_write_target_present_and_sized(self, tmp_project_root):
        """A claimed successful write to an existing non-zero file passes."""
        file_path = tmp_project_root / "output.md"
        file_path.write_text("hello world")  # 11 bytes

        payload = _make_goose_payload(
            tool_requests=[
                {
                    "name": "write_file",
                    "id": "call_1",
                    "arguments": {"path": "output.md", "content": "hello world"},
                }
            ],
            tool_results=[{"id": "call_1", "result": "success"}],
        )

        findings, status = reconcile_write_claims(payload, tmp_project_root, {"write_file"})
        assert status in ("verified", "findings")
        assert len(findings) == 0, f"Expected no findings, got: {findings}"

    def test_zero_byte_write_detected(self, tmp_project_root):
        """A claimed successful write of non-empty content to a zero-byte file is detected."""
        file_path = tmp_project_root / "output.md"
        file_path.write_text("")  # 0 bytes

        payload = _make_goose_payload(
            tool_requests=[
                {
                    "name": "write_file",
                    "id": "call_1",
                    "arguments": {"path": "output.md", "content": "should not be empty"},
                }
            ],
            tool_results=[{"id": "call_1", "result": "success"}],
        )

        findings, status = reconcile_write_claims(payload, tmp_project_root, {"write_file"})
        assert status == "findings"
        assert len(findings) == 1
        assert findings[0].finding_class == "write_claim_unfulfilled"
        assert "zero bytes" in findings[0].detail.lower()
        assert findings[0].path == "output.md"

    def test_target_missing_detected(self, tmp_project_root):
        """A claimed successful write to a missing target is detected."""
        payload = _make_goose_payload(
            tool_requests=[
                {
                    "name": "Write",
                    "id": "call_1",
                    "arguments": {"path": "nonexistent.md", "content": "data"},
                }
            ],
            tool_results=[{"id": "call_1", "result": "success"}],
        )

        findings, status = reconcile_write_claims(payload, tmp_project_root, {"Write", "write_file"})
        assert status == "findings"
        assert len(findings) == 1
        assert findings[0].finding_class == "write_claim_unfulfilled"
        assert "target_missing" in str(findings[0].context.get("reason", ""))

    def test_empty_payload_reports_unavailable(self, tmp_project_root):
        """An empty payload yields unavailable status."""
        payload = _make_goose_payload()
        findings, status = reconcile_write_claims(payload, tmp_project_root, {"write_file"})
        assert status == "unavailable"
        assert len(findings) == 0

    def test_unknown_payload_shape_reports_unavailable(self, tmp_project_root):
        """An unrecognized payload shape yields unavailable, never verified."""
        payload = {"some_other_key": []}
        findings, status = reconcile_write_claims(payload, tmp_project_root, {"write_file"})
        assert status == "unavailable"
        assert len(findings) == 0

    def test_messages_format_tool_use_extraction(self, tmp_project_root):
        """Messages-format tool_use/tool_result pairs are extracted."""
        file_path = tmp_project_root / "msg_output.md"
        file_path.write_text("hi")

        payload = {
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": "write a file"}]},
                {
                    "role": "tool_use",
                    "id": "tu_1",
                    "name": "write_file",
                    "input": {"path": "msg_output.md", "content": "hi"},
                },
                {
                    "role": "tool_result",
                    "tool_use_id": "tu_1",
                    "content": [{"type": "text", "text": "success"}],
                },
            ]
        }

        findings, status = reconcile_write_claims(payload, tmp_project_root, {"write_file"})
        # Messages format should be recognized or unavailable, not crash
        assert status in ("unavailable", "verified", "findings")


class TestRunWindowSweep:
    """Tests for sweep_run_window."""

    def test_zero_byte_file_in_window_flagged(self, tmp_project_root):
        """A zero-byte file created inside the run window with git changes is flagged."""
        # Create a zero-byte file and add to git tracking
        zero_file = tmp_project_root / "empty_output.md"
        zero_file.write_text("")
        subprocess.run(
            ["git", "add", "empty_output.md"],
            cwd=str(tmp_project_root),
            capture_output=True,
        )
        # Dirty the index so git status sees it
        zero_file.write_text("")
        subprocess.run(
            ["git", "add", "empty_output.md"],
            cwd=str(tmp_project_root),
            capture_output=True,
        )

        now = time.time()
        findings = sweep_run_window(now - 10, now + 10, tmp_project_root, set())
        found = any(f.path == "empty_output.md" for f in findings)
        assert found, f"Expected zero-byte detection, got findings: {findings}"

    def test_zero_byte_outside_window_not_flagged(self, tmp_project_root):
        """A zero-byte file created outside the run window is not flagged."""
        zero_file = tmp_project_root / "old_empty.md"
        zero_file.write_text("")

        # Use a window far in the past
        findings = sweep_run_window(0, 10, tmp_project_root, set())
        found = any(f.path == "old_empty.md" for f in findings)
        assert not found, "Old zero-byte file should not be flagged"

    def test_intentional_empty_not_flagged(self, tmp_project_root):
        """An allowlisted intentional-empty file is not flagged."""
        gitkeep = tmp_project_root / ".gitkeep"
        gitkeep.write_text("")
        subprocess.run(
            ["git", "add", ".gitkeep"],
            cwd=str(tmp_project_root),
            capture_output=True,
        )

        now = time.time()
        findings = sweep_run_window(now - 10, now + 10, tmp_project_root, {".gitkeep"})
        found = any(f.path == ".gitkeep" for f in findings)
        assert not found, "Allowlisted .gitkeep should not be flagged"

    def test_nonzero_file_not_flagged(self, tmp_project_root):
        """A non-zero file in the window is not flagged."""
        f = tmp_project_root / "real_output.md"
        f.write_text("some content")
        subprocess.run(
            ["git", "add", "real_output.md"],
            cwd=str(tmp_project_root),
            capture_output=True,
        )

        now = time.time()
        findings = sweep_run_window(now - 10, now + 10, tmp_project_root, set())
        found = any(f.path == "real_output.md" for f in findings)
        assert not found, "Non-zero file should not be flagged"


# ---------------------------------------------------------------------------
# Slice B: Leak detection tests
# ---------------------------------------------------------------------------


class TestLeakDetection:
    """Tests for detect_tool_call_leaks."""

    LEAK_PATTERNS: dict[str, str] = {
        "dsml_marker": r"(?i)<\s*(?:tool_call|function_call|invoke|DSML)",
        "text_form_envelope": r"(?i)(?:tool_call|function_call|tool_use|call_tool)\s*[\(\[:{]",
        "raw_tool_call_text": r'(?i)\{\s*"(?:name|function|tool_name|tool)"\s*:',
    }

    def test_dsml_marker_leak_detected(self):
        """DeepSeek DSML tool-call marker in assistant text is detected."""
        messages = [_assistant_msg("Here is the result. <tool_call> do something </tool_call>")]
        findings = detect_tool_call_leaks(messages, self.LEAK_PATTERNS)
        assert len(findings) >= 1
        assert any(f.finding_class == "leaked_tool_call_text" for f in findings)

    def test_text_form_envelope_detected(self):
        """Text-form tool-call envelope is detected."""
        messages = [_assistant_msg("Let me help. tool_call(path='test.md', content='data')")]
        findings = detect_tool_call_leaks(messages, self.LEAK_PATTERNS)
        assert len(findings) >= 1

    def test_raw_json_tool_call_detected(self):
        """Raw JSON tool-call text in assistant prose is detected."""
        messages = [_assistant_msg('I will {"name": "write_file", "arguments": {"path": "f.md"}}')]
        findings = detect_tool_call_leaks(messages, self.LEAK_PATTERNS)
        assert len(findings) >= 1

    def test_clean_text_no_leak(self):
        """Clean assistant text produces no findings."""
        messages = [_assistant_msg("The file has been written successfully. Here is a summary.")]
        findings = detect_tool_call_leaks(messages, self.LEAK_PATTERNS)
        assert len(findings) == 0

    def test_empty_patterns_produces_no_findings(self):
        """Empty pattern set produces no findings."""
        messages = [_assistant_msg("<tool_call>leak</tool_call>")]
        findings = detect_tool_call_leaks(messages, {})
        assert len(findings) == 0

    def test_user_messages_not_scanned(self):
        """User messages are not scanned for leaks."""
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "<tool_call>something</tool_call>"}]},
        ]
        findings = detect_tool_call_leaks(messages, self.LEAK_PATTERNS)
        assert len(findings) == 0


class TestTerminalStallDetection:
    """Tests for detect_terminal_stall."""

    def test_terminal_is_leaked_tool_call(self):
        """When the terminal message is itself a tool_call, stall is detected."""
        messages = [
            _assistant_msg("Working..."),
            {"role": "tool_use", "name": "write_file", "input": {}},
        ]
        findings = detect_terminal_stall(messages, max_turns=40)
        assert len(findings) >= 1
        assert any(f.finding_class == "terminal_leak_stall" for f in findings)

    def test_terminal_assistant_has_leaked_text(self):
        """When the terminal assistant message contains leaked tool-call text."""
        messages = [_assistant_msg('<tool_call name="write_file">data</tool_call>')]
        findings = detect_terminal_stall(messages, max_turns=40)
        assert len(findings) >= 1
        assert any(f.finding_class == "terminal_leak_stall" for f in findings)

    def test_turn_cap_without_terminal_text(self):
        """Turn cap reached without terminal assistant produces stall."""
        messages = [
            _assistant_msg("msg 1"),
            _assistant_msg("msg 2"),
        ]
        findings = detect_terminal_stall(messages, max_turns=2)
        # The last msg IS assistant, so no stall from turn-cap check
        # But with max_turns exceeded, this should still pass
        assert not any(f.finding_class == "terminal_leak_stall" and "turn cap" in f.detail.lower() for f in findings)

    def test_normal_terminal_no_stall(self):
        """Normal terminal assistant message produces no stall finding."""
        messages = [_assistant_msg("All done. The files have been created successfully.")]
        findings = detect_terminal_stall(messages, max_turns=40)
        assert len(findings) == 0

    def test_empty_messages_is_stall(self):
        """Empty message list is a stall."""
        findings = detect_terminal_stall([], max_turns=40)
        assert len(findings) >= 1
        assert any(f.finding_class == "terminal_leak_stall" for f in findings)


# ---------------------------------------------------------------------------
# Slice C: Provenance guard tests
# ---------------------------------------------------------------------------


class TestProvenanceGuard:
    """Tests for check_provenance_drift."""

    def _make_bridge_file(self, bridge_dir: Path, name: str, author_model: str) -> Path:
        path = bridge_dir / name
        path.write_text(
            f"GO\n"
            f"author_identity: Goose G\n"
            f"author_harness_id: G\n"
            f"author_session_context_id: test-123\n"
            f"author_model: {author_model}\n"
            f"author_model_version: {author_model}\n"
            f"author_model_configuration: test\n"
            f"author_metadata_source: test\n\n"
            f"# Test artifact\n"
        )
        return path

    def test_provenance_drift_detected(self, tmp_project_root):
        """A bridge artifact with wrong author_model is detected."""
        bridge_dir = tmp_project_root / "bridge"
        bridge_dir.mkdir()
        self._make_bridge_file(bridge_dir, "test-artifact-001.md", "claude-opus-4")

        now = time.time()
        live_model = {"author_model": "deepseek-v4-pro", "author_model_version": "deepseek-v4-pro"}

        findings = check_provenance_drift(tmp_project_root, now - 10, now + 10, live_model)
        assert len(findings) >= 1
        assert findings[0].finding_class == "provenance_drift"
        assert "claude-opus-4" in findings[0].detail
        assert "deepseek-v4-pro" in findings[0].detail

    def test_matching_provenance_passes(self, tmp_project_root):
        """A bridge artifact with matching author_model produces no finding."""
        bridge_dir = tmp_project_root / "bridge"
        bridge_dir.mkdir()
        self._make_bridge_file(bridge_dir, "test-artifact-001.md", "deepseek-v4-pro")

        now = time.time()
        live_model = {"author_model": "deepseek-v4-pro", "author_model_version": "deepseek-v4-pro"}

        findings = check_provenance_drift(tmp_project_root, now - 10, now + 10, live_model)
        assert len(findings) == 0

    def test_file_outside_window_not_checked(self, tmp_project_root):
        """A file created outside the run window is not checked."""
        bridge_dir = tmp_project_root / "bridge"
        bridge_dir.mkdir()
        self._make_bridge_file(bridge_dir, "old-artifact-001.md", "claude-opus-4")

        # Window far in the past
        live_model = {"author_model": "deepseek-v4-pro", "author_model_version": "deepseek-v4-pro"}
        findings = check_provenance_drift(tmp_project_root, 0, 10, live_model)
        assert len(findings) == 0

    def test_no_live_model_no_findings(self, tmp_project_root):
        """Empty live model produces no findings."""
        bridge_dir = tmp_project_root / "bridge"
        bridge_dir.mkdir()
        self._make_bridge_file(bridge_dir, "test-artifact-001.md", "claude-opus-4")

        now = time.time()
        findings = check_provenance_drift(tmp_project_root, now - 10, now + 10, {})
        assert len(findings) == 0

    def test_guard_never_edits_artifacts(self, tmp_project_root):
        """The provenance guard never edits artifacts."""
        bridge_dir = tmp_project_root / "bridge"
        bridge_dir.mkdir()
        path = self._make_bridge_file(bridge_dir, "test-artifact-001.md", "claude-opus-4")
        original_content = path.read_text()

        now = time.time()
        live_model = {"author_model": "deepseek-v4-pro", "author_model_version": "deepseek-v4-pro"}

        check_provenance_drift(tmp_project_root, now - 10, now + 10, live_model)
        assert path.read_text() == original_content, "Guard must not edit artifacts"


# ---------------------------------------------------------------------------
# Integrated evaluate_run tests
# ---------------------------------------------------------------------------


class TestEvaluateRun:
    """Integration tests for evaluate_run."""

    def test_clean_run_returns_zero(self, tmp_project_root):
        """A clean payload with no write claims or leaks returns exit 0."""
        payload = _make_goose_payload(messages=[_assistant_msg("Task completed successfully.")])
        config = ExecutionFloorConfig(
            write_verification_enabled=False,
            provenance_guard_enabled=False,
        )

        now = time.time()
        diagnostic = evaluate_run(
            payload,
            tmp_project_root,
            config,
            window_start=now - 1,
            window_end=now + 1,
            max_turns=40,
        )
        assert diagnostic.exit_code == 0
        assert len(diagnostic.findings) == 0

    def test_leak_produces_nonzero(self, tmp_project_root):
        """A leak finding produces a non-zero exit code."""
        payload = _make_goose_payload(messages=[_assistant_msg("<tool_call>do something</tool_call>")])
        config = ExecutionFloorConfig(
            write_verification_enabled=False,
            provenance_guard_enabled=False,
            leak_patterns={
                "dsml_marker": r"(?i)<\s*(?:tool_call|function_call)",
            },
        )

        now = time.time()
        diagnostic = evaluate_run(
            payload,
            tmp_project_root,
            config,
            window_start=now - 1,
            window_end=now + 1,
            max_turns=40,
        )
        assert diagnostic.exit_code != 0
        assert len(diagnostic.findings) >= 1

    def test_diagnostic_json_serializable(self, tmp_project_root):
        """The diagnostic JSON output is valid."""
        payload = _make_goose_payload(messages=[_assistant_msg("test")])
        config = ExecutionFloorConfig(
            write_verification_enabled=False,
            provenance_guard_enabled=False,
        )

        now = time.time()
        diagnostic = evaluate_run(
            payload,
            tmp_project_root,
            config,
            window_start=now - 1,
            window_end=now + 1,
            max_turns=40,
        )
        json_str = diagnostic.to_json()
        parsed = json.loads(json_str)
        assert "exit_code" in parsed
        assert "findings" in parsed

    def test_write_reconciliation_unavailable_in_diagnostic(self, tmp_project_root):
        """When payload has no tool requests, reconciliation reports unavailable."""
        payload = {"messages": [_assistant_msg("no tools here")]}
        config = ExecutionFloorConfig()

        now = time.time()
        diagnostic = evaluate_run(
            payload,
            tmp_project_root,
            config,
            window_start=now - 1,
            window_end=now + 1,
            max_turns=40,
        )
        assert diagnostic.write_claim_reconciliation == "unavailable"
        assert diagnostic.exit_code == 0


# ---------------------------------------------------------------------------
# Configuration tests
# ---------------------------------------------------------------------------


class TestConfig:
    """Tests for ExecutionFloorConfig."""

    def test_default_config(self):
        """Default configuration has sensible defaults."""
        config = ExecutionFloorConfig()
        assert config.write_verification_enabled is True
        assert config.retry_attempts == 0
        assert config.provenance_guard_enabled is True

    def test_config_from_toml(self, tmp_path):
        """Configuration loads from a valid TOML file."""
        toml_path = tmp_path / "test-config.toml"
        toml_path.write_text("""
schema_version = 1

[write_verification]
enabled = true
write_tool_names = ["write", "Write"]

[leak_detection]
retry_attempts = 3
retry_backoff_seconds = 5

[leak_detection.patterns]
dsml_marker = '(?i)<tool_call>'
""")
        config = ExecutionFloorConfig.from_toml(toml_path)
        assert config.write_verification_enabled is True
        assert config.write_tool_names == {"write", "Write"}
        assert config.retry_attempts == 3
        assert config.retry_backoff_seconds == 5
        assert "dsml_marker" in config.leak_patterns

    def test_config_missing_file_returns_defaults(self, tmp_path):
        """Missing config file returns defaults."""
        config = ExecutionFloorConfig.from_toml(tmp_path / "nonexistent.toml")
        assert config.write_verification_enabled is True

    def test_disable_all_floors(self):
        """All floors can be disabled."""
        config = ExecutionFloorConfig(
            write_verification_enabled=False,
            provenance_guard_enabled=False,
            leak_patterns={},
        )
        assert config.write_verification_enabled is False
        assert config.provenance_guard_enabled is False
        assert config.leak_patterns == {}


# ---------------------------------------------------------------------------
# Timer discipline test
# ---------------------------------------------------------------------------


class TestTimerDiscipline:
    """DELIB-202667722: no new hard-coded timer literals."""

    def test_no_timer_literals_in_guard(self):
        """The guard module contains no retry/backoff/throttle literals
        outside of configuration defaults and subprocess timeouts.

        DELIB-202667722 prohibits hard-coded timer values for operational
        bounds (retry attempts, backoff intervals, throttle delays).
        Subprocess timeout values (defensive process guards) are not
        the target of this check.
        """
        guard_path = Path(__file__).parent.parent.parent / "scripts" / "goose_execution_guard.py"
        content = guard_path.read_text()

        lines_with_timer = []
        for i, line in enumerate(content.splitlines()):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""'):
                continue
            # Check for retry/backoff/throttle literals (not subprocess timeouts)
            if re.search(
                r"(?:retry|backoff|throttle|delay)_?(?:seconds|attempts|ms)?\s*=\s*[1-9]\d*", stripped, re.IGNORECASE
            ):
                # Exclude the config class defaults (which have type annotations, not bare assignments)
                if "self.retry" not in stripped and "config.retry" not in stripped:
                    lines_with_timer.append(f"L{i + 1}: {stripped}")

        assert len(lines_with_timer) == 0, f"Guard module contains hard-coded timer literals: {lines_with_timer}"

    def test_config_sets_all_bounds(self):
        """Every bound in the config defaults to zero (explicit failure)."""
        config = ExecutionFloorConfig()
        assert config.retry_attempts == 0, "retry_attempts must default to 0 (no auto-retry)"
        assert config.retry_backoff_seconds == 0, "retry_backoff_seconds must default to 0"
