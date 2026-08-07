REVISED
::init gtkb pb
::open build
author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-08-04T14-29-28Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive;role=prime-builder;::init gtkb pb;build activity

bridge_kind: prime_proposal
Document: gtkb-wi5626-lifecycle-aware-clause-preflight
Version: 007 (REVISED; substantive response to NO-GO v006)
Responds to: bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-006.md
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

# REVISED Implementation Proposal - WI-5626 lifecycle-aware clause preflight (shared resolver contract)

## Revision Claim

Version 005 was NO-GO at version 006. The single blocking finding F4 requires
the WI-5626 consumer to align with a **public, operation-neutral** WI-5629
resolver contract that separates lifecycle/audit resolution from operation
authorization, and to consume named public fields without reparsing numbered
files. This revision makes that alignment explicit and implementable against
the **already-landed, independently VERIFIED** WI-5629 shared resolver
(`scripts/bridge_lifecycle_resolver.py`), which WI-5626 imports and consumes.

## Response To Finding F4 (P0)

F4 requires: (1) one public operation-neutral WI-5629 resolver contract
separating lifecycle/audit resolution from operation authorization; (2) named
public result and error fields consumed by both `implementation_authorization.py`
and `adr_dcl_clause_preflight.py`; (3) aligned proposal matrices plus
shared-resolver and both-consumer tests; (4) citation of
`DCL-PROJECT-DEPENDENCY-ORDERING-001` and a fresh operation-time check.

### (1) Public operation-neutral contract - ADOPTED from landed WI-5629

`scripts/bridge_lifecycle_resolver.py` (independently VERIFIED via
`gtkb-wi5629-corrected-malformed-verdict-chain`) already exposes:

```python
resolve_bridge_lifecycle(project_root: Path, bridge_id: str) -> BridgeLifecycleResolution
```

`BridgeLifecycleResolution` (frozen dataclass) separates **audit/lifecycle
state** from **operation authorization**:

- `audit_versions: tuple[BridgeVersion, ...]` - full structural history.
- `latest_strict_state: BridgeVersion` - the operative strict lifecycle state.
- `review_artifact: BridgeVersion | None` - the reviewable latest strict
  artifact (may be a pending `NO-ACTION`).
- `implementation_artifact: BridgeVersion | None` - the approved proposal or
  report for implementation authority.
- `implementation_verdict: BridgeVersion | None` - the latest `GO`/`NO-GO`.
- `quarantined_paths: tuple[str, ...]` - malformed versions quarantined.
- `blocking_diagnostics: tuple[LifecycleDiagnostic, ...]` - fail-closed
  diagnostics.

`BridgeLifecycleResolutionError` (RuntimeError) carries a stable `code`, exact
`path`, `version`, and `diagnostics`. It is the single failure surface:
arbitrary malformed, unreadable, ambiguous, cross-thread, stale-fallback, or
incomplete correction state raises this error.

This is the public, operation-neutral contract. It does not make malformed
content a lifecycle status; it quarantines paths and reports diagnostics.

### (2) Named public fields consumed by both consumers - ALIGNED

- `implementation_authorization.py` consumes `implementation_artifact`,
  `implementation_verdict`, `latest_strict_state`, and
  `blocking_diagnostics`/`BridgeLifecycleResolutionError` to decide
  implementation authority (operation authorization).
- `adr_dcl_clause_preflight.py` consumes `latest_strict_state` and
  `implementation_artifact` to select the clause-bearing Prime artifact, and
  maps every `BridgeLifecycleResolutionError` to mandatory exit 5
  (lifecycle/audit resolution), while never parsing numbered files itself.

Both consumers read the **same** named fields from the **same**
`resolve_bridge_lifecycle` call. No consumer owns a second status parser or a
malformed-history exception.

### Pending-correction semantics (the F4 core inconsistency) - RESOLVED

The F4 inconsistency was that a pending `NO-ACTION` must be "evaluated
directly" while the same pending correction "raises a fail-closed resolver
error." This is resolved by the contract's separation:

