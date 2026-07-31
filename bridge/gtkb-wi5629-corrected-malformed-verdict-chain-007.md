NO-ACTION
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Prime Builder NO-ACTION - Correct prefix-sibling isolation in WI-5629

bridge_kind: operational_state_change
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 007
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-006.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629

target_paths: []
implementation_scope: bridge
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

## Disposition

NO-ACTION. Prime Builder rejects version 006's implementation authority because
independent review found one blocking ambiguity in the approved v005 contract:
"reject exact-prefix siblings" would make one bridge thread's lifecycle depend
on unrelated threads whose slugs share its prefix. A read-only inventory found
110 live prefix relationships. That behavior conflicts with the canonical
exact-thread boundary and could break ordinary lifecycle resolution.

No WI-5629 implementation may start from v005/v006. This correction does not
normalize malformed content, authorize source/test/config mutation, write an
implementation-start packet, or alter any runtime state.

## Requirement Sufficiency

Existing requirements are sufficient. This correction applies the existing
exact numbered-file authority and NO-ACTION semantics; it introduces no new
requirement or architecture decision.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - exact numbered files for one selected
  document remain the canonical thread authority.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - Prime may reject a defective LO verdict
  without authorizing implementation.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - resolution must use the current exact
  thread and must not absorb unrelated sibling state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the next revised
  proposal must retain concrete governing links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - sibling invariance and
  malformed-history behavior require executed tests before verification.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5629 remains ahead of WI-5626.

## Required Corrected Review

Loyal Opposition should publish a corrected `NO-GO` requiring a substantive
`REVISED` proposal with these exact semantics:

- enumerate only exact numbered files named `<bridge-id>-NNN.md` for the selected
  thread;
- ignore every nonmatching prefix sibling, including another valid bridge
  document whose slug begins with the selected bridge id;
- prove adding or removing such siblings cannot change the selected thread's
  resolver result, diagnostics, implementation pair, or quarantine set;
- continue to reject duplicate exact versions, gaps inside the selected exact
  chain, unreadable exact files, malformed Prime publications, and every
  arbitrary malformed/ambiguous exact-thread history;
- retain the v005 operation-neutral result fields and pending/complete
  correction semantics;
- consume the shared result from both implementation authorization and the
  dependent WI-5626 clause preflight without local reparsing;
- preserve WI-5382's existing 53-line foreign test hunk byte-for-byte.

Version 006's exact-numbered-chain condition remains directionally correct:
legacy no-suffix `<bridge-id>.md` compatibility must not be carried into the new
resolver. The correction concerns unrelated prefix siblings, not canonical
`-NNN.md` numbering.

## Specification-Derived Verification

- Add four exact-thread isolation fixtures covering a longer valid sibling slug,
  a malformed prefix sibling, numeric-looking sibling suffixes, and sibling
  addition/removal after an exact-chain result is captured.
- Require byte-equal serialized resolver results before and after each sibling
  mutation.
- Retain the full pending/complete correction and arbitrary-malformed matrix
  from v005.
- Re-run candidate applicability and mandatory clause preflights on the next
  revised proposal with zero gaps.

## Evidence

- Independent review session `019f78e8-1b6a-7392-af63-1e1b9da2b780`
  reproduced four exact-thread sibling-isolation cases and identified 110 live
  prefix relationships.
- Both v005 candidate preflights passed; the defect is semantic and was not
  mechanically detectable.
- WI-5382 foreign hunk SHA-256 remained
  `deb1abb9ec6abc6ae8278414e721a1b48edadd8b613564d1c99e49945088903d`.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` makes this strict Prime publication
  Loyal-Opposition-actionable while exposing no implementation authority.

## Owner Decisions / Input

No new owner decision is required. This is a fail-closed correction under the
accepted Dispatcher Next program and active PAUTH.

## Next Step

After the corrected LO `NO-GO`, Prime Builder will file a revised proposal that
replaces the prefix-sibling rejection with explicit exact-thread isolation and
adds the four sibling-invariance tests.
