"""Tests for harness_probe_dsv4pro-r1.py per WI-5808 / DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.

Bridge: gtkb-wi5808-harness-probe-dsv4pro-r1 (GO at 008).
Target: platform_tests/scripts/test_harness_probe_dsv4pro-r1.py.

Each test maps to a specific check in the probe and exercises both
success and failure paths where applicable.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure the scripts dir is importable (hyphenated module; use importlib)
_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import importlib  # noqa: E402

_probe = importlib.import_module("harness_probe_dsv4pro-r1")
check_project_root_containment = _probe.check_project_root_containment
check_venv_resolution = _probe.check_venv_resolution
check_git_read_health = _probe.check_git_read_health
check_gt_cli_reachability = _probe.check_gt_cli_reachability
check_report_determinism = _probe.check_report_determinism
check_session_envelope_presence = _probe.check_session_envelope_presence
run_all_checks = _probe.run_all_checks
_PROBE_PATH = Path(_probe.__file__)


# ---------------------------------------------------------------------------
# Test: project_root_containment
# ---------------------------------------------------------------------------


class TestProjectRootContainment:
    """Tests for check 1: project-root containment."""

    def test_cwd_inside_root(self, tmp_path: Path):
        """CWD inside the project root passes the containment check."""
        root = tmp_path / "gtkb"
        root.mkdir()
        subdir = root / "sub"
        subdir.mkdir()
        with patch("pathlib.Path.cwd", return_value=subdir):
            result = check_project_root_containment(root, expected_root=root)
        assert result["passed"] is True
        assert result["check"] == "project_root_containment"

    def test_cwd_equals_root(self, tmp_path: Path):
        """CWD exactly equal to the project root passes."""
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            result = check_project_root_containment(tmp_path, expected_root=tmp_path)
        assert result["passed"] is True

    def test_cwd_outside_root(self, tmp_path: Path):
        """CWD outside the project root fails."""
        root = tmp_path / "gtkb"
        root.mkdir()
        outside = tmp_path / "other"
        outside.mkdir()
        with patch("pathlib.Path.cwd", return_value=outside):
            result = check_project_root_containment(root, expected_root=root)
        assert result["passed"] is False
        assert "outside" in result["detail"].lower()

    def test_arbitrary_root_cannot_self_certify(self, tmp_path: Path):
        """An arbitrary supplied root fails even when cwd is inside it."""
        canonical = tmp_path / "gtkb"
        supplied = tmp_path / "other"
        canonical.mkdir()
        supplied.mkdir()
        with patch("pathlib.Path.cwd", return_value=supplied):
            result = check_project_root_containment(supplied, expected_root=canonical)
        assert result["passed"] is False
        assert result["project_root"] != result["expected_project_root"]


# ---------------------------------------------------------------------------
# Test: project_venv_resolution
# ---------------------------------------------------------------------------


class TestVenvResolution:
    """Tests for check 2: venv resolution and groundtruth_kb import."""

    def test_venv_missing(self, tmp_path: Path):
        """Missing venv python.exe produces a failing result."""
        root = tmp_path
        result = check_venv_resolution(root, timeout=30)
        assert result["passed"] is False
        assert result["venv_exists"] is False

    def test_venv_exists_import_fails(self, tmp_path: Path):
        """Existing venv that cannot import groundtruth_kb fails."""
        root = tmp_path / "gtkb"
        root.mkdir()
        venv_dir = root / "groundtruth-kb" / ".venv" / "Scripts"
        venv_dir.mkdir(parents=True)
        python_exe = venv_dir / "python.exe"
        python_exe.write_text("fake python")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stderr="ImportError")
            result = check_venv_resolution(root, timeout=30)
        assert result["passed"] is False
        assert result["venv_exists"] is True
        assert result["import_groundtruth_kb"] is False

    def test_venv_exists_import_ok(self, tmp_path: Path):
        """Existing venv with successful import passes."""
        root = tmp_path / "gtkb"
        root.mkdir()
        venv_dir = root / "groundtruth-kb" / ".venv" / "Scripts"
        venv_dir.mkdir(parents=True)
        python_exe = venv_dir / "python.exe"
        python_exe.write_text("fake python")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result = check_venv_resolution(root, timeout=30)
        assert result["passed"] is True
        assert result["import_groundtruth_kb"] is True


# ---------------------------------------------------------------------------
# Test: git_read_health
# ---------------------------------------------------------------------------


class TestGitReadHealth:
    """Tests for check 3: git read health."""

    def test_clean_repo(self, tmp_path: Path):
        """A clean git repo returns HEAD sha and dirty_count=0."""
        root = tmp_path / "repo"
        root.mkdir()
        subprocess.run(["git", "init", str(root)], capture_output=True, check=True)
        subprocess.run(
            ["git", "-C", str(root), "commit", "--allow-empty", "-m", "init"],
            capture_output=True,
            check=True,
        )
        head = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        result = check_git_read_health(root, timeout=30)
        assert result["passed"] is True
        assert result["head_sha"] == head
        assert result["dirty_count"] == 0

    def test_dirty_repo(self, tmp_path: Path):
        """A repo with uncommitted changes reports dirty_count > 0."""
        root = tmp_path / "repo"
        root.mkdir()
        subprocess.run(["git", "init", str(root)], capture_output=True, check=True)
        subprocess.run(
            ["git", "-C", str(root), "commit", "--allow-empty", "-m", "init"],
            capture_output=True,
            check=True,
        )
        (root / "new_file.txt").write_text("dirty")
        result = check_git_read_health(root, timeout=30)
        assert result["passed"] is True
        assert result["dirty_count"] == 1

    def test_not_a_repo(self, tmp_path: Path):
        """A non-git directory fails with errors."""
        with patch("subprocess.run") as mock_run:
            # Both git calls fail
            mock_run.side_effect = [
                MagicMock(returncode=128, stdout="", stderr="fatal: not a git repository"),
                MagicMock(returncode=128, stdout="", stderr="fatal: not a git repository"),
            ]
            result = check_git_read_health(tmp_path, timeout=30)
        assert result["passed"] is False
        assert result["head_sha"] is None


# ---------------------------------------------------------------------------
# Test: gt_cli_reachability
# ---------------------------------------------------------------------------


class TestGtCliReachability:
    """Tests for check 4: gt CLI reachability."""

    def test_gt_help_exit_zero(self, tmp_path: Path):
        """gt --help returns exit 0."""
        gt_exe = tmp_path / "groundtruth-kb" / ".venv" / "Scripts" / "gt.exe"
        gt_exe.parent.mkdir(parents=True)
        gt_exe.write_text("fake")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="help text", stderr="")
            result = check_gt_cli_reachability(tmp_path, timeout=30)
        assert result["passed"] is True
        assert result["exit_code"] == 0
        assert mock_run.call_args[0][0] == [str(gt_exe), "--help"]

    def test_gt_help_exit_nonzero(self, tmp_path: Path):
        """gt --help returning non-zero exit code fails."""
        gt_exe = tmp_path / "groundtruth-kb" / ".venv" / "Scripts" / "gt.exe"
        gt_exe.parent.mkdir(parents=True)
        gt_exe.write_text("fake")
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
            result = check_gt_cli_reachability(tmp_path, timeout=30)
        assert result["passed"] is False
        assert result["exit_code"] == 1

    def test_gt_not_found(self, tmp_path: Path):
        """gt not found raises OSError, captured as failure."""
        gt_exe = tmp_path / "groundtruth-kb" / ".venv" / "Scripts" / "gt.exe"
        gt_exe.parent.mkdir(parents=True)
        gt_exe.write_text("fake")
        with patch("subprocess.run", side_effect=OSError("not found")):
            result = check_gt_cli_reachability(tmp_path, timeout=30)
        assert result["passed"] is False
        assert "not found" in result["detail"]

    def test_canonical_gt_executable_missing(self, tmp_path: Path):
        """The probe does not fall back to PATH when canonical gt.exe is absent."""
        with patch("subprocess.run") as mock_run:
            result = check_gt_cli_reachability(tmp_path, timeout=30)
        assert result["passed"] is False
        assert "not found" in result["detail"]
        mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# Test: session_envelope_presence
# ---------------------------------------------------------------------------


class TestSessionEnvelopePresence:
    """Tests for check 5: session-envelope surface presence."""

    def test_envelope_found(self, tmp_path: Path):
        """Envelope file exists -> passes."""
        session_dir = tmp_path / "harness-state" / "codex" / "session-envelopes"
        session_dir.mkdir(parents=True)
        (session_dir / "fixture-session.json").write_text("{}")
        result = check_session_envelope_presence(tmp_path)
        assert result["passed"] is True
        assert len(result["found"]) > 0

    def test_envelope_absent(self, tmp_path: Path):
        """No envelope file -> fails."""
        result = check_session_envelope_presence(tmp_path)
        assert result["passed"] is False
        assert len(result["found"]) == 0


# ---------------------------------------------------------------------------
# Test: run_all_checks integration
# ---------------------------------------------------------------------------


class TestRunAllChecks:
    """Integration tests for run_all_checks."""

    def test_output_structure(self, tmp_path: Path):
        """Report has expected top-level keys and six results."""
        with patch("subprocess.run") as mock_run:
            # run_all_checks calls: git rev-parse, git status, gt --help
            # plus potentially venv python subprocess
            mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
            report = run_all_checks(tmp_path, timeout=30)
        assert report["probe"] == "harness_probe_dsv4pro-r1"
        assert "generated_at" in report
        assert "project_root" in report
        assert "overall_passed" in report
        assert isinstance(report["overall_passed"], bool)
        assert len(report["results"]) == 6
        checks = [r["check"] for r in report["results"]]
        assert checks == [
            "project_root_containment",
            "project_venv_resolution",
            "git_read_health",
            "gt_cli_reachability",
            "session_envelope_presence",
            "report_determinism",
        ]
        for r in report["results"]:
            assert "passed" in r
            assert "detail" in r


# ---------------------------------------------------------------------------
# Test: report determinism
# ---------------------------------------------------------------------------


class TestReportDeterminism:
    """Tests for check 6: report determinism (byte-identical JSON
    apart from generated_at field)."""

    def test_deterministic_output_excluding_generated_at(self, tmp_path: Path):
        """Two runs produce identical JSON after removing generated_at."""
        root = tmp_path / "gtkb"
        root.mkdir()
        venv_dir = root / "groundtruth-kb" / ".venv" / "Scripts"
        venv_dir.mkdir(parents=True)
        (venv_dir / "python.exe").write_text("fake")

        with patch("pathlib.Path.cwd", return_value=root), patch("subprocess.run") as mock_run:

            def fake_run(args, **kwargs):
                if "rev-parse" in str(args):
                    return MagicMock(returncode=0, stdout="abc1234\n", stderr="")
                elif "status" in str(args) and "--porcelain" in str(args) or "import groundtruth_kb" in str(args):
                    return MagicMock(returncode=0, stdout="", stderr="")
                elif "help" in str(args):
                    return MagicMock(returncode=0, stdout="help", stderr="")
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = fake_run
            report1 = run_all_checks(root, timeout=30)
            report2 = run_all_checks(root, timeout=30)

        r1 = {k: v for k, v in report1.items() if k != "generated_at"}
        r2 = {k: v for k, v in report2.items() if k != "generated_at"}
        bytes1 = _probe.json.dumps(r1, sort_keys=True, separators=(",", ":")).encode()
        bytes2 = _probe.json.dumps(r2, sort_keys=True, separators=(",", ":")).encode()
        assert bytes1 == bytes2

    def test_internal_determinism_check_detects_changed_snapshot(self, tmp_path: Path):
        """The sixth check compares serialized snapshot bytes, not dict identity."""
        first = [{"check": "one", "passed": True, "detail": "stable"}]
        second = [{"check": "one", "passed": False, "detail": "changed"}]
        result = check_report_determinism(tmp_path, first, second)
        assert result["passed"] is False

    def test_generated_at_differs(self, tmp_path: Path):
        """generated_at field exists and is an ISO timestamp."""
        root = tmp_path / "gtkb"
        root.mkdir()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="ok\n", stderr="")
            report = run_all_checks(root, timeout=30)
        assert "generated_at" in report
        assert "T" in report["generated_at"]


# ---------------------------------------------------------------------------
# Test: CLI interface
# ---------------------------------------------------------------------------


class TestCliInterface:
    """Tests for the argparse CLI (--timeout, --project-root)."""

    def test_timeout_flag_parsing(self):
        """--timeout sets the timeout value."""
        mod = importlib.import_module("harness_probe_dsv4pro-r1")  # noqa: E402

        with (
            patch("sys.argv", ["probe", "--timeout", "15.5"]),
            patch.object(mod, "run_all_checks", return_value={"probe": "test"}) as mock_run,
        ):
            mod.main()
            call_args = mock_run.call_args
            assert call_args[0][1] == 15.5

    def test_project_root_flag(self, tmp_path: Path):
        """--project-root overrides auto-detection."""
        mod = importlib.import_module("harness_probe_dsv4pro-r1")  # noqa: E402

        with (
            patch("sys.argv", ["probe", "--timeout", "60", "--project-root", str(tmp_path)]),
            patch.object(mod, "run_all_checks", return_value={"probe": "test"}) as mock_run,
        ):
            mod.main()
            call_args = mock_run.call_args
            assert call_args[0][0] == tmp_path

    def test_timeout_is_required(self):
        """No hard-coded fallback is used when the caller omits --timeout."""
        mod = importlib.import_module("harness_probe_dsv4pro-r1")  # noqa: E402
        with (
            patch("sys.argv", ["probe"]),
            patch.object(mod, "run_all_checks") as mock_run,
            pytest.raises(SystemExit),
        ):
            mod.main()
        mock_run.assert_not_called()

    def test_timeout_must_be_positive(self):
        """Zero and negative observation windows fail before subprocess work."""
        mod = importlib.import_module("harness_probe_dsv4pro-r1")  # noqa: E402
        with (
            patch("sys.argv", ["probe", "--timeout", "0"]),
            patch.object(mod, "run_all_checks") as mock_run,
            pytest.raises(SystemExit),
        ):
            mod.main()
        mock_run.assert_not_called()

    def test_no_hardcoded_subprocess_timeout_or_cli_default(self):
        """All subprocess timeouts flow from the required caller value."""
        tree = ast.parse(_PROBE_PATH.read_text(encoding="utf-8"))
        timeout_argument_seen = False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Attribute) and node.func.attr == "run":
                timeout_keywords = [kw for kw in node.keywords if kw.arg == "timeout"]
                assert len(timeout_keywords) == 1
                assert not isinstance(timeout_keywords[0].value, ast.Constant)
            if isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument":
                if any(isinstance(arg, ast.Constant) and arg.value == "--timeout" for arg in node.args):
                    timeout_argument_seen = True
                    keywords = {kw.arg: kw.value for kw in node.keywords}
                    assert "default" not in keywords
                    assert isinstance(keywords.get("required"), ast.Constant)
                    assert keywords["required"].value is True
        assert timeout_argument_seen is True
