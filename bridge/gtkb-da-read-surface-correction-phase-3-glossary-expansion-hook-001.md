# Implementation Proposal — GTKB-DA-READ-SURFACE-CORRECTION Phase 3: UserPromptSubmit Glossary-Expansion Hook

- Status: NEW
- Date: 2026-05-09
- Session: S331 (continuation)
- Author: Prime Builder (Claude Code, harness B)
- bridge_kind: prime_implementation_proposal
- Umbrella work item: `GTKB-DA-READ-SURFACE-CORRECTION` (Phase 3 of multi-phase plan; implements `DCL-CONCEPT-ON-CONTACT-001` Stage A — owner-prompt detection. Stages B and C are deferred to Phase 6.)
- Depends on: Phase 0 VERIFIED (`-006`); Phase 1 VERIFIED (`-010`) — the canonical-terminology glossary now contains the load-bearing concepts the hook will index; Phase 2 VERIFIED (`-008`) — establishes the auto-DB-open + graceful-degradation pattern this hook reuses.

## Summary

Install a `UserPromptSubmit` hook (`.claude/hooks/glossary-expansion.py`) that detects keyword overlap between the owner's prompt and glossary terms and injects matched glossary entries as `<system-reminder>` context. For prompt tokens that do NOT match the glossary but appear concept-shaped, a low-threshold semantic search against the Deliberation Archive produces candidate prior-deliberation entries flagged as "candidate for glossary promotion".

The hook is **not a gate**: it does not block, it surfaces. Failure modes are bounded by token-budget cap, similarity threshold, and graceful-degradation fallback. This is the long-tail catch path described in the S331 plan as Tier 3 — the safety net for concepts the glossary has not yet absorbed.

A Codex parity template is installed at `.codex/gtkb-hooks/glossary-expansion.py` per `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (forward-compatible; not live on Windows). `.codex/hooks.json` registers the hook intent; `tests/scripts/test_codex_hook_parity.py` is extended to cover the new hook.

## Specification Links

Cross-cutting:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (path-trigger via rule-file references; no scope conflict — Phase 3 reads `.claude/rules/canonical-terminology.md` but does not modify it)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001` — Phase 3 modifies `.claude/settings.json` and `.codex/hooks.json` to register the new hook. Per `config/governance/narrative-artifact-approval.toml` excluded-by-design list, `.claude/rules/*.toml` and `.claude/hooks/*.py` are NOT in the protected narrative-artifact set; settings.json is also outside the protected set. So Phase 3 does NOT require a narrative-artifact approval packet — direct Write paths are governed by `scanner-safe-writer` and the bridge protocol's normal GO/VERIFIED cycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

Phase 0 framing:

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — Phase 3 implements the auto-injection placement target (the third placement surface after glossary-load and bridge-template).
- `ADR-DA-READ-SURFACE-PLACEMENT-001` — Path A (auto-inject) is implemented here as the long-tail catch.
- `DCL-CONCEPT-ON-CONTACT-001` — Stage A (owner-prompt detection) is implemented by this hook. Stages B (bridge proposal/review) and C (rule-file edit) remain Phase 6 scope.

Topic-specific:

- `.claude/hooks/` — UserPromptSubmit hook contract; existing hooks `owner-decision-tracker.py`, `formal-artifact-approval-gate.py`, etc. provide the implementation pattern.
- `.claude/settings.json` — hook registration.
- `.claude/rules/canonical-terminology.md` — Phase 1's backfilled glossary; the hook indexes this file at startup.
- `.codex/gtkb-hooks/` and `.codex/hooks.json` — Codex parity surface.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — forward-compatible Codex parity contract.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — cross-harness enforcement contract.
- `SPEC-2098`, `ADR-008` — DA authority.
- `tests/scripts/test_codex_hook_parity.py` — existing parity test infrastructure.
- Phase 2 helper at `.claude/skills/bridge-propose/helpers/write_bridge.py` — provides the `_try_open_default_db` + `search_deliberations` pattern Phase 3 reuses.

## Prior Deliberations

- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` — owner agreement that auto-injection is the long-tail catch path, not the primary placement; placement-over-coercion principle.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-0877`, `DELIB-0879` — anchor records for the `isolation` topic (the S331 replay test for the hook).
- `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION` — startup-time loading authority; per-prompt expansion is its per-turn complement.
- `DELIB-S324-OM-DELTA-0001-CHOICE`, `DELIB-S324-OM-DELTA-0003-CHOICE` — operating-model framing relevant to placement.
- `DELIB-0835` — strict artifact approval; informs the hook's non-mutation contract (read-only injection only).
- Hook-installation precedent: `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` (owner-decision-tracker), `bridge/gtkb-narrative-artifact-approval-extension-001-011.md` (narrative-artifact-approval-gate). These set the pattern for adding `PreToolUse`/`Stop`/`UserPromptSubmit` hooks under settings.json registration.
- Phase 0 closure: `bridge/gtkb-da-read-surface-correction-phase-0-formalization-006.md`. Phase 1 closure: `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-010.md`. Phase 2 closure: `bridge/gtkb-da-read-surface-correction-phase-2-template-pre-population-008.md`.

S331 in-session decisions: same set as Phases 0-2 (begin/parallelize, cost-irrelevant, quality-and-completeness-only, owner-direction-via-AUQ). Phase 3 directly implements the long-tail Tier-3 placement Codex-side review of `-002` originally articulated.

## Owner Decisions / Input

Authorizing context:

- Phase 0 VERIFIED + four Phase 0 artifacts at `specified` in MemBase.
- Phase 1 VERIFIED + glossary backfill landed.
- Phase 2 VERIFIED + bridge-propose helper extended.
- 2026-05-09 owner direction (S331): "Please continue."

Future owner approvals this proposal will surface:

1. Approval of the hook's matching algorithm parameters (glossary-index build strategy; tokenization rules; semantic threshold; token-budget cap).
2. Approval of the "candidate for glossary promotion" surfacing format.
3. Confirmation of harness-parity scope (Codex parallel hook is forward-compatible per the existing fallback ADR; not live on Windows).

## Proposed Hook Behavior

### Algorithm

1. **Hook entry**: invoked on `UserPromptSubmit` with stdin JSON containing `prompt` text. The hook is registered in `.claude/settings.json` under the existing `UserPromptSubmit` hooks array (alongside `owner-decision-tracker.py`).
2. **Glossary index build**: at hook startup, parse `.claude/rules/canonical-terminology.md`. For each `### <heading>` within `## Canonical Terms`, `## GT-KB Platform & Lifecycle Terms`, `## GT-KB DA Read-Surface and Operational Vocabulary` (the Phase-1-backfilled section), and any other top-level glossary section: extract heading text, plus any `**Canonical alias:**` / `**Allowed synonyms:**` line tokens. Build an index `{term_lower → (heading, entry_lines)}`.
3. **Tokenize prompt**:
   - Lowercase.
   - Extract candidate matches via regex: `[a-z][a-z0-9-]+(?:\s+[a-z][a-z0-9-]+){0,3}` (1- to 4-word phrases of lowercase tokens).
   - Filter against a small stop-word list (`the`, `is`, `at`, `of`, `and`, `or`, `to`, `for`, `with`, `as`).
4. **Glossary match**: for each candidate phrase, check exact-match against the index. (Phase 3 uses exact match only; fuzzy/Levenshtein matching is future scope.)
5. **Concept-shaped non-match filter**: candidate phrases that do NOT match the glossary AND meet `len(phrase.split()) >= 2 OR len(phrase) >= 8` are forwarded to semantic search.
6. **Semantic search (default-on, auto-DB-open)**: same pattern as Phase 2's helper:
   - `_try_open_default_db()` opens `KnowledgeDB("groundtruth.db")`; returns `None` on failure (graceful degradation).
   - For each forwarded phrase, call `db.search_deliberations(phrase, limit=2)` with a similarity threshold floor.
   - `db=False` env-var or hook-config flag explicitly disables semantic search (for tests).
7. **Combine + format**:
   - Glossary matches: format the entire glossary entry (heading through next `### ` or end-of-section) into the injection.
   - Semantic matches: format as a single bullet list under `### Candidate concepts (not yet in glossary)` with each entry tagged `[candidate for promotion]`.
