"""Release-gate test: the bridge ignore patterns must be root-anchored (WI-7671).

`.gitignore` excludes the repository-root `bridge/` coordination directory,
because canon section 6 makes bridge material ephemeral coordination that is
never committed. That intent is correct and this test preserves it.

The patterns were written unanchored, as `bridge/` and `bridge/*`. Git matches
an unanchored directory pattern at ANY depth, so they also matched the Python
package `groundtruth-kb/src/groundtruth_kb/bridge/` and silently ignored every
new module added there. The 26 modules already in that package stayed tracked
only because git ignores untracked files alone, which hid the defect until
WI-7118 added `vocabulary.py`, the single source
`SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001` clause 5 requires. Nothing errored at
any step; the file simply would not have been committed.

Both halves are asserted here because fixing either one alone reintroduces the
other defect: over-anchoring would let bridge coordination material into git
history, and under-anchoring would silently drop package modules.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

PACKAGE_MODULE = "groundtruth-kb/src/groundtruth_kb/bridge/vocabulary.py"
ROOT_BRIDGE_FILE = "bridge/example-thread-001.md"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _check_ignore(rel_path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "check-ignore", "-v", rel_path],
        capture_output=True,
        text=True,
        cwd=_project_root(),
    )


def test_root_bridge_coordination_material_is_ignored() -> None:
    """Canon section 6: bridge material must never be committed."""
    result = _check_ignore(ROOT_BRIDGE_FILE)
    assert result.returncode == 0, (
        f"Expected the repository-root bridge directory to be gitignored, but "
        f"`git check-ignore` returned exit {result.returncode} for "
        f"{ROOT_BRIDGE_FILE}. Bridge coordination material would be committable, "
        "which canon section 6 forbids."
    )


def test_bridge_python_package_is_not_ignored() -> None:
    """A new module in the bridge package must be trackable."""
    result = _check_ignore(PACKAGE_MODULE)
    assert result.returncode != 0, (
        f"{PACKAGE_MODULE} is gitignored by `{result.stdout.strip()}`. An "
        "unanchored `bridge/` pattern matches a directory of that name at any "
        "depth, so new modules in the canonical bridge package are silently "
        "omitted from version control and from a fresh clone, with no error at "
        "any step. Anchor the pattern to the repository root as `/bridge/`."
    )


def test_no_unanchored_bridge_pattern_survives() -> None:
    """The regression floor: catch the pattern shape, not just today's paths.

    A path-based check alone would pass again the moment someone adds a new
    unanchored variant, so this asserts the shape directly.
    """
    gitignore = (_project_root() / ".gitignore").read_text(encoding="utf-8")
    offenders = [
        line
        for raw in gitignore.splitlines()
        if (line := raw.strip())
        and not line.startswith("#")
        and line.lstrip("!").rstrip("*").rstrip("/").endswith("bridge")
        and not line.lstrip("!").startswith("/")
    ]
    assert offenders == [], (
        f"Unanchored bridge ignore pattern(s) present: {offenders}. Git matches "
        "these at any depth, which silently untracks the groundtruth_kb bridge "
        "package. Anchor each to the repository root with a leading slash."
    )
