# tests/test_host/test_build_contract.py — AI Software Quality Prevention Tests
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
#
# 7 test classes that catch the 7 systematic failure modes identified in S209
# for AI-generated software. Each class validates cross-layer consistency
# between .dockerignore, Dockerfile*, suites.py, CI workflow, and test
# expectations — without requiring a running container.
#
# Run: pytest tests/test_host/test_build_contract.py -v

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Project root — two levels up from this test file (tests/test_host/)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Lazy-loaded file contents (parsed once, reused across all classes)
# ---------------------------------------------------------------------------


def _read_lines(relpath: str) -> list[str]:
    """Read a project file and return its lines."""
    path = PROJECT_ROOT / relpath
    assert path.exists(), f"Required file missing: {relpath}"
    return path.read_text(encoding="utf-8").splitlines()


def _read_text(relpath: str) -> str:
    """Read a project file and return its full text."""
    path = PROJECT_ROOT / relpath
    assert path.exists(), f"Required file missing: {relpath}"
    return path.read_text(encoding="utf-8")


# Pre-parse all files used by multiple classes
_dockerfile_lines: list[str] | None = None
_dockerfile_test_lines: list[str] | None = None
_dockerignore_lines: list[str] | None = None
_workflow_text: str | None = None
_req_test_text: str | None = None


def _get_dockerfile() -> list[str]:
    global _dockerfile_lines
    if _dockerfile_lines is None:
        _dockerfile_lines = _read_lines("Dockerfile")
    return _dockerfile_lines


def _get_dockerfile_test() -> list[str]:
    global _dockerfile_test_lines
    if _dockerfile_test_lines is None:
        _dockerfile_test_lines = _read_lines("Dockerfile.test")
    return _dockerfile_test_lines


def _get_dockerignore() -> list[str]:
    global _dockerignore_lines
    if _dockerignore_lines is None:
        _dockerignore_lines = _read_lines(".dockerignore")
    return _dockerignore_lines


def _get_workflow() -> str:
    global _workflow_text
    if _workflow_text is None:
        _workflow_text = _read_text(".github/workflows/build-test-host.yml")
    return _workflow_text


def _get_req_test() -> str:
    global _req_test_text
    if _req_test_text is None:
        _req_test_text = _read_text("requirements-test.txt")
    return _req_test_text


def _active_dockerignore_patterns() -> set[str]:
    """Return the set of uncommented, non-empty lines from .dockerignore."""
    return {
        line.strip()
        for line in _get_dockerignore()
        if line.strip() and not line.strip().startswith("#")
    }


def _extract_copy_sources(lines: list[str]) -> list[str]:
    """Extract COPY source paths from Dockerfile lines (single-source COPYs)."""
    sources: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("COPY ") and not stripped.startswith("COPY --from"):
            # COPY src/ ./src/  OR  COPY a b c ./dest/
            parts = stripped.split()
            # Last element is destination; everything between COPY and dest is source
            sources.extend(parts[1:-1])
    return sources


def _extract_from_image(lines: list[str]) -> str | None:
    """Extract the FROM image string from Dockerfile lines."""
    for line in lines:
        if line.strip().startswith("FROM "):
            return line.strip().split()[1]
    return None


# ---------------------------------------------------------------------------
# Import SuiteConfig from test_host for contract validation
# ---------------------------------------------------------------------------

# Add project root to path so we can import test_host.suites
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from test_host.suites import SUITE_CONFIGS  # noqa: E402


# ===========================================================================
# 1. TestConfigurationDriftAcrossLayers
# ===========================================================================

