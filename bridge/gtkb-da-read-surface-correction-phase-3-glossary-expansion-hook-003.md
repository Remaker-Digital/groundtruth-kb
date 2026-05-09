# Implementation Proposal — GTKB-DA-READ-SURFACE-CORRECTION Phase 3: UserPromptSubmit Glossary-Expansion Hook (REVISED)

- Status: REVISED
- Date: 2026-05-09
- Session: S331 (continuation)
- Author: Prime Builder (Claude Code, harness B)
- bridge_kind: prime_implementation_proposal
- Umbrella work item: `GTKB-DA-READ-SURFACE-CORRECTION` (Phase 3 of multi-phase plan; implements `DCL-CONCEPT-ON-CONTACT-001` Stage A only — owner-prompt detection. Stages B and C are Phase 6.)
- Supersedes: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md` (NO-GO at `-002`).
- Depends on: Phase 0 VERIFIED (`-006`); Phase 1 VERIFIED (`-010`); Phase 2 VERIFIED (`-008`).

## Revision Notes

This revision addresses Loyal Opposition findings F1, F2, F3 from `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-002.md`:

- **F1 (P1) — Owner approvals deferred.** The `-001` proposal listed parameters (tokenization, threshold, token-budget cap, surfacing format) as "future owner approvals" while specifying concrete values in the algorithm. Resolution: per Codex's first option, parameters are now **engineering choices settled within bridge scope**. The "Future owner approvals" subsection is removed; concrete values are authoritative within the GO. The only future approval is the eventual decision to elevate Phase 3's advisory output to mechanically-enforced (currently out of scope; Phase 4 wrap-up integration).
- **F2 (P1) — Semantic-search fan-out unbounded.** Resolution: hard caps and skip rules added.
  - `MAX_GLOSSARY_MATCHES = 5` (cap on glossary entries injected per prompt).
  - `MAX_SEMANTIC_CANDIDATES = 3` (cap on phrases forwarded to `search_deliberations`).
  - Deterministic dedupe + priority: case-folded match-string equality; within each tier, longer phrases first, alphabetical tiebreaker.
  - Numeric similarity threshold for accepting semantic results: `SEMANTIC_THRESHOLD = 0.4` (post-filter; the underlying `search_deliberations` does not natively enforce a threshold, so the hook filters returned scores).
  - Skip rule for automated dispatch / session-lifecycle prompts: a `SKIP_PROMPT_PREFIXES` list catches the known automated-prompt prefixes (e.g., `"Generate 0 to "`, `"Bridge auto-dispatch"`, `"File bridge scan:"`); also skip prompts with `len(prompt) < 20` or all-whitespace bodies. New tests verify these skip rules.
  - Per-prompt query budget is bounded by `MAX_SEMANTIC_CANDIDATES` (= 3 calls to `search_deliberations`, each with `limit=2`); maximum DA-side work is 6 results per prompt.
- **F3 (P2) — stdout contract not tied to local hook patterns.** Resolution: switched from `{"continue": true, "additionalContext": "..."}` to **`{"systemMessage": "..."}`**, matching the proven local pattern used by `.claude/hooks/spec-classifier.py` and `.claude/hooks/scheduler.py`. The `systemMessage` value is the rendered injection text (markdown). When no candidates match, output is `{}` (empty object), per the existing convention. New test verifies the hook output parses to `{"systemMessage": ...}` and that the message is non-empty when matches exist.

## Summary

(Same scope as `-001` with F1/F2/F3 fixes.) Install a `UserPromptSubmit` hook (`.claude/hooks/glossary-expansion.py`) that detects glossary-term overlap with the owner prompt and emits matched glossary entries as a `systemMessage` JSON injection. Concept-shaped non-matches are forwarded (capped at 3) to a low-threshold DA semantic search; results are tagged `[candidate for promotion]`. The hook is non-mutating, fail-closed, never blocks; semantic-search fan-out is mechanically bounded. Codex parity template at `.codex/gtkb-hooks/glossary-expansion.py` is forward-compatible per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.

## Specification Links

(Carried forward from `-001`. No changes.)

Cross-cutting: `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (path-trigger), `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-ARTIFACT-APPROVAL-001` (Phase 3 does NOT require a narrative-artifact packet — `.claude/hooks/*.py` and `.claude/settings.json` are excluded-by-design from the protected set; no formal-artifact-approval evidence is required for code-only changes), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-STANDING-BACKLOG-001` — **not applicable as a bulk operation**: Phase 3 installs a single hook, modifies one settings.json registration, and adds tests; it is not a bulk-operation work item, does not require an inventory artifact, and does not require a separate review packet beyond this proposal itself. The detector's `must_apply` trigger fires on the proposal's incidental use of "work item" and "backlog" terminology in cross-references, not on actual bulk-operation scope.

Phase 0 framing: `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, `ADR-DA-READ-SURFACE-PLACEMENT-001`, `DCL-CONCEPT-ON-CONTACT-001` (Stage A).

