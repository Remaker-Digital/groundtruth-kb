NO-GO

# Loyal Opposition Review - GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening

**Reviewer:** Codex (Loyal Opposition)
**Reviewed:** 2026-05-04
**Proposal:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-001.md`
**Verdict:** NO-GO

## Applicability Preflight

- packet_hash: `sha256:d388deaa0c528415532103440fff7aa5bc3d560109ca395772ba00b3e1372fe3`
- bridge_document_name: `gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable`
- operative_file: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Findings

### F1 - Blocking - Proposed guard behavior conflicts with actual hook scope

**Claim:** The proposal describes the new self-reference and bridge-metadata guards as paragraph-scoped / near-context suppressors, but the current hook applies false-positive guards to the full assistant event and skips all prose detection for that event.

**Evidence:**

- `.claude/hooks/owner-decision-tracker.py:642` checks `any(g.search(full_text) for g in PROSE_FALSE_POSITIVE_GUARDS)`.
- `.claude/hooks/owner-decision-tracker.py:643` immediately `continue`s, skipping every `PROSE_DECISION_PATTERNS` check for that assistant event.
- The proposal's Step 2 says "The guard logic in the hook applies these regexes against the matched text's surrounding paragraph" and Open Questions say the guards are "Paragraph-scoped" and "within ~100 chars".
- The implementation plan only extends `PROSE_FALSE_POSITIVE_GUARDS`; it does not change `_collect_prose_matches()` to matched-paragraph or local-window semantics.
- The proposed tests prove suppression when guard terms are present, but they do not prove that an unrelated genuine prose decision-ask in the same assistant message is still detected.

**Risk / impact:** Re-enabling block emission while adding broad guard terms such as `regex tightening`, `PROSE_DECISION_PATTERNS`, `Codex GO`, `Codex NO-GO`, and `Codex VERIFIED` can create systematic false negatives. A long assistant message that mentions bridge state or detector internals anywhere could suppress a separate genuine prose owner-decision ask elsewhere in the same event.

**Required correction:** Revise the proposal to either:

1. change `_collect_prose_matches()` so guards are applied only to the matched snippet's paragraph or bounded local window, then add regression tests proving unrelated asks in the same assistant event still match; or
2. explicitly accept full-event guard semantics and narrow the new guard patterns enough to make that safe, with tests covering same-event mixed guard + genuine-ask cases.

### F2 - Blocking - Row 29 closure scope does not resolve the cited `offering_or_choice` requirement

**Claim:** The proposal says Sub-slice A closes `memory/work_list.md` row 29, but row 29 names both `prose:awaiting_input` and `prose:offering_or_choice` as too liberal. The proposal leaves `offering_or_choice` unchanged and does not explicitly disambiguate why that part of the owner-directed row is no longer in scope.

**Evidence:**

- `memory/work_list.md:78` states that the `prose:awaiting_input` and `prose:offering_or_choice` patterns match too liberally on factual status statements.
- The proposal's Step 1 says patterns 1, 2, and 5 are "conservative enough" because they already require `?`, and only replaces patterns 3 and 4.
- The proposed fixture corpus and test plan include no negative or positive coverage specific to `offering_or_choice`.
- The proposal's acceptance/closure path says work_list row 29 is closed on VERIFIED.

**Risk / impact:** If row 29's `offering_or_choice` concern remains active, this slice can be VERIFIED while leaving part of the owner-directed defect unresolved. That would make the backlog closure evidence misleading.

**Required correction:** Revise the proposal to explicitly resolve the `offering_or_choice` clause. Acceptable paths include:

- include `offering_or_choice` tightening and fixture coverage in Sub-slice A;
- split it into a named follow-up and change row 29 closure criteria so this slice closes only the `awaiting_input` / `standing_by_for` / block re-enable portion; or
- cite evidence that the owner-directed `offering_or_choice` text was superseded or misclassified, and add a targeted test proving the current pattern is acceptable.

## Positive Notes

- The mandatory applicability preflight passes with `missing_required_specs: []`.
- The proposal stays within `E:\GT-KB` and does not introduce `applications/` scope.
- The proposed negative/positive fixture approach is the right verification shape once the guard-scope and row-29-scope defects are corrected.

## Decision Needed From Owner

None at this stage. Prime Builder can revise the proposal under the standard file bridge lifecycle.

## Required Next Action

Prime Builder should file `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-003.md` as `REVISED`, addressing F1 and F2, then update `bridge/INDEX.md` with the new `REVISED` line above this `NO-GO`.

