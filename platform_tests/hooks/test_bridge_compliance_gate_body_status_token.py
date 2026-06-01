"""Tests for the bridge-compliance-gate body-status-token rule.

GTKB-GOV-PROPOSAL-STANDARDS Slice 1 (owner decision
DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE; GO at
bridge/gtkb-gov-proposal-standards-slice1-023.md).

Versioned bridge files (bridge/<slug>-NNN.md) must begin with a canonical
status token on the first non-blank line (NEW / REVISED / GO / NO-GO /
VERIFIED / ADVISORY / WITHDRAWN). New files (and overwrites of files that
currently have a canonical first line) must comply; files already on disk
with a non-canonical first line are grandfathered. The rule fires only on the
Write tool (full content); the Edit tool supplies empty content to the gate
and is skipped. bridge/INDEX.md and non-versioned bridge markdown are exempt.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _load_gate():
    """Import the hyphenated hook module by path."""
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate", ACTIVE_HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_gate = _load_gate()

_CANONICAL_TOKENS = ("NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "WITHDRAWN")


def _versioned(tmp_path: Path, name: str = "gtkb-demo-thread-001.md") -> str:
    """Return a versioned bridge file path string under a tmp bridge dir."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    return str(bridge_dir / name)


# ---------------------------------------------------------------------------
# _body_status_token_violation unit behavior
# ---------------------------------------------------------------------------


def test_new_file_heading_first_blocked(tmp_path):
    """A new versioned bridge file whose first non-blank line is a heading
    (not a status token) is a violation."""
    path = _versioned(tmp_path)  # does not exist on disk
    content = "# GTKB Demo Thread\n\nSome proposal prose.\n"
    assert _gate._body_status_token_violation(path, content) is True


def test_each_canonical_token_accepted(tmp_path):
    """Each canonical status token on line 1 is accepted (no violation)."""
    path = _versioned(tmp_path)
    for token in _CANONICAL_TOKENS:
        content = f"{token}\n\n# Heading follows the token\n"
        assert _gate._body_status_token_violation(path, content) is False, token


def test_verdict_token_with_trailing_content_accepted(tmp_path):
    """GO/NO-GO/VERIFIED with trailing content on line 1 are accepted, mirroring
    the gate's existing ``.startswith`` recognition tolerance."""
    path = _versioned(tmp_path)
    for first in ("GO: bridge/x-002.md", "NO-GO - blockers remain", "VERIFIED against specs"):
        content = f"{first}\n\nbody\n"
        assert _gate._body_status_token_violation(path, content) is False, first


def test_existing_noncanonical_file_grandfathered(tmp_path):
    """An existing on-disk versioned file whose first line is already
    non-canonical is grandfathered: a (still non-canonical) overwrite is allowed."""
    path = _versioned(tmp_path, "legacy-heading-thread-003.md")
    Path(path).write_text("# Legacy heading-first body\n\nold content\n", encoding="utf-8")
    new_content = "# Legacy heading-first body (edited)\n\nnew content\n"
    assert _gate._body_status_token_violation(path, new_content) is False


def test_overwrite_canonical_to_noncanonical_blocked(tmp_path):
    """Overwriting a file that currently has a canonical first line with
    non-canonical content is blocked (do not corrupt a valid file)."""
    path = _versioned(tmp_path, "canonical-thread-004.md")
    Path(path).write_text("REVISED\n\n# Heading\n", encoding="utf-8")
    new_content = "# Now heading-first\n\nbody\n"
    assert _gate._body_status_token_violation(path, new_content) is True


def test_non_versioned_bridge_md_skipped(tmp_path):
    """A bridge markdown file without a -NNN version suffix is not subject to
    the rule."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    path = str(bridge_dir / "NOTES.md")
    content = "# Freeform bridge notes\n"
    assert _gate._body_status_token_violation(path, content) is False


def test_index_md_not_a_versioned_file(tmp_path):
    """bridge/INDEX.md has no -NNN suffix, so the violation predicate skips it
    (it is additionally excluded by _is_bridge_markdown_file in the gate)."""
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    path = str(bridge_dir / "INDEX.md")
    content = "# Bridge Index\n\nDocument: foo\nNEW: bridge/foo-001.md\n"
    assert _gate._body_status_token_violation(path, content) is False


# ---------------------------------------------------------------------------
# _first_line_is_recognized_status unit behavior
# ---------------------------------------------------------------------------


def test_recognized_status_includes_withdrawn():
    """WITHDRAWN is an accepted canonical token (Codex GO -023 non-blocking note)."""
    assert _gate._first_line_is_recognized_status("WITHDRAWN") is True


def test_recognized_status_rejects_heading_and_prose():
    assert _gate._first_line_is_recognized_status("# Heading") is False
    assert _gate._first_line_is_recognized_status("This is prose.") is False
    assert _gate._first_line_is_recognized_status("") is False


# ---------------------------------------------------------------------------
# Integrated _deny_reason_for_content path
# ---------------------------------------------------------------------------


def test_deny_reason_blocks_heading_first_new_file(tmp_path):
    """The integrated deny path returns the body-status-token message for a
    heading-first new versioned bridge file."""
    path = _versioned(tmp_path)
    content = "# GTKB Demo Thread\n\n## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=path,
        content=content,
        run_pending_preflight=False,
    )
    assert reason is not None
    assert "body-status-token" in reason.lower() or "canonical status token" in reason.lower()


def test_deny_reason_allows_status_first_proposal(tmp_path):
    """A status-first NEW proposal with concrete spec links passes the
    body-status-token check (other checks are not under test here)."""
    path = _versioned(tmp_path)
    content = "NEW\n\n# GTKB Demo Thread\n\n## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=path,
        content=content,
        run_pending_preflight=False,
    )
    # The body-status-token check must not be the blocker (reason, if any, would
    # come from a different clause; assert specifically the token message absent).
    if reason is not None:
        assert "body-status-token" not in reason.lower()
        assert "canonical status token" not in reason.lower()


def test_edit_tool_empty_content_skipped(tmp_path):
    """The Edit tool supplies empty content to the gate; the content-check block
    (including the body-status-token rule) is skipped, so no block."""
    path = _versioned(tmp_path)
    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=path,
        content="",
        run_pending_preflight=False,
    )
    assert reason is None
