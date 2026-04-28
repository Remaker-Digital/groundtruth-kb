# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""AST gate — no module-level ``_MANAGED_*`` lists in ``src/groundtruth_kb/``.

Enforces that the five parallel ``_MANAGED_*`` lists formerly scattered
across ``upgrade.py``, ``scaffold.py``, and (implicitly) ``doctor.py``
have been consolidated into the declarative TOML registry at
``templates/managed-artifacts.toml``. Any future attempt to re-introduce a
parallel ``_MANAGED_*`` module-level binding in the production source tree
will fail this check at CI time.

Scope: ``src/groundtruth_kb/`` only. Tests may still use ``_MANAGED_HOOKS``
etc. as local identifiers if needed, but the production code must not.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# Module-level bindings that would re-introduce parallel manifests.
_FORBIDDEN_NAMES: frozenset[str] = frozenset(
    {
        "_MANAGED_HOOKS",
        "_MANAGED_RULES",
        "_MANAGED_SKILLS",
        "_MANAGED_SKILLS_INITIAL",
        "_MANAGED_SETTINGS_PRETOOLUSE_HOOKS",
        "_MANAGED_GITIGNORE_PATTERNS",
    }
)


def _src_root() -> Path:
    """Return the repository's ``src/groundtruth_kb/`` path.

    Located relative to this test file to avoid CWD dependence.
    """
    # tests/ is a sibling of src/
    return Path(__file__).resolve().parent.parent / "src" / "groundtruth_kb"


def _python_files() -> list[Path]:
    """Enumerate every ``.py`` file under ``src/groundtruth_kb/``."""
    root = _src_root()
    if not root.is_dir():
        pytest.fail(f"expected src tree at {root!r}, not found")
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def _module_level_assigned_names(tree: ast.Module) -> set[str]:
    """Return the set of module-level assignment target names."""
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    names.add(tgt.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def test_no_module_level_managed_lists_in_src() -> None:
    """No ``.py`` under ``src/groundtruth_kb/`` may bind a ``_MANAGED_*`` name at module scope."""
    offenders: list[tuple[Path, set[str]]] = []
    for path in _python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            pytest.fail(f"syntax error in {path}: {exc}")
        names = _module_level_assigned_names(tree)
        bad = names & _FORBIDDEN_NAMES
        if bad:
            offenders.append((path, bad))

    if offenders:
        detail = "\n".join(f"  {p.relative_to(_src_root().parent.parent)}: {sorted(names)}" for p, names in offenders)
        pytest.fail(
            "Parallel manifest lists reintroduced in src tree. "
            "All managed artifacts must live in templates/managed-artifacts.toml "
            f"(see bridge/gtkb-managed-artifact-registry-007.md).\n{detail}"
        )
