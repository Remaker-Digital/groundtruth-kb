"""WI-7298 regression coverage for resolvable verdict provenance."""

from __future__ import annotations

import builtins
import re
import runpy
from pathlib import Path

import pytest

from scripts.bridge_author_metadata import (
    PLACEHOLDER_VALUES,
    SYNTHETIC_SESSION_CONTEXT_IDS,
    SYNTHETIC_SESSION_CONTEXT_RE,
    UNRESOLVABLE_SESSION_CONTEXT_ID_PREFIXES,
    is_synthetic_session_context_id,
)

ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / ".harness-baseline-configuration" / "hooks" / "bridge-compliance-gate.py"
AUTHOR_SESSION_RE = re.compile(r"^author_session_context_id:\s*(?P<value>.*?)\s*$", re.IGNORECASE | re.MULTILINE)


def _expected_unresolvable(value: str) -> bool:
    text = value.strip().strip("`")
    lowered = text.lower()
    return (
        lowered in PLACEHOLDER_VALUES
        or lowered in SYNTHETIC_SESSION_CONTEXT_IDS
        or SYNTHETIC_SESSION_CONTEXT_RE.fullmatch(text) is not None
        or any(character.isspace() for character in text)
        or lowered.split("-", 1)[0] in UNRESOLVABLE_SESSION_CONTEXT_ID_PREFIXES
    )


@pytest.mark.parametrize(
    "value",
    [
        "unset-interactive-goose (harness-native session id unavailable)",
        "unset-interactive-goose",
        "unavailable-interactive-harness",
        "unknown-session",
        "missing-context",
        "none-provided",
        "null-context",
        "absent-context",
        "notset-context",
        "nosession-context",
    ],
)
def test_phrase_and_negation_placeholders_are_unresolvable(value: str) -> None:
    assert is_synthetic_session_context_id(value)


@pytest.mark.parametrize(
    "value",
    [
        "01a0436a-62b1-7c92-afa6-76882a435966",
        "G-20260827T0626PDT-lo-goose-opaque",
        "SENV-0211ce093b0044e5b1481b3a9f7528e6",
        "codex-thread-123",
    ],
)
def test_single_token_session_context_ids_remain_resolvable(value: str) -> None:
    assert not is_synthetic_session_context_id(value)


def test_bare_placeholder_class_is_independent_of_metadata_gap_check() -> None:
    for value in PLACEHOLDER_VALUES:
        assert is_synthetic_session_context_id(value)


def test_real_bridge_corpus_has_no_shape_rule_false_positives() -> None:
    values = {
        match.group("value").strip()
        for path in (ROOT / "bridge").glob("*.md")
        for match in AUTHOR_SESSION_RE.finditer(path.read_text(encoding="utf-8", errors="replace"))
    }
    assert len(values) >= 300
    assert any(any(character.isspace() for character in value) for value in values)
    actual = {value for value in values if is_synthetic_session_context_id(value)}
    expected = {value for value in values if _expected_unresolvable(value)}
    assert actual == expected


def test_partial_install_fallback_matches_canonical_predicate(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def fail_canonical_import(name: str, *args: object, **kwargs: object) -> object:
        if name == "scripts.bridge_author_metadata":
            raise ImportError("exercise the bridge-gate partial-install fallback")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_canonical_import)
    namespace = runpy.run_path(str(GATE_PATH), run_name="wi7298_partial_install_gate")
    fallback = namespace["is_synthetic_session_context_id"]
    cases = {
        "",
        "unknown",
        "openrouter-harness-f",
        "ollama-harness-d",
        "unset-interactive-goose",
        "unset-interactive-goose (no native id)",
        "unavailable-context",
        "01a0436a-62b1-7c92-afa6-76882a435966",
        "G-20260827T0626PDT-lo-goose-opaque",
    }
    assert {value: fallback(value) for value in cases} == {
        value: is_synthetic_session_context_id(value) for value in cases
    }


def test_compliance_gate_denies_placeholder_before_publication() -> None:
    namespace = runpy.run_path(str(GATE_PATH), run_name="wi7298_live_gate")
    deny_reason = namespace["_deny_reason_for_content"]
    deny_reason.__globals__["_verdict_self_review_deny"] = lambda *_args, **_kwargs: None
    content = """NO-GO
::init gtkb pb
::open build

author_identity: loyal-opposition/goose
author_harness_id: G
author_session_context_id: unset-interactive-goose (native id unavailable)
author_model: fixture
author_model_version: fixture
author_model_configuration: fixture
"""
    reason = deny_reason(
        cwd_path=ROOT,
        file_path="bridge/wi7298-placeholder-verdict-002.md",
        content=content,
        run_pending_preflight=False,
    )
    assert reason is not None
    assert "real author_session_context_id" in reason
    assert "unset-interactive-goose" in reason
