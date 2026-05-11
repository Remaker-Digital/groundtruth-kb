# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for `scripts/_session_init_keyword.py`.

Authority: bridge `gtkb-loyal-opposition-startup-symmetry-001` GO at -008,
IP-1 (init-keyword regex + matching helper).

Specs: ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 (NEW),
DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 (NEW),
DCL-SESSION-START-APP-SCOPE-BINDING-001 (NEW).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import _session_init_keyword as ik  # noqa: E402


# ---------------------------------------------------------------------------
# Positive: verb-led forms
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prompt,expected_scope,expected_mode",
    [
        ("init session", None, "default"),
        ("init gtkb", "gtkb", "default"),
        ("init gt-kb", "gtkb", "default"),
        ("init groundtruth-kb", "gtkb", "default"),
        ("start gtkb session", "gtkb", "default"),
        ("start agent_red", "agent_red", "default"),
        ("start agent-red", "agent_red", "default"),
        ("start agent red", "agent_red", "default"),
        ("init gtkb advisory", "gtkb", "advisory"),
        ("start agent_red advisory", "agent_red", "advisory"),
        ("begin gt-kb", "gtkb", "default"),
        ("initialize agent red", "agent_red", "default"),
        ("open groundtruth-kb", "gtkb", "default"),
    ],
)
def test_verb_led_forms_match(prompt: str, expected_scope: str | None, expected_mode: str) -> None:
    result = ik.match_init_keyword(prompt)
    assert result is not None, f"expected match for {prompt!r}"
    assert result.app_scope == expected_scope
    assert result.mode == expected_mode


# ---------------------------------------------------------------------------
# Positive: standalone legacy phrasings
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prompt,expected_mode",
    [
        ("GT-KB startup", "default"),
        ("gt-kb startup", "default"),
        ("GroundTruth-KB startup", "default"),
        ("GT-KB startup advisory", "advisory"),
    ],
)
def test_standalone_legacy_phrasings_match(prompt: str, expected_mode: str) -> None:
    result = ik.match_init_keyword(prompt)
    assert result is not None, f"expected match for {prompt!r}"
    assert result.app_scope == "gtkb"
    assert result.mode == expected_mode


# ---------------------------------------------------------------------------
# Negative: bare verbs (per F2 of -002 fix; object is mandatory)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("prompt", ["start", "begin", "open", "init", "initialize"])
def test_bare_verbs_do_not_match(prompt: str) -> None:
    assert ik.match_init_keyword(prompt) is None, (
        f"bare verb {prompt!r} must not match (per F2 fix; object mandatory)"
    )


# ---------------------------------------------------------------------------
# Negative: ordinary prompts and bridge-dispatch text
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prompt",
    [
        "Hello, what is the status?",
        "Bridge auto-dispatch notification (cross-harness trigger).",
        "Continue working on the proposal.",
        "What does init even mean here?",
        "",
    ],
)
def test_ordinary_prompts_do_not_match(prompt: str) -> None:
    assert ik.match_init_keyword(prompt) is None


# ---------------------------------------------------------------------------
# Punctuation + whitespace tolerance
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prompt",
    [
        "  init gtkb  ",
        "init gtkb.",
        "init gtkb?",
        "INIT GTKB",
        "Init Gtkb",
    ],
)
def test_whitespace_punctuation_case_tolerance(prompt: str) -> None:
    result = ik.match_init_keyword(prompt)
    assert result is not None
    assert result.app_scope == "gtkb"
    assert result.mode == "default"


# ---------------------------------------------------------------------------
# DCL-SESSION-START-APP-SCOPE-BINDING-001: app-scope normalization
# ---------------------------------------------------------------------------


def test_session_object_resolves_to_none_app_scope() -> None:
    """`init session` -> default work subject (app_scope=None)."""
    result = ik.match_init_keyword("init session")
    assert result is not None
    assert result.app_scope is None


def test_gtkb_aliases_normalize_to_gtkb() -> None:
    for alias in ("gtkb", "gt-kb", "groundtruth-kb"):
        result = ik.match_init_keyword(f"init {alias}")
        assert result is not None
        assert result.app_scope == "gtkb"


def test_agent_red_aliases_normalize_to_agent_red() -> None:
    for alias in ("agent_red", "agent-red", "agent red"):
        result = ik.match_init_keyword(f"start {alias}")
        assert result is not None
        assert result.app_scope == "agent_red"