- `resolve_bridge_lifecycle` exposes the pending correction's reviewable strict
  `NO-ACTION` as `review_artifact` (a **reviewable audit view**), while
  simultaneously leaving `implementation_artifact` unresolved and carrying a
  `PENDING_CORRECTION_DIAGNOSTIC` in `blocking_diagnostics`.
- `adr_dcl_clause_preflight.py` uses `latest_strict_state` /
  `implementation_artifact` for **clause-bearing selection**, which fail closed
  (exit 5) while a correction is pending; it does **not** use the pending
  `review_artifact` as an operative implementation artifact.
- Only after the complete two-link corrected chain (per WI-5629) is strict
  does `implementation_artifact` resolve and quarantine the malformed LO
  verdict, enabling GO-based implementation authority.

Thus both the version-002 F1 pending-correction retention **and** the WI-5629
fail-closed invariant hold, with no undocumented local exception.

### (3) Aligned matrices + shared-resolver and both-consumer tests

The version-005 consumer matrix is retained and aligned to the contract's named
fields. The test additions are:

- `NEW -> malformed LO verdict -> NO-ACTION` (pending): `resolve_bridge_lifecycle`
  returns `review_artifact == NO-ACTION`, `implementation_artifact is None`,
  `PENDING_CORRECTION_DIAGNOSTIC` present; clause preflight exits 5.
- `NEW -> malformed LO verdict -> NO-ACTION -> corrected GO` (complete):
  `implementation_artifact == corrected GO`, malformed verdict quarantined;
  clause preflight selects the corrected Prime artifact and passes.
- `NEW -> malformed REVISED -> GO`: resolver raises
  `BridgeLifecycleResolutionError`; clause preflight exits 5, no operative
  artifact.
- Ordinary `NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED` phases: clause preflight
  selects `latest_strict_state` / `implementation_artifact` per phase.
- Both-consumer contract test: the same resolver result feeds both
  `implementation_authorization` authority logic and clause-preflight
  selection without reparse.

### (4) DCL-PROJECT-DEPENDENCY-ORDERING-001

- `DCL-PROJECT-DEPENDENCY-ORDERING-001` is cited below.
- At implementation start, a fresh operation-time check confirms canonical
  membership order (WI-5629 `membership_order: 1`, WI-5626 `membership_order:
  2`), predecessor exact `VERIFIED` (WI-5629), and absence of an active
  predecessor claim. The current records already satisfy this; the gate is
  made durable and explicit.

## Version-005 Findings Already Closed (retained)

- Version 002 F1/F2 (pending vs corrected NO-ACTION separation, direct terminal
  Slice-2 authority): retained.
- Version 003 (live proof, mandatory exit 5, diagnostic-only report mode):
  retained.
- Version 004 F3 (blanket malformed-history skipping removed): retained; WI-5626
  remains hard-gated on WI-5629 as single lifecycle authority.

## Implementation Scope

1. In `scripts/adr_dcl_clause_preflight.py`, import and call
   `resolve_bridge_lifecycle` from `scripts.bridge_lifecycle_resolver`;
   replace any status reparse with consumption of `latest_strict_state` /
   `implementation_artifact` / `review_artifact`; map every
   `BridgeLifecycleResolutionError` to mandatory exit 5.
2. Add the focused consumer tests in
   `platform_tests/scripts/test_adr_dcl_clause_preflight.py` covering the
   matrix in (3).
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

- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-005.md` - prior REVISED
  proposal.
- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-006.md` - NO-GO with
  finding F4.
- `gtkb-wi5629-corrected-malformed-verdict-chain` - independently VERIFIED
  resolver authority.

## Request

Request independent Loyal Opposition review (GO/NO-GO) of this REVISED
proposal. If GO, Prime Builder will acquire a fresh claim, pass schema-v3
implementation-start for the two declared targets, implement the consumer
alignment, and file an implementation report requesting VERIFIED.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
