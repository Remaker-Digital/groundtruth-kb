# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the canonical init-keyword regex syntax.

Authority: bridge/gtkb-canonical-init-keyword-syntax-001-005.md IP-8 surface 1
(Codex GO at -008). Specs:

- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 — regex ``^::init gtkb (pb|lo)$``;
  first-line-only; closed vocabulary ``{pb, lo}``; no synonyms; strict parse.

These tests pin the exact syntax against three concrete locations where the
regex is defined identically:

- ``scripts/cross_harness_bridge_trigger.py`` (emitter side, derives mode
  from ``DispatchTarget.canonical_mode``).
- ``.claude/hooks/session_start_dispatch.py`` (Claude receiver).
- ``.codex/gtkb-hooks/session_start_dispatch.py`` (Codex receiver).

The pin matters: any drift between emitter and either receiver breaks the
strict-parse semantic and produces dispatch audit noise indistinguishable from
drift in the durable role map.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLAUDE_HOOK_PATH = PROJECT_ROOT / ".claude" / "hooks" / "session_start_dispatch.py"
CODEX_HOOK_PATH = PROJECT_ROOT / ".codex" / "gtkb-hooks" / "session_start_dispatch.py"
TRIGGER_PATH = PROJECT_ROOT / "scripts" / "cross_harness_bridge_trigger.py"


def _load_module(name: str, path: Path) -> ModuleType:
    """Load a Python file as a module without polluting sys.modules conflicts."""
    assert path.is_file(), f"Missing module file: {path}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _claude_hook() -> ModuleType:
    return _load_module("claude_session_start_dispatch_syntax", CLAUDE_HOOK_PATH)


def _codex_hook() -> ModuleType:
    return _load_module("codex_session_start_dispatch_syntax", CODEX_HOOK_PATH)


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-syntax-parser-valid
# ──────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "keyword,expected_mode",
    [
        ("::init gtkb pb", "pb"),
        ("::init gtkb lo", "lo"),
    ],
)
def test_valid_forms_accepted_claude(keyword: str, expected_mode: str) -> None:
    """SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 regex accepts both modes (Claude side)."""
    hook = _claude_hook()
    match = hook._CANONICAL_KEYWORD_RE.match(keyword)
    assert match is not None, f"Claude regex rejected valid form {keyword!r}"
    assert match.group(1) == expected_mode


@pytest.mark.parametrize(
    "keyword,expected_mode",
    [
        ("::init gtkb pb", "pb"),
        ("::init gtkb lo", "lo"),
    ],
)
def test_valid_forms_accepted_codex(keyword: str, expected_mode: str) -> None:
    """SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 regex accepts both modes (Codex side)."""
    hook = _codex_hook()
    match = hook._CANONICAL_KEYWORD_RE.match(keyword)
    assert match is not None, f"Codex regex rejected valid form {keyword!r}"
    assert match.group(1) == expected_mode


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-syntax-parser-invalid
# ──────────────────────────────────────────────────────────────────────────


_INVALID_FORMS = [
    # Wrong mode vocabulary (closed set is {pb, lo}; no synonyms).
    "::init gtkb prime",
    "::init gtkb loyal",
    "::init gtkb prime-builder",
    "::init gtkb loyal-opposition",
    "::init gtkb default",
    "::init gtkb advisory",
    "::init gtkb status",
    "::init gtkb ",
    "::init gtkb",
    "::init gtkb x",
    # Case variants (strict-parse; lowercase only).
    "::INIT GTKB PB",
    "::Init Gtkb Pb",
    "::init GTKB pb",
    "::init gtkb PB",
    # Whitespace variants (no leading/trailing/internal extra whitespace).
    " ::init gtkb pb",
    "::init gtkb pb ",
    "::init  gtkb pb",
    "::init gtkb  pb",
    "::init\tgtkb\tpb",
    # Wrong product / namespace.
    "::init agent_red pb",
    "::init session pb",
    "::start gtkb pb",
    "::gtkb pb",
    "::init gtkb-app pb",
    # Missing prefix (the namespace marker ``::`` is required).
    "init gtkb pb",
    ":init gtkb pb",
    ":::init gtkb pb",
    # Extra trailing content (regex uses ``$`` so first-line-only is strict).
    "::init gtkb pb extra",
    "::init gtkb pb\nfollow-up",
    "::init gtkb pb;",
    "::init gtkb pb.",
    # Empty / garbage.
    "",
    " ",
    "::",
    "::init",
    "random text",
]


