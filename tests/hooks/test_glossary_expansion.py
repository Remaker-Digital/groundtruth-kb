# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for Phase 3 of GTKB-DA-READ-SURFACE-CORRECTION.

Coverage matches the test plan in
``bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-005.md``:

1.  S331-replay regression — prompt with "isolation" → glossary entry injected.
2.  Multi-term match (cap respected) — 7+ terms → ≤ MAX_GLOSSARY_MATCHES.
3.  Concept-shaped non-match → DA candidate (fake DB).
4.  Semantic-search cap — many concept-shaped phrases → ≤ MAX_SEMANTIC_CANDIDATES calls.
5.  Distance-threshold filter (F1 of -004 fix) — low-distance accepted, high-distance rejected, text-match fallback handled.
6.  Token-budget cap — output ≤ TOKEN_BUDGET_BYTES.
7.  Output contract — JSON parses to {} or {"systemMessage": ...}.
8.  No-match — stop-word-only prompt → {}.
9.  DA-failure graceful degradation — fake DB raises → glossary still injected.
10. Skip rules — each prefix → {}.
11. Audit log schema.
12. Codex parity (extended ``tests/scripts/test_codex_hook_parity.py``).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "glossary-expansion.py"
CODEX_HOOK_PATH = REPO_ROOT / ".codex" / "gtkb-hooks" / "glossary-expansion.py"
GLOSSARY_PATH = REPO_ROOT / ".claude" / "rules" / "canonical-terminology.md"


