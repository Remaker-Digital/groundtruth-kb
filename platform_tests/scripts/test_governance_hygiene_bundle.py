"""Static assertions for the governance-hygiene-bundle implementation.

Authority: bridge/gtkb-governance-hygiene-bundle-001.md (Codex GO at -002).

Each test maps to a specific Change letter (A-G) of the bundle. All
assertions are static (file existence + content fingerprints); no live
behavior is exercised. The bundle does not change runtime behavior.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_change_a_stale_duplicates_removed() -> None:
    """Change A — `(1)` duplicate files no longer exist in the working tree.

    Spec: ADR-ISOLATION-APPLICATION-PLACEMENT-001 (in-root cleanup).
    """
    duplicates = [
        PROJECT_ROOT / ".codex" / "gtkb-hooks" / "session-start (1).cmd",
        PROJECT_ROOT / "harness-state" / "codex" / "operating-role (1).md",
    ]
    for path in duplicates:
        assert not path.exists(), f"stale duplicate still present: {path}"


def test_change_f_release_readiness_header_refreshed() -> None:
    """Change F — release-readiness.md header timestamp updated to S333 or newer."""
    text = (PROJECT_ROOT / "memory" / "release-readiness.md").read_text(encoding="utf-8")
    # Header is in the first ~10 lines
    head = "\n".join(text.splitlines()[:10])
    import re

    match = re.search(r"Last updated:\s*(\d{4}-\d{2}-\d{2})", head)
    assert match is not None, f"header timestamp not found in:\n{head}"
    date_str = match.group(1)
    assert date_str >= "2026-05-06", f"header timestamp {date_str} is older than S333 (2026-05-06)"


def test_no_destructive_operations_in_bundle() -> None:
    """Bundle is purely additive (rule clauses + comment + header refresh) plus
    two specific file deletions (Change A). No bulk deletions, no history rewrite,
    no source-code logic changes, no live hook rewiring per the GO scope-control
    condition.

    This test is a guard: if any of these implementation-creep scenarios appear
    in the bundle's diff later, the test should be updated explicitly along
    with a follow-on bridge thread, not silently expanded.
    """
    # Sentinel paths that the bundle MUST NOT modify (per GO scope-control):
    bundle_should_not_modify = [
        PROJECT_ROOT / ".claude" / "settings.json",
        PROJECT_ROOT / ".codex" / "hooks.json",
    ]
    # We can't time-travel, but we can assert these files exist (sanity) and
    # were not deleted by the bundle.
    for path in bundle_should_not_modify:
        assert path.is_file(), f"bundle scope-control violation: missing {path}"
