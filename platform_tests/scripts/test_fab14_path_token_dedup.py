"""FAB-14/WI-4485: PATH_TOKEN_RE is a single canonical source (no drift).

The constant previously had two drifted copies (implementation_start_gate.py vs
bridge_applicability_preflight.py — one carried 'memory/', the other did not).
adr_dcl_applicability_discovery.py later retained a third copy with skills-dir
members but no memory/ member. All live consumers now import the one canonical
object from implementation_authorization, which makes future divergence
structurally impossible (asserted by identity below).
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if _SCRIPTS.is_dir() and str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import adr_dcl_applicability_discovery as add  # noqa: E402
import bridge_applicability_preflight as bap  # noqa: E402
import implementation_authorization as ia  # noqa: E402


def test_path_token_re_is_one_shared_object():
    # bridge_applicability_preflight and adr_dcl_applicability_discovery both
    # import the canonical object; implementation_start_gate's former copy was
    # dead code and is gone.
    assert bap.PATH_TOKEN_RE is ia.PATH_TOKEN_RE
    assert add.PATH_TOKEN_RE is ia.PATH_TOKEN_RE


def test_path_token_re_matches_memory_paths():
    # The canonical pattern includes 'memory/'; the formerly-drifted preflight
    # copy did not — both now agree.
    assert ia.PATH_TOKEN_RE.search("see memory/MEMORY.md for context") is not None


def test_path_token_re_matches_skills_dirs():
    assert ia.PATH_TOKEN_RE.search("review .claude/skills/bridge/SKILL.md") is not None
    assert ia.PATH_TOKEN_RE.search("review .codex/skills/bridge/SKILL.md") is not None


def test_path_token_re_ignores_prose_word_slash_word():
    # Prose 'word/word' tokens (e.g. GO/NO-GO) are not harvested as repo paths.
    assert ia.PATH_TOKEN_RE.search("the verdict was GO/NO-GO today") is None
