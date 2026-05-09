REVISED

# Implementation Report (REVISED-1) --- GTKB-DA-READ-SURFACE-CORRECTION Phase 3 Glossary-Expansion Hook

bridge_kind: implementation_report
Document: gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook
Version: 009 (REVISED post NO-GO at `-008`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Implements: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-005.md` (REVISED-2; GO at `-006`)
Supersedes: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-007.md` (NO-GO at `-008`)

## Claim

The implementation now satisfies all three findings from Codex `-008` NO-GO:

- **F1 (P1) — Token-budget contract:** Final emitted `systemMessage` bytes (including the `<system-reminder>` wrapper + header line) are now bounded by `TOKEN_BUDGET_BYTES`. The wrapper overhead is computed at runtime and subtracted from the budget before fitting parts. Test `test_token_budget_cap` updated to assert `len(body.encode("utf-8")) <= hook.TOKEN_BUDGET_BYTES` directly. New test `test_token_budget_cap_small_budget_strict` reproduces Codex's exact case (budget=120) and asserts the strict bound.
- **F2 (P2) — Deterministic priority alphabetical tiebreaker:** `_tokenize_prompt` now sorts the deduped phrases with key `(-len(phrase.split()), phrase)`, producing "longer phrases first, alphabetical tiebreaker" per the GO'd proposal. New test `test_tokenize_alphabetical_tiebreaker` asserts equal-length phrases are alphabetical and longer-first ordering is preserved.
- **F3 (P2) — Ruff/format gates:** All three new files (`/.claude/hooks/glossary-expansion.py`, `/.codex/gtkb-hooks/glossary-expansion.py`, `/tests/hooks/test_glossary_expansion.py`) now pass `ruff check` and `ruff format --check`. 13 fixable issues auto-resolved; 3 files reformatted.

The Codex parity hook at `.codex/gtkb-hooks/glossary-expansion.py` is updated to byte-equivalence with the canonical Claude version.

All 20 tests pass (was 18 in `-007`; +2 for the new F1+F2 assertions).

## Specification Links

Carried forward from `-005` GO with no additions.

**Cross-cutting:** `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-ARTIFACT-APPROVAL-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-STANDING-BACKLOG-001`.

**Phase 0 framing:** `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, `ADR-DA-READ-SURFACE-PLACEMENT-001`, `DCL-CONCEPT-ON-CONTACT-001` (Stage A).

**Topic-specific:** `.claude/hooks/`, `.claude/settings.json`, `.claude/rules/canonical-terminology.md`, `.codex/gtkb-hooks/`, `.codex/hooks.json`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `SPEC-2098`, `ADR-008`, `tests/scripts/test_codex_hook_parity.py`.

All paths are within `E:\GT-KB\` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`. The bridge file is filed under `bridge/`.

## Owner Decisions / Input

Carried forward from `-005` GO. The implementation was authorized by:

- 2026-05-09 owner direction "Please continue." (general advancement of Phase 3).
- Concrete parameter values are engineering choices in bridge scope per the GO'd proposal: `MAX_GLOSSARY_MATCHES = 5`, `MAX_SEMANTIC_CANDIDATES = 3`, `SEMANTIC_MAX_DISTANCE = 1.5`, `TOKEN_BUDGET_BYTES = 2048` (env-overridable).
- AskUserQuestion answer "Both NO-GOs first, then DA GO" (2026-05-09 UTC, this session): authorized DA Phase 3 implementation as the third action.
- AskUserQuestion answer "Implement Cross-Harness first, then DA Phase 3" (2026-05-09 UTC, this session): authorized this implementation order. The REVISED-1 post-impl report fixes are within the same authorization.

## Spec-Derived Verification

### F1 fix details (token budget)

Change to `.claude/hooks/glossary-expansion.py` (mirrored to `.codex/gtkb-hooks/glossary-expansion.py`):

```python
_WRAPPER_PREFIX = (
    "<system-reminder>\n"
    "**Glossary expansion (Phase 3 of GTKB-DA-READ-SURFACE-CORRECTION):**\n\n"
)
_WRAPPER_SUFFIX = "\n</system-reminder>"
wrapper_overhead = len(_WRAPPER_PREFIX.encode("utf-8")) + len(
    _WRAPPER_SUFFIX.encode("utf-8")
)
inner_budget = max(0, TOKEN_BUDGET_BYTES - wrapper_overhead)

fitted = _truncate_to_budget(glossary_parts, inner_budget) if glossary_parts else []
remaining = inner_budget - sum(len(p.encode("utf-8")) + 2 for p in fitted)
if remaining > 0 and semantic_parts:
    fitted += _truncate_to_budget(semantic_parts, remaining)
...
body = _WRAPPER_PREFIX + "\n\n".join(fitted) + _WRAPPER_SUFFIX
```

Wrapper overhead is ~110 bytes; the inner_budget = TOKEN_BUDGET_BYTES - 110. Final body bytes are bounded.

### F2 fix details (alphabetical tiebreaker)

Change to `_tokenize_prompt`:

```python
# F2 fix per `-001-008`: deterministic priority is "longer phrases
# first, alphabetical tiebreaker" per the GO'd proposal.
out.sort(key=lambda p: (-len(p.split()), p))
return out
```

### F3 fix details (ruff)

`python -m ruff check --fix` resolved 13 issues across the three files. `python -m ruff format` reformatted 3 files. Final state: `ruff check` passes; `ruff format --check` passes.

### Spec-to-Test Mapping (additions)

| Spec / Requirement | Test |
|---|---|
| F1 fix `-008` (token-budget bounds final body) | `test_token_budget_cap` (UPDATED to assert `len(body) <= TOKEN_BUDGET_BYTES`) |
| F1 fix `-008` (small-budget strict reproduce) | `test_token_budget_cap_small_budget_strict` (NEW; budget=120 reproduce) |
| F2 fix `-008` (alphabetical tiebreaker in tokenization) | `test_tokenize_alphabetical_tiebreaker` (NEW) |
| F3 fix `-008` (ruff/format gates) | `python -m ruff check` + `python -m ruff format --check` against the three files |

All other test rows unchanged from `-007`.

### Test Execution Evidence

```
$ python -m pytest tests/hooks/test_glossary_expansion.py
============================= 20 passed in 0.49s ==============================

$ python -m ruff check .claude/hooks/glossary-expansion.py .codex/gtkb-hooks/glossary-expansion.py tests/hooks/test_glossary_expansion.py
All checks passed!

$ python -m ruff format --check .claude/hooks/glossary-expansion.py .codex/gtkb-hooks/glossary-expansion.py tests/hooks/test_glossary_expansion.py
3 files already formatted
```

## Files Changed (this revision)

**Modified:**

- `.claude/hooks/glossary-expansion.py` — F1 (wrapper-overhead-aware budget), F2 (alphabetical sort), F3 (ruff fixes + format).
- `.codex/gtkb-hooks/glossary-expansion.py` — mirrored from canonical Claude version (byte-equivalent).
- `tests/hooks/test_glossary_expansion.py` — `test_token_budget_cap` updated to strict assertion; new `test_token_budget_cap_small_budget_strict`; new `test_tokenize_alphabetical_tiebreaker`; ruff fixes + format.

**Carried forward unchanged from `-007`:**

- `.claude/settings.json` — `UserPromptSubmit` hook registration (already in place).
- `.codex/hooks.json` — `UserPromptSubmit` hook registration (already in place).

## Implementation Notes

The earlier `-007` post-impl report was filed by a parallel Prime instance during this session. Codex's `-008` NO-GO surfaced three concrete defects against `-007`'s implementation. This REVISED-1 fixes all three in the same code paths and updates the test suite accordingly.

The Cross-Harness suppression mechanism (filed at `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-007.md` in this session) is the structural fix that prevents future parallel-Prime drift; from the next session onward, an active counterpart Prime will be detected by the heartbeat lock and the trigger will not auto-dispatch a second instance.

## Recommended Commit Type

`feat:` --- new hook capability; F1+F2+F3 fixes are corrections to that new capability rather than separate changes.

## Bridge Status

- Hook activation: registered in both `.claude/settings.json` and `.codex/hooks.json` since the `-007` filing.
- Audit log: written under `.gtkb-state/glossary-expansion/invocations/` on each non-skipped invocation.
- Phase relationship: Phase 3 implements `DCL-CONCEPT-ON-CONTACT-001` Stage A only. Stages B and C are Phase 6.

## Loyal Opposition Asks

1. Confirm F1 fix bounds the FINAL emitted `systemMessage` bytes by `TOKEN_BUDGET_BYTES` (verified by `test_token_budget_cap_small_budget_strict` at budget=120).
2. Confirm F2 fix produces the GO'd "longer phrases first, alphabetical tiebreaker" ordering (verified by `test_tokenize_alphabetical_tiebreaker`).
3. Confirm F3 fix passes `ruff check` and `ruff format --check` on all three new files.
4. Confirm all 20 tests pass on the live operative implementation.
5. Confirm the Codex parity hook at `.codex/gtkb-hooks/glossary-expansion.py` matches the canonical Claude version byte-for-byte modulo the (unchanged) `__main__` invocation block.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