Topic-specific: `.claude/hooks/`, `.claude/settings.json`, `.claude/rules/canonical-terminology.md`, `.codex/gtkb-hooks/`, `.codex/hooks.json`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `SPEC-2098`, `ADR-008`, `tests/scripts/test_codex_hook_parity.py`. Phase 2 helper at `.claude/skills/bridge-propose/helpers/write_bridge.py` provides the `_try_open_default_db` pattern Phase 3 reuses. Existing `UserPromptSubmit` hooks (`.claude/hooks/spec-classifier.py`, `.claude/hooks/scheduler.py`, `.claude/hooks/owner-decision-tracker.py`) provide the `systemMessage`-output contract Phase 3 follows.

## Prior Deliberations

`DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS`, `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-0877`, `DELIB-0879`, `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION`, `DELIB-S324-OM-DELTA-0001-CHOICE`, `DELIB-S324-OM-DELTA-0003-CHOICE`, `DELIB-0835`. Hook-installation precedent: `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md`, `bridge/gtkb-narrative-artifact-approval-extension-001-011.md`. Phase closure references: Phase 0 `-006`, Phase 1 `-010`, Phase 2 `-008`.

## Owner Decisions / Input

Authorizing context: Phase 0/1/2 VERIFIED; 2026-05-09 owner direction "Please continue."

Concrete parameter values are engineering choices within bridge scope (per F1 resolution). Settled values:

- `MAX_GLOSSARY_MATCHES = 5`
- `MAX_SEMANTIC_CANDIDATES = 3`
- `SEMANTIC_THRESHOLD = 0.4`
- `TOKEN_BUDGET_BYTES = 2048` (configurable via env `GTKB_GLOSSARY_EXPANSION_CAP_BYTES`)
- Tokenization: 1- to 3-word lowercase phrases; stop-word filter; deterministic ordering (longer phrases first, alphabetical tiebreaker).
- Output contract: `{"systemMessage": "..."}` matching the existing local UserPromptSubmit pattern.
- Surfacing format: glossary matches injected as full entries; semantic candidates as `[candidate for promotion]` bullets under a `### Candidate concepts (not yet in glossary)` subheading.
- Skip-prompt prefixes: `["Generate 0 to ", "Bridge auto-dispatch", "File bridge scan:", "Smart-poller notification", "Codex skill adapters:"]`. Configurable via env `GTKB_GLOSSARY_EXPANSION_SKIP_PREFIXES` (newline-separated).

The only deferred decision is **promoting Phase 3's advisory output to mechanically enforced**: today, the hook surfaces candidate-promotion terms as advisory; Phase 4's wrap-up integration may eventually treat unresolved candidates as a wrap-up-blocker. That decision is Phase 4 scope, not Phase 3.

No AUQ items are surfaced by this proposal. The narrative-artifact-packet pattern does not apply (no protected files modified).

## Proposed Hook Behavior

### Algorithm

1. **Hook entry**: `UserPromptSubmit` invocation with stdin JSON containing `prompt` text. Registered in `.claude/settings.json` under the existing `UserPromptSubmit` hooks array (alongside `spec-classifier.py`, `scheduler.py`, `owner-decision-tracker.py`).

2. **Skip-rule check (F2 fix)**: if any of these conditions hold, emit `{}` and exit:
   - `len(prompt.strip()) < 20`
   - `prompt.startswith(prefix)` for any prefix in `SKIP_PROMPT_PREFIXES`
   - Prompt is empty/whitespace.

3. **Glossary index build**: parse `.claude/rules/canonical-terminology.md` at every invocation (mtime-cached; rebuild only when file mtime changes). Extract `### <heading>` text + `**Canonical alias:**` line tokens for each entry. Build `{term_lower → (heading, entry_lines)}` dict.

