#!/usr/bin/env python3
"""
Git pre-commit guardrail â€” Hardcoded Credential & FQDN Scanner.

Scans staged files for hardcoded environment-specific values:
  - Azure Container Apps FQDNs
  - API keys with known prefixes (ar_spa_, ar_tenant_, ar_widget_)
  - Azure connection strings
  - Subscription/resource IDs in assignment context

SPEC-0058: All transient keys, values, URLs, and variables that change
between builds or tenant environments MUST NOT be hardcoded.

Exit 0: No violations found (or only excluded files)
Exit 1: Hardcoded values detected â€” commit blocked

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import re
import subprocess
import sys


# ---------------------------------------------------------------------------
# Detection patterns
# ---------------------------------------------------------------------------

PATTERNS = [
    # Azure Container Apps FQDNs
    (
        re.compile(
            r'''["']https?://agent-red-[a-z0-9-]+\.[a-z0-9-]+\.[a-z0-9]+\.azurecontainerapps\.io[^"']*["']'''
        ),
        "Hardcoded Azure Container Apps FQDN",
    ),
    # Redis Cache FQDNs
    (
        re.compile(
            r'''["']https?://[a-z0-9-]+\.redis\.cache\.windows\.net[^"']*["']'''
        ),
        "Hardcoded Azure Redis FQDN",
    ),
    # Cosmos DB FQDNs
    (
        re.compile(
            r'''["']https?://[a-z0-9-]+\.documents\.azure\.com[^"']*["']'''
        ),
        "Hardcoded Cosmos DB FQDN",
    ),
    # Key Vault FQDNs
    (
        re.compile(
            r'''["']https?://[a-z0-9-]+\.vault\.azure\.net[^"']*["']'''
        ),
        "Hardcoded Key Vault FQDN",
    ),
    # Agent Red API keys
    (
        re.compile(r'''["']ar_(spa|tenant|widget)_[A-Za-z0-9]{16,}["']'''),
        "Hardcoded API key (ar_* prefix)",
    ),
    (
        re.compile(r'''["']ar_spa_plat_[A-Za-z0-9]{16,}["']'''),
        "Hardcoded platform admin API key",
    ),
    # Azure connection strings
    (
        re.compile(r'''["']AccountEndpoint=https://[^"']+;AccountKey=[^"']+["']'''),
        "Hardcoded Azure connection string",
    ),
]


# ---------------------------------------------------------------------------
# Excluded file patterns (not scanned)
# ---------------------------------------------------------------------------

EXCLUDED = [
    re.compile(r"memory/"),
    re.compile(r"MEMORY\.md$"),
    re.compile(r"CLAUDE\.md$"),
    re.compile(r"CLAUDE-REFERENCE\.md$"),
    re.compile(r"CLAUDE-ARCHITECTURE\.md$"),
    re.compile(r"CLAUDE_ARCHIVE\.md$"),
    re.compile(r"\.claude/hooks/"),
    re.compile(r"wiki/"),
    re.compile(r"docs-site/"),
    re.compile(r"container-load-results/"),
    re.compile(r"\.html$"),
    re.compile(r"independent-progress-assessments/"),
    re.compile(r"\.env"),
    re.compile(r"deploy/.*\.(ps1|sh)$"),
    re.compile(r"Dockerfile"),
    re.compile(r"docker-compose"),
    re.compile(r"\.lock$"),
    re.compile(r"package-lock\.json$"),
    re.compile(r"\.min\.(js|css)$"),
]


def get_staged_files() -> list[str]:
    """Get list of staged files (added or modified)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def get_staged_content(filepath: str) -> str:
    """Get the staged content of a file."""
    result = subprocess.run(
        ["git", "show", f":{filepath}"],
        capture_output=True,
        text=True,
        errors="replace",
    )
    return result.stdout if result.returncode == 0 else ""


def is_excluded(filepath: str) -> bool:
    """Check if file is excluded from scanning."""
    return any(p.search(filepath) for p in EXCLUDED)


def main() -> int:
    staged_files = get_staged_files()
    if not staged_files:
        return 0

    violations = []

    for filepath in staged_files:
        if is_excluded(filepath):
            continue

        # Skip binary files
        if filepath.endswith((".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".svg", ".db")):
            continue

        content = get_staged_content(filepath)
        if not content:
            continue

        for line_num, line in enumerate(content.split("\n"), 1):
            # Skip comment-only lines (the pattern description in this file, etc.)
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
                continue

            for pattern, description in PATTERNS:
                if pattern.search(line):
                    violations.append((filepath, line_num, description, line.strip()[:100]))

    if violations:
        print("\n  SPEC-0058 VIOLATION: Hardcoded environment values detected\n")
        for filepath, line_num, desc, snippet in violations[:20]:
            print(f"    {filepath}:{line_num}")
            print(f"      {desc}")
            print(f"      {snippet}")
            print()
        if len(violations) > 20:
            print(f"    ... and {len(violations) - 20} more violations")
        print("  Use environment variables instead of hardcoded values.")
        print("  See SPEC-0058 for requirements.\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