class TestConfigurationDriftAcrossLayers:
    """Failure mode: .dockerignore, Dockerfiles, suite configs, and CI workflow
    form an implicit contract that drifts silently between sessions.

    Metric: inconsistencies / cross_layer_checks — target: 0/12
    """

    @pytest.mark.parametrize("path", [
        "tests/",
        "src/",
        "config/",
        "pyproject.toml",
        "CLAUDE.md",
    ])
    def test_dockerignore_does_not_exclude_test_host_paths(self, path: str):
        """Dockerfile.test needs these paths — .dockerignore must not exclude them."""
        patterns = _active_dockerignore_patterns()
        # Check both exact match and trailing-slash variant
        assert path not in patterns, (
            f".dockerignore excludes '{path}' which is required by Dockerfile.test"
        )
        bare = path.rstrip("/")
        assert bare not in patterns, (
            f".dockerignore excludes '{bare}' which is required by Dockerfile.test"
        )

    def test_dockerfile_test_copies_playwright_deps_when_required(self):
        """Suites with requires_playwright=True need Playwright in the container."""
        playwright_suites = [
            s for s in SUITE_CONFIGS.values()
            if s.requires_playwright and not s.is_composite
        ]
        assert playwright_suites, "Expected at least one Playwright suite"
        text = "\n".join(_get_dockerfile_test())
        assert "playwright install" in text.lower(), (
            "Dockerfile.test must install Playwright for playwright-requiring suites"
        )

    def test_dockerfile_test_copies_locust_deps_when_required(self):
        """Suites with requires_locust=True need Locust in the requirements."""
        locust_suites = [
            s for s in SUITE_CONFIGS.values()
            if s.requires_locust and not s.is_composite
        ]
        assert locust_suites, "Expected at least one Locust suite"
        req_text = _get_req_test()
        assert "locust" in req_text.lower(), (
            "requirements-test.txt must include locust for locust-requiring suites"
        )

    def test_both_dockerfiles_use_same_base_image(self):
        """Both Dockerfiles must use the same Python base image for consistency."""
        prod_base = _extract_from_image(_get_dockerfile())
        test_base = _extract_from_image(_get_dockerfile_test())
        assert prod_base is not None, "Dockerfile missing FROM"
        assert test_base is not None, "Dockerfile.test missing FROM"
        assert prod_base == test_base, (
            f"Base image mismatch: Dockerfile uses {prod_base}, "
            f"Dockerfile.test uses {test_base}"
        )

    def test_both_dockerfiles_copy_src_and_config(self):
        """Both Dockerfiles must COPY src/ and config/ for import consistency."""
        for label, lines in [
            ("Dockerfile", _get_dockerfile()),
            ("Dockerfile.test", _get_dockerfile_test()),
        ]:
            sources = _extract_copy_sources(lines)
            assert any(s.startswith("src/") or s == "src/" for s in sources), (
                f"{label} must COPY src/"
            )
            assert any(s.startswith("config/") or s == "config/" for s in sources), (
                f"{label} must COPY config/"
            )

    def test_github_workflow_references_dockerfile_test(self):
        """CI workflow must build with Dockerfile.test, not Dockerfile."""
        workflow = _get_workflow()
        assert "Dockerfile.test" in workflow, (
            "build-test-host.yml must reference Dockerfile.test"
        )
        # Should NOT build with the production Dockerfile
        assert "docker build -f Dockerfile.test" in workflow or \
               "-f Dockerfile.test" in workflow, (
            "Workflow must use '-f Dockerfile.test' flag"
        )


# ===========================================================================
# 2. TestEnvironmentAssumptionMismatch
# ===========================================================================

class TestEnvironmentAssumptionMismatch:
    """Failure mode: Code works locally but fails in container due to missing files.

    Metric: missing_copies / required_copies — target: 0/5
    """

    def test_dockerfile_test_copies_all_suite_test_dirs(self):
        """Every suite test directory referenced in SUITE_CONFIGS must be COPYed."""
        test_sources = _extract_copy_sources(_get_dockerfile_test())
        for name, cfg in SUITE_CONFIGS.items():
            if cfg.is_composite:
                continue
            for arg in cfg.pytest_args:
                # Test paths are positional args that look like directory paths
                if arg.startswith("tests/") and not arg.startswith("--"):
                    # The COPY line needs to cover this path.
                    # Dockerfile.test copies "tests/" which covers all subdirs.
                    found = any(
                        s.rstrip("/") == "tests" or s == "tests/" or
                        arg.startswith(s.rstrip("/"))
                        for s in test_sources
                    )
                    assert found, (
                        f"Suite '{name}' references {arg} but Dockerfile.test "
                        f"does not COPY a parent directory"
                    )

    def test_dockerfile_test_copies_essential_project_files(self):
        """src/, config/, and pyproject.toml must all be present in test image."""
        sources = _extract_copy_sources(_get_dockerfile_test())
        for required in ["src/", "config/", "pyproject.toml"]:
            found = any(s.rstrip("/") == required.rstrip("/") for s in sources)
            assert found, (
                f"Dockerfile.test must COPY {required}"
            )

    def test_requirements_test_includes_base(self):
        """requirements-test.txt must chain to production requirements.txt."""
        req_text = _get_req_test()
        assert "-r requirements.txt" in req_text, (
            "requirements-test.txt must include '-r requirements.txt' "
            "to chain production dependencies"
        )


