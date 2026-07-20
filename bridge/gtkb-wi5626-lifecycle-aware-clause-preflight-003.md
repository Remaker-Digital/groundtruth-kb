REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Revised Implementation Proposal - Resolve lifecycle artifacts in clause preflight

bridge_kind: prime_proposal
Document: gtkb-wi5626-lifecycle-aware-clause-preflight
Version: 003
Responds to: bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-002.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5626

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Replace numeric latest-file selection in
`adr_dcl_clause_preflight.py --bridge-id <slug>` with an explicit lifecycle
state machine that selects the Prime artifact whose clauses are currently being
evaluated.

The revised state machine distinguishes a pending Prime `NO-ACTION` correction
from the substantive artifact authorized by a later corrected Loyal Opposition
verdict:

1. Latest strict `NEW` or `REVISED`: evaluate that file directly.
2. Latest strict `NO-ACTION`: evaluate that file directly while it is the
   pending correction action.
3. Latest strict `GO`, `NO-GO`, or `VERIFIED`: scan backward and evaluate the
   nearest preceding strict `NEW` or `REVISED`, skipping LO verdicts,
   `NO-ACTION` correction envelopes, and malformed historical files.
4. Missing, unsupported, unreadable, or unresolvable chains fail closed with
   the existing mandatory exit code `5`.

Explicit `--content-file` remains authoritative and unchanged.

## Finding Responses

### F1 - NO-ACTION lifecycle semantics and the live-defect proof were inconsistent

Accepted and corrected. Version 001 did not distinguish pending correction
review from the state after a corrected verdict.

The rule above now makes that distinction mechanically:

- In `NEW -> malformed verdict -> NO-ACTION`, the pending latest `NO-ACTION`
  remains directly evaluable for Loyal Opposition correction review.
- In `NEW -> malformed verdict -> NO-ACTION -> GO`, the corrected `GO` causes
  bridge-id mode to skip the correction envelope and malformed verdict and
  evaluate the original `NEW`.
- In `NEW proposal -> GO -> NEW implementation report -> VERIFIED`, the latest
  `VERIFIED` resolves to the nearest preceding `NEW`, which is the
  implementation report.

The cited foundation thread now has exact corrected `GO` at version 004.
Therefore the live proof is no longer hypothetical: after implementation,
`--bridge-id gtkb-dispatcher-next-foundation-spike` and explicit
`--content-file bridge/gtkb-dispatcher-next-foundation-spike-001.md` must both
evaluate version 001 and return the same gate result.

### F2 - Direct Slice-2 clause-preflight authority was omitted

Accepted and corrected. The direct authority is
`bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-003.md`,
approved at version 004 and terminally VERIFIED at version 008.

This proposal preserves both binding Slice-2 constraints:

- Mandatory mode fails closed with exit `5` when no operative file can be
  resolved or evaluated.
- `--report-only` remains diagnostic, adds its non-authorization banner, and
  preserves the mandatory mode's underlying exit code. It cannot satisfy
  GO/VERIFIED.

The verification plan now tests both constraints through the lifecycle-aware
resolver.

## Requirement Sufficiency

Existing requirements and the VERIFIED Slice-2 authority are sufficient. This
is a bounded resolver correction; it does not create a new bridge lifecycle or
weaken clause evidence.

## In-Root Placement Evidence

Both exact targets are inside `E:\GT-KB` and are clean at revision time:

- `scripts/adr_dcl_clause_preflight.py`
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - lifecycle authority comes from the exact
  canonical numbered thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal
  authorization evaluates the approved Prime proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification evaluates
  the Prime implementation report carrying executed spec-derived evidence.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - a pending NO-ACTION is directly
  reviewable, but a corrected verdict does not convert the correction envelope
  into implementation evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

Direct implementation authority:

- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-003.md`
  - defines the mandatory clause-test preflight.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md`
  - terminal VERIFIED evidence for fail-closed missing-operative-file and
  diagnostic-only report mode.

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` directs the Master
Prime Builder to carry Dispatcher Next and derived defects to governed
terminal states while preserving independent review, claims, and
implementation-start authorization. No additional owner input is required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-1614` - GO for the revised Slice-2 proposal and implementation-report
  conditions.
- `DELIB-1615` - missing-operative-file mandatory fail-closed requirement.
- `DELIB-1616` - initial Slice-2 review leading to strict mandatory semantics.
- `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md`
  - terminal verification of those constraints.

## Revised Scope

1. Add strict first-line status parsing for exact thread files.
2. Enumerate only exact `<slug>-NNN.md` candidates and retain numeric version
   order.
3. Implement the four-rule lifecycle state machine in the Revision Claim.
4. Ignore malformed historical status files as evidence, while failing closed
   if the remaining strict chain cannot resolve an operative artifact.