def _load_hook_module(monkeypatch=None, audit_dir: Path | None = None):
    """Load the hook module by file path (it is not on sys.path)."""
    sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
    spec = importlib.util.spec_from_file_location("glossary_expansion_under_test", HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if audit_dir is not None:
        module.AUDIT_LOG_DIR = audit_dir
    # Reset glossary index cache between tests so monkeypatched glossary paths
    # are honored.
    module._GLOSSARY_INDEX_CACHE["mtime"] = None
    module._GLOSSARY_INDEX_CACHE["index"] = {}
    module._GLOSSARY_INDEX_CACHE["entries"] = {}
    return module


@pytest.fixture
def hook(tmp_path):
    return _load_hook_module(audit_dir=tmp_path / "invocations")


# --------------------------------------------------------------------------
# Test 1 — S331-replay regression
# --------------------------------------------------------------------------


def test_s331_replay_isolation_injects_glossary_entry(hook, monkeypatch):
    """Prompt mentioning 'isolation' must inject the isolation glossary entry."""
    monkeypatch.setenv("GTKB_GLOSSARY_EXPANSION_DB", "false")  # focus on glossary path
    result = hook._process("Please review the GT-KB isolation work and confirm next steps.")
    assert "systemMessage" in result, f"Expected systemMessage; got {result!r}"
    body = result["systemMessage"]
    assert "<system-reminder>" in body
    assert "Glossary expansion" in body
    assert "### isolation" in body
    assert "Full-lifecycle independence" in body  # snippet from the entry's Definition


# --------------------------------------------------------------------------
# Test 2 — Multi-term match cap respected
# --------------------------------------------------------------------------


def test_multi_term_match_cap_respected(hook, monkeypatch):
    """Many glossary terms → at most MAX_GLOSSARY_MATCHES injected."""
    monkeypatch.setenv("GTKB_GLOSSARY_EXPANSION_DB", "false")
    prompt = (
        "Discussion of isolation, placement, bias case, salience case, harness, "
        "harness identity, role assignment, bridge thread, applicability preflight, "
        "doctor, AskUserQuestion."
    )
    result = hook._process(prompt)
    assert "systemMessage" in result
    body = result["systemMessage"]
    heading_count = body.count("\n### ")
    assert heading_count <= hook.MAX_GLOSSARY_MATCHES, (
        f"Expected at most {hook.MAX_GLOSSARY_MATCHES} ### headings; got {heading_count}"
    )


# --------------------------------------------------------------------------
# Test 3 + 4 — Concept-shaped non-match → DA candidate; semantic cap
# --------------------------------------------------------------------------


class _FakeDB:
    """Fake KnowledgeDB exposing search_deliberations with controlled results."""

    def __init__(self, results_per_phrase: dict[str, list[dict]] | None = None, raise_on_query: bool = False):
        self._results = results_per_phrase or {}
        self._raise = raise_on_query
        self.calls: list[tuple[str, int]] = []

    def search_deliberations(self, query: str, *, limit: int = 5):
        self.calls.append((query, limit))
        if self._raise:
            raise RuntimeError("fake DB failure")
        return self._results.get(query, self._results.get("*", []))


def test_concept_shaped_non_match_emits_candidate(hook, monkeypatch):
    """A concept-shaped non-match phrase reaches semantic search and surfaces
    as a [candidate for promotion] bullet."""
    fake_db = _FakeDB(
        results_per_phrase={
            "*": [
                {
                    "id": "DELIB-FAKE-100",
                    "title": "Fake match A",
                    "search_method": "semantic",
                    "score": 0.5,
                },
            ],
        }
    )
    monkeypatch.setattr(hook, "_try_open_default_db", lambda: fake_db)
    # Concept-shaped phrase (>= 8 chars or >= 2 words) that won't match the glossary.
    result = hook._process("What is xenoblastic recursion in modern systems? Need analysis.")
    assert "systemMessage" in result, f"Expected systemMessage; got {result!r}"
    body = result["systemMessage"]
    assert "[candidate for promotion]" in body
    assert "DELIB-FAKE-100" in body
    assert len(fake_db.calls) > 0
    assert len(fake_db.calls) <= hook.MAX_SEMANTIC_CANDIDATES


def test_semantic_search_cap(hook, monkeypatch):
    """Many concept-shaped non-matches → at most MAX_SEMANTIC_CANDIDATES calls."""
    fake_db = _FakeDB(results_per_phrase={"*": []})
    monkeypatch.setattr(hook, "_try_open_default_db", lambda: fake_db)
    # 10+ concept-shaped phrases (each ≥ 8 chars).
    prompt = "alphafoo betagamma deltatron epsilonix zetaomega etaprime thetabeta iotacent kappadelta lambdamicron."
    hook._process(prompt)
    assert len(fake_db.calls) <= hook.MAX_SEMANTIC_CANDIDATES, (
        f"Expected ≤ {hook.MAX_SEMANTIC_CANDIDATES} calls; got {len(fake_db.calls)}"
    )


def test_tokenize_alphabetical_tiebreaker(hook):
    """F2 fix per `-001-008`: within the tokenizer output, equal-length phrases must be alphabetical.

    Per the GO'd proposal: deterministic priority is "longer phrases
    first, alphabetical tiebreaker". Earlier implementation produced
    prompt-order tiebreaker, which Codex flagged as a deviation.
    """
    # Non-alphabetical word order: zzz, mmm, aaa.
    prompt = "zzzulu mmmike aaalpha bbbravo"
    phrases = hook._tokenize_prompt(prompt)
    # Group by length (in word count).
    by_length: dict[int, list[str]] = {}
    for p in phrases:
        by_length.setdefault(len(p.split()), []).append(p)
    # Every length group must be alphabetically sorted.
    for n, group in by_length.items():
        assert group == sorted(group), f"Length-{n} phrases not alphabetical: {group!r}"
    # Longer phrases must come BEFORE shorter ones in the overall list.
    lengths_in_order = [len(p.split()) for p in phrases]
    assert lengths_in_order == sorted(lengths_in_order, reverse=True), (
        f"Tokenizer output not in length-descending order: {lengths_in_order!r}"
    )


# --------------------------------------------------------------------------
# Test 5 — Distance-threshold filter (F1 of -004 fix)
# --------------------------------------------------------------------------


def test_distance_threshold_low_high_and_text_fallback(hook, monkeypatch):
    """Low distance accepted; high distance rejected; text-match fallback handled."""
    fake_db = _FakeDB(
        results_per_phrase={
            "*": [
                {"id": "DELIB-LOW-001", "title": "Low distance hit", "search_method": "semantic", "score": 0.5},
                {"id": "DELIB-HIGH-001", "title": "Too far", "search_method": "semantic", "score": 2.5},
                {"id": "DELIB-TEXT-001", "title": "Text match fallback", "search_method": "text_match", "score": None},
            ],
        }
    )
    monkeypatch.setattr(hook, "_try_open_default_db", lambda: fake_db)
    result = hook._process("xenoblastic recursion in modern systems")
    body = result.get("systemMessage", "")
    assert "DELIB-LOW-001" in body, "Low-distance hit should be accepted"
    assert "DELIB-HIGH-001" not in body, "High-distance hit should be rejected"
    assert "DELIB-TEXT-001" in body, "Text-match-fallback row should be accepted"
    assert "(distance ≈" in body, "Semantic row should render with distance label"
    assert "(text-match fallback)" in body, "Text-match row should render with fallback label"
    assert "similarity" not in body, "Distance must not be labeled as similarity"


# --------------------------------------------------------------------------
# Test 6 — Token-budget cap
# --------------------------------------------------------------------------


def test_token_budget_cap(hook, monkeypatch):
    """Output (final emitted systemMessage including wrapper) is bounded by TOKEN_BUDGET_BYTES.

    Per F1 of `-001-008`: the cap must apply to the FINAL emitted bytes,
    not just the inner parts. Using a small budget proves the wrapper
    overhead is accounted for.
    """
    monkeypatch.setenv("GTKB_GLOSSARY_EXPANSION_DB", "false")
    monkeypatch.setattr(hook, "TOKEN_BUDGET_BYTES", 500)
    # Hit many glossary terms; each entry is sizable.
    prompt = (
        "isolation placement bias case salience case harness harness identity "
        "role assignment bridge thread applicability preflight"
    )
    result = hook._process(prompt)
    body = result.get("systemMessage", "")
    # F1 fix: the FINAL body bytes (including <system-reminder> wrapper +
    # header line) must be <= TOKEN_BUDGET_BYTES.
    assert len(body.encode("utf-8")) <= hook.TOKEN_BUDGET_BYTES, (
        f"body is {len(body.encode('utf-8'))} bytes, budget is {hook.TOKEN_BUDGET_BYTES}"
    )


def test_token_budget_cap_small_budget_strict(hook, monkeypatch):
    """F1 fix: even with a very small budget, the FINAL body bytes are bounded.

    Codex's reproduce: budget=120 → previously body=128 (8 bytes over).
    After the F1 fix, the body must be <= 120 OR the hook must emit
    empty {} when no part fits within the inner budget.
    """
    monkeypatch.setenv("GTKB_GLOSSARY_EXPANSION_DB", "false")
    monkeypatch.setattr(hook, "TOKEN_BUDGET_BYTES", 120)
    prompt = "isolation placement bias case salience"
    result = hook._process(prompt)
    body = result.get("systemMessage", "")
    if body:
        assert len(body.encode("utf-8")) <= hook.TOKEN_BUDGET_BYTES, (
            f"body is {len(body.encode('utf-8'))} bytes, budget is {hook.TOKEN_BUDGET_BYTES}"
        )


# --------------------------------------------------------------------------
# Test 7 — Output contract
# --------------------------------------------------------------------------


def test_output_contract_json_shape(hook, monkeypatch, tmp_path):
    """Hook output must parse as JSON and be either {} or {"systemMessage": ...}."""
    monkeypatch.setenv("GTKB_GLOSSARY_EXPANSION_DB", "false")
    # No-match prompt → {}.
    out = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps({"prompt": "the and of to for with as that in"}),
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "GTKB_GLOSSARY_EXPANSION_DB": "false", "CLAUDE_PROJECT_DIR": str(REPO_ROOT)},
    )
    assert out.returncode == 0
    data = json.loads(out.stdout)
    assert data == {} or (isinstance(data, dict) and set(data.keys()) == {"systemMessage"})
    # Match prompt → {"systemMessage": ...}.
    out2 = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps({"prompt": "Discuss the GT-KB isolation work please."}),
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "GTKB_GLOSSARY_EXPANSION_DB": "false", "CLAUDE_PROJECT_DIR": str(REPO_ROOT)},
    )
    assert out2.returncode == 0
    data2 = json.loads(out2.stdout)
    assert isinstance(data2, dict)
    assert set(data2.keys()) == {"systemMessage"}
    assert isinstance(data2["systemMessage"], str)
    assert data2["systemMessage"]


