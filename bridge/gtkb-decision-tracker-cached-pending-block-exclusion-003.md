REVISED

# Implementation Proposal - Owner-Decision-Tracker Cached Pending Block Exclusion - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-decision-tracker-cached-pending-block-exclusion
Version: 003
Responds to: bridge/gtkb-decision-tracker-cached-pending-block-exclusion-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: [".claude/hooks/owner-decision-tracker.py", "platform_tests/hooks/test_owner_decision_tracker.py"]

## Claim

REVISED-1 closes both `-002` Codex findings:

- F1 (P1) closed: `Specification Links` now cites the 1 missing required spec (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`) plus all 3 missing advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`). Applicability preflight now returns `preflight_passed: true` after INDEX update.
- F2 (P1) closed: `target_paths` is now a concrete JSON metadata line listing exactly two in-root paths — the hook source and the existing test file. The conditional clauses and duplicated entries in `-001` are removed.

The implementation substance from `-001` is preserved unchanged: extend `_is_inside_structural_context` in `.claude/hooks/owner-decision-tracker.py` to treat matches inside a `### Pending Owner Decisions` markdown section as structural context (skip the match). This eliminates the recursive-fire pattern where the cached SessionStart payload's `### Pending Owner Decisions` block — when re-rendered verbatim per the SessionStart contract — contains DECISION-NNNN body text that lexically matches `PROSE_DECISION_PATTERNS` and triggers Stop-mode blocks that have nothing to do with the agent's actual prose.

Recurrence evidence remains current: S350 has accumulated DECISION-0572 and DECISION-0585 as persistent false positives, both re-firing on every session start through the cached pending block.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`:

- `E:\GT-KB\.claude\hooks\owner-decision-tracker.py` - hook source (the `_is_inside_structural_context` extension).
- `E:\GT-KB\platform_tests\hooks\test_owner_decision_tracker.py` - existing test file confirmed by `-002` evidence at line 151; the 4 new tests will live here.
- Bridge file itself at `E:\GT-KB\bridge\gtkb-decision-tracker-cached-pending-block-exclusion-003.md`.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, both target paths are within the GT-KB platform root and do not touch any application tree.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; `bridge/INDEX.md` updated to insert the REVISED-1 entry at the top of this thread's version list; no prior version deletion or rewrite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`; no `applications/` paths touched (closes F1 of `-002` — this spec was missing in `-001`).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited in this flat list.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below; each linked spec maps to at least one of the 4 named tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - hook change is a durable governance artifact (closes F1 advisory spec from `-002`).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development pattern; structural-context exclusion is a tracked deterministic behavior (closes F1 advisory spec from `-002`).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - hook gate fires deterministically on Stop event; the exclusion narrows the fire condition (closes F1 advisory spec from `-002`).
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001` - deterministic pattern matching only; no LLM classifiers. Section-scope structural exclusion is deterministic (regex over heading lines).
- `SPEC-AUQ-POLICY-ENGINE-001` - central deterministic policy engine returning canonical outcomes; structural pre-check is the engine's existing exception surface; this proposal extends that surface by one context class.
- `GOV-STANDING-BACKLOG-001` - no work_item is required for this single-function hook tightening; the fix is operational hygiene, not backlog work.
- `.claude/rules/prime-builder-role.md` § "AskUserQuestion as the Only Valid Owner-Decision Channel" - the rule the tracker enforces; this proposal narrows enforcement scope (excludes cached pending blocks), not the AUQ-only contract itself.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol invariants honored.
- `.claude/rules/codex-review-gate.md` - Loyal Opposition review gate honored.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md` REVISED-1 Codex GO at `-004` - established the Stop-mode block decision (the substrate this proposal narrows).
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` VERIFIED - Sub-slice A activated the tracker; established `PROSE_DECISION_PATTERNS` + `PROSE_FALSE_POSITIVE_GUARDS` contract.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-005.md` Codex GO at `-006` - Sub-slice A follow-up that added the structural pre-check for fenced code / indented code / blockquotes / HTML comments. This proposal extends that pre-check with a 5th context.

## Prior Deliberations

