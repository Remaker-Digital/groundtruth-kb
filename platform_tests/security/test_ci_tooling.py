"""Tests for CI/CD tooling improvements (S161 Group 3).

Validates SPEC-1695 (import-cycle detection), SPEC-1696 (pip-audit),
SPEC-1697 (Ruff blocking), SPEC-1698 (xdist), SPEC-1699 (radon/vulture).

These tests validate CI pipeline configuration files (.github/workflows/)
which are only present in the git working tree, not in Docker containers.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pathlib
import re

import pytest

# Skip entire module when running inside the test host container
# (no .github/workflows/ directory available)
pytestmark = pytest.mark.skipif(
    not pathlib.Path(".github/workflows").exists(),
    reason="CI workflow files not available (container environment)",
)


def _read_workflow(name: str) -> str:
    import pathlib

    p = pathlib.Path(".github/workflows") / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _read_pyproject() -> str:
    import pathlib

    return pathlib.Path("pyproject.toml").read_text(encoding="utf-8")


def _read_requirements_test() -> str:
    import pathlib

    return pathlib.Path("requirements-test.txt").read_text(encoding="utf-8")


class TestImportCycleDetection:
    """SPEC-1695: lint.yml MUST detect circular imports in src/."""

    def test_lint_workflow_has_import_cycle_step(self):
        yml = _read_workflow("lint.yml")
        has_cycle = "import-cycle" in yml or "import_cycle" in yml or "circular" in yml.lower()
        assert has_cycle, "lint.yml must have an import-cycle detection job or step"

    def test_import_cycle_step_scans_src(self):
        yml = _read_workflow("lint.yml")
        assert "src/" in yml or "src" in yml

    def test_import_cycle_is_blocking(self):
        yml = _read_workflow("lint.yml")
        # Extract import-cycles job section only
        assert "import-cycles:" in yml
        section = yml.split("import-cycles:")[1]
        for sep in ["pip-audit:", "complexity:", "syntax:"]:
            if sep in section:
                section = section[: section.index(sep)]
        assert "continue-on-error: true" not in section


class TestPipAuditScanning:
    """SPEC-1696: CI MUST run pip-audit."""

    def test_lint_workflow_has_pip_audit(self):
        yml = _read_workflow("lint.yml")
        assert "pip-audit" in yml, "lint.yml must include pip-audit step"

    def test_pip_audit_is_blocking(self):
        yml = _read_workflow("lint.yml")
        # Extract pip-audit job section only
        assert "pip-audit:" in yml
        section = yml.split("pip-audit:")[1]
        for sep in ["complexity:", "syntax:", "import-cycles:"]:
            if sep in section:
                section = section[: section.index(sep)]
        assert "continue-on-error: true" not in section

    def test_pip_audit_installed(self):
        yml = _read_workflow("lint.yml")
        assert "pip-audit" in yml


class TestRuffBlocking:
    """SPEC-1697: lint.yml MUST fail on E+F categories."""

    def test_ruff_check_exists(self):
        yml = _read_workflow("lint.yml")
        assert "ruff check" in yml

    def test_ruff_select_includes_e_f(self):
        toml = _read_pyproject()
        match = re.search(r"select\s*=\s*\[([^\]]+)\]", toml)
        assert match
        selected = match.group(1)
        assert '"E"' in selected
        assert '"F"' in selected

    def test_ruff_has_blocking_step(self):
        yml = _read_workflow("lint.yml")
        lines = yml.split("\n")
        found_blocking = False
        i = 0
        while i < len(lines):
            if "ruff check" in lines[i]:
                is_blocking = True
                for j in range(max(0, i - 3), min(len(lines), i + 3)):
                    if "continue-on-error: true" in lines[j]:
                        is_blocking = False
                        break
                if is_blocking:
                    found_blocking = True
                    break
            i += 1
        assert found_blocking, "Must have at least one blocking ruff check step"


class TestXdistParallel:
    """SPEC-1698: python-tests.yml SHOULD use -n auto."""

    def test_xdist_in_test_dependencies(self):
        deps = _read_requirements_test()
        assert "pytest-xdist" in deps

    def test_xdist_used_in_ci(self):
        yml = _read_workflow("python-tests.yml")
        assert "-n " in yml or "--numprocesses" in yml, "python-tests.yml should use pytest-xdist -n flag"


class TestComplexityAnalysis:
    """SPEC-1699: lint.yml SHOULD include radon and/or vulture."""

    def test_lint_has_complexity_or_deadcode_step(self):
        yml = _read_workflow("lint.yml")
        assert "radon" in yml or "vulture" in yml, "lint.yml should include radon or vulture analysis"

    def test_complexity_step_references_src(self):
        yml = _read_workflow("lint.yml")
        if "radon" in yml or "vulture" in yml:
            assert "src/" in yml

    def test_complexity_analysis_installed(self):
        yml = _read_workflow("lint.yml")
        has_install = ("radon" in yml and "pip install" in yml) or ("vulture" in yml and "pip install" in yml)
        assert has_install, "Complexity tools must be installed"
