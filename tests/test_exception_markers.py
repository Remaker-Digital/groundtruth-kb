"""CI gate: broad exception governance for groundtruth-kb.

Every non-reraising ``except Exception`` or ``except BaseException`` handler
in ``src/groundtruth_kb/`` must carry an ``# intentional-catch:`` marker on
the ``except`` line.  Re-raise cleanup handlers (containing a top-level bare
``raise``) are exempt.

Phase 4D of the GT-KB quality plan.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import ast
import pathlib
import sys
from unittest import mock

import pytest

_SRC_ROOT = pathlib.Path(__file__).resolve().parent.parent / "src" / "groundtruth_kb"


# ---------------------------------------------------------------------------
# CI gate: every non-reraising broad handler must be annotated
# ---------------------------------------------------------------------------


def _collect_broad_handlers() -> list[tuple[str, int, str]]:  # [(rel_path, lineno, "marked"|"unmarked"|"reraise")]
    """Walk the source tree and classify every broad exception handler."""
    results: list[tuple[str, int, str]] = []
    for py in sorted(_SRC_ROOT.rglob("*.py")):
        try:
            source = py.read_text(encoding="utf-8")
            lines = source.splitlines()
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler):
                continue
            if node.type is None:
                continue  # bare except: — not in scope
            if isinstance(node.type, ast.Name) and node.type.id in (
                "Exception",
                "BaseException",
            ):
                # Check for a top-level bare raise in the handler body
                has_bare_raise = any(isinstance(stmt, ast.Raise) and stmt.exc is None for stmt in node.body)
                if has_bare_raise:
                    results.append((str(py.relative_to(_SRC_ROOT)), node.lineno, "reraise"))
                else:
                    line_text = lines[node.lineno - 1]
                    if "# intentional-catch:" in line_text:
                        results.append((str(py.relative_to(_SRC_ROOT)), node.lineno, "marked"))
                    else:
                        results.append((str(py.relative_to(_SRC_ROOT)), node.lineno, "unmarked"))
    return results


def test_broad_exceptions_are_annotated() -> None:
    """Every non-reraising 'except Exception' must have an intentional-catch marker."""
    handlers = _collect_broad_handlers()
    assert handlers, "Expected to find broad exception handlers in the source tree"

    violations = [(f, ln) for f, ln, cat in handlers if cat == "unmarked"]
    if violations:
        detail = "\n".join(f"  {f}:{ln}" for f, ln in violations)
        pytest.fail(f"{len(violations)} unannotated non-reraising broad exception handler(s):\n{detail}")

    # Sanity: confirm we found the expected categories
    reraise_count = sum(1 for _, _, cat in handlers if cat == "reraise")
    marked_count = sum(1 for _, _, cat in handlers if cat == "marked")
    assert reraise_count >= 7, f"Expected >=7 re-raise handlers, found {reraise_count}"
    assert marked_count >= 21, f"Expected >=21 marked handlers, found {marked_count}"


# ---------------------------------------------------------------------------
# Narrowing tests
# ---------------------------------------------------------------------------


def test_narrowed_db_persist_quality_scores() -> None:
    """db.py persist_quality_scores catches sqlite3.IntegrityError, not Exception.

    Verified via AST: the except handler in persist_quality_scores must NOT
    catch bare Exception.
    """
    source = _SRC_ROOT / "db.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "persist_quality_scores":
            for child in ast.walk(node):
                if isinstance(child, ast.ExceptHandler) and child.type is not None and isinstance(child.type, ast.Name):
                    assert child.type.id != "Exception", (
                        f"persist_quality_scores still catches Exception at line {child.lineno}"
                    )
            break
    else:
        pytest.fail("persist_quality_scores function not found in db.py")


def test_pid_is_running_narrowed_windows() -> None:
    """Windows _pid_is_running catches (OSError, AttributeError, ImportError), not Exception."""
    from groundtruth_kb.bridge.launcher import _pid_is_running

    with (
        mock.patch.object(sys, "platform", "win32"),
        mock.patch.dict("sys.modules", {"ctypes": mock.MagicMock(side_effect=AttributeError)}),
    ):
        # Force reimport scenario — the function uses inline import
        result = _pid_is_running(99999)
        assert result is False


def test_pid_is_running_unix_no_broad_catch() -> None:
    """Unix _pid_is_running only catches OSError, not Exception."""
    from groundtruth_kb.bridge.launcher import _pid_is_running

    if sys.platform == "win32":
        # On Windows, we test the Unix path by mocking platform
        with mock.patch.object(sys, "platform", "linux"):
            # OSError should be caught
            with mock.patch("os.kill", side_effect=OSError("No such process")):
                assert _pid_is_running(99999) is False

            # Non-OSError exceptions should propagate (no broad catch)
            with (
                mock.patch("os.kill", side_effect=RuntimeError("unexpected")),
                pytest.raises(RuntimeError, match="unexpected"),
            ):
                _pid_is_running(99999)
    else:
        # On Unix, test directly
        with mock.patch("os.kill", side_effect=OSError("No such process")):
            assert _pid_is_running(99999) is False

        with (
            mock.patch("os.kill", side_effect=RuntimeError("unexpected")),
            pytest.raises(RuntimeError, match="unexpected"),
        ):
            _pid_is_running(99999)