# ===========================================================================
# 3. TestDockerfileCacheInvalidation
# ===========================================================================

class TestDockerfileCacheInvalidation:
    """Failure mode: Dockerfile changes invalidate Docker layer cache,
    causing slow or failing builds.

    Metric: ordering_violations / ordering_checks — target: 0/4
    """

    @pytest.mark.parametrize("label,lines_fn", [
        ("Dockerfile", _get_dockerfile),
        ("Dockerfile.test", _get_dockerfile_test),
    ])
    def test_requirements_copied_before_src(self, label: str, lines_fn):
        """requirements*.txt COPY must appear before src/ COPY for layer caching."""
        lines = lines_fn()
        req_line = None
        src_line = None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("COPY") and "requirements" in stripped:
                if req_line is None:
                    req_line = i
            if stripped.startswith("COPY") and "src/" in stripped:
                if src_line is None:
                    src_line = i
        assert req_line is not None, f"{label}: no COPY requirements* found"
        assert src_line is not None, f"{label}: no COPY src/ found"
        assert req_line < src_line, (
            f"{label}: COPY requirements (line {req_line + 1}) must appear "
            f"before COPY src/ (line {src_line + 1}) for cache efficiency"
        )

    def test_no_apt_after_pip(self):
        """apt-get install after pip install wastes cache and bloats layers."""
        for label, lines_fn in [
            ("Dockerfile", _get_dockerfile),
            ("Dockerfile.test", _get_dockerfile_test),
        ]:
            lines = lines_fn()
            last_pip_line = -1
            for i, line in enumerate(lines):
                if "pip install" in line:
                    last_pip_line = i
                if "apt-get install" in line and last_pip_line >= 0:
                    # Exception: Dockerfile.test installs Node.js after system deps
                    # but before pip. Check only if apt-get is AFTER pip.
                    if i > last_pip_line:
                        pytest.fail(
                            f"{label}: apt-get install at line {i + 1} appears "
                            f"after pip install at line {last_pip_line + 1}"
                        )

    def test_pip_uses_no_cache_dir(self):
        """All pip install commands must use --no-cache-dir."""
        for label, lines_fn in [
            ("Dockerfile", _get_dockerfile),
            ("Dockerfile.test", _get_dockerfile_test),
        ]:
            lines = lines_fn()
            for i, line in enumerate(lines):
                if "pip install" in line and "upgrade pip" not in line:
                    assert "--no-cache-dir" in line, (
                        f"{label} line {i + 1}: pip install without --no-cache-dir"
                    )


# ===========================================================================
# 4. TestStaleInterfaceContracts
# ===========================================================================