- `DELIB-1526` - prior owner-decision-tracker review that required strict evidence and fail-closed owner-decision visibility behavior. This proposal preserves the fail-closed behavior for prose decision-asks; it only excludes the cached pending block, which is by construction a list of already-tracked decisions (not new asks).
- Memory `feedback_avoid_quoting_decision_tracker_fragments` (S328) - the operational workaround Prime Builder has been applying when this fires; this proposal converts the workaround into a deterministic exclusion.
- No surfaced deliberation waives the existing AUQ-only enforcement contract; this proposal preserves it.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner directive "Please continue working on bridge items" - authorizes Prime Builder to file this REVISED-1 addressing the `-002` NO-GO findings.
- 2026-05-14 UTC, S350: prior owner directive (FYI screenshot acknowledgement that the recursive-fire pattern keeps recurring) + "Please continue" - authorizes the underlying fix substance preserved from `-001`.
- 2026-05-14 UTC, S350: owner AskUserQuestion answer "Parallel research + serialized Writes now (Recommended)" - established the broader session-batch authorization under which this REVISED-1 is filed.
- This proposal interprets the persistent recurrence of DECISION-0572 and DECISION-0585 across multiple S350 turns as durable owner-visible evidence that the false-positive cycle is a real workflow defect, not a one-off.
- DECISION-0572 and DECISION-0585 are themselves instances of the false-positive pattern this proposal eliminates; they do not constitute additional owner-decision inputs to this thread (the tracker pattern matched cached prose, not a fresh agent ask).
- No new owner approval is required for this REVISED-1. The fix narrows existing deterministic enforcement scope; no protected narrative artifact is edited; no governed canonical artifact (GOV/ADR/DCL/SPEC/PB/DA) is inserted.

## Requirement Sufficiency

Existing requirements sufficient. The AUQ-only enforcement contract at `.claude/rules/prime-builder-role.md` and the tracker's behavior contract at `SPEC-AUQ-POLICY-ENGINE-001` are unchanged; this proposal narrows a deterministic false-positive surface within the existing contract. Cached SessionStart payloads are the rendering surface this fix targets; SessionStart rendering itself is not modified.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation is not a bulk operation against the standing backlog. The fix is a single-function source edit (extension of `_is_inside_structural_context` in `.claude/hooks/owner-decision-tracker.py`) plus 4 new tests in the existing test file `platform_tests/hooks/test_owner_decision_tracker.py`. No MemBase insert; no formal-artifact-approval packet required (no protected narrative artifact edited; no governed canonical artifact inserted). No inventory of multiple artifacts; no review packet beyond IP-1 + IP-2 + IP-3 scoped to two files. The review packet is bounded to one hook function + one test module + 4 test assertions. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` does not require bulk-operation evidence here because no backlog mutation is in scope.

## Proposed Scope

### IP-1: Extend `_is_inside_structural_context` with section-scope exclusion

In `.claude/hooks/owner-decision-tracker.py` (around lines 183-199 per the existing structural pre-check):

- Add a 5th structural context: section-heading scope for `Pending Owner Decisions` blocks.
- Scan `text[:match_start]` for the last line matching `^#{2,3}\s+Pending Owner Decisions\s*$` (case-insensitive).
- If found, scan the remaining `text[last_heading_end:match_start]` for a subsequent line matching `^#{1,3}\s+` (any heading of equal or higher level that would close the section).
- If a `Pending Owner Decisions` heading is present AND no closing heading appears before the match position, the match is inside the cached pending block — return `True` from `_is_inside_structural_context`.
- No change to `PROSE_DECISION_PATTERNS` or `PROSE_FALSE_POSITIVE_GUARDS`. The fix is structural-context exclusion only.

### IP-2: Add 4 unit tests to the existing test module

In `platform_tests/hooks/test_owner_decision_tracker.py` (confirmed exists per `-002` finding F2 evidence at line 151):

- `test_structural_context_pending_owner_decisions_block_h3`: an `offering_or_choice` match inside a `### Pending Owner Decisions` block returns `_is_inside_structural_context = True`. Fixture text: a synthetic startup payload with a `### Pending Owner Decisions` heading followed by the DECISION-NNNN body containing the lexical match.
- `test_structural_context_pending_owner_decisions_block_h2`: same for `## Pending Owner Decisions` (h2 variant).
- `test_structural_context_pending_owner_decisions_closes_at_next_heading`: a match AFTER a sibling-level heading that closes the pending block returns `_is_inside_structural_context = False` (the structural protection ends at the next heading).
- `test_structural_context_genuine_ask_unaffected`: a normal prose decision-ask outside any pending block still matches (regression check; verifies `PROSE_DECISION_PATTERNS` enforcement remains intact for genuine asks).

### IP-3: No tracking work_item

The fix is operational hygiene (single-function hook tightening), not backlog work. No tracking `work_items` row is created. Per `GOV-STANDING-BACKLOG-001`, the standing backlog tracks new capability / defect / regression items; this fix narrows an existing deterministic false-positive class within a known hook's enforcement scope.

## Specification-Derived Verification Plan

Each linked specification maps to at least one named test or verification step.

