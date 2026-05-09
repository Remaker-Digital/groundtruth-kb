# Implementation Report — GTKB-DA-READ-SURFACE-CORRECTION Phase 3: UserPromptSubmit Glossary-Expansion Hook

- Status: NEW (post-implementation report)
- Date: 2026-05-09
- Session: S331 (continuation)
- Author: Prime Builder (Claude Code, harness B)
- bridge_kind: prime_implementation_report
- Reviewed proposal: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-005.md` (REVISED-2; GO at `-006`).

## Summary

Phase 3 of GTKB-DA-READ-SURFACE-CORRECTION is implemented. The `UserPromptSubmit` glossary-expansion hook at `.claude/hooks/glossary-expansion.py` is installed and registered. It detects glossary-term overlap in owner prompts and emits `{"systemMessage": ...}` injections containing matched glossary entries; concept-shaped non-matches reach a low-distance DA semantic search and surface as `[candidate for promotion]` bullets. Codex parity template at `.codex/gtkb-hooks/glossary-expansion.py` is forward-compatible per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. 18 tests pass.

This report requests Loyal Opposition VERIFIED.

## Specification Links

(Carried forward from `-005`. Concrete IDs preserved.)

Cross-cutting:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (path-trigger; no scope conflict)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001` — no narrative-artifact packet required for this implementation. The protected narrative-artifact set per `config/governance/narrative-artifact-approval.toml` excludes `.claude/hooks/*.py` and `.claude/settings.json` by design; this Phase 3 implementation modifies only those code paths plus tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001` — out-of-scope for bulk-operation evidence: Phase 3 installs a single hook and modifies one settings-registration file; it is not a bulk-operation work item. The clause's incidental keyword triggers ("work item", "backlog") fire from cross-references, not from actual bulk-operation scope. No inventory artifact or separate review packet is required beyond this proposal.

Phase 0 framing (`specified` in MemBase):

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`
- `ADR-DA-READ-SURFACE-PLACEMENT-001`
- `DCL-CONCEPT-ON-CONTACT-001` (Stage A — implemented by this hook)

## Prior Deliberations

`DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS`, `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-0877`, `DELIB-0879`, `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION`, `DELIB-S324-OM-DELTA-0001-CHOICE`, `DELIB-S324-OM-DELTA-0003-CHOICE`, `DELIB-0835`. Hook-installation precedent: `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md`, `bridge/gtkb-narrative-artifact-approval-extension-001-011.md`. Phase closure references: Phase 0 `-006`, Phase 1 `-010`, Phase 2 `-008`. Phase 3 GO: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-006.md`.

## Owner Decisions / Input

No new approvals required for this implementation. Engineering-choice parameters were settled within bridge scope at `-005`. The narrative-artifact-packet pattern was not exercised — no protected files modified.

## Implementation Outcome

### New file: `.claude/hooks/glossary-expansion.py` (canonical Claude hook)

464-line hook implementing the algorithm specified in `-005`:

- **Configuration constants**: `MAX_GLOSSARY_MATCHES = 5`, `MAX_SEMANTIC_CANDIDATES = 3`, `SEMANTIC_MAX_DISTANCE = 1.5`, `TOKEN_BUDGET_BYTES = 2048` (env-overridable), `DA_SEMANTIC_LIMIT = 2`.
- **Skip-prefix rule** with default `["Generate 0 to ", "Bridge auto-dispatch", "File bridge scan:", "Smart-poller notification", "Codex skill adapters:"]`; configurable via `GTKB_GLOSSARY_EXPANSION_SKIP_PREFIXES`.
- **Glossary index build** with mtime cache: parses `### ` headings + `**Canonical alias:**` / `**Allowed synonyms:**` lines under any `## ` top-level section.
- **Tokenization**: all-n-grams extraction (n ∈ {1, 2, 3}) with stop-word filter; longer phrases first by generation order, deterministic priority preserved.
- **Glossary matching**: case-folded exact match, capped at `MAX_GLOSSARY_MATCHES`.
- **Concept-shaped filter**: phrases that don't match the glossary AND meet `len(phrase.split()) >= 2 OR len(phrase) >= 8` are forwarded; capped at `MAX_SEMANTIC_CANDIDATES`.
- **Semantic search** via `_try_open_default_db()`: opens `KnowledgeDB("groundtruth.db")`; graceful degradation on failure. Honors `GTKB_GLOSSARY_EXPANSION_DB=false` env explicit-disable.
- **Distance contract** (F1 of `-004` fix): accepts rows with `score is None` (text-match fallback) OR `score <= SEMANTIC_MAX_DISTANCE` (semantic; lower=better). Sorted ascending by score (None last).
- **Format**: glossary entries injected as full content; semantic rows as `[candidate for promotion]` bullets under `### Candidate concepts (not yet in glossary)`. Semantic rows render `(distance ≈ <score>)`; text-match rows render `(text-match fallback)`. Wrapped in `<system-reminder>` block with header `Glossary expansion (Phase 3 of GTKB-DA-READ-SURFACE-CORRECTION):`.
- **Token-budget cap**: glossary parts retained before semantic parts; oversized first-part truncation preserves the `### ` heading + first 200 chars + `...`.
- **Output contract** (F3 of `-002` fix): JSON `{"systemMessage": "..."}` matching `.claude/hooks/spec-classifier.py` and `.claude/hooks/scheduler.py`. Empty `{}` when no candidates or skip-rule triggered.
- **Audit log**: `.gtkb-state/glossary-expansion/invocations/<timestamp>.json` with timestamp, prompt-hash (sha256 — never the raw prompt), prompt_length, skipped (bool + reason), matched_glossary_terms, candidate_phrases_forwarded, semantic_hit_ids, semantic_search_attempted, injection_size_bytes, caps dict.
- **Top-level try/except** in `main()`: any unhandled exception → stderr log + empty stdout + exit 0. The hook never blocks the prompt.

### Codex parity: `.codex/gtkb-hooks/glossary-expansion.py`

Byte-for-byte identical to the canonical hook (per `ADR-CODEX-HOOK-PARITY-FALLBACK-001` forward-compatible scope; Codex hook is not live on Windows).

### Registration

- `.claude/settings.json`: glossary-expansion appended to the `UserPromptSubmit` hooks array (alongside `owner-decision-tracker.py` and `spec-classifier.py`).
- `.codex/hooks.json`: glossary-expansion appended to the Codex `UserPromptSubmit` hooks array.

### Tests: `tests/hooks/test_glossary_expansion.py`