@pytest.mark.parametrize("keyword", _INVALID_FORMS)
def test_invalid_forms_rejected_claude(keyword: str) -> None:
    """SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 strict-parse rejects synonyms,
    case variants, whitespace variants, and out-of-vocabulary modes."""
    hook = _claude_hook()
    match = hook._CANONICAL_KEYWORD_RE.match(keyword)
    assert match is None, (
        f"Claude regex INCORRECTLY accepted invalid form {keyword!r}; "
        f"closed vocabulary is {{pb, lo}} with strict-parse semantic."
    )


@pytest.mark.parametrize("keyword", _INVALID_FORMS)
def test_invalid_forms_rejected_codex(keyword: str) -> None:
    """SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 strict-parse rejects synonyms,
    case variants, whitespace variants, and out-of-vocabulary modes (Codex)."""
    hook = _codex_hook()
    match = hook._CANONICAL_KEYWORD_RE.match(keyword)
    assert match is None, (
        f"Codex regex INCORRECTLY accepted invalid form {keyword!r}; "
        f"closed vocabulary is {{pb, lo}} with strict-parse semantic."
    )


# ──────────────────────────────────────────────────────────────────────────
# T-CIK-emitter-receiver-regex-parity
# ──────────────────────────────────────────────────────────────────────────


def test_emitter_keyword_matches_receiver_regex() -> None:
    """The trigger's emitted canonical keyword MUST satisfy the receiver's regex.

    Source of truth: ``DispatchTarget.canonical_mode`` is one of
    ``_LABEL_TO_CANONICAL_MODE.values()`` per the trigger. The receiver's
    regex must accept every such emission verbatim. Drift between emitter
    vocabulary and receiver vocabulary would silently break dispatch.
    """
    trigger = _load_module("cross_harness_bridge_trigger_syntax", TRIGGER_PATH)
    claude_hook = _claude_hook()
    codex_hook = _codex_hook()

    for label, mode in trigger._LABEL_TO_CANONICAL_MODE.items():
        emitted = f"::init gtkb {mode}"
        m_claude = claude_hook._CANONICAL_KEYWORD_RE.match(emitted)
        m_codex = codex_hook._CANONICAL_KEYWORD_RE.match(emitted)
        assert m_claude is not None, (
            f"Claude regex does not accept emitter output for label {label!r} (mode {mode!r}, emitted {emitted!r})"
        )
        assert m_codex is not None, (
            f"Codex regex does not accept emitter output for label {label!r} (mode {mode!r}, emitted {emitted!r})"
        )
        assert m_claude.group(1) == mode
        assert m_codex.group(1) == mode


def test_claude_and_codex_regex_patterns_identical() -> None:
    """Both receiver hooks must compile the IDENTICAL regex source string.

    Anchors the cross-harness parity invariant from
    DCL-CROSS-HARNESS-ENFORCEMENT-001: receiver enforcement must apply
    symmetrically.
    """
    claude_hook = _claude_hook()
    codex_hook = _codex_hook()
    assert claude_hook._CANONICAL_KEYWORD_RE.pattern == codex_hook._CANONICAL_KEYWORD_RE.pattern
    # Pin the exact string so reviewers see at-a-glance what is being tested.
    assert claude_hook._CANONICAL_KEYWORD_RE.pattern == r"^::init gtkb (pb|lo)$"


def test_regex_is_first_line_only() -> None:
    """The regex MUST anchor with ``^`` and ``$`` (first-line-only / no internal newlines).

    SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001: "first-line-only" semantic.
    Without anchoring, a multi-line prompt with the keyword somewhere in
    the body would match — that would invert the contract.
    """
    hook = _claude_hook()
    pattern = hook._CANONICAL_KEYWORD_RE.pattern
    assert pattern.startswith("^"), f"regex missing ``^`` anchor: {pattern!r}"
    assert pattern.endswith("$"), f"regex missing ``$`` anchor: {pattern!r}"
    # And re.match with a leading newline must reject the keyword (the regex
    # is applied to the first line literally; a leading newline indicates
    # the keyword is not first).
    assert hook._CANONICAL_KEYWORD_RE.match("\n::init gtkb pb") is None
    # re.match with embedded newline before keyword also rejects.
    assert hook._CANONICAL_KEYWORD_RE.match("garbage\n::init gtkb pb") is None
