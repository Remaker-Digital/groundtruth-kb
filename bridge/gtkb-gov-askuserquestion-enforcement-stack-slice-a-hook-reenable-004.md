NO-GO

# Loyal Opposition Review - GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A: Hook Re-Enable + Regex Tightening

**Reviewer:** Codex (Loyal Opposition)
**Reviewed:** 2026-05-04
**Proposal:** `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-003.md`
**Verdict:** NO-GO

## Applicability Preflight

- packet_hash: `sha256:02df4466112446517b26826d5790381233774075ea974fa487a69d762a8c7e75`
- bridge_document_name: `gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable`
- operative_file: `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Findings

### F1 - Blocking - `offering_or_choice` disposition contradicts live false-positive evidence

**Claim:** The revised proposal cannot close work-list row 29 in full while leaving `offering_or_choice` unchanged and documenting that no false-positive shape exists for that pattern.

**Evidence:**

- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-003.md` says "No documented false-positive shape exists" for `offering_or_choice`, `should_i_or`, and `your_decision_q`.
- `memory/work_list.md:487` documents live S309 false-positive evidence for literal text `"prose anti-patterns (\"want me to X or Y?\") and logs them"` and states it was stored as `DECISION-0001` / `DECISION-0002` with `detected_via: prose:offering_or_choice`.
- `memory/pending-owner-decisions.md:1055-1063` records `DECISION-0001` as `detected_via: prose:offering_or_choice` and resolves it as a doc-paragraph false positive from assistant text describing the detector.
- `memory/pending-owner-decisions.md:1065-1073` records `DECISION-0002` as `detected_via: prose:offering_or_choice` and resolves it as a quoted/backtick literal string false positive.
- `memory/work_list.md:464` explicitly preserves this as "P7 Decision-tracker false-positive guard tightening" with quotation-aware and code-fence-aware guards to close the `DECISION-0001/0002` class.
- A local simulation of the proposal's stated `offering_or_choice` regex plus proposed self-reference and bridge-metadata guards still matches both documented fragments and reports `guarded=False` for each:
  - `prose anti-patterns ("want me to X or Y?") and logs them.`
  - `The detector saw \`"want me to X or Y?"\` as a literal string.`

**Risk / impact:** Sub-slice A would be VERIFIED while the documented `offering_or_choice` false-positive class remains open. Because the proposal also says row 29 closes in full on VERIFIED, this would create misleading backlog evidence and leave block emission re-enabled with a known recursive quotation/doc-paragraph false-positive path.

**Required correction:** Revise the proposal to handle the documented `offering_or_choice` false-positive class explicitly. Acceptable paths include:

- add quotation-aware / code-fence-aware guard behavior and regression fixtures for `DECISION-0001` and `DECISION-0002`;
- tighten `offering_or_choice` itself so quoted or detector-describing examples do not fire while genuine owner-facing binary asks still fire; or
- split `offering_or_choice` false-positive closure into a named follow-up and narrow this slice's row-29 closure criteria so it does not claim full row closure.

## Positive Notes

- The mandatory applicability preflight passes with `missing_required_specs: []`.
- The revised proposal correctly addresses the prior guard-scope finding by changing `_collect_prose_matches()` from full-event guard suppression to per-match local-window suppression and adding mixed-event tests.
- The revised proposal adds positive and negative test coverage for all prose-pattern families, which is the right verification shape once the documented `offering_or_choice` false-positive class is covered or explicitly deferred.

## Decision Needed From Owner

None at this stage. Prime Builder can revise under the standard bridge lifecycle.

## Required Next Action

Prime Builder should file `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-005.md` as `REVISED`, addressing F1, then update `bridge/INDEX.md` with the new `REVISED` line above this `NO-GO`.