8. **Token-budget cap**: total injection size ≤ 2 KB. Priority: glossary matches before semantic candidates. Truncation rules: drop lowest-similarity semantic candidates first; never truncate inside a glossary entry; if even one glossary entry exceeds the cap alone, surface only its heading + first 200 chars + ellipsis.
9. **Output**: stdout-injection per the `UserPromptSubmit` hook contract (JSON `{"continue": true, "additionalContext": "<injected text>"}`). The injected text is a `<system-reminder>` block headed by `Glossary expansion (Phase 3 of GTKB-DA-READ-SURFACE-CORRECTION):`.
10. **Audit log**: write `.gtkb-state/glossary-expansion/invocations/<timestamp>.json` with: timestamp, prompt-hash (sha256 of prompt; not the prompt itself, for log-volume reasons), matched glossary terms, candidate phrases sent to semantic search, semantic-search hit IDs, injection size, threshold used, semantic_search_attempted (bool).

### Failure modes (bounded; fail-closed, never block)

- *No matches*: hook produces no injection; prompt proceeds normally.
- *DA query failure or DB unavailable*: hook logs the failure; prompt proceeds with glossary matches only (no semantic candidates).
- *Glossary parse failure*: hook fails closed (no injection); prompt proceeds normally; failure logged.
- *Hook itself errors*: per Claude Code hook contract, errors are logged via stderr; exit 0 with empty stdout means no injection. The hook never blocks the prompt.
- *Audit log write failure*: silent (non-fatal); prompt proceeds.

### Token-budget cap design

The 2 KB cap is per-prompt, not per-day or per-session. Rationale: each invocation is independent; a session with many prompts accumulates ≤ 2 KB × N prompts of glossary-expansion context. The owner can adjust the cap via env var `GTKB_GLOSSARY_EXPANSION_CAP_BYTES`.

### Codex parity (forward-compatible per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`)

The Codex template at `.codex/gtkb-hooks/glossary-expansion.py` mirrors the canonical Claude logic. `.codex/hooks.json` is updated with the registration intent. Per the ADR, this is forward-compatible-only on Windows; the canonical enforcement boundary is the Claude `UserPromptSubmit` hook. The `tests/scripts/test_codex_hook_parity.py` is extended to verify the template exists and matches the canonical structure.

## Test Plan / Verification

Spec-to-test mapping:

| Linked specification | Phase 3 test |
|---|---|
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | Hook surfaces glossary entries as agent-side reading material on prompt match. |
| `ADR-DA-READ-SURFACE-PLACEMENT-001` | Hook implements Path A (auto-inject) as the long-tail placement target. |
| `DCL-CONCEPT-ON-CONTACT-001` (Stage A) | Hook surfaces "candidate for glossary promotion" terms when concept-shaped non-matches are detected; the surfaced candidate list is the input to Phase 4's wrap-up enforcement check. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Codex parity template exists and matches canonical structure. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex hook is forward-compatible-only; not asserted live on Windows. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests below execute against the installed hook. |

Tests (in `tests/hooks/test_glossary_expansion.py` unless noted):

