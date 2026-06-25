"""Spec-derived tests for write-time + impl-start self-review verdict detection (WI-4829).

Verifies the defense-in-depth self-review gate authorized by DELIB-20266105:
the shared comparator (`scripts/bridge_review_independence.py`), the
verdict-write-time enforcement at the compliance-gate template hook and the verify
`write_verdict` helper, and the impl-start backstop in
`scripts/implementation_authorization.py`. Hermetic: all fixtures live under
pytest ``tmp_path``; no MemBase, no live bridge files, no git.

Authority: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-SELF-REVIEW-WRITE-TIME-GATE-2026-06-25
/ DELIB-20266105; GOV-DOCUMENT-AUTHOR-PROVENANCE-001.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _PROJECT_ROOT / "scripts"
for _p in (_PROJECT_ROOT, _SCRIPTS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import bridge_review_independence as bri  # noqa: E402
import implementation_authorization as ia  # noqa: E402


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, _PROJECT_ROOT / rel)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before exec so @dataclass can resolve cls.__module__ in sys.modules.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_GATE = _load("self_review_gate_under_test", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py")
_WRITE_VERDICT = _load("self_review_write_verdict_under_test", ".claude/skills/verify/helpers/write_verdict.py")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _bridge_file(content: str) -> str:
    return content if content.endswith("\n") else content + "\n"


# --------------------------------------------------------------------------
# Pure comparator (single-sourced refusal semantics)
# --------------------------------------------------------------------------


def test_comparator_equal_sessions_refused():
    assert bri.self_review_reason("S1", "S1") == bri.AUTHOR_MEETS_REVIEWER_REFUSED


def test_comparator_distinct_sessions_independent():
    assert bri.self_review_reason("S1", "S2") is None


def test_comparator_missing_fails_closed():
    assert bri.self_review_reason("S1", "") == bri.AUTHOR_SESSION_CONTEXT_MISSING
    assert bri.self_review_reason("", "S2") == bri.AUTHOR_SESSION_CONTEXT_MISSING
    assert bri.self_review_reason(None, None) == bri.AUTHOR_SESSION_CONTEXT_MISSING


def test_parse_author_session_context_id():
    assert bri.parse_author_session_context_id("GO\nauthor_session_context_id: ABC-1\n") == "ABC-1"
    assert bri.parse_author_session_context_id('GO\nauthor_session_context_id: "Q"\n') == "Q"
    assert bri.parse_author_session_context_id("GO\nno author line here\n") is None


# --------------------------------------------------------------------------
# Reviewed-artifact resolution: Responds-to over latest file
# --------------------------------------------------------------------------


def test_reviewed_artifact_uses_responds_to_over_latest(tmp_path):
    bridge = tmp_path / "bridge"
    _write(bridge / "slug-001.md", _bridge_file("NEW\nauthor_session_context_id: PROP"))
    _write(bridge / "slug-003.md", _bridge_file("NEW\nauthor_session_context_id: REPORT"))
    _write(bridge / "slug-004.md", _bridge_file("GO\nauthor_session_context_id: GO_LO"))
    # VERIFIED -005 reviews report -003, even though GO -004 is the newest file.
    verdict = _bridge_file("VERIFIED\nauthor_session_context_id: VERIF_LO\nResponds to: bridge/slug-003.md")
    resolved = bri.reviewed_artifact_path(verdict, "slug", tmp_path)
    assert resolved is not None and resolved.name == "slug-003.md"


def test_reviewed_artifact_falls_back_to_latest_without_reference(tmp_path):
    bridge = tmp_path / "bridge"
    _write(bridge / "slug-001.md", _bridge_file("NEW\nauthor_session_context_id: PROP"))
    resolved = bri.reviewed_artifact_path("GO\nauthor_session_context_id: LO\n", "slug", tmp_path)
    assert resolved is not None and resolved.name == "slug-001.md"


def test_verdict_self_review_reason_blocks_equal(tmp_path):
    bridge = tmp_path / "bridge"
    _write(bridge / "slug-001.md", _bridge_file("NEW\nauthor_session_context_id: SAME"))
    verdict = _bridge_file("GO\nauthor_session_context_id: SAME\nResponds to: bridge/slug-001.md")
    assert bri.verdict_self_review_reason(verdict, "slug", tmp_path) == bri.AUTHOR_MEETS_REVIEWER_REFUSED


def test_verdict_self_review_reason_independent_passes(tmp_path):
    bridge = tmp_path / "bridge"
    _write(bridge / "slug-001.md", _bridge_file("NEW\nauthor_session_context_id: PROP"))
    verdict = _bridge_file("GO\nauthor_session_context_id: LO\nResponds to: bridge/slug-001.md")
    assert bri.verdict_self_review_reason(verdict, "slug", tmp_path) is None


# --------------------------------------------------------------------------
# Compliance-gate template hook (verdict-write-time, Write-tool path)
# --------------------------------------------------------------------------


def test_compliance_gate_blocks_self_review_verdict(tmp_path, monkeypatch):
    monkeypatch.setattr(_GATE, "_canonical_project_root", lambda _cwd: tmp_path)
    _write(tmp_path / "bridge" / "slug-001.md", _bridge_file("NEW\nauthor_session_context_id: SAME"))
    verdict = _bridge_file("GO\nauthor_session_context_id: SAME\nResponds to: bridge/slug-001.md")
    deny = _GATE._verdict_self_review_deny("bridge/slug-002.md", verdict, tmp_path)
    assert deny is not None and "Self-review" in deny


def test_compliance_gate_allows_independent_verdict(tmp_path, monkeypatch):
    monkeypatch.setattr(_GATE, "_canonical_project_root", lambda _cwd: tmp_path)
    _write(tmp_path / "bridge" / "slug-001.md", _bridge_file("NEW\nauthor_session_context_id: PROP"))
    verdict = _bridge_file("GO\nauthor_session_context_id: LO\nResponds to: bridge/slug-001.md")
    assert _GATE._verdict_self_review_deny("bridge/slug-002.md", verdict, tmp_path) is None


# --------------------------------------------------------------------------
# Verify helper (write_bytes path that bypasses the PreToolUse hook)
# --------------------------------------------------------------------------


def test_write_verdict_refuses_self_review(tmp_path):
    _write(tmp_path / "bridge" / "slug-003.md", _bridge_file("NEW\nauthor_session_context_id: SAME"))
    verdict = _bridge_file("VERIFIED\nauthor_session_context_id: SAME\nResponds to: bridge/slug-003.md")
    with pytest.raises(_WRITE_VERDICT.VerifiedFinalizationError):
        _WRITE_VERDICT._assert_verdict_review_independence("slug", verdict, tmp_path)


def test_write_verdict_allows_independent(tmp_path):
    _write(tmp_path / "bridge" / "slug-003.md", _bridge_file("NEW\nauthor_session_context_id: REPORT"))
    verdict = _bridge_file("VERIFIED\nauthor_session_context_id: LO\nResponds to: bridge/slug-003.md")
    # Must not raise.
    _WRITE_VERDICT._assert_verdict_review_independence("slug", verdict, tmp_path)


# --------------------------------------------------------------------------
# Impl-start backstop
# --------------------------------------------------------------------------


def test_impl_start_refuses_self_review_go(tmp_path):
    go_path = tmp_path / "go.md"
    _write(go_path, _bridge_file("GO\nauthor_session_context_id: SAME"))
    proposal = _bridge_file("NEW\nauthor_session_context_id: SAME")
    with pytest.raises(ia.AuthorizationError):
        ia._go_self_review_error(proposal, go_path)


def test_impl_start_allows_independent_go(tmp_path):
    go_path = tmp_path / "go.md"
    _write(go_path, _bridge_file("GO\nauthor_session_context_id: LO"))
    proposal = _bridge_file("NEW\nauthor_session_context_id: PROP")
    # Must not raise.
    ia._go_self_review_error(proposal, go_path)


def test_impl_start_missing_author_fails_closed(tmp_path):
    go_path = tmp_path / "go.md"
    _write(go_path, _bridge_file("GO\n(no author metadata)"))
    proposal = _bridge_file("NEW\nauthor_session_context_id: PROP")
    with pytest.raises(ia.AuthorizationError):
        ia._go_self_review_error(proposal, go_path)
