# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Dockerfile.test coverage test — ensures every file path referenced by a test
via pathlib.Path("...") is available inside the test-host container.

This test parses all test files for Path("...") string arguments, extracts
the referenced filesystem paths, then verifies each one is covered by a COPY
directive in Dockerfile.test.  If a new test references a source file that
isn't copied into the container, this test fails *before* the container is
built — catching the problem at commit time rather than after a 6-minute ACR
build + deploy cycle.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DOCKERFILE_TEST = _PROJECT_ROOT / "Dockerfile.test"

# ---------------------------------------------------------------------------
# Paths that are legitimately NOT expected in the container image
# ---------------------------------------------------------------------------
EXCLUDED_PREFIXES = (
    "/tmp",           # Runtime temp files
    "/app",           # Container workdir — already exists at runtime
    ".github",        # CI workflows — tests skip if absent
    "docs",           # Documentation dir — tests skip if absent
    "node_modules",   # Never copied
)

# Individual files to exclude from coverage checking
EXCLUDED_FILES: set[str] = set()


def _parse_dockerfile_copy_targets(dockerfile: Path) -> list[str]:
    """Extract destination-side paths from COPY directives in Dockerfile.test.

    Returns a list of paths that exist inside the container after build.
    For directory copies (ending with /) the trailing slash is preserved so
    we can do prefix matching.
    """
    targets: list[str] = []
    for line in dockerfile.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("COPY "):
            continue
        # COPY may have multiple space-separated sources + one destination
        parts = line.split()
        # parts[0] = "COPY", parts[-1] = destination, rest = sources
        sources = parts[1:-1]
        for src in sources:
            # Normalize: strip leading ./ if present
            src = src.lstrip("./")
            targets.append(src)
    return targets


def _extract_path_strings_from_tests(tests_dir: Path) -> dict[str, list[str]]:
    """Walk all .py files under tests/ and extract Path("literal") arguments.

    Returns {test_file_relative: [path_string, ...]}.
    Uses AST parsing for accuracy — only picks up `Path("string_literal")`.
    """
    results: dict[str, list[str]] = {}
    for py_file in sorted(tests_dir.rglob("*.py")):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except SyntaxError:
            continue

        paths_in_file: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            # Match Path("...") or pathlib.Path("...")
            func = node.func
            is_path_call = False
            if isinstance(func, ast.Name) and func.id == "Path":
                is_path_call = True
            elif isinstance(func, ast.Attribute) and func.attr == "Path":
                is_path_call = True
            if not is_path_call:
                continue
            if not node.args:
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                paths_in_file.append(arg.value)

        if paths_in_file:
            rel = str(py_file.relative_to(tests_dir.parent))
            results[rel] = paths_in_file

    return results


def _is_excluded(path_str: str) -> bool:
    """Check if a path should be excluded from coverage verification."""
    if path_str in EXCLUDED_FILES:
        return True
    for prefix in EXCLUDED_PREFIXES:
        # Match exact name or name followed by / (directory separator)
        if path_str == prefix or path_str.startswith(prefix + "/"):
            return True
    # Absolute paths (Windows or Unix) are not container-relative
    if path_str.startswith("/") and not path_str.startswith("/tmp") and not path_str.startswith("/app"):
        return True
    if len(path_str) >= 3 and path_str[1] == ":" and path_str[2] in ("/", "\\"):
        return True
    return False


def _is_covered(path_str: str, copy_targets: list[str]) -> bool:
    """Check if a path is covered by any COPY directive.

    A path is covered if:
    - It exactly matches a copied file, OR
    - It starts with a copied directory prefix (e.g. src/ covers src/foo.py)
    """
    normalized = path_str.lstrip("./")
    for target in copy_targets:
        target_norm = target.rstrip("/")
        # Exact file match
        if normalized == target_norm:
            return True
        # Directory prefix match (target is a directory copy)
        if target.endswith("/") and normalized.startswith(target_norm + "/"):
            return True
        # Also handle case where target doesn't end with / but is a dir
        # e.g. COPY src/ covers src/foo/bar.py
        if normalized.startswith(target_norm + "/"):
            return True
    return False


@pytest.mark.skipif(
    not _DOCKERFILE_TEST.is_file(),
    reason="Dockerfile.test not present (container environment)",
)
class TestDockerfileTestCoverage(unittest.TestCase):
    """Verify every Path() reference in tests is available in the container."""

    def test_all_test_paths_covered_by_dockerfile(self):
        """Every Path('...') in test files must be covered by Dockerfile.test COPY."""
        project_root = Path(__file__).resolve().parent.parent.parent
        dockerfile = project_root / "Dockerfile.test"
        tests_dir = project_root / "tests"

        assert dockerfile.exists(), f"Dockerfile.test not found at {dockerfile}"
        assert tests_dir.exists(), f"tests/ not found at {tests_dir}"

        copy_targets = _parse_dockerfile_copy_targets(dockerfile)
        path_refs = _extract_path_strings_from_tests(tests_dir)

        uncovered: list[str] = []
        for test_file, paths in sorted(path_refs.items()):
            for p in paths:
                if _is_excluded(p):
                    continue
                if not _is_covered(p, copy_targets):
                    uncovered.append(f"  {test_file}: Path(\"{p}\")")

        if uncovered:
            msg = (
                f"Found {len(uncovered)} Path() reference(s) in tests not covered "
                f"by Dockerfile.test COPY directives:\n"
                + "\n".join(uncovered)
                + "\n\nFix: Add the missing COPY directive(s) to Dockerfile.test, "
                "or add the path to EXCLUDED_PREFIXES/EXCLUDED_FILES if it's "
                "a runtime-only path."
            )
            self.fail(msg)

    def test_copy_targets_parse_correctly(self):
        """Sanity check: parser finds known COPY targets."""
        project_root = Path(__file__).resolve().parent.parent.parent
        dockerfile = project_root / "Dockerfile.test"
        if not dockerfile.exists():
            self.skipTest("Dockerfile.test not found")

        targets = _parse_dockerfile_copy_targets(dockerfile)
        # These should always be present
        self.assertIn("src/", targets)
        self.assertIn("tests/", targets)
        self.assertIn("pyproject.toml", targets)