1. *S331-replay regression*: simulate a UserPromptSubmit event with prompt text containing the word `isolation`. Assert the hook's stdout injection contains the `isolation` glossary entry's full content (heading through `Implementation pointer:`).
2. *Multi-term match*: prompt contains `isolation`, `bridge thread`, and `placement`. Assert all three glossary entries are injected; assert no duplicate entries.
3. *Concept-shaped non-match → DA candidate*: with a fake `KnowledgeDB`, prompt contains a synthetic concept-shaped phrase that does NOT match the glossary. Assert the hook calls `search_deliberations(phrase, limit=2)`. Assert the result is formatted as `[candidate for promotion]` under the candidate-concepts subheading.
4. *Token-budget cap*: prompt contains many matching terms exceeding 2 KB. Assert the injection ≤ 2 KB. Assert glossary matches retained before semantic candidates; assert no glossary entry split mid-content.
5. *No-match*: prompt contains only common words and stop-words. Assert no injection (empty `additionalContext`); assert the hook's exit is 0 (continue).
6. *DA-failure graceful degradation*: fake DB raises on `search_deliberations`. Assert glossary matches still injected; assert no exception escapes the hook.
7. *Glossary parse failure*: pass a missing or corrupted glossary path via env var `GTKB_GLOSSARY_PATH`. Assert the hook fails closed (no injection); assert exit 0; assert log entry written.
8. *Audit log schema*: assert the audit log file is written with the expected fields (timestamp, prompt_hash, matched_glossary_terms, candidate_phrases, semantic_hit_ids, injection_size_bytes, threshold, semantic_search_attempted).
9. *Settings.json registration*: existing `.claude/settings.json` contains the hook command in the `UserPromptSubmit` array.
10. *Codex parity (extended `tests/scripts/test_codex_hook_parity.py`)*: `.codex/gtkb-hooks/glossary-expansion.py` exists and matches the canonical Claude hook's documented behavior (string-presence checks for the key functions/constants). `.codex/hooks.json` registration intent is present.

## Risk and Rollback

Risks:

- *Token-budget exhaustion at scale*: hook injects context on every prompt. Mitigation: 2 KB cap; per-prompt audit log; configurable via env var.
- *False-positive semantic candidates*: low threshold catches the long tail but may surface irrelevant matches. Mitigation: clearly tagged `[candidate for promotion]`; never authoritative; author can ignore. The Phase 4 wrap-up check enforces resolution but only on flagged terms; false positives are dropped during owner-acknowledged deferral.
- *Glossary index staleness*: hook builds index at startup; glossary edits during a session aren't reflected. Mitigation: refresh on file mtime change at every invocation (cheap; mtime check is sub-millisecond).
- *Hook latency adds to every prompt*: indexed lookups should be sub-100ms; semantic search is the slower path (200-500ms). Mitigation: only run semantic search on concept-shaped non-matches; cache recent-prompt results within the same Python process invocation; total budget per prompt should stay under 1 second.
- *Hook failure cascades into Claude UI block*: per Claude Code hook contract, hook errors are non-fatal (stderr logged, exit 0). The hook is wrapped in a top-level try/except that swallows all exceptions and emits empty stdout.

Rollback: remove the hook registration from `.claude/settings.json`; the hook file remains on disk as inert code. Full revert via `git checkout HEAD -- .claude/hooks/glossary-expansion.py .claude/settings.json .codex/gtkb-hooks/glossary-expansion.py .codex/hooks.json`. No MemBase state is mutated by the hook.

## Recommended Commit Type

`feat:` — new hook capability. Adds a `UserPromptSubmit` context-injection mechanism that did not previously exist for the glossary/DA surface. Existing hooks (`owner-decision-tracker`, `formal-artifact-approval-gate`, etc.) are unchanged.

## Files Changed

This proposal's commit will include:

- `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md` (this file; new)
- `bridge/INDEX.md` (NEW entry inserted at top)

Phase 3 implementation (after Codex GO):

Canonical Claude surfaces:
- `.claude/hooks/glossary-expansion.py` — new hook implementation.
- `.claude/settings.json` — `UserPromptSubmit` hook registration.

Codex parity surfaces (per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; forward-compatible):
- `.codex/gtkb-hooks/glossary-expansion.py` — Codex template.
- `.codex/hooks.json` — registration intent.

Tests:
- `tests/hooks/__init__.py` — new (if absent).
- `tests/hooks/test_glossary_expansion.py` — new (10 tests covering the test plan).
- `tests/scripts/test_codex_hook_parity.py` — extended for the new hook.

State directory:
- `.gtkb-state/glossary-expansion/` — created at first invocation; not committed.

Implementation report: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-NNN.md`.

## Applicability Preflight

Self-check via `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook --json` (after NEW INDEX entry in place):

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:dccc4c2defc01ada8208638b4bd3fe3fa514429b19f637235203d2400f4d373c`

## Clause Applicability

Self-check via `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`:

- Exit code: `0` (pass)
- Operative file: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md`
- Clauses evaluated: 5; must_apply: 4 (all with evidence); may_apply: 1; blocking gaps: 0.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
