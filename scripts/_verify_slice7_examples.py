"""GTKB-ISOLATION-017 Slice 7 — content-presence + banned-token verification.

Per bridge `gtkb-isolation-017-slice7-examples-2026-05-03-002.md` GO
condition 5: production-path and credential leakage checks must execute over
every new example file. This script enumerates those checks.

Per condition 4: cross-link to `scripts/release_candidate_gate.py` must
resolve to the actual workspace path `E:/GT-KB/scripts/release_candidate_gate.py`,
NOT a path under `groundtruth-kb/scripts/`.
"""

from __future__ import annotations

import pathlib
import re
import sys

EXAMPLES = (
    "clean-adopter-minimal",
    "adopter-with-transport-tests",
    "adopter-with-release-gate",
    "existing-adopter-migration",
)

REQUIRED_PER_EXAMPLE = ("README.md", "groundtruth.toml", ".gitignore")

# Required dashboard-rendering anchor in every example README per
# Phase 9 Exit Criterion 4 line 349-350.
DASHBOARD_HEADING_RE = re.compile(r"^##\s+Dashboard rendering", re.MULTILINE)

# Banned tokens — production-paths / credentials / non-public secrets.
# Contextual references (e.g., "Agent Red" in WALKTHROUGH prose) are
# acceptable per Codex condition 5 ("Contextual references to Agent Red are
# acceptable only if they do not disclose production paths, Azure workspace
# names, or secrets"). The check distinguishes contextual mentions from
# production-shaped tokens.
BANNED_TOKEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # Azure workspace names (e.g., "agent-red-...workspace-..." patterns)
    ("azure-workspace", re.compile(r"\bagent-red[\w-]*workspace[\w-]*\b", re.IGNORECASE)),
    # Live secrets / api keys (case-insensitive substring)
    ("api-key-literal", re.compile(r"\b(?:sk-|pk_live_|api[_-]?key\s*=\s*[\"'][^\"']+[\"'])\b", re.IGNORECASE)),
    # Production hostnames
    ("prod-host", re.compile(r"\b(?:prod\.|production\.|\.prod\b)[\w.-]*\b", re.IGNORECASE)),
    # SSO provider tokens
    ("sso-token", re.compile(r"\b(?:client_secret|password|passwd)\s*=\s*[\"'][^\"']+[\"']", re.IGNORECASE)),
)


def _check_required_files(example_root: pathlib.Path) -> list[str]:
    return [name for name in REQUIRED_PER_EXAMPLE if not (example_root / name).exists()]


def _check_dashboard_anchor(readme_path: pathlib.Path) -> bool:
    return bool(DASHBOARD_HEADING_RE.search(readme_path.read_text(encoding="utf-8")))


def _check_banned_tokens(text: str) -> list[str]:
    hits: list[str] = []
    for label, pattern in BANNED_TOKEN_PATTERNS:
        if pattern.search(text):
            hits.append(label)
    return hits


def _check_release_gate_cross_link(readme_path: pathlib.Path) -> str | None:
    """If the README references the workspace release-gate script, the path
    must resolve to ``<workspace>/scripts/release_candidate_gate.py``,
    NOT a path under ``groundtruth-kb/scripts/``.
    """
    text = readme_path.read_text(encoding="utf-8")
    bad = re.search(r"groundtruth-kb/scripts/release_candidate_gate\.py", text)
    if bad:
        return f"{readme_path}: cross-link points at groundtruth-kb/scripts/ (should be workspace-level scripts/)"
    return None


def main() -> int:
    examples_root = pathlib.Path("groundtruth-kb/examples")
    if not examples_root.exists():
        print(f"FAIL: examples root not found: {examples_root}")
        return 1

    failures: list[str] = []

    for name in EXAMPLES:
        example_root = examples_root / name
        if not example_root.exists():
            failures.append(f"{name}: example directory missing")
            continue
        missing = _check_required_files(example_root)
        if missing:
            failures.append(f"{name}: missing required files: {missing}")
        readme = example_root / "README.md"
        if readme.exists() and not _check_dashboard_anchor(readme):
            failures.append(f"{name}: README.md missing '## Dashboard rendering' section")
        link_issue = _check_release_gate_cross_link(readme) if readme.exists() else None
        if link_issue:
            failures.append(link_issue)

        for path in example_root.rglob("*"):
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            hits = _check_banned_tokens(content)
            if hits:
                failures.append(f"{path}: banned tokens detected: {hits}")

    if failures:
        print("FAIL:")
        for line in failures:
            print(f"  {line}")
        return 1

    print("PASS: all 4 examples have required files + dashboard-rendering section")
    print("PASS: no banned production-path / credential tokens detected")
    print("PASS: no broken release-gate cross-links")
    return 0


if __name__ == "__main__":
    sys.exit(main())
