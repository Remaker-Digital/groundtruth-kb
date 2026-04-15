# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Import hygiene checks for test_bridge_*.py files.

Verifies that no test_bridge_*.py file (other than this file) has
top-level imports of groundtruth_kb.bridge or any submodule thereof.
All bridge imports must live inside fixtures or test functions so that
bridge/__init__.py (which calls DB_PATH.parent.mkdir at import time)
cannot run before PRIME_BRIDGE_DB is redirected by a monkeypatch.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# The four prohibited top-level import patterns
# ---------------------------------------------------------------------------

_THIS_FILE = Path(__file__).resolve()
_TESTS_DIR = _THIS_FILE.parent


def _collect_bridge_test_files() -> list[Path]:
    """Return all test_bridge_*.py files in the tests directory, excluding this file."""
    return sorted(p for p in _TESTS_DIR.glob("test_bridge_*.py") if p.resolve() != _THIS_FILE)


def _is_bridge_import_name(name: str) -> bool:
    """Return True if name refers to groundtruth_kb.bridge or any submodule."""
    return name == "groundtruth_kb.bridge" or name.startswith("groundtruth_kb.bridge.")


def _is_bridge_from_import(node: ast.ImportFrom) -> bool:
    """Detect: from groundtruth_kb.bridge[...] import ... OR from groundtruth_kb import bridge[_...]."""
    module = node.module or ""
    if module == "groundtruth_kb.bridge" or module.startswith("groundtruth_kb.bridge."):
        return True
    # from groundtruth_kb import bridge[_anything]
    if module == "groundtruth_kb":
        for alias in node.names:
            if alias.name == "bridge" or alias.name.startswith("bridge_"):
                return True
    return False


def _is_bridge_importlib_call(call: ast.Call) -> bool:
    """Detect: importlib.import_module("groundtruth_kb.bridge...")."""
    if not isinstance(call.func, ast.Attribute):
        return False
    if call.func.attr != "import_module":
        return False
    if not (call.args and isinstance(call.args[0], ast.Constant)):
        return False
    arg = str(call.args[0].value)
    return _is_bridge_import_name(arg)


def _stmt_has_bridge_importlib_call(stmt: ast.stmt) -> bool:
    """Walk stmt's subtree for a bridge importlib.import_module(...) Call."""
    return any(isinstance(node, ast.Call) and _is_bridge_importlib_call(node) for node in ast.walk(stmt))


def _find_top_level_violations(source: str) -> list[str]:
    """Parse source, return list of violation descriptions for top-level bridge imports."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"SyntaxError: {exc}"]

    violations: list[str] = []
    for node in ast.iter_child_nodes(tree):
        # Pattern 1: import groundtruth_kb.bridge[...]
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_bridge_import_name(alias.name):
                    violations.append(f"line {node.lineno}: import {alias.name}")

        # Pattern 2: from groundtruth_kb.bridge[...] import ...
        elif isinstance(node, ast.ImportFrom):
            if _is_bridge_from_import(node):
                violations.append(f"line {node.lineno}: from {node.module or ''} import ...")

        # Pattern 3 & 4: importlib.import_module("groundtruth_kb.bridge...")
        # — covers bare Expr, Assign, and AnnAssign forms
        elif _stmt_has_bridge_importlib_call(node):
            violations.append(f"line {node.lineno}: importlib.import_module(groundtruth_kb.bridge...) at top level")

    return violations


# ---------------------------------------------------------------------------
# Parametrized test — one run per test_bridge_*.py file
# ---------------------------------------------------------------------------

_BRIDGE_TEST_FILES = _collect_bridge_test_files()


@pytest.mark.parametrize(
    "test_file",
    _BRIDGE_TEST_FILES,
    ids=[f.name for f in _BRIDGE_TEST_FILES],
)
def test_no_top_level_bridge_imports(test_file: Path) -> None:
    """Fail if test_file has any top-level groundtruth_kb.bridge import."""
    source = test_file.read_text(encoding="utf-8")
    violations = _find_top_level_violations(source)
    assert not violations, (
        f"{test_file.name} has top-level bridge imports (must be inside fixtures/functions):\n"
        + "\n".join(f"  {v}" for v in violations)
    )


# ---------------------------------------------------------------------------
# Negative tests for helper correctness
# ---------------------------------------------------------------------------


def test_non_bridge_import_not_flagged() -> None:
    """from other_module import something should NOT be flagged."""
    source = "from other_module import bridge\n"
    violations = _find_top_level_violations(source)
    assert not violations


def test_non_bridge_importlib_not_flagged() -> None:
    """importlib.import_module('other.module') should NOT be flagged."""
    source = "import importlib\nx = importlib.import_module('other.module')\n"
    violations = _find_top_level_violations(source)
    assert not violations


def test_bridge_import_expression_is_flagged() -> None:
    """importlib.import_module('groundtruth_kb.bridge') as expression should be flagged."""
    source = "import importlib\nimportlib.import_module('groundtruth_kb.bridge')\n"
    violations = _find_top_level_violations(source)
    assert any("importlib" in v for v in violations)


def test_bridge_import_assignment_is_flagged() -> None:
    """x = importlib.import_module('groundtruth_kb.bridge.context') as assignment is flagged."""
    source = "import importlib\nx = importlib.import_module('groundtruth_kb.bridge.context')\n"
    violations = _find_top_level_violations(source)
    assert any("importlib" in v for v in violations)


def test_bridge_annotated_assignment_is_flagged() -> None:
    """x: T = importlib.import_module('groundtruth_kb.bridge') as annotated-assign is flagged."""
    source = "import importlib\nfrom typing import Any\nx: Any = importlib.import_module('groundtruth_kb.bridge')\n"
    violations = _find_top_level_violations(source)
    assert any("importlib" in v for v in violations)


def test_from_groundtruth_kb_import_bridge_flagged() -> None:
    """from groundtruth_kb import bridge should be flagged."""
    source = "from groundtruth_kb import bridge\n"
    violations = _find_top_level_violations(source)
    assert violations  # should produce at least one violation


def test_from_groundtruth_kb_bridge_context_flagged() -> None:
    """from groundtruth_kb.bridge.context import agent_peer should be flagged."""
    source = "from groundtruth_kb.bridge.context import agent_peer\n"
    violations = _find_top_level_violations(source)
    assert violations


def test_from_groundtruth_kb_bridge_flagged() -> None:
    """from groundtruth_kb.bridge import runtime should be flagged."""
    source = "from groundtruth_kb.bridge import runtime\n"
    violations = _find_top_level_violations(source)
    assert violations


def test_inner_bridge_import_not_flagged() -> None:
    """Bridge import inside a function is NOT a top-level import — should not be flagged."""
    source = (
        "def test_something():\n"
        "    from groundtruth_kb.bridge.context import agent_peer\n"
        "    assert agent_peer('codex') == 'prime'\n"
    )
    violations = _find_top_level_violations(source)
    assert not violations
