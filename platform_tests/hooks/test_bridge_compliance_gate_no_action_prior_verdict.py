# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the bridge-compliance-gate NO-ACTION prior-verdict guard (WI-5082 Slice 2a).

Enforces DCL-NO-ACTION-STATUS-SEMANTICS-001: a NO-ACTION bridge write is
well-formed only when a prior Loyal Opposition GO or NO-GO verdict exists in the
same numbered thread. Advisory threads have no prior verdict, so NO-ACTION used
to close an advisory is blocked.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_HOOK = REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"


def _load_gate():
    spec = importlib.util.spec_from_file_location("bridge_compliance_gate", ACTIVE_HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_gate = _load_gate()

_SLUG = "gtkb-demo-advisory"

_NO_ACTION_BODY = """NO-ACTION

# Prime disposition

Disposition: NO-ACTION on this advisory thread.
"""


def _bridge_dir(tmp_path: Path) -> Path:
    d = tmp_path / "bridge"
    d.mkdir(exist_ok=True)
    return d


def _write_version(tmp_path: Path, version: int, status: str) -> None:
    d = _bridge_dir(tmp_path)
    body = f"""{status}

# {status} body
"""
    (d / f"{_SLUG}-{version:03d}.md").write_text(body, encoding="utf-8")


def _target(tmp_path: Path, version: int) -> str:
    return str(_bridge_dir(tmp_path) / f"{_SLUG}-{version:03d}.md")


# --- helper unit behavior ---------------------------------------------------


def test_blocked_when_priors_advisory_only(tmp_path):
    _write_version(tmp_path, 1, "ADVISORY")
    reason = _gate._no_action_prior_verdict_deny(_target(tmp_path, 2), _NO_ACTION_BODY)
    assert reason is not None
    assert "NO-ACTION bridge write blocked" in reason


def test_blocked_when_no_priors(tmp_path):
    reason = _gate._no_action_prior_verdict_deny(_target(tmp_path, 1), _NO_ACTION_BODY)
    assert reason is not None
    assert "NO-ACTION bridge write blocked" in reason


def test_allowed_when_prior_go_exists(tmp_path):
    _write_version(tmp_path, 1, "NEW")
    _write_version(tmp_path, 2, "GO")
    assert _gate._no_action_prior_verdict_deny(_target(tmp_path, 3), _NO_ACTION_BODY) is None


def test_allowed_when_prior_nogo_exists(tmp_path):
    _write_version(tmp_path, 1, "NEW")
    _write_version(tmp_path, 2, "NO-GO")
    assert _gate._no_action_prior_verdict_deny(_target(tmp_path, 3), _NO_ACTION_BODY) is None


def test_non_no_action_first_line_ignored(tmp_path):
    _write_version(tmp_path, 1, "ADVISORY")
    go_body = """GO

# verdict
"""
    assert _gate._no_action_prior_verdict_deny(_target(tmp_path, 2), go_body) is None


def test_prefix_slug_sibling_not_cross_matched(tmp_path):
    # A different slug that shares this slug as a prefix must not satisfy the guard.
    d = _bridge_dir(tmp_path)
    (d / f"{_SLUG}-extra-002.md").write_text("GO\n\n# unrelated\n", encoding="utf-8")
    reason = _gate._no_action_prior_verdict_deny(_target(tmp_path, 2), _NO_ACTION_BODY)
    assert reason is not None, "GO on a prefix-sharing DIFFERENT slug must not allow this NO-ACTION"


# --- integrated deny path ---------------------------------------------------


def test_integrated_deny_blocks_no_action_without_verdict(tmp_path):
    _write_version(tmp_path, 1, "ADVISORY")
    content = """NO-ACTION
bridge_kind: operational_state_change
Document: gtkb-demo-advisory
Version: 002

# Prime disposition

Disposition: NO-ACTION on this advisory thread.
"""
    reason = _gate._deny_reason_for_content(
        cwd_path=tmp_path,
        file_path=_target(tmp_path, 2),
        content=content,
        run_pending_preflight=False,
    )
    assert reason is not None
    assert "NO-ACTION bridge write blocked" in reason