5. Preserve explicit `--content-file` behavior.
6. Preserve mandatory exit `5` and report-only non-authorization semantics.
7. Add focused fixtures for proposal, revision, pending correction, corrected
   verdict, implementation report, malformed history, unsupported terminal
   state, missing/unreadable chain, exact sibling isolation, and report-only.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; WI-5626; TEST-11671; bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-002.md; bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-008.md",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Exact numbered bridge chain, lifecycle state machine, operative Prime artifact, mandatory clause evaluation, implementation-start authorization, implementation report, independent verification.",
  "before_behavior": "Bridge-id mode evaluates the numerically latest file, including LO verdict and correction envelopes that do not carry the substantive Prime clause evidence.",
  "after_behavior": "Pending Prime actions remain directly evaluable; a following LO verdict resolves to the nearest substantive Prime NEW or REVISED artifact; unresolved chains fail closed.",
  "self_descriptive_naming": "Resolver helpers and tests name strict status parsing and operative lifecycle artifact selection.",
  "obsolete_guidance_disposition": "Numeric top-of-stack is no longer described as synonymous with operative content. No historical bridge artifact is rewritten.",
  "history_preservation": "All numbered bridge files, deliberations, work-item versions, and authorization records remain append-only.",
  "baseline": {
    "foundation_thread": "NEW v001, malformed decorated verdict v002, pending correction v003, exact corrected GO v004",
    "slice_2": "terminal VERIFIED at version 008 with mandatory fail-closed and diagnostic-only report-mode semantics",
    "implementation_targets": "two clean files"
  },
  "expected_result": {
    "pending_no_action": "version 003 is directly evaluable while latest",
    "corrected_foundation_chain": "latest GO v004 resolves to substantive NEW v001",
    "implementation_report_chain": "VERIFIED resolves to the nearest preceding NEW report",
    "runtime_effect": "no dispatcher restart, reconfiguration, route, cap, lease, TAFE, credential, deployment, release, or Git operation"
  },
  "rollback": {
    "instructions": "Before VERIFIED, revert only the two scoped files and file a revised implementation report. After VERIFIED, use a governed follow-on correction.",
    "verification": "Rerun the focused resolver tests, Slice-2 fail-closed/report-only regressions, and live foundation equivalence proof."
  },
  "hard_invariants": [
    "Explicit --content-file remains authoritative and unchanged.",
    "Only exact numbered files for the requested slug participate.",
    "Malformed status files never become clause evidence.",
    "Missing or unresolvable lifecycle chains fail closed with exit 5.",
    "Report-only remains diagnostic and non-authorizing.",
    "No implementation occurs without independent GO, exact claim, and implementation-start authorization."
  ],
  "fail_closed_conditions": [
    "No exact canonical versioned files exist.",
    "The latest strict verdict has no preceding strict NEW or REVISED artifact.",
    "The latest strict lifecycle status is unsupported by this resolver.",
    "A selected candidate is unreadable.",
    "Clause evidence is absent from the resolved artifact."
  ],
  "essential_context_preservation": "Preserve WI-5626, TEST-11671, the owner program deliberation, Slice-2 terminal authority, malformed-status evidence tracked by WI-5625, exact thread isolation, and the foundation spike target boundary."
}
```

## Specification-Derived Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Proposal authorization | Fixture `NEW proposal -> GO` | Bridge-id mode evaluates the NEW proposal and matches explicit content mode. |
| Pending correction | Fixture `NEW -> malformed verdict -> NO-ACTION` | Latest strict NO-ACTION is evaluated directly while pending. |
| Corrected verdict | Fixture `NEW -> malformed verdict -> NO-ACTION -> GO` | Resolver skips malformed and correction envelopes and evaluates the original NEW. |
| Revised proposal | Fixture `NEW -> NO-GO -> REVISED -> GO` | Resolver evaluates the nearest REVISED artifact. |
| Verification lifecycle | Fixture `NEW proposal -> GO -> NEW implementation report -> VERIFIED` | Resolver evaluates the newest NEW implementation report. |
| Slice-2 fail closed | Missing thread, unsupported latest strict status, unreadable selected file, and verdict without preceding NEW/REVISED | Mandatory mode exits `5` and reports no operative lifecycle artifact. |
| Slice-2 report-only | Run each clean and failing fixture with `--report-only` | Diagnostic banner is present and the underlying mandatory exit code is unchanged; output is non-authorizing. |
| Exact thread | Prefix-sibling fixture | A sibling slug cannot influence selection. |
| Explicit override | Existing content-file tests | Explicit content behavior remains unchanged and authoritative. |
| Focused regression | `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | Exit 0. |
| Static quality | `python -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py` | Exit 0. |
| Formatting | `python -m ruff format --check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py` | Exit 0. |
| Live defect proof | Run bridge-id mode for `gtkb-dispatcher-next-foundation-spike` and explicit content mode for version 001 | Both report version 001 as operative, evaluate identical bytes, and return the same gate result. |
| Live nonimpairment | `gt bridge dispatch health --json` before and after | Daemon remains running with no restart or configuration/state mutation. |

## Acceptance Criteria

- Pending `NO-ACTION` is directly evaluable only while it is the latest strict
  Prime action.
- A corrected LO verdict resolves past correction and malformed envelopes to
  the nearest substantive Prime `NEW` or `REVISED`.
- Proposal and implementation-report phases resolve independently and
  deterministically.
- Missing, unsupported, unreadable, and unresolvable chains fail closed with
  mandatory exit `5`.
- Report-only remains diagnostic and non-authorizing.
- Explicit content mode and exact sibling isolation remain unchanged.
- The corrected foundation live proof selects version 001 through both modes.
- Only the two declared clean targets change.
- The live dispatcher is not restarted or reconfigured.

## Pre-Filing Preflight Subsection

The governed revision helper must pass candidate applicability and mandatory
clause preflights with no missing required/advisory specifications and no
blocking gaps before filing.

## Risks and Rollback

- Risk: multiple `NEW` phases could select the proposal instead of the
  implementation report. Mitigation: always choose the nearest preceding
  strict `NEW` or `REVISED` behind the latest LO verdict.
- Risk: pending correction and corrected verdict states could collapse.
  Mitigation: explicit top-state rules plus separate fixtures for both shapes.
- Risk: malformed historical files could become authority. Mitigation: strict
  first-line parsing excludes them and unresolved chains fail closed.
- Risk: resolver changes could weaken Slice-2 behavior. Mitigation: direct
  terminal Slice-2 authority plus mandatory exit and report-only regression
  tests.
- Rollback: restore only the two scoped files before VERIFIED and file a
  revised report. After VERIFIED, use a governed follow-on proposal.
