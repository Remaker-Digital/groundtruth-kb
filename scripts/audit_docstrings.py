"""Audit docstring coverage for src/groundtruth_kb/ (Phase 4A).

Produces two analyses:

  1. Per-file interrogate coverage (same as the docstring-coverage workflow).
  2. Public-API subset: every symbol in `groundtruth_kb.__all__` is inspected
     via Python introspection. Classes are expanded to include their public
     methods (non-underscore names). Each symbol / method is reported as
     "has docstring" or "missing".

The public-API subset is the measurement we actually care about for
production-grade readiness: third-party developers consuming
`from groundtruth_kb import KnowledgeDB` will read the docstrings of the
public surface, not the private helpers.

Run: python scripts/audit_docstrings.py > docs/reports/v0.4-baseline/docstrings.md

Verified against:
  - interrogate 1.7.0
  - groundtruth-kb 0.4.0 (993f31b8d42ac272b9716c191527b599d08ba632)

© 2026 Remaker Digital. Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import inspect

import interrogate
from interrogate import config as _cfg
from interrogate import coverage as _cov

import groundtruth_kb

# ---------------------------------------------------------------------------
# Part 1: interrogate per-file analysis
# ---------------------------------------------------------------------------


def run_interrogate() -> tuple[object, str]:
    """Run interrogate against src/groundtruth_kb/ and return the results + version."""
    cfg = _cfg.InterrogateConfig(
        color=False,
        fail_under=0,
        ignore_init_module=True,
        ignore_init_method=False,
        ignore_magic=True,
        ignore_module=False,
        ignore_private=False,
        ignore_semiprivate=False,
        ignore_property_setters=False,
        ignore_property_decorators=False,
        ignore_nested_classes=False,
        ignore_nested_functions=False,
        ignore_overloaded_functions=False,
        omit_covered_files=False,
        ignore_regex=False,
        include_regex=False,
    )
    results = _cov.InterrogateCoverage(
        paths=["src/groundtruth_kb"],
        conf=cfg,
    ).get_coverage()
    return results, interrogate.__version__


# ---------------------------------------------------------------------------
# Part 2: public-API subset analysis (Codex Condition 1)
# ---------------------------------------------------------------------------


def has_docstring(obj: object) -> bool:
    """Return True if the object has a non-empty docstring."""
    doc = inspect.getdoc(obj)
    return doc is not None and doc.strip() != ""


def audit_public_api() -> tuple[list[dict], int, int]:
    """Audit every symbol in groundtruth_kb.__all__ for docstring presence.

    Returns (rows, covered_count, total_count) where rows is a list of
    dicts with name, kind, has_doc, module.
    """
    rows: list[dict] = []

    for name in groundtruth_kb.__all__:
        obj = getattr(groundtruth_kb, name, None)
        if obj is None:
            rows.append(
                {
                    "name": name,
                    "kind": "missing",
                    "has_doc": False,
                    "module": "-",
                    "notes": "symbol not importable",
                }
            )
            continue

        # Attributes like __version__ don't have docstrings
        if isinstance(obj, str) and name == "__version__":
            rows.append(
                {
                    "name": name,
                    "kind": "attribute",
                    "has_doc": True,  # not applicable
                    "module": "groundtruth_kb",
                    "notes": "version string (N/A)",
                }
            )
            continue

        # Exceptions: inspect.isclass sees them as classes, which is correct
        if inspect.isclass(obj):
            class_has_doc = has_docstring(obj)
            module = getattr(obj, "__module__", "?")
            rows.append(
                {
                    "name": name,
                    "kind": "class",
                    "has_doc": class_has_doc,
                    "module": module,
                    "notes": "class",
                }
            )
            # Expand public methods (non-underscore, non-inherited-from-object)
            for method_name, method_obj in inspect.getmembers(obj):
                if method_name.startswith("_"):
                    continue
                # Skip methods inherited from object/Exception base
                if not hasattr(method_obj, "__qualname__"):
                    continue
                qualname = getattr(method_obj, "__qualname__", "")
                if "." not in qualname or not qualname.startswith(obj.__name__):
                    continue  # inherited, not defined on this class
                if inspect.isfunction(method_obj) or inspect.ismethod(method_obj):
                    rows.append(
                        {
                            "name": f"{name}.{method_name}",
                            "kind": "method",
                            "has_doc": has_docstring(method_obj),
                            "module": module,
                            "notes": "public method",
                        }
                    )
            continue

        # Functions
        if inspect.isfunction(obj) or inspect.isbuiltin(obj):
            rows.append(
                {
                    "name": name,
                    "kind": "function",
                    "has_doc": has_docstring(obj),
                    "module": getattr(obj, "__module__", "?"),
                    "notes": "function",
                }
            )
            continue

        # Catch-all
        rows.append(
            {
                "name": name,
                "kind": type(obj).__name__,
                "has_doc": has_docstring(obj),
                "module": "?",
                "notes": "unclassified",
            }
        )

    covered = sum(1 for r in rows if r["has_doc"])
    total = len(rows)
    return rows, covered, total


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def main() -> None:
    results, interrogate_version = run_interrogate()
    public_rows, public_covered, public_total = audit_public_api()
    public_pct = (public_covered / public_total * 100) if public_total else 0.0

    print("# Docstring Coverage Baseline (Phase 4A)")
    print()
    print(f"Generated with `interrogate {interrogate_version}` against `src/groundtruth_kb/`.")
    print()
    print("## Part 1: Per-file coverage (whole package)")
    print()
    print(f"- **Total nodes:** {results.total}")
    print(f"- **Covered:** {results.covered}")
    print(f"- **Missing:** {results.missing}")
    print(f"- **Coverage:** {results.perc_covered:.2f}%")
    print()
    print("### Per-file breakdown (sorted worst-first)")
    print()
    print("| File | Total | Covered | Missing | % |")
    print("|---|---:|---:|---:|---:|")
    sorted_files = sorted(results.file_results, key=lambda f: (f.perc_covered, -f.total))
    for fr in sorted_files:
        rel_name = fr.filename.replace("\\", "/").split("src/groundtruth_kb/")[-1]
        print(f"| `{rel_name}` | {fr.total} | {fr.covered} | {fr.missing} | {fr.perc_covered:.1f}% |")
    print()
    print(f"Total files audited: **{len(results.file_results)}**")
    print()
    print("## Part 2: Public API subset (Codex Condition 1)")
    print()
    print(
        "The public API is defined by `groundtruth_kb.__init__.py::__all__`. "
        "This section audits docstring presence on every exported symbol and, "
        "for classes, every public method (non-underscore name defined on the class)."
    )
    print()
    print(f"- **Public symbols + methods:** {public_total}")
    print(f"- **With docstring:** {public_covered}")
    print(f"- **Missing docstring:** {public_total - public_covered}")
    print(f"- **Public API coverage:** {public_pct:.2f}%")
    print()
    print("### Per-symbol breakdown")
    print()
    print("| Symbol | Kind | Module | Has docstring |")
    print("|---|---|---|:---:|")
    for row in public_rows:
        tick = "yes" if row["has_doc"] else "no"
        module_short = row["module"].replace("groundtruth_kb.", "")
        print(f"| `{row['name']}` | {row['kind']} | `{module_short}` | {tick} |")
    print()
    print("### Missing-docstring list (Phase 4B targets)")
    print()
    missing = [r for r in public_rows if not r["has_doc"]]
    if missing:
        for row in missing:
            print(f"- `{row['name']}` ({row['kind']}, `{row['module']}`)")
    else:
        print("_None — all public API symbols have docstrings._")
    print()
    print("## Notes")
    print()
    print(
        "- **Private modules are NOT included** in the public API subset. They still appear in Part 1's per-file table."
    )
    print(
        "- **Inherited methods (from `object`/`Exception`) are skipped** in the public-API "
        "audit because they are not defined on the class itself."
    )
    print(
        "- **`__version__`** is a string attribute, not a documentable symbol; marked "
        "N/A in the public API table but counted as covered to avoid false-negative."
    )
    print()
    print("---")
    print()
    print("*Generated by `scripts/audit_docstrings.py`. Part of the Phase 4A measurement-only audit baseline.*")


if __name__ == "__main__":
    main()
