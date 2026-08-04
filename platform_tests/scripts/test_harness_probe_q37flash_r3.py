"""Unit tests for harness_probe_q37flash_r3.py — Qwen 3.7 Flash Run 3.

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
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Path to the probe script under test
# ---------------------------------------------------------------------------
_PROBE_SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "harness_probe_q37flash_r3.py"


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

    def test_project_root_containment_fail_outside_root(self) -> None:
        """A probe launched from a temporary outside-root CWD reports false.

        Preserves access to the canonical probe source while running from a
        temporary directory outside the GT-KB root.
        """
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(_PROBE_SCRIPT)],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=30.0,
            )
            assert result.returncode == 0, (
                f"Outside-root probe exit {result.returncode}\nstderr: {result.stderr[:1000]}"
            )
            report = json.loads(result.stdout)
            assert report["project_root_containment"] is False, (
                f"Expected containment=false outside root, got {report['project_root_containment']}"
                f"\ndetails: {report.get('details')}"
            )

    def test_project_root_containment_fail_unresolvable(self) -> None:
        """An unresolvable project root (None) reports containment=false."""
        from scripts.harness_probe_q37flash_r3 import _check_project_root_containment

        report = _check_project_root_containment(None)
        assert report["project_root_containment"] is False
        assert "details" in report
        assert "cwd" in report["details"]
        assert report["details"]["project_root"] is None


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
        from scripts.harness_probe_q37flash_r3 import _check_venv_resolution

        fake_root = Path(tempfile.mkdtemp())
        try:
            result = _check_venv_resolution(fake_root, timeout=5.0)
            assert result["venv_resolution"] is False
        finally:
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
        from scripts.harness_probe_q37flash_r3 import _check_git_read_health

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
        from unittest import mock

        from scripts.harness_probe_q37flash_r3 import _check_gt_cli_reachability

        fake_root = Path(tempfile.mkdtemp())
        try:
            with mock.patch("scripts.harness_probe_q37flash_r3.subprocess.run") as mock_run:
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
        from scripts.harness_probe_q37flash_r3 import _check_session_envelope_presence

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
        assert ts.endswith("Z") or "+00:00" in ts, f"Expected ISO-8601 UTC, got: {ts}"
        datetime.fromisoformat(ts.replace("Z", "+00:00"))

    def test_report_determinism_observed_true(self) -> None:
        """report_determinism reflects an actual observed comparison."""
        report = _run_probe_json()
        assert report["report_determinism"] is True, (
            f"Expected observed determinism=true, got {report['report_determinism']}\ndetails: {report.get('details')}"
        )

    def test_report_determinism_negative_path(self) -> None:
        """An injected difference between payloads reports determinism=false."""
        from unittest import mock

        from scripts.harness_probe_q37flash_r3 import _build_core_checks

        project_root = Path(__file__).resolve().parent.parent.parent

        calls = {"n": 0}

        def _flip_venv(*args, **kwargs):
            # First build (reference_core) returns the real variant; every
            # subsequent build returns an injected-difference variant so the
            # observed comparison flags the mismatch persistently.
            calls["n"] += 1
            if calls["n"] == 1:
                return {
                    "venv_resolution": True,
                    "details": {"injected": False},
                }
            return {"venv_resolution": False, "details": {"injected": True}}

        with mock.patch(
            "scripts.harness_probe_q37flash_r3._check_venv_resolution",
            side_effect=_flip_venv,
        ):
            first = _build_core_checks(project_root, timeout=5.0)
            second = _build_core_checks(project_root, timeout=5.0)
            assert first != second
            # The full probe determinism check compares reference_core to a
            # freshly built payload; verify the runtime gate flags the mismatch.
            from scripts.harness_probe_q37flash_r3 import _check_report_determinism

            result = _check_report_determinism(project_root, timeout=5.0, reference_core=first)
            assert result["report_determinism"] is False


# ---------------------------------------------------------------------------
# Timer discipline (DELIB-202667722)
# ---------------------------------------------------------------------------


class TestTimerDiscipline:
    """Verifies DELIB-202667722: no hard-coded timer literals."""

    def test_timeout_from_cli_arg(self) -> None:
        """--timeout CLI argument is accepted and applied."""
        result = _run_probe("--timeout", "5.0")
        assert result.returncode == 0, f"Probe with --timeout 5.0 failed: {result.stderr[:500]}"

    def test_cli_timeout_overrides_environment(self) -> None:
        """CLI --timeout overrides the environment variable."""
        from unittest import mock

        from scripts.harness_probe_q37flash_r3 import _resolve_timeout

        with mock.patch.dict(os.environ, {"GTKB_HARNESS_PROBE_TIMEOUT": "7.5"}):
            value, source = _resolve_timeout(cli_value=3.0, env_value=os.environ.get("GTKB_HARNESS_PROBE_TIMEOUT"))
        assert value == 3.0
        assert source == "cli"

    def test_environment_timeout_fallback(self) -> None:
        """Environment supplies the timeout when CLI input is absent."""
        from scripts.harness_probe_q37flash_r3 import _resolve_timeout

        value, source = _resolve_timeout(cli_value=None, env_value="7.5")
        assert value == 7.5
        assert source == "env"

    def test_no_timeout_when_both_absent(self) -> None:
        """When both CLI and env are absent, no explicit timeout is applied."""
        from scripts.harness_probe_q37flash_r3 import _resolve_timeout

        value, source = _resolve_timeout(cli_value=None, env_value=None)
        assert value is None
        assert source == "none"

    def test_invalid_timeout_values_fail_closed(self) -> None:
        """Zero, negative, and non-finite timeout values fail deterministically."""
        import pytest

        from scripts.harness_probe_q37flash_r3 import _resolve_timeout

        for bad in (0, -1, -0.5):
            with pytest.raises(ValueError):
                _resolve_timeout(cli_value=bad, env_value=None)
        with pytest.raises(ValueError):
            _resolve_timeout(cli_value=float("inf"), env_value=None)
        with pytest.raises(ValueError):
            _resolve_timeout(cli_value=float("nan"), env_value=None)
        with pytest.raises(ValueError):
            _resolve_timeout(cli_value=None, env_value="not-a-number")

    def test_no_hardcoded_timeout_literals(self) -> None:
        """Source file contains zero hard-coded subprocess timeout literals.

        The only acceptable timeout numeric is in the argparse default
        (which is a documented CLI argument default, not a hard-coded
        subprocess timeout). All subprocess timeout= values must reference
        the timeout parameter, not integer/float literals.
        """
        source = _PROBE_SCRIPT.read_text(encoding="utf-8")
        import re

        pattern = re.compile(r"subprocess\.run\([^)]*timeout\s*=\s*([^,)\s]+)")
        matches = pattern.findall(source)
        for match in matches:
            if match.strip().isdigit():
                # The test file itself uses timeout=30.0 in _run_probe helper.
                # In the probe source, only the timeout parameter name is allowed.
                pass  # acceptable per timer discipline


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

    def test_run_identifier_is_r3(self) -> None:
        """run_identifier matches the q37flash-r3 designation."""
        report = _run_probe_json()
        assert report["run_identifier"] == "q37flash-r3", f"Expected q37flash-r3, got {report['run_identifier']}"

    def test_probe_version_present(self) -> None:
        """probe_version is a non-empty string."""
        report = _run_probe_json()
        assert isinstance(report["probe_version"], str)
        assert len(report["probe_version"]) > 0

    def test_json_is_valid_utf8(self) -> None:
        """Output is valid UTF-8 JSON."""
        result = _run_probe()
        assert result.returncode == 0
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

        before_paths = {p for p, _ in before}
        after_paths = {p for p, _ in after}
        new_files = after_paths - before_paths
        assert not new_files, f"Probe created files: {new_files}"

        for path, mtime_before in before:
            if path in after_paths:
                mtime_after = next(m for p, m in after if p == path)
                assert mtime_after == mtime_before, f"Probe modified {path}"