# --------------------------------------------------------------------------
# Test 8 — No-match
# --------------------------------------------------------------------------


def test_no_match_returns_empty(hook, monkeypatch):
    """Prompt with no glossary terms and no concept-shaped phrases → {}."""
    monkeypatch.setenv("GTKB_GLOSSARY_EXPANSION_DB", "false")
    # All-stop-word prompt over 20 chars.
    result = hook._process("the and of to for with as the and of to for")
    assert result == {}


# --------------------------------------------------------------------------
# Test 9 — DA-failure graceful degradation
# --------------------------------------------------------------------------


def test_da_failure_graceful_degradation(hook, monkeypatch):
    """When the fake DB raises, glossary matches are still injected."""
    fake_db = _FakeDB(raise_on_query=True)
    monkeypatch.setattr(hook, "_try_open_default_db", lambda: fake_db)
    result = hook._process("Discuss the GT-KB isolation context here.")
    assert "systemMessage" in result
    body = result["systemMessage"]
    assert "### isolation" in body  # glossary still injected
    # No exception escaped.


# --------------------------------------------------------------------------
# Test 10 — Skip rules
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prefix",
    [
        "Generate 0 to ",
        "Bridge auto-dispatch",
        "File bridge scan:",
        "Smart-poller notification",
        "Codex skill adapters:",
    ],
)
def test_skip_prefixes(hook, monkeypatch, prefix):
    """Prompts starting with a skip prefix → {} (no glossary processing, no DA call)."""
    fake_db = _FakeDB()
    monkeypatch.setattr(hook, "_try_open_default_db", lambda: fake_db)
    prompt = prefix + " ".join(["isolation"] * 5)  # would otherwise match
    result = hook._process(prompt)
    assert result == {}, f"Skip prefix {prefix!r} did not skip"
    assert len(fake_db.calls) == 0


