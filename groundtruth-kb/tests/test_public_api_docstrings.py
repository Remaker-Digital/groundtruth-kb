"""Phase 4B.3: regression guard for public API docstring coverage.

Locks docstring coverage at 100% on every symbol in groundtruth_kb.__all__
plus every public method of every exported class. Prevents doc-bitrot when
new methods are added to KnowledgeDB or GateRegistry.

Mirrors the semantics of scripts/audit_docstrings.py:
- Walk groundtruth_kb.__all__
- __version__ is a string attribute (N/A) — treated as covered, not checked
- Exported classes are expanded to their public non-underscore methods defined
  on the class itself (inherited methods from object/Exception are excluded)
- Functions are checked directly

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import inspect

import groundtruth_kb


def _collect_public_api_symbols() -> list[tuple[str, object]]:
    """Walk __all__ and expand exported classes into their public methods.

    Returns a list of (qualified_name, object) pairs for every symbol that
    must have a docstring.  Mirrors scripts/audit_docstrings.py semantics:
    - __version__ is skipped (string attribute, N/A).
    - Class-level docstring is included as a separate entry.
    - Public methods are non-underscore names whose __qualname__ starts with
      the class name, meaning they are defined on the class (not inherited).
    """
    symbols: list[tuple[str, object]] = []

    for name in groundtruth_kb.__all__:
        obj = getattr(groundtruth_kb, name, None)
        if obj is None:
            continue

        # __version__ is a string attribute — skip (treated as covered, N/A)
        if isinstance(obj, str) and name == "__version__":
            continue

        if inspect.isclass(obj):
            # Include the class docstring itself
            symbols.append((name, obj))
            # Expand to public methods defined on this class
            for method_name, method_obj in inspect.getmembers(obj):
                if method_name.startswith("_"):
                    continue
                qualname = getattr(method_obj, "__qualname__", "")
                # Exclude methods inherited from object/Exception
                if not qualname.startswith(obj.__name__ + "."):
                    continue
                if inspect.isfunction(method_obj) or inspect.ismethod(method_obj):
                    symbols.append((f"{name}.{method_name}", method_obj))
        else:
            # Functions and other callables
            symbols.append((name, obj))

    return symbols


def test_public_api_has_docstrings() -> None:
    """Every public API symbol must have a non-empty docstring.

    Phase 4B.3 closed 27 gaps in KnowledgeDB and GateRegistry. This test
    pins the guarantee so future method additions cannot silently regress.
    """
    missing = []
    for symbol_name, obj in _collect_public_api_symbols():
        doc = inspect.getdoc(obj)
        if doc is None or not doc.strip():
            missing.append(symbol_name)

    assert not missing, (
        f"Public API symbols missing docstrings ({len(missing)} found): "
        f"{sorted(missing)}. "
        f"Add Google-style docstrings matching the quality criteria in "
        f"bridge/gtkb-phase4b3-public-api-docstrings-001.md."
    )
