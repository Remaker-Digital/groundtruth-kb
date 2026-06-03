"""Slice D of GTKB-STARTUP-REFRACTOR-001 (WI-4272): the shared SessionStart
dispatch core must stay stdlib-light so the SessionStart hot path is not slowed
by heavy module-level imports (``groundtruth_kb``, the DB API, or third-party
packages). Preserving this property is why the duplication existed before the
extraction; it must survive de-duplication.

These are MODULE-LEVEL import checks: the ``groundtruth_kb.mode_switch.pending``
import is intentionally lazy (inside ``main()``), so it does not slow module
import and is correctly excluded by inspecting only top-level statements.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "scripts" / "session_start_dispatch_core.py"

# Standard-library modules the core legitimately imports at module level.
_ALLOWED_STDLIB = {
    "__future__",
    "hashlib",
    "json",
    "os",
    "re",
    "subprocess",
    "sys",
    "datetime",
    "enum",
    "pathlib",
    "types",
}
# In-root stdlib-light helper modules the core imports at module level.
_ALLOWED_LOCAL = {
    "scripts.harness_identity",
    "scripts.harness_projection_reader",
}
_FORBIDDEN_PREFIXES = ("groundtruth_kb",)


def _module_level_imports(source: str) -> set[str]:
    """Return module names imported at MODULE level (not inside functions)."""

    tree = ast.parse(source)
    mods: set[str] = set()
    for node in tree.body:  # top-level statements only — import-time weight
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            mods.add(node.module)
    return mods


def test_core_does_not_import_groundtruth_kb_at_module_level() -> None:
    mods = _module_level_imports(CORE.read_text(encoding="utf-8"))
    forbidden = sorted(m for m in mods if any(m == p or m.startswith(p + ".") for p in _FORBIDDEN_PREFIXES))
    assert not forbidden, (
        f"SessionStart dispatch core must stay stdlib-light: forbidden module-level imports {forbidden}. "
        "Heavy imports (groundtruth_kb / DB) belong in lazy function-level imports."
    )


def test_core_module_level_imports_are_stdlib_or_local_helpers() -> None:
    mods = _module_level_imports(CORE.read_text(encoding="utf-8"))
    unexpected = []
    for module_name in sorted(mods):
        top = module_name.split(".")[0]
        if module_name in _ALLOWED_STDLIB or top in _ALLOWED_STDLIB:
            continue
        if module_name in _ALLOWED_LOCAL:
            continue
        unexpected.append(module_name)
    assert not unexpected, (
        f"SessionStart dispatch core has unexpected (possibly heavy) module-level imports: {unexpected}"
    )