def test_skip_short_prompt(hook, monkeypatch):
    """Prompts < 20 chars are skipped."""
    monkeypatch.setenv("GTKB_GLOSSARY_EXPANSION_DB", "false")
    result = hook._process("isolation here")  # 15 chars, would otherwise match
    assert result == {}


# --------------------------------------------------------------------------
# Test 11 — Audit log schema
# --------------------------------------------------------------------------


def test_audit_log_schema(hook, tmp_path, monkeypatch):
    """Audit log file is written with all expected fields."""
    audit_dir = tmp_path / "invocations"
    monkeypatch.setattr(hook, "AUDIT_LOG_DIR", audit_dir)
    monkeypatch.setenv("GTKB_GLOSSARY_EXPANSION_DB", "false")
    hook._process("Discuss the GT-KB isolation context here.")
    files = list(audit_dir.glob("*.json"))
    assert files, "Expected at least one audit log file"
    log = json.loads(files[0].read_text(encoding="utf-8"))
    expected_fields = {
        "timestamp",
        "prompt_hash",
        "prompt_length",
        "skipped",
        "skip_reason",
        "matched_glossary_terms",
        "candidate_phrases_forwarded",
        "semantic_hit_ids",
        "semantic_search_attempted",
        "injection_size_bytes",
        "caps",
    }
    missing = expected_fields - set(log)
    assert not missing, f"Audit log missing fields: {missing}"
    assert "MAX_GLOSSARY_MATCHES" in log["caps"]
    assert "SEMANTIC_MAX_DISTANCE" in log["caps"]


# --------------------------------------------------------------------------
# Test 12 — Codex parity surface
# --------------------------------------------------------------------------


def test_codex_parity_hook_exists_with_same_constants():
    """Codex hook template exists and contains the same caps/threshold constants."""
    assert CODEX_HOOK_PATH.exists(), f"Codex hook missing at {CODEX_HOOK_PATH}"
    canon_text = HOOK_PATH.read_text(encoding="utf-8")
    codex_text = CODEX_HOOK_PATH.read_text(encoding="utf-8")
    for token in (
        "MAX_GLOSSARY_MATCHES",
        "MAX_SEMANTIC_CANDIDATES",
        "SEMANTIC_MAX_DISTANCE",
        "TOKEN_BUDGET_BYTES",
        "_try_open_default_db",
        "SKIP_PROMPT_PREFIXES" if False else "_skip_prefixes",
    ):
        assert token in canon_text, f"{token} missing from canonical hook"
        assert token in codex_text, f"{token} missing from Codex parity hook"


def test_settings_json_registers_hook():
    """The Claude settings.json registers the hook in UserPromptSubmit."""
    settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    ups = settings["hooks"]["UserPromptSubmit"][0]["hooks"]
    commands = [h.get("command", "") for h in ups]
    assert any("glossary-expansion.py" in c for c in commands), (
        f"glossary-expansion.py not registered in UserPromptSubmit; commands: {commands}"
    )