class TestStaleInterfaceContracts:
    """Failure mode: Suite configs reference paths or files that no longer exist.

    Metric: stale_paths / total_paths — target: 0
    """

    def test_suite_test_directories_exist(self):
        """Every test directory in SUITE_CONFIGS must exist on the filesystem."""
        missing = []
        for name, cfg in SUITE_CONFIGS.items():
            if cfg.is_composite:
                continue
            for arg in cfg.pytest_args:
                if arg.startswith("tests/") and not arg.startswith("--"):
                    full_path = PROJECT_ROOT / arg.rstrip("/")
                    if not full_path.exists():
                        missing.append(f"Suite '{name}': {arg}")
        assert not missing, (
            "Suite test directories missing from filesystem:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )

    def test_ignore_targets_exist(self):
        """Every --ignore= target in suite configs must exist on the filesystem."""
        missing = []
        for name, cfg in SUITE_CONFIGS.items():
            if cfg.is_composite:
                continue
            for arg in cfg.pytest_args:
                if arg.startswith("--ignore="):
                    target = arg.split("=", 1)[1]
                    full_path = PROJECT_ROOT / target
                    if not full_path.exists():
                        missing.append(f"Suite '{name}': --ignore={target}")
        assert not missing, (
            "Ignore targets missing from filesystem:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )

    def test_composite_suites_reference_valid_individuals(self):
        """Composite suites must only reference defined individual suites."""
        for name, cfg in SUITE_CONFIGS.items():
            if not cfg.is_composite:
                continue
            for member in cfg.composite_suites:
                assert member in SUITE_CONFIGS, (
                    f"Composite suite '{name}' references undefined "
                    f"suite '{member}'"
                )
                assert not SUITE_CONFIGS[member].is_composite, (
                    f"Composite suite '{name}' references another composite "
                    f"'{member}' (nesting not supported)"
                )


# ===========================================================================
# 5. TestSpeculativeBreadthGuard
# ===========================================================================

class TestSpeculativeBreadthGuard:
    """Failure mode: Suites created speculatively without verification,
    composites missing members.

    Metric: coverage_gaps / total_suites — target: 0
    """

    def test_individual_suites_have_test_paths(self):
        """Every non-composite, non-load suite must have at least one test path."""
        for name, cfg in SUITE_CONFIGS.items():
            if cfg.is_composite or cfg.requires_locust:
                continue  # Load suites use wrapper scripts, not pytest paths
            test_paths = [
                a for a in cfg.pytest_args
                if a.startswith("tests/") and not a.startswith("--")
            ]
            assert test_paths, (
                f"Suite '{name}' has no test paths in pytest_args"
            )

    def test_individual_suites_have_estimated_tests(self):
        """Every non-composite suite must declare estimated_tests > 0."""
        for name, cfg in SUITE_CONFIGS.items():
            if cfg.is_composite:
                continue
            assert cfg.estimated_tests > 0, (
                f"Suite '{name}' has estimated_tests={cfg.estimated_tests} — "
                f"must be positive"
            )

    def test_full_composite_includes_all_individuals(self):
        """The 'full' composite suite must include every individual suite."""
        individual_names = {
            name for name, cfg in SUITE_CONFIGS.items()
            if not cfg.is_composite
        }
        full_suite = SUITE_CONFIGS.get("full")
        assert full_suite is not None, "Missing 'full' composite suite"
        full_members = set(full_suite.composite_suites)
        missing = individual_names - full_members
        assert not missing, (
            f"'full' composite is missing individual suites: {sorted(missing)}"
        )

    def test_ignore_patterns_target_files_not_directories(self):
        """--ignore= patterns should target specific files, not entire directories."""
        for name, cfg in SUITE_CONFIGS.items():
            if cfg.is_composite:
                continue
            for arg in cfg.pytest_args:
                if arg.startswith("--ignore="):
                    target = arg.split("=", 1)[1]
                    # Should end with .py (targeting a file, not a directory)
                    assert target.endswith(".py"), (
                        f"Suite '{name}': --ignore={target} targets a directory "
                        f"(not a .py file). Prefer granular file ignores."
                    )

    def test_composite_estimated_tests_within_tolerance(self):
        """Composite estimated_tests should be within 20% of component sum."""
        for name, cfg in SUITE_CONFIGS.items():
            if not cfg.is_composite:
                continue
            component_sum = sum(
                SUITE_CONFIGS[member].estimated_tests
                for member in cfg.composite_suites
                if member in SUITE_CONFIGS
            )
            if component_sum == 0:
                continue
            ratio = cfg.estimated_tests / component_sum
            assert 0.8 <= ratio <= 1.2, (
                f"Composite '{name}' estimated_tests={cfg.estimated_tests} "
                f"but component sum={component_sum} (ratio={ratio:.2f}, "
                f"expected 0.80–1.20)"
            )


# ===========================================================================
# 6. TestErrorMessageOpacity
# ===========================================================================

class TestErrorMessageOpacity:
    """Failure mode: Diagnostic output truncated or missing, hiding root causes.

    Metric: suites_with_diagnostics / applicable_suites — target: 100%
    """

    def test_runstate_has_diagnostic_fields(self):
        """RunState must have failures list and stdout_tail for debugging."""
        from test_host.cosmos_writer import RunState
        state = RunState(run_id="test", environment="test", suite="test")
        assert hasattr(state, "failures"), "RunState missing 'failures' field"
        assert isinstance(state.failures, list), "RunState.failures must be a list"
        assert hasattr(state, "stdout_tail"), "RunState missing 'stdout_tail' field"

    def test_testresult_has_detail_field(self):
        """TestResult must have a detail field for error messages."""
        from test_host.cosmos_writer import TestResult
        result = TestResult(name="x", category="x", status="fail", detail="msg")
        assert result.detail == "msg", "TestResult.detail not stored"

    def test_suites_have_explicit_timeout(self):
        """Every non-composite suite must have --timeout=N in pytest_args."""
        for name, cfg in SUITE_CONFIGS.items():
            if cfg.is_composite or cfg.requires_locust:
                continue
            timeout_args = [a for a in cfg.pytest_args if a.startswith("--timeout=")]
            assert timeout_args, (
                f"Suite '{name}' missing --timeout=N in pytest_args"
            )

    def test_suites_have_verbosity_flag(self):
        """Every non-composite suite must specify -v or -q for output control."""
        for name, cfg in SUITE_CONFIGS.items():
            if cfg.is_composite or cfg.requires_locust:
                continue
            has_verbosity = any(
                a in ("-v", "-q", "--verbose", "--quiet")
                for a in cfg.pytest_args
            )
            assert has_verbosity, (
                f"Suite '{name}' missing verbosity flag (-v or -q) in pytest_args"
            )


# ===========================================================================
# 7. TestDiagnosticHypothesisStructure
# ===========================================================================

class TestDiagnosticHypothesisStructure:
    """Failure mode: Failures lumped into single bucket, preventing structured
    diagnosis and pattern recognition.

    Metric: diagnostic_fields_present / diagnostic_fields_required — target: 10/10
    """

    def test_testresult_status_values_cover_required_set(self):
        """TestResult status should accept pass, fail, skip, and error."""
        from test_host.cosmos_writer import TestResult
        for status in ("pass", "fail", "skip", "error"):
            r = TestResult(name="x", category="test", status=status)
            assert r.status == status

    def test_runstate_has_separate_counters(self):
        """RunState must have separate failed, errored, and skipped counters."""
        from test_host.cosmos_writer import RunState
        state = RunState(run_id="x", environment="x", suite="x")
        assert hasattr(state, "failed"), "RunState missing 'failed' counter"
        assert hasattr(state, "errored"), "RunState missing 'errored' counter"
        assert hasattr(state, "skipped"), "RunState missing 'skipped' counter"
        # Verify they're numeric and independent
        assert state.failed == 0
        assert state.errored == 0
        assert state.skipped == 0

    def test_ignore_patterns_have_explanatory_comments(self):
        """Every --ignore= pattern in suites.py should have a preceding comment."""
        lines = _read_lines("test_host/suites.py")
        violations = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"--ignore=') or stripped.startswith("'--ignore="):
                # Check if there's a comment on this line or a preceding line
                has_comment = "#" in stripped
                if not has_comment and i > 0:
                    prev = lines[i - 1].strip()
                    has_comment = prev.startswith("#")
                if not has_comment:
                    violations.append(f"Line {i + 1}: {stripped}")
        assert not violations, (
            "--ignore= patterns without explanatory comments:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )

    def test_testresult_has_category_and_latency(self):
        """TestResult must have category and latency_ms for structured diagnosis."""
        from test_host.cosmos_writer import TestResult
        r = TestResult(
            name="test_example",
            category="unit",
            status="pass",
            latency_ms=42.5,
        )
        assert r.category == "unit"
        assert r.latency_ms == 42.5

    def test_runstate_tracks_phase_progress(self):
        """RunState must track phase progress for composite suite diagnosis."""
        from test_host.cosmos_writer import RunState
        state = RunState(run_id="x", environment="x", suite="x")
        assert hasattr(state, "current_phase")
        assert hasattr(state, "phases_completed")
        assert hasattr(state, "phases_total")
        assert isinstance(state.phases_completed, list)
