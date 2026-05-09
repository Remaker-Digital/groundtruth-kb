# DRAFT — Phase 3 Bridge Proposal: UserPromptSubmit Glossary-Expansion Hook

**Status:** working draft. Not filed. Becomes `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md` after Phase 0 GO + Phase 1 backfill (Phase 1 is required for hook to deliver value; Phase 0 alone is not sufficient).

---

# Implementation Proposal — GTKB-DA-READ-SURFACE-CORRECTION Phase 3: UserPromptSubmit Glossary-Expansion Hook

- Status: NEW
- Author: Prime Builder (Claude Code, harness B)
- bridge_kind: prime_implementation_proposal
- Umbrella work item: `GTKB-DA-READ-SURFACE-CORRECTION` (Phase 3 of multi-phase plan; Phase 3 implements DCL-CONCEPT-ON-CONTACT-001 Stage A only — owner-prompt detection. Stages B (bridge proposal/review) and C (rule-file edit) are deferred to a new follow-on Phase 6 per F2 of the -002 NO-GO.)
- Depends on: Phase 0 GO + Phase 0 artifacts in MemBase + Phase 1 backfill complete (the glossary must contain substantive content for matches to be useful).

## Summary

Install a `UserPromptSubmit` hook (`.claude/hooks/glossary-expansion.py`) that detects keyword overlap between the owner's prompt and glossary terms (canonical names + allowed synonyms) and injects the matched glossary entries as `<system-reminder>` context. For prompt tokens that do NOT match the glossary but appear concept-shaped, a low-threshold semantic match against the DA produces candidate prior-deliberation entries flagged for glossary promotion.

The hook is **not a gate**: it does not block, it surfaces. Failure modes are bounded by token-budget cap and similarity threshold. This is the long-tail catch path described in the S331 plan as Tier 3 — the safety net for concepts not yet absorbed into the glossary.

A Codex parallel hook is installed via the existing harness-parity infrastructure to cover Codex sessions.

## Specification Links

Cross-cutting:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (path-trigger; no scope conflict)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

Phase 0 framing:

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`
- `ADR-DA-READ-SURFACE-PLACEMENT-001`
- `DCL-CONCEPT-ON-CONTACT-001` — the hook surfaces "candidate for promotion" terms; Phase 4 wrap-up check enforces resolution.

Topic-specific:

- `.claude/hooks/` infrastructure — UserPromptSubmit hook contract.
- `.claude/rules/canonical-terminology.md` — glossary surface (must be Phase-1-backfilled).
- `SPEC-2098`, `ADR-008` — DA authority.
- Harness parity: `tests/scripts/test_codex_hook_parity.py` and `.codex/gtkb-hooks/` for Codex-side parallel.
- DCL-CROSS-HARNESS-ENFORCEMENT-001 — cross-harness enforcement contract.

## Prior Deliberations

- DA (S331): owner agreement that auto-injection is the long-tail catch path, not the primary placement.
- DA (S331): owner concern that strict enforcement against agent bias produces workaround behavior.
- DA: "Agents must initialize with core terminology, services, artifacts, and access methods" — startup-time loading authority.
- DA: relevant prior hook-install threads (e.g., bridge-compliance-gate, owner-decision-tracker) for hook-installation precedent and pattern.

## Owner Decisions / Input

Authorizing context: Phase 0 GO + Phase 1 backfill complete.

Future owner approvals this proposal will surface:

1. Approval of the hook's matching algorithm (keyword overlap + low-threshold semantic).
2. Approval of the token-budget cap (default 2 KB injection per prompt).
3. Approval of the "candidate for glossary promotion" surfacing format.
4. Confirmation of harness-parity scope (Codex parallel hook installation).

## Proposed Hook Behavior

### Algorithm

1. On `UserPromptSubmit`, read the owner prompt text.
2. Tokenize: extract noun phrases via simple heuristics (capitalized phrases, hyphenated compounds, n-gram extraction up to 3 words, stop-word filtering).
3. For each token, check against the glossary index:
   - Build the index at hook startup by parsing `.claude/rules/canonical-terminology.md` for all `### ` headings + each entry's `Allowed synonyms:` line.
   - Match: case-insensitive substring or fuzzy match (Levenshtein <= 1 for short tokens).
4. For matches: read the full glossary entry (heading through next `### ` or end-of-section); concatenate matched entries into an injection block.
5. For non-matches: filter to concept-shaped tokens (Title Case nouns, hyphenated compounds, length >= 2 words OR >= 8 characters). For these tokens, run a DA semantic search via `groundtruth_kb.db.KnowledgeDB.search_deliberations(token, limit=2)` with a low similarity threshold. Surface matches as candidate entries flagged "candidate for glossary promotion".
6. Token-budget cap: total injection size <= 2 KB. Priority: glossary matches before DA candidates. Truncation rules: drop lowest-similarity DA candidates first; never truncate inside a glossary entry.
7. Format the injection as a single `<system-reminder>` block with a clear header and the matched-entries body.
8. Output the injection via the UserPromptSubmit hook's stdout context-injection contract.

