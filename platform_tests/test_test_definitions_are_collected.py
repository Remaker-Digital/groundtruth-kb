"""c123 (batch design WP5, G44(b)): every test definition under the test roots sits in a file pytest collects.

pytest collects test_*.py files only (pyproject.toml python_files). Four package __init__.py files held suites that
pytest never collected: one drove a removed command and retired approval gates, and three were stale copies of
collected modules. They are package markers now, and this guard keeps any .py file under the test roots that defines a
top-level test_* function or Test* class in a test_*.py file.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEST_ROOTS = ("platform_tests", "groundtruth-kb/tests")
SKIPPED_PARTS = frozenset({"__pycache__", ".pytest-tmp", "node_modules"})


def _defines_tests(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    return any(
        (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"))
        or (isinstance(node, ast.ClassDef) and node.name.startswith("Test"))
        for node in tree.body
    )


def uncollected(base: Path, roots: tuple[str, ...] = TEST_ROOTS) -> list[str]:
    found = []
    for root in roots:
        for path in sorted((base / root).rglob("*.py")):
            if SKIPPED_PARTS & set(path.parts) or path.name == "conftest.py" or path.name.startswith("test_"):
                continue
            if _defines_tests(path):
                found.append(path.relative_to(base).as_posix())
    return found


def test_every_test_definition_is_in_a_collected_file() -> None:
    assert uncollected(ROOT) == []


def test_the_guard_finds_a_suite_in_a_package_marker(tmp_path: Path) -> None:
    package = tmp_path / "platform_tests" / "pkg"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("def test_never_collected():\n    assert False\n", encoding="utf-8")
    (package / "helpers.py").write_text(
        "class TestShaped:\n    pass\n\n\ndef build():\n    return 1\n", encoding="utf-8"
    )
    (package / "plain.py").write_text("def build():\n    return 1\n", encoding="utf-8")
    (package / "test_collected.py").write_text("def test_collected():\n    pass\n", encoding="utf-8")
    (package / "conftest.py").write_text("def test_fixture_module():\n    pass\n", encoding="utf-8")

    assert uncollected(tmp_path) == ["platform_tests/pkg/__init__.py", "platform_tests/pkg/helpers.py"]
