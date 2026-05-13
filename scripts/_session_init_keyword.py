"""Init-keyword matcher for session-startup symmetry contract.

Authority: bridge `gtkb-loyal-opposition-startup-symmetry-001` GO at -008.
Specs: ADR-SESSION-START-INIT-KEYWORD-CONTRACT-001 (NEW),
DCL-SESSION-START-INIT-KEYWORD-MATCHING-001 (NEW),
DCL-SESSION-START-APP-SCOPE-BINDING-001 (NEW).

Init keyword grammar (canonical):
- Verb forms: ``init``, ``initialize``, ``start``, ``begin``, ``open``.
- Object (mandatory after a verb): one of ``session`` | ``gtkb`` | ``gt-kb`` |
  ``groundtruth-kb`` | ``agent_red`` | ``agent-red`` | ``agent red``.
- Optional ``session`` legacy-phrasing-variant (e.g., ``start gtkb session``).
- Optional ``advisory`` mode suffix.
- Standalone forms: ``GT-KB startup`` | ``GroundTruth-KB startup`` (legacy;
  retained per S337 owner choice). ``advisory`` mode suffix is optional here too.
- Bare verbs (``start``, ``begin``, ``open``, ``init``) DO NOT match per the
  F2-of-002 fix; object is mandatory.

App-scope normalization:
- ``session`` (default) -> ``None`` (uses default work subject).
- ``gtkb`` | ``gt-kb`` | ``groundtruth-kb`` (with optional ``session`` suffix)
  -> ``"gtkb"``.
- ``agent_red`` | ``agent-red`` | ``agent red`` -> ``"agent_red"``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Canonical regex (case-insensitive). Object is mandatory after verbs; bare
# verbs do not match. Standalone form: ``GT-KB startup`` / ``GroundTruth-KB
# startup``. Optional trailing punctuation. Optional ``advisory`` mode suffix.
INIT_KEYWORD_REGEX = re.compile(
    r"""
    ^\s*
    (?:
        # Verb-led form: verb + object [+ legacy 'session'] [+ mode]
        (?:init|initialize|start|begin|open)
        \s+
        (?P<obj>session|gtkb|gt-kb|groundtruth-kb|agent_red|agent-red|agent\s+red)
        (?:\s+session)?
        (?:\s+(?P<mode>advisory))?
        |
        # Standalone legacy phrasings
        (?P<startup>gt-kb|groundtruth-kb)\s+startup
        (?:\s+(?P<mode2>advisory))?
    )
    \s*[.?!]?\s*$
    """,
    re.IGNORECASE | re.VERBOSE | re.UNICODE,
)


@dataclass(frozen=True)
class InitKeywordMatch:
    """Resolved init-keyword match.

    Attributes:
        app_scope: Canonical app-scope key derived from the object. ``None``
            when the object is ``session`` (default work subject); ``"gtkb"``
            for ``gtkb``/``gt-kb``/``groundtruth-kb`` (and the standalone
            ``GT-KB startup`` / ``GroundTruth-KB startup`` legacy phrasings);
            ``"agent_red"`` for ``agent_red``/``agent-red``/``agent red``.
        mode: ``"default"`` (no suffix) or ``"advisory"`` (when ``advisory``
            suffix is present).
    """

    app_scope: str | None
    mode: str


def _normalize_object(raw_obj: str) -> str | None:
    """Map a matched object token to its canonical app-scope key."""
    lowered = re.sub(r"\s+", " ", raw_obj.strip().lower())
    if lowered == "session":
        return None
    if lowered in ("gtkb", "gt-kb", "groundtruth-kb"):
        return "gtkb"
    if lowered in ("agent_red", "agent-red", "agent red"):
        return "agent_red"
    # Defensive: regex matched but normalizer didn't recognize.
    return None


def match_init_keyword(prompt: str) -> InitKeywordMatch | None:
    """Return an ``InitKeywordMatch`` if ``prompt`` is a canonical init keyword.

    Returns ``None`` for non-matching prompts (treated as normal task by the
    UserPromptSubmit gate; disclosure not relayed).
    """
    if not prompt:
        return None
    match = INIT_KEYWORD_REGEX.match(prompt)
    if match is None:
        return None
    if match.group("obj"):
        app_scope = _normalize_object(match.group("obj"))
    elif match.group("startup"):
        # ``GT-KB startup`` / ``GroundTruth-KB startup`` legacy phrasings always
        # bind to gtkb_infrastructure scope.
        app_scope = "gtkb"
    else:
        return None
    mode = match.group("mode") or match.group("mode2") or "default"
    return InitKeywordMatch(app_scope=app_scope, mode=mode.lower())