| Linked spec / clause | Verification step | Expected result |
|---|---|---|
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | All 4 new tests assert deterministic regex/structural behavior with no LLM input | 4 PASS |
| `SPEC-AUQ-POLICY-ENGINE-001` | `test_structural_context_genuine_ask_unaffected` ensures the policy engine's positive-detection path remains intact | 1 PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | spec-to-test mapping is one test per assertion class; this table is the mapping | 4 tests cover 4 distinct assertion classes |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All target paths in-root under `E:\GT-KB` | confirmed in `## In-Root Placement Evidence` |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `bridge/INDEX.md` updated to insert REVISED-1 entry at top of this thread's version list; no deletion or rewrite | confirmed at filing time |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `## Specification Links` cites all triggered specs | applicability preflight returns `preflight_passed: true` after INDEX update |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This verification-plan table is the spec-to-test mapping | each linked spec has a named test or verification step |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | Not a bulk operation; IP-3 explicitly notes no tracking WI | clause-preflight `may_apply` (per `-002` clause table line 95); proposal text declares scope is not bulk |

Commands at implementation time (executed after Codex GO):

1. `python -m pytest platform_tests/hooks/test_owner_decision_tracker.py -v --tb=short` - all 4 new tests PASS + existing test suite continues to PASS.
2. `python -m ruff check .claude/hooks/owner-decision-tracker.py platform_tests/hooks/test_owner_decision_tracker.py` - zero errors.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-decision-tracker-cached-pending-block-exclusion` - `preflight_passed: true` against this REVISED-1 operative file.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-decision-tracker-cached-pending-block-exclusion` - exit 0; no blocking gaps.
5. Manual smoke: in a fresh session, render the cached startup payload's `### Pending Owner Decisions` block; Stop hook MUST NOT emit a block decision based on text inside that block.
6. Negative manual smoke: in the same response, append a genuine prose decision-ask outside the pending block; Stop hook MUST emit a block decision (verifies fix is scoped to the pending block, not a blanket pattern weakening).

## Risks and Rollback

- Risk: false-negative cascade if a genuine prose decision-ask appears inside a `Pending Owner Decisions` section. Mitigation: by SessionStart contract, the pending block contains a list of pre-existing decisions, not new asks. The `closes_at_next_heading` test verifies scope termination so subsequent prose is still scanned.
- Risk: section regex too narrow (matches only exact heading text `Pending Owner Decisions`). Mitigation: this is the only known recurring false-positive source; future cached-block contexts would need their own follow-up proposal.
- Risk: SessionStart payload generator changes the heading wording in a future revision. Mitigation: the SessionStart contract requires verbatim rendering of the cached payload (per the explicit "Do not summarize, paraphrase, shorten, reorder, or omit" instruction); cache-generator changes already require their own bridge thread review where this heading dependency would surface.
- Rollback: revert the new branch in `_is_inside_structural_context` and remove the 4 new tests. Hook reverts to pre-fix behavior (fenced/indented/blockquote/HTML-comment structural pre-check only).

## Sequenced Dependencies

This thread is independent of other in-flight bridge work. No coupling to startup-payload, gov-code-quality, spec-lifecycle, or active-workspace threads. The fix only touches one hook function and one test file; no shared paths with parallel-session work.

## Recommended Commit Type

`fix:` - narrows a deterministic false-positive class in an existing hook. Single-function source edit + 4 new tests. Net diff ~30 lines source + ~100 lines tests. Not net-new capability; not refactor; not chore. Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline: this is a regression-fix commit.

## Bridge-Compliance Self-Check

- First line is `REVISED`.
- Title line includes `REVISED-1` and the thread topic.
- Metadata: `bridge_kind: implementation_proposal`, `Document:`, `Version: 003`, `Responds to: bridge/gtkb-decision-tracker-cached-pending-block-exclusion-002.md`, `Author: Prime Builder (Claude, harness B)`, `Date: 2026-05-14 UTC`, `Session: S350`, `target_paths: [JSON list with 2 in-root entries]` (closes F2 of `-002`).
- `## Specification Links` is a plain heading with flat bullets; no `###` sub-headings inside; cites `bridge/INDEX.md` insertion-at-top discipline; explicitly adds the 1 missing required + 3 missing advisory specs cited by `-002` F1.
- `## Prior Deliberations` cites real DELIB IDs.
- `## Owner Decisions / Input` is non-empty, substantive; cites the operative S350 directives.
- `## Requirement Sufficiency` has exactly one operative state.
- `## Clause Scope Clarification (Not a Bulk Operation)` is present with evidence tokens (`formal-artifact-approval`, `inventory`, `review packet`).
- `## In-Root Placement Evidence` enumerates each target path.
- `## Proposed Scope` uses `### IP-N` sub-headings.
- `## Recommended Commit Type` is present (`fix:`).
- F1 from `bridge/gtkb-decision-tracker-cached-pending-block-exclusion-002.md` is closed by adding all missing specs to `## Specification Links`.
- F2 from `bridge/gtkb-decision-tracker-cached-pending-block-exclusion-002.md` is closed by reformatting `target_paths` as concrete JSON metadata.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