### Failure modes (bounded)

- *No matches*: hook produces no injection; prompt proceeds normally.
- *DA query failure*: hook logs the failure to `.gtkb-state/glossary-expansion/last-failure.json`; prompt proceeds without DA candidates.
- *Glossary parse failure*: hook fails closed (no injection); prompt proceeds normally; failure logged.
- *Hook itself errors*: per existing hook infrastructure, errors are logged and do not block the prompt.

### Audit log

The hook logs each invocation to `.gtkb-state/glossary-expansion/invocations/<timestamp>.json` with: matched terms, candidate terms (DA matches), injection size, similarity scores. The log enables Phase 4 verification (does the hook actually surface relevant context?) and Phase 4's wrap-up check (which candidate terms were flagged this session?).

### Codex parity

Install a parallel hook in `.codex/gtkb-hooks/glossary-expansion.py` using the existing harness-parity testing infrastructure (`tests/scripts/test_codex_hook_parity.py`). The hook's behavior is harness-agnostic; the integration point differs (Claude UserPromptSubmit vs. Codex equivalent). Parity is verified by the existing parity test suite plus a new test for the glossary-expansion hook specifically.

## Test Plan / Verification

Spec-to-test mapping:

| Linked specification | Phase 3 test |
|---|---|
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | Hook surfaces glossary entries as agent-side reading material. |
| `ADR-DA-READ-SURFACE-PLACEMENT-001` | Hook implements one of the named placement targets (UserPromptSubmit). |
| `DCL-CONCEPT-ON-CONTACT-001` | Hook surfaces "candidate for glossary promotion" terms; Phase 4 wrap-up check enforces resolution. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Codex parity hook verified by existing parity infrastructure + new dedicated test. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests below execute against the installed hook. |

Tests:

1. *S331-replay regression*: simulate the S331 owner message ("we have found another misunderstanding regarding the concept GT-KB isolation"); verify the hook produces an injection containing the `isolation` glossary entry.
2. *DA candidate surfacing test*: simulate an owner message naming a load-bearing concept that is NOT yet in the glossary (use a concept removed from the glossary for the test); verify the hook produces a "candidate for promotion" candidate entry from the DA.
3. *Token budget test*: simulate an owner message with many matching terms exceeding the 2 KB cap; verify truncation drops DA candidates before glossary entries; verify glossary entries are never split.
4. *No-match test*: simulate an owner message with no matching terms; verify no injection is produced; verify prompt proceeds.
5. *Failure-mode test*: simulate DA query failure; verify hook logs and prompt proceeds without DA candidates.
6. *Harness parity test*: invoke the equivalent Codex hook with the same prompts; verify equivalent behavior.

## Risk and Rollback

Risks:

- *Token-budget exhaustion at scale*: hook injects context on every prompt. Mitigation: 2 KB cap; per-prompt audit; configurable.
- *False-positive DA candidates*: low similarity threshold catches the long tail but may surface irrelevant matches. Mitigation: clearly labeled as "candidate" not "authoritative"; doesn't gate response; author can ignore.
- *Glossary index staleness*: hook builds index at startup; glossary edits during a session aren't reflected. Mitigation: refresh on file mtime change; or rebuild on demand.
- *Hook adds latency to every prompt*: indexed lookups should be fast (<100 ms); DA semantic search is the slower path (200-500 ms). Mitigation: only run DA search on concept-shaped tokens that didn't match the glossary; cache recent DA queries.

Rollback: disable the hook by removing its registration in `.claude/settings.json`; revert the hook file via git. No MemBase state is mutated.

## Recommended Commit Type

`feat:` — new hook capability. Adds a UserPromptSubmit context-injection mechanism that did not previously exist for the glossary/DA surface.

## Files Changed

- `.claude/hooks/glossary-expansion.py` (new)
- `.claude/settings.json` (registration)
- `.codex/gtkb-hooks/glossary-expansion.py` (new; Codex parallel)
- `.codex/config.toml` and `.codex/hooks.json` (Codex-side registration; per harness-parity-fallback ADR, may remain forward-compatible until live on Windows)
- `tests/hooks/test_glossary_expansion.py` (new)
- `tests/scripts/test_codex_hook_parity.py` (extended)
- `bridge/gtkb-da-read-surface-correction-phase-3-glossary-expansion-hook-001.md` (this proposal)
- `bridge/INDEX.md`

## Applicability Preflight

To be populated against the live bridge file.

## Clause Applicability

To be populated by clause preflight after INDEX entry.
