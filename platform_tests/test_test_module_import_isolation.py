"""No test module imports another test module; the shared fixture helpers are not test modules (c102, Q-3, D23).

A test module that exports fixtures is collected and executed whenever it is imported, its module-level setup runs
for every importer and fixture identity depends on import order. Shared fixtures and helpers therefore live in
helper modules (file names not starting with ``test_``, containing no test) that test modules import explicitly;
this module keeps both halves of that arrangement true for the two test trees.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_TREES = ("platform_tests", "groundtruth-kb/tests")
HELPER_MODULES = (
    "platform_tests/groundtruth_kb/native_fixtures.py",
    "platform_tests/groundtruth_kb/bridge_fixtures.py",
    "platform_tests/groundtruth_kb/finalization_fixtures.py",
    "platform_tests/groundtruth_kb/postgres_fixtures.py",
    "platform_tests/groundtruth_kb/cli/registry_cli_fixtures.py",
    "platform_tests/scripts/openrouter_fixtures.py",
    "platform_tests/scripts/provider_fixtures.py",
    "platform_tests/scripts/sot_hook_fixtures.py",
)


def _test_modules() -> list[Path]:
    return sorted(
        path for tree in TEST_TREES for path in (REPO_ROOT / tree).rglob("test_*.py") if "__pycache__" not in path.parts
    )


def _package_parts(path: Path) -> list[str]:
    """Dotted-name parts of the package holding ``path`` (groundtruth-kb/tests is imported as ``tests``)."""
    parts = list(path.resolve().relative_to(REPO_ROOT).parts[:-1])
    if parts[:2] == ["groundtruth-kb", "tests"]:
        parts = parts[1:]
    return parts


def _imported_names(path: Path) -> list[tuple[int, str]]:
    """Every dotted module name an import statement in ``path`` names (module-level or nested)."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                package = _package_parts(path)
                base = ".".join(package[: len(package) - (node.level - 1)])
                module = f"{base}.{node.module}" if node.module else base
            else:
                module = node.module or ""
            names.append((node.lineno, module))
            names.extend((node.lineno, f"{module}.{alias.name}") for alias in node.names)
    return names


def _names_a_test_module(dotted: str) -> bool:
    return any(segment.startswith("test_") for segment in dotted.split("."))


def test_no_test_module_imports_another_test_module() -> None:
    violations = [
        f"{path.relative_to(REPO_ROOT).as_posix()}:{line} imports {dotted}"
        for path in _test_modules()
        for line, dotted in _imported_names(path)
        if _names_a_test_module(dotted)
    ]
    assert not violations, "test modules importing test modules:\n" + "\n".join(violations)


@pytest.mark.parametrize("relative", HELPER_MODULES)
def test_shared_fixture_helpers_are_not_test_modules(relative: str) -> None:
    path = REPO_ROOT / relative
    assert path.is_file(), f"{relative} is absent"
    assert not path.name.startswith("test_"), f"{relative} would be collected as a test module"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    collected = [
        node.name
        for node in tree.body
        if (isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name.startswith("test_"))
        or (isinstance(node, ast.ClassDef) and node.name.startswith("Test"))
    ]
    assert not collected, f"{relative} defines collectable tests: {collected}"
    imported = [dotted for _, dotted in _imported_names(path) if _names_a_test_module(dotted)]
    assert not imported, f"{relative} imports a test module: {imported}"
