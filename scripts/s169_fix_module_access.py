"""S169: Fix domain module access pattern for repo variables.

Changes from direct imports (creates local copy, invisible to mock.patch)
to module-attribute access (reads from _monolith at runtime, visible to patches).

Before: from ._monolith import _tenant_repo  # local copy
After:  from ... import _monolith as _state   # module ref, use _state._tenant_repo

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re
import pathlib

PKG = pathlib.Path("src/multi_tenant/superadmin_api")

# Variables that live in _monolith and are assigned by configure_*() at runtime.
# These MUST be accessed via module attribute, not direct import.
REPO_VARS = [
    "_tenant_repo",
    "_audit_repo",
    "_prefs_repo",
    "_conv_repo",
    "_usage_repo",
    "_nats_mgr",
    "_secret_service",
    "_incident_repo",
    "_alert_rule_repo",
    "_alert_history_repo",
    "_platform_admin_repo",
    "_admin_doc_repo",
    "_pipeline_metrics_configured",
]


def fix_file(filepath: pathlib.Path) -> int:
    """Fix a single domain module. Returns number of replacements made."""
    text = filepath.read_text(encoding="utf-8")
    original = text
    changes = 0

    # Step 1: Replace the import block.
    # Pattern: from src.multi_tenant.superadmin_api._monolith import (\n    router,\n    _var1,\n    ...)
    import_pattern = re.compile(
        r"from src\.multi_tenant\.superadmin_api\._monolith import \(\s*\n"
        r"(.*?)\)",
        re.DOTALL,
    )
    match = import_pattern.search(text)
    if not match:
        print(f"  SKIP {filepath.name}: no _monolith import block found")
        return 0

    import_body = match.group(1)
    # Extract imported names
    imported_names = [
        n.strip().rstrip(",") for n in import_body.split("\n") if n.strip() and not n.strip().startswith("#")
    ]

    # Separate router (keep as local binding) from repo vars (use _state.)
    has_router = "router" in imported_names
    repo_names_in_file = [n for n in imported_names if n in REPO_VARS]

    # Build replacement import
    new_import_lines = [
        "from src.multi_tenant.superadmin_api import _monolith as _state",
    ]
    if has_router:
        new_import_lines.append("")
        new_import_lines.append("router = _state.router")

    new_import = "\n".join(new_import_lines)
    text = text[: match.start()] + new_import + text[match.end() :]
    changes += 1

    # Step 2: Replace all bare repo variable references with _state.varname
    # We need to match standalone uses, not already-prefixed or in strings.
    for var in REPO_VARS:
        # Match the variable name when:
        # - NOT preceded by a dot (would be obj._var) or by "_state." (already fixed)
        # - NOT preceded by another word char (would be part of a larger name)
        # - IS followed by a non-word char or end of string
        pattern = re.compile(
            r"(?<!\.)"  # not preceded by dot
            r"(?<!_state\.)"  # not already prefixed
            r"\b" + re.escape(var) + r"\b"  # whole word
        )
        count = len(pattern.findall(text))
        if count > 0:
            text = pattern.sub(f"_state.{var}", text)
            changes += count

    if text != original:
        filepath.write_text(text, encoding="utf-8")
        print(f"  FIXED {filepath.name}: {changes} changes")
    else:
        print(f"  UNCHANGED {filepath.name}")

    return changes


def fix_dashboard_forward_ref(filepath: pathlib.Path) -> None:
    """Add TenantDistributionSummary import to _dashboard.py for Pydantic."""
    text = filepath.read_text(encoding="utf-8")

    # Add import of TenantDistributionSummary from _tenants AFTER the _state import
    if "TenantDistributionSummary" in text and "from src.multi_tenant.superadmin_api._tenants import" not in text:
        # Insert after the _state import line
        marker = "from src.multi_tenant.superadmin_api import _monolith as _state"
        if marker in text:
            text = text.replace(
                marker,
                marker + "\nfrom src.multi_tenant.superadmin_api._tenants import TenantDistributionSummary",
            )
            filepath.write_text(text, encoding="utf-8")
            print("  FIXED _dashboard.py: added TenantDistributionSummary import")


def main():
    total = 0
    for name in ["_tenants.py", "_dashboard.py", "_operations.py", "_copilot.py", "_platform.py"]:
        filepath = PKG / name
        print(f"\nProcessing {name}:")
        total += fix_file(filepath)

    print(f"\nFixing Pydantic forward reference in _dashboard.py:")
    fix_dashboard_forward_ref(PKG / "_dashboard.py")

    print(f"\nTotal changes: {total}")


if __name__ == "__main__":
    main()
