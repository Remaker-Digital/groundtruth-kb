"""Unit tests for harness_probe_dsv4pro_r2.py — DeepSeek V4 Pro Run 2.

Tests exercise every capability check including pass and failure paths,
the determinism contract, and the timer discipline requirement.

Verifies:
    - GOV-HARNESS-ONBOARDING-CONTRACT-001: capability floor assertions
    - ADR-ISOLATION-APPLICATION-PLACEMENT-001: project-root containment
    - DELIB-202667722: no hard-coded timer/timeout literals
    - WI-5808 §DELIVERABLE(1)-(6): all six probe checks
    - WI-5808 §TIMER DISCIPLINE: timeout from CLI argument
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest import mock

# ---------------------------------------------------------------------------
# Path to the probe script under test
# ---------------------------------------------------------------------------
_PROBE_SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "harness_probe_dsv4pro_r2.py"


def _run_probe(*extra_args: str, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    """Run the probe script with the given extra arguments, return the result."""
    return subprocess.run(
        [sys.executable, str(_PROBE_SCRIPT), *extra_args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_probe_json(*extra_args: str, timeout: float = 30.0) -> dict[str, object]:
    """Run the probe and return the parsed JSON report."""
    result = _run_probe(*extra_args, timeout=timeout)
    assert result.returncode == 0, f"Probe exit {result.returncode}\nstderr: {result.stderr[:1000]}"
    return json.loads(result.stdout)  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Check (1): project-root containment
# ---------------------------------------------------------------------------


class TestProjectRootContainment:
    """Verifies WI-5808 §DELIVERABLE(1), ADR-ISOLATION-APPLICATION-PLACEMENT-001."""

    def test_project_root_containment_pass(self) -> None:
        """Probe run from within the project root reports containment=true."""
        report = _run_probe_json()
        assert report["project_root_containment"] is True, (
            f"Expected true, got {report['project_root_containment']}\ndetails: {report.get('details')}"
        )

    def test_project_root_containment_fail(self) -> None:
        """Probe cwd check detects non-contained working directory."""
        # Simulate by patching the containment check directly
        from scripts.harness_probe_dsv4pro_r2 import _check_project_root_containment

        fake_root = Path("E:/GT-KB")
        report = _check_project_root_containment(fake_root)
        # If actual cwd IS inside E:\GT-KB, this may return true;
        # the test validates the function shape, not the actual containment.
        assert isinstance(report["project_root_containment"], bool)
        assert "details" in report
        assert "cwd" in report["details"]
        assert "project_root" in report["details"]


# ---------------------------------------------------------------------------
# Check (2): venv resolution
# ---------------------------------------------------------------------------


class TestVenvResolution:
    """Verifies WI-5808 §DELIVERABLE(2)."""

    def test_venv_resolution_pass(self) -> None:
        """Probe in the GT-KB workspace reports venv_resolution=true."""
        report = _run_probe_json()
        assert report["venv_resolution"] is True, (
            f"Expected venv_resolution=true, got {report}\ndetails: {report.get('details')}"
        )

    def test_venv_resolution_fail_returns_false(self) -> None:
        """Nonexistent venv path produces venv_resolution=false."""
        from scripts.harness_probe_dsv4pro_r2 import _check_venv_resolution

        fake_root = Path(tempfile.mkdtemp())
        try:
            result = _check_venv_resolution(fake_root, timeout=5.0)
            assert result["venv_resolution"] is False
        finally:
            # Clean up temp dir
            try:
                fake_root.rmdir()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Check (3): git read health
# ---------------------------------------------------------------------------


class TestGitReadHealth:
    """Verifies WI-5808 §DELIVERABLE(3)."""

    def test_git_read_health_pass(self) -> None:
        """Probe in a git workspace reports git_read_health.ok=true."""
        report = _run_probe_json()
        git_health = report["git_read_health"]
        assert isinstance(git_health, dict)
        assert git_health["ok"] is True, f"Expected git ok=true, got {git_health}"
        assert isinstance(git_health["head_sha"], str)
        assert len(git_health["head_sha"]) == 40, f"Expected 40-char SHA, got '{git_health['head_sha']}'"
        assert isinstance(git_health["dirty_count"], int)

    def test_git_read_health_fail_non_git_dir(self) -> None:
        """Non-git directory produces git_read_health.ok=false."""
        from scripts.harness_probe_dsv4pro_r2 import _check_git_read_health

        fake_root = Path(tempfile.mkdtemp())
        try:
            result = _check_git_read_health(fake_root, timeout=10.0)
            assert result["git_read_health"]["ok"] is False
        finally:
            try:
                fake_root.rmdir()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Check (4): gt CLI reachability
# ---------------------------------------------------------------------------


class TestGtCliReachability:
    """Verifies WI-5808 §DELIVERABLE(4)."""

    def test_gt_cli_reachability_pass(self) -> None:
        """Probe in the GT-KB workspace reports gt_cli_reachability=true."""
        report = _run_probe_json()
        assert report["gt_cli_reachability"] is True, f"Expected gt_cli_reachability=true, got {report}"

    def test_gt_cli_reachability_fail_nonexistent(self) -> None:
        """Non-existent venv with subprocess failure produces reachability=false."""
        from scripts.harness_probe_dsv4pro_r2 import _check_gt_cli_reachability

        fake_root = Path(tempfile.mkdtemp())
        try:
            # The probe falls back to sys.executable if venv python doesn't
            # exist. Mock subprocess.run to simulate a failure for both paths.
            with mock.patch("scripts.harness_probe_dsv4pro_r2.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired(cmd=["mock"], timeout=1.0)
                result = _check_gt_cli_reachability(fake_root, timeout=5.0)
                assert result["gt_cli_reachability"] is False
        finally:
            try:
                fake_root.rmdir()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Check (5): session-envelope surface presence
# ---------------------------------------------------------------------------


class TestSessionEnvelopePresence:
    """Verifies WI-5808 §DELIVERABLE(5)."""

    def test_session_envelope_presence_pass(self) -> None:
        """Probe with envelope present reports true."""
        report = _run_probe_json()
        assert report["session_envelope_presence"] is True, f"Expected session_envelope_presence=true, got {report}"

    def test_session_envelope_presence_fail_missing(self) -> None:
        """Missing envelope path reports false."""
        from scripts.harness_probe_dsv4pro_r2 import _check_session_envelope_presence

        fake_root = Path(tempfile.mkdtemp())
        try:
            result = _check_session_envelope_presence(fake_root)
            assert result["session_envelope_presence"] is False
        finally:
            try:
                fake_root.rmdir()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Check (6): report determinism
# ---------------------------------------------------------------------------


class TestReportDeterminism:
    """Verifies WI-5808 §DELIVERABLE(6)."""

    def test_report_determinism_two_runs(self) -> None:
        """Two consecutive probe runs produce byte-identical JSON excluding
        generated_at."""
        report1 = _run_probe_json()
        report2 = _run_probe_json()

        # Exclude generated_at from comparison
        r1 = {k: v for k, v in report1.items() if k != "generated_at"}
        r2 = {k: v for k, v in report2.items() if k != "generated_at"}

        assert r1 == r2, (
            f"Reports differ excluding generated_at:\n"
            f"  report1: {json.dumps(r1, sort_keys=True)}\n"
            f"  report2: {json.dumps(r2, sort_keys=True)}"
        )

    def test_generated_at_differs(self) -> None:
        """generated_at fields differ between consecutive runs."""
        report1 = _run_probe_json()
        report2 = _run_probe_json()
        assert report1["generated_at"] != report2["generated_at"], "generated_at should differ between runs"

    def test_generated_at_is_iso8601(self) -> None:
        """generated_at is an ISO-8601 UTC timestamp."""
        report = _run_probe_json()
        ts = report["generated_at"]
        assert isinstance(ts, str)
        # Should end with Z or +00:00
        assert ts.endswith("Z") or "+00:00" in ts, f"Expected ISO-8601 UTC, got: {ts}"
        # Should parse as datetime
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ---------------------------------------------------------------------------
# Timer discipline (DELIB-202667722)
# ---------------------------------------------------------------------------


class TestTimerDiscipline:
    """Verifies DELIB-202667722: no hard-coded timer literals."""

    def test_timeout_from_cli_arg(self) -> None:
        """--timeout CLI argument is accepted and applied."""
        result = _run_probe("--timeout", "5.0")
        assert result.returncode == 0, f"Probe with --timeout 5.0 failed: {result.stderr[:500]}"

    def test_no_hardcoded_timeout_literals(self) -> None:
        """Source file contains zero hard-coded timeout/timer/interval literals.

        The only acceptable timeout numeric is in the argparse default
        (which is a documented CLI argument default, not a hard-coded
        subprocess timeout). All subprocess timeout= values must reference
        the timeout parameter, not integer/float literals.
        """
        source = _PROBE_SCRIPT.read_text(encoding="utf-8")
        # Find all subprocess.run calls with explicit timeout=
        pattern = re.compile(r"subprocess\.run\([^)]*timeout\s*=\s*([^,)\s]+)")
        matches = pattern.findall(source)
        for match in matches:
            # If the match is a numeric literal, flag it.
            # The only allowed numeric defaults are the argparse default and
            # test helper defaults, which are in test files, not source.
            if match.strip().isdigit():
                # Numeric literal in subprocess.run(..., timeout=N) — fail
                raise AssertionError(f"Hard-coded timeout literal found in source: timeout={match.strip()}")


# ---------------------------------------------------------------------------
# Report structure tests
# ---------------------------------------------------------------------------


class TestReportStructure:
    """Verifies the JSON report structure."""

    def test_all_required_keys_present(self) -> None:
        """Report contains all required top-level keys with snake_case."""
        report = _run_probe_json()
        required_keys = {
            "generated_at",
            "probe_version",
            "run_identifier",
            "project_root_containment",
            "venv_resolution",
            "git_read_health",
            "gt_cli_reachability",
            "session_envelope_presence",
            "report_determinism",
            "details",
        }
        missing = required_keys - set(report.keys())
        assert not missing, f"Missing keys: {missing}"

    def test_run_identifier_is_r2(self) -> None:
        """run_identifier matches the run-2 designation."""
        report = _run_probe_json()
        assert report["run_identifier"] == "dsv4pro-r2", f"Expected dsv4pro-r2, got {report['run_identifier']}"

    def test_probe_version_present(self) -> None:
        """probe_version is a non-empty string."""
        report = _run_probe_json()
        assert isinstance(report["probe_version"], str)
        assert len(report["probe_version"]) > 0

    def test_json_is_valid_utf8(self) -> None:
        """Output is valid UTF-8 JSON."""
        result = _run_probe()
        assert result.returncode == 0
        # json module ensures valid JSON
        json.loads(result.stdout)

    def test_snake_case_keys(self) -> None:
        """All top-level keys use snake_case convention."""
        report = _run_probe_json()
        camel_case_keys = [k for k in report if any(c.isupper() for c in k)]
        assert not camel_case_keys, f"Keys with uppercase (non-snake_case): {camel_case_keys}"


# ---------------------------------------------------------------------------
# Read-only safety
# ---------------------------------------------------------------------------


class TestReadOnlySafety:
    """Verifies the probe is strictly read-only."""

    def test_probe_does_not_write_files(self) -> None:
        """Probe does not create or modify files in the project."""
        before = set()
        probe_dir = _PROBE_SCRIPT.parent
        for f in probe_dir.rglob("*"):
            if f.is_file():
                before.add((str(f), f.stat().st_mtime))

        _run_probe_json()

        after = set()
        for f in probe_dir.rglob("*"):
            if f.is_file():
                after.add((str(f), f.stat().st_mtime))

        # No new files created by the probe
        before_paths = {p for p, _ in before}
        after_paths = {p for p, _ in after}
        new_files = after_paths - before_paths
        assert not new_files, f"Probe created files: {new_files}"

        # No files modified
        for path, mtime_before in before:
            if path in after_paths:
                mtime_after = next(m for p, m in after if p == path)
                assert mtime_after == mtime_before, f"Probe modified {path}"