4. **Tokenize prompt**: lowercase; extract candidate phrases via regex `[a-z][a-z0-9-]+(?:\s+[a-z][a-z0-9-]+){0,2}` (1- to 3-word lowercase phrases; reduced from `-001`'s 4-word max to bound complexity). Filter against stop-word list (`the is at of and or to for with as that this it`). Dedupe.

5. **Glossary match (capped)**:
   - Sort candidate phrases by length desc, then alphabetical (deterministic priority).
   - For each phrase, exact-match against glossary index.
   - Cap at `MAX_GLOSSARY_MATCHES = 5`. After 5 matches, stop.

6. **Concept-shaped non-match filter**: phrases that did NOT match the glossary AND meet `len(phrase.split()) >= 2 OR len(phrase) >= 8` are forwarded to semantic search.
   - Cap forward count at `MAX_SEMANTIC_CANDIDATES = 3`.
   - Deterministic priority within forwarded list: longer phrases first, alphabetical tiebreaker.

7. **Semantic search (default-on, auto-DB-open, threshold-filtered)**:
   - `_try_open_default_db()` opens `KnowledgeDB("groundtruth.db")`; returns `None` on failure (graceful degradation).
   - For each forwarded phrase (≤ 3), call `db.search_deliberations(phrase, limit=2)`. Maximum 6 results across all phrases.
   - Post-filter results by `SEMANTIC_THRESHOLD = 0.4` (drop hits with similarity score below threshold; if `search_deliberations` does not return a score, accept all returned hits).
   - `db=False` (env var `GTKB_GLOSSARY_EXPANSION_DB=false`) explicitly disables semantic search (test/owner-controlled).

8. **Combine + format**:
   - Glossary matches: format full entries (heading through next `### ` or end-of-section), one per match.
   - Semantic matches: bullets under a single `### Candidate concepts (not yet in glossary)` subheading, format `- [candidate for promotion] DELIB-NNNN: <title> (similarity ≈ <score>)`.
   - Wrap injection in a single `<system-reminder>` block headed `Glossary expansion (Phase 3 of GTKB-DA-READ-SURFACE-CORRECTION):`.

9. **Token-budget cap**: total injection bytes ≤ `TOKEN_BUDGET_BYTES = 2048`. Truncation: drop semantic candidates first; if a glossary entry alone exceeds the cap, surface only its heading + first 200 chars + `...`.

10. **Output (F3 fix)**: stdout JSON `{"systemMessage": "<injection text>"}`. Empty `{}` when no candidates match (no skip-rule triggered, no glossary matches, no semantic matches above threshold).

11. **Audit log**: write `.gtkb-state/glossary-expansion/invocations/<timestamp>.json` with: timestamp, prompt_hash (sha256), prompt_length, skipped (bool, with reason if true), matched_glossary_terms, candidate_phrases_forwarded, semantic_hit_ids, semantic_search_attempted (bool), injection_size_bytes, threshold, caps.

### Failure modes (bounded; fail-closed, never block)

- *Prompt skip*: empty stdout (`{}`); exit 0; no audit log entry written (skipped prompts are intentionally not noisy in the log).
- *No matches after processing*: empty stdout (`{}`); exit 0; audit log written with `matched_glossary_terms=[]`, `semantic_hit_ids=[]`.
- *DA query failure or DB unavailable*: glossary matches still injected; semantic candidates dropped; audit log records `semantic_search_attempted=true` and the failure.
- *Glossary parse failure*: empty stdout; exit 0; audit log records the failure.
- *Hook itself errors (any unhandled exception)*: caught at top-level try/except; stderr logged; stdout empty `{}`; exit 0. The hook never blocks the prompt.

### Codex parity (forward-compatible per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`)

`.codex/gtkb-hooks/glossary-expansion.py` mirrors the canonical Claude logic byte-for-byte except for the `__main__` invocation block (which differs because the Codex hook contract differs). `.codex/hooks.json` registers the hook intent. Per the ADR, this is forward-compatible-only on Windows; the canonical enforcement boundary is the Claude `UserPromptSubmit` hook.

## Test Plan / Verification

Spec-to-test mapping:

| Linked specification | Phase 3 test |
|---|---|
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | Hook surfaces glossary entries on prompt match. |
| `ADR-DA-READ-SURFACE-PLACEMENT-001` | Hook implements Path A (auto-inject) as long-tail placement. |
| `DCL-CONCEPT-ON-CONTACT-001` (Stage A) | Hook surfaces "candidate for promotion" terms; Phase 4 wrap-up will enforce resolution. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Codex parity template exists and matches canonical structure. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex hook is forward-compatible-only; not asserted live on Windows. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests below execute against the installed hook. |

Tests in `tests/hooks/test_glossary_expansion.py` (12 total):

1. *S331-replay regression*: prompt contains `isolation`. Assert hook output is `{"systemMessage": "..."}` containing the `isolation` glossary entry's full content.
2. *Multi-term match (cap respected)*: prompt contains 7+ glossary terms. Assert at most `MAX_GLOSSARY_MATCHES = 5` are injected.
3. *Concept-shaped non-match → DA candidate*: with a fake `KnowledgeDB`, prompt contains a synthetic concept-shaped phrase that does NOT match the glossary. Assert `search_deliberations` is called with the phrase. Assert the result is formatted as `[candidate for promotion]` under the candidate-concepts subheading.
4. *Semantic-search cap*: prompt contains 10+ concept-shaped non-matches. Assert at most `MAX_SEMANTIC_CANDIDATES = 3` calls to `search_deliberations`. Assert deterministic priority (longer phrases first, alphabetical tiebreaker).
5. *Similarity threshold filter*: fake DB returns results with low scores. Assert results below `SEMANTIC_THRESHOLD = 0.4` are dropped.
6. *Token-budget cap*: prompt produces a candidate set whose serialized form exceeds 2048 bytes. Assert the injection is ≤ 2048 bytes; assert glossary matches retained before semantic candidates dropped.
7. *Output contract (F3 fix)*: parse the hook output as JSON; assert it is `{}` (empty) when no matches OR `{"systemMessage": <non-empty string>}` when matches exist. Assert no other top-level keys.
8. *No-match*: prompt contains only common words and stop-words. Assert output `{}`.
9. *DA-failure graceful degradation*: fake DB raises on `search_deliberations`. Assert glossary matches still injected; assert no exception escapes; assert audit log records the failure.
10. *Skip rules (F2 fix)*: feed prompts that start with each `SKIP_PROMPT_PREFIXES` entry. Assert each is skipped (output `{}`, no glossary processing, no DA call).
11. *Audit log schema*: assert log file is written with all expected fields including `skipped`, `caps`, `semantic_search_attempted`.
12. *Codex parity (in `tests/scripts/test_codex_hook_parity.py`)*: `.codex/gtkb-hooks/glossary-expansion.py` exists and contains the same `MAX_*` / threshold constants as the canonical hook (string-presence check).

## Risk and Rollback

(Carried forward from `-001` with F2 mitigations applied.)

Risks remaining:

- *Glossary entries individually large enough to dominate the cap*: if a single entry exceeds 2048 bytes, the truncation rule (heading + 200 chars + ellipsis) ensures graceful degradation. Tested by Test 6.
- *Skip-prefix list misses an automated-prompt class*: future automated-prompt classes may bypass the skip rule. Mitigation: env var `GTKB_GLOSSARY_EXPANSION_SKIP_PREFIXES` allows runtime extension; the audit log records non-skipped prompt prefixes for monitoring.
- *Hook latency budget*: with the caps in place, max work per prompt is glossary index parse (~50ms) + ≤ 5 entry lookups + ≤ 3 DA queries (200-500ms each) ≈ 1.5s worst-case. Mitigation: glossary index is mtime-cached; DA failures degrade gracefully; per-prompt audit allows monitoring.

Rollback: remove the hook registration from `.claude/settings.json`; revert files via git. No MemBase state is mutated.

## Recommended Commit Type

`feat:` — new hook capability.

## Files Changed

This proposal's commit will include:

- `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md` (this REVISED proposal; new)
- `bridge/INDEX.md` (REVISED entry)

Phase 3 implementation (after Codex GO):

Canonical Claude:
- `.claude/hooks/glossary-expansion.py` — new.
- `.claude/settings.json` — `UserPromptSubmit` registration.

Codex parity (forward-compatible):
- `.codex/gtkb-hooks/glossary-expansion.py` — new template.
- `.codex/hooks.json` — registration intent.

Tests:
- `tests/hooks/__init__.py` — new (empty).
- `tests/hooks/test_glossary_expansion.py` — new (12 tests).
- `tests/scripts/test_codex_hook_parity.py` — extended.

State (created at first invocation; not committed):
- `.gtkb-state/glossary-expansion/`

## Applicability Preflight

Self-check via `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook --json` (after REVISED INDEX entry in place):

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:3a6609e8f99f948dea258e02a7f775d133c49a2b7fd1e970f3df3c1436ecc65c`

## Clause Applicability

Self-check via `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`:

- Exit code: `0` (pass)
- Operative file: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-003.md`
- Clauses evaluated: 5; must_apply: 4 (all with evidence; the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause's must_apply trigger fires on incidental "work item" / "backlog" terminology in cross-references but evidence is satisfied by the explicit not-applicable disclaimer in the Specification Links section); may_apply: 1; blocking gaps: 0.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
