#!/usr/bin/env python3
"""Pre-commit check: architectural grep guards.

Verifies that critical architectural patterns still exist in the codebase.
If a commit removes a mandatory pattern, the commit is rejected.

Guards:
  1. SLIM transport (src/agents/containers/slim_server_app.py must exist)
  2. MCP plugin registry (src/agents/plugins/registry.py must contain PluginAgentRegistry)
  3. MCP plugin dispatch (src/agents/plugins/dispatch.py must contain PluginDispatcher)
  4. Transport hierarchy enforcement (src/agents/ must reference SLIM or NatsTransport)
  5. Protected behavior assertions (PB-* patterns in test files)

Exit codes:
  0 = pass
  1 = fail (architectural pattern missing)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _file_exists(rel_path: str) -> bool:
    return (PROJECT_ROOT / rel_path).exists()


def _file_contains(rel_path: str, pattern: str) -> bool:
    path = PROJECT_ROOT / rel_path
    if not path.exists():
        return False
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return pattern in content
    except OSError:
        return False


def _grep_exists(directory: str, pattern: str) -> bool:
    """Check if pattern exists anywhere in directory using git grep (fast)."""
    result = subprocess.run(
        ["git", "grep", "-l", pattern, "--", directory],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    return bool(result.stdout.strip())


def get_staged_files() -> set[str]:
    """Return set of all staged files (added, modified, deleted)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    return {line.strip().replace("\\", "/") for line in result.stdout.strip().splitlines()}


# ---------------------------------------------------------------------------
# Guard definitions
# ---------------------------------------------------------------------------

GUARDS: list[dict] = [
    {
        "name": "SLIM transport server",
        "trigger_paths": ["src/agents/"],
        "check": lambda: _file_exists("src/agents/containers/slim_server_app.py"),
        "message": "src/agents/containers/slim_server_app.py must exist (SPEC-1780, PB-AGNTCY-001)",
    },
    {
        "name": "MCP Plugin Registry class",
        "trigger_paths": ["src/agents/plugins/"],
        "check": lambda: _file_contains("src/agents/plugins/registry.py", "class PluginAgentRegistry"),
        "message": "PluginAgentRegistry must exist in src/agents/plugins/registry.py (SPEC-1706)",
    },
    {
        "name": "MCP Plugin Dispatcher class",
        "trigger_paths": ["src/agents/plugins/"],
        "check": lambda: _file_contains("src/agents/plugins/dispatch.py", "class PluginDispatcher"),
        "message": "PluginDispatcher must exist in src/agents/plugins/dispatch.py (SPEC-1706)",
    },
    {
        "name": "Transport hierarchy reference",
        "trigger_paths": ["src/agents/"],
        "check": lambda: (
            _grep_exists("src/agents/", "SLIMTransport")
            or _grep_exists("src/agents/", "NatsTransport")
        ),
        "message": "src/agents/ must reference SLIMTransport or NatsTransport (SPEC-1780/1788)",
    },
    {
        "name": "EntitlementService class",
        "trigger_paths": ["src/multi_tenant/"],
        "check": lambda: _file_contains(
            "src/multi_tenant/entitlement_service.py", "class EntitlementService"
        ),
        "message": "EntitlementService must exist in src/multi_tenant/entitlement_service.py (SPEC-1815)",
    },
    {
        "name": "Verification runner",
        "trigger_paths": ["src/multi_tenant/"],
        "check": lambda: _file_exists("src/multi_tenant/verification_runner.py"),
        "message": "src/multi_tenant/verification_runner.py must exist (SPEC-1845/1846)",
    },
]


def main() -> int:
    staged = get_staged_files()
    if not staged:
        return 0

    violations: list[str] = []

    for guard in GUARDS:
        # Only check guards whose trigger paths overlap with staged files
        relevant = any(
            any(f.startswith(tp) for tp in guard["trigger_paths"])
            for f in staged
        )
        if not relevant:
            continue

        if not guard["check"]():
            violations.append(f"  FAIL [{guard['name']}]: {guard['message']}")

    if violations:
        print("=" * 70)
        print("ARCHITECTURAL GUARD FAILED — mandatory patterns missing")
        print("=" * 70)
        for v in violations:
            print(v)
        print()
        print("These patterns are protected by architectural specifications.")
        print("If removal is intentional, get owner approval first.")
        print("=" * 70)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