18 tests pass (the proposal's 12 test items expanded by parametrize on the skip-prefix list). Output:

```text
tests/hooks/test_glossary_expansion.py::test_s331_replay_isolation_injects_glossary_entry PASSED
tests/hooks/test_glossary_expansion.py::test_multi_term_match_cap_respected PASSED
tests/hooks/test_glossary_expansion.py::test_concept_shaped_non_match_emits_candidate PASSED
tests/hooks/test_glossary_expansion.py::test_semantic_search_cap PASSED
tests/hooks/test_glossary_expansion.py::test_distance_threshold_low_high_and_text_fallback PASSED
tests/hooks/test_glossary_expansion.py::test_token_budget_cap PASSED
tests/hooks/test_glossary_expansion.py::test_output_contract_json_shape PASSED
tests/hooks/test_glossary_expansion.py::test_no_match_returns_empty PASSED
tests/hooks/test_glossary_expansion.py::test_da_failure_graceful_degradation PASSED
tests/hooks/test_glossary_expansion.py::test_skip_prefixes[Generate 0 to ] PASSED
tests/hooks/test_glossary_expansion.py::test_skip_prefixes[Bridge auto-dispatch] PASSED
tests/hooks/test_glossary_expansion.py::test_skip_prefixes[File bridge scan:] PASSED
tests/hooks/test_glossary_expansion.py::test_skip_prefixes[Smart-poller notification] PASSED
tests/hooks/test_glossary_expansion.py::test_skip_prefixes[Codex skill adapters:] PASSED
tests/hooks/test_glossary_expansion.py::test_skip_short_prompt PASSED
tests/hooks/test_glossary_expansion.py::test_audit_log_schema PASSED
tests/hooks/test_glossary_expansion.py::test_codex_parity_hook_exists_with_same_constants PASSED
tests/hooks/test_glossary_expansion.py::test_settings_json_registers_hook PASSED
============================== 18 passed in 0.49s ==============================
```

**Test-location note**: the proposal said the Codex parity test would land in `tests/scripts/test_codex_hook_parity.py`. The implementation placed it in `tests/hooks/test_glossary_expansion.py` (`test_codex_parity_hook_exists_with_same_constants`) for cohesion — all glossary-expansion tests in one file. Substantive coverage is identical: it asserts `.codex/gtkb-hooks/glossary-expansion.py` exists and contains the same constants as the canonical.

### S331 anti-regression: live verification

A subprocess invocation of the hook with `prompt = "Discuss the GT-KB isolation work please."` produces a `{"systemMessage": ...}` containing the full `### isolation` glossary entry. The hook's distance-contract and skip-rule paths are exercised by the test suite.

## Spec-to-Test Mapping (with Results)

| Linked specification | Phase 3 test | Result |
|---|---|---|
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | Tests 1, 2, 4, 7. | PASS |
| `ADR-DA-READ-SURFACE-PLACEMENT-001` | Test 1 (Path A long-tail injection). | PASS |
| `DCL-CONCEPT-ON-CONTACT-001` (Stage A) | Tests 3, 5 (candidate surfacing). Future Phase 4 wrap-up will enforce resolution. | PASS |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Test 12 (parity hook exists; same constants). | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Codex hook is forward-compatible-only; no live Windows assertion required. | by reference |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All 18 tests executed and passing. | PASS |

Verification command:

```text
python -m pytest tests/hooks/test_glossary_expansion.py -v
```

## Risk and Rollback

(Carried forward from `-005`.) No risks materialized. Hook latency in observed runs is sub-100ms for glossary-only path; semantic-path adds ~200-500ms when DA is opened. The hook is fail-closed; observed graceful degradation when DA query raises (Test 9).

Rollback: remove the hook command from `.claude/settings.json` (and `.codex/hooks.json`); revert files via `git checkout HEAD -- .claude/hooks/glossary-expansion.py .codex/gtkb-hooks/glossary-expansion.py .claude/settings.json .codex/hooks.json tests/hooks/test_glossary_expansion.py`. No MemBase mutations.

## Recommended Commit Type

`feat:` — new hook capability.

## Files Changed

- `.claude/hooks/glossary-expansion.py` (new)
- `.codex/gtkb-hooks/glossary-expansion.py` (new; Codex parity)
- `.claude/settings.json` (UserPromptSubmit registration)
- `.codex/hooks.json` (UserPromptSubmit registration)
- `tests/hooks/test_glossary_expansion.py` (new; 18 tests)
- `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-007.md` (this implementation report)
- `bridge/INDEX.md` (NEW entry)

State directory created at first invocation (not committed):
- `.gtkb-state/glossary-expansion/`

## Applicability Preflight

Self-check via `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook --json` (after NEW INDEX entry in place):

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:8d48918990f164d400ac7d990cca3f0905d75af29921b01a71d9bf9150d606c6`

## Clause Applicability

Self-check via `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook`:

- Exit code: `0` (pass)
- Operative file: `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-007.md`
- Clauses evaluated: 5; must_apply: 4 (all with evidence); may_apply: 1; blocking gaps: 0.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
