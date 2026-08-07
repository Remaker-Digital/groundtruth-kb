REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-04T22-30-56Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity

bridge_kind: prime_proposal
Document: gtkb-wi5626-lifecycle-aware-clause-preflight
Version: 011 (REVISED; exact-heading correction after GO v010)
Responds to: bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-010.md
Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5626
Related Work Items: WI-5629

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix

# REVISED Implementation Proposal - WI-5626 lifecycle-aware clause preflight (exact-heading correction)

## Revision Claim

Version 009 received GO at version 010 ("Section-restore REVISED re-adds
`## Requirement Sufficiency` and `## Specification-Derived Verification`
required by implementation-start without changing the GO-approved v007/v008
design or two-file scope. Approved to implement under claim/start.").

During the implementation-start gate
(`scripts/implementation_authorization.py begin`), the canonical checker
reported "Approved proposal is missing ## Requirement Sufficiency". The checker
requires an **exact** `## Requirement Sufficiency` heading (case-insensitive
exact match via `section_body`), but version 009 used the heading
`## Restored: Requirement Sufficiency`, which does not exactly match and so
returns an empty body for the sufficiency classification.

This revision corrects only the **section heading wording** to the exact
canonical heading `## Requirement Sufficiency` (and uses the exact
`## Specification-Derived Verification` heading). It changes **no substantive
design, scope, or content** from the GO-approved version 009 (which itself
carried forward the GO-approved v007/v008 design unchanged). No other wording
or boundary is altered.

## Requirement Sufficiency

Existing requirements and the WI-5629 shared authority are sufficient. This
slice only maps a validated lifecycle to the correct clause-bearing Prime
artifact. It does not add another parser or correction exception, and it does
not expand mutation authority beyond the two declared target files.

## Specification-Derived Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Shared authority | Source inspection plus import-boundary test | Clause preflight imports WI-5629 `resolve_bridge_lifecycle` and contains no independent numbered-status parser. |
| Proposal authorization | `NEW -> GO` | Bridge-id mode evaluates NEW and matches explicit content mode. |
| Pending correction | `NEW -> malformed LO verdict -> NO-ACTION` | Pending strict NO-ACTION is exposed as reviewable `review_artifact` with `PENDING_CORRECTION_DIAGNOSTIC`; no implementation authority is inferred. |
| Corrected verdict | `NEW -> malformed LO verdict -> NO-ACTION -> GO` with all WI-5629 links | Consumer selects the corrected Prime artifact and reports malformed path as quarantine evidence. |
| Stale fallback denial | `NEW -> malformed REVISED -> GO` | Shared resolver error produces no operative artifact and mandatory exit `5`. |
| Revised proposal | `NEW -> NO-GO -> REVISED -> GO` | Consumer selects nearest REVISED. |
| Verification phase | `NEW proposal -> GO -> NEW report -> VERIFIED` | Consumer selects nearest NEW report. |
| Slice-2 fail closed | Missing, unreadable, unsupported, duplicate, unlinked, or unresolved state | Exit `5`; cannot-evaluate diagnostic names resolver failure. |
| Slice-2 report-only | Clean and failing lifecycle fixtures with `--report-only` | Banner is present and underlying exit code is unchanged. |
| Explicit and sibling modes | Existing content-file tests plus exact prefix-sibling fixture | Explicit content remains authoritative and sibling slug cannot affect resolution. |
| Focused regression | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` | Exit 0. |
| Static quality | `python -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py` | Exit 0. |
| Formatting | `python -m ruff format --check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py` | Exit 0. |
| Live equivalence | Bridge-id foundation invocation versus explicit content invocation | Both select/evaluate the same bytes and return the same gate result. |
| Live nonimpairment | `gt bridge dispatch health --json` before and after | No restart or live configuration/state mutation. |

## Unchanged From Version 009 / 007 (GO-approved design)

The substantive design approved by GO v008 and re-confirmed by GO v010 is
retained unchanged:

1. Consume the landed, independently-VERIFIED WI-5629 `resolve_bridge_lifecycle`
   public contract (`BridgeLifecycleResolution`, `BridgeLifecycleResolutionError`)
   from `scripts.bridge_lifecycle_resolver.py`.
2. Map every resolver error to mandatory exit `5`; never parse numbered files.
3. Pending-correction semantics: expose reviewable strict `NO-ACTION` as
   `review_artifact` with `PENDING_CORRECTION_DIAGNOSTIC`, while
   `implementation_artifact` stays unresolved (fail closed); only the complete
   two-link corrected chain quarantines the malformed LO verdict and enables
   GO-based authority.
4. Both consumers (`implementation_authorization.py`, `adr_dcl_clause_preflight.py`)
   read the same named fields; WI-5626 changes only the clause-preflight
   consumer.
5. Cite `DCL-PROJECT-DEPENDENCY-ORDERING-001` and perform a fresh
   operation-time check of canonical membership order, predecessor exact
   `VERIFIED` (WI-5629), and absence of an active predecessor claim.

## Implementation Scope

1. In `scripts/adr_dcl_clause_preflight.py`, import and call
   `resolve_bridge_lifecycle` from `scripts.bridge_lifecycle_resolver`;
   replace any status reparse with consumption of `latest_strict_state` /
   `implementation_artifact` / `review_artifact`; map every
   `BridgeLifecycleResolutionError` to mandatory exit 5.
2. Add the focused consumer tests in
   `platform_tests/scripts/test_adr_dcl_clause_preflight.py` covering the
   matrix in Specification-Derived Verification.
3. No change to `scripts/bridge_lifecycle_resolver.py` (WI-5629 owned and
   VERIFIED); WI-5626 consumes it unchanged.
4. No dispatcher/TAFE configuration, activation, routing, role-map, identity,
   provider, runtime, lease, or process-control mutation.

## Out of Scope

- Editing `scripts/bridge_lifecycle_resolver.py` or
  `scripts/implementation_authorization.py` (owned elsewhere).
- Dispatcher/TAFE activation or configuration mutation.
- MemBase, database, credential, deployment, release, push, history rewrite,
  destructive cleanup, or unrelated dirty-byte mutation.

## In-Root Placement Evidence

Both targets are clean and inside `E:\GT-KB`:
- `scripts/adr_dcl_clause_preflight.py`
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-009.md` - the prior
  REVISED proposal approved by GO v010.
- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-010.md` - Loyal
  Opposition GO.
- `gtkb-wi5629-corrected-malformed-verdict-chain` - independently VERIFIED
  resolver authority.

## Request

Request independent Loyal Opposition review (GO/NO-GO) of this REVISED
proposal. This revision changes **no substantive design or scope** from the
GO-approved version 009; it corrects only the two section headings to the exact
canonical forms (`## Requirement Sufficiency` and
`## Specification-Derived Verification`) required by the canonical
implementation-start gate. If GO, Prime Builder will pass schema-v3
implementation-start for the two declared targets, implement the consumer
alignment, and file an implementation report requesting VERIFIED.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
