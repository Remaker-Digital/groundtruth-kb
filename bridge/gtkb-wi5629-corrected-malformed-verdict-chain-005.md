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

# Revised Implementation Proposal - Operation-neutral corrected bridge lifecycle resolution

bridge_kind: prime_proposal
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 005
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-004.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629

target_paths: ["scripts/bridge_lifecycle_resolver.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Create one strict, operation-neutral resolver for exact numbered bridge files
and make implementation authorization consume it. The resolver distinguishes:

1. structural lifecycle validity;
2. the latest strict state visible for audit;
3. the Prime artifact currently reviewable by Loyal Opposition; and
4. the proposal/verdict pair, if any, that can authorize implementation.

This separation resolves the dependent WI-5626 contract. An exact pending
correction:

```text
strict Prime NEW/REVISED vN
-> malformed LO-verdict-shaped vN+1
-> strict Prime NO-ACTION vN+2 responding exactly to vN+1
```

is structurally resolvable and exposes vN+2 as `review_artifact`. It exposes no
`implementation_artifact` or `implementation_verdict`, does not quarantine the
malformed file, and carries a stable implementation-blocking diagnostic.

Only the completed correction:

```text
strict Prime NEW/REVISED vN
-> malformed LO-verdict-shaped vN+1
-> strict Prime NO-ACTION vN+2 responding exactly to vN+1
-> strict corrected LO GO/NO-GO/VERIFIED vN+3 responding exactly to vN+2
```

may quarantine vN+1 from lifecycle authority. A corrected `GO` exposes the
nearest valid Prime proposal and corrected GO as the implementation pair.
Arbitrary malformed, unreadable, duplicate, non-adjacent, cross-thread,
wrong-role, wrong-document, wrong-link, Prime-shaped malformed, or multiply
malformed state remains a structural resolver error. Malformed content never
becomes a valid status.

## Finding Responses

### WI-5626 v006 F4 - Pending correction producer/consumer contradiction

Accepted and corrected. Version 001 conflated structural resolution with
implementation authorization by making a pending correction a resolver error.
This revision defines a public result that both consumers can use without
reparsing:

- `audit_versions`: every exact version and its strict or malformed
  classification, oldest first;
- `latest_strict_state`: the latest strictly parsed version record;
- `review_artifact`: the strict Prime artifact that Loyal Opposition can
  evaluate now;
- `implementation_artifact`: the strict Prime proposal authorized for
  implementation, or `None`;
- `implementation_verdict`: the authorizing strict GO record, or `None`;
- `quarantined_paths`: malformed paths superseded by a complete correction;
- `blocking_diagnostics`: stable typed diagnostics, including
  `PENDING_CORRECTION_NO_IMPLEMENTATION_AUTHORITY`.

Structural ambiguity raises `BridgeLifecycleResolutionError` and returns no
result. A pending correction returns a result because its strict NO-ACTION is a
real, reviewable Prime publication, but its implementation fields remain
`None`. `implementation_authorization.py` requires a non-null implementation
pair and rejects every blocking diagnostic applicable to implementation.
WI-5626 can later consume `review_artifact` and structural errors without
inventing a second parser or weakening implementation authority.

### WI-5626 v006 dependency-order requirement

Accepted. `DCL-PROJECT-DEPENDENCY-ORDERING-001` is now explicit. Operation-time
implementation start must confirm:

- WI-5629 is membership order 1 and WI-5626 is order 2 in
  `PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE`;
- WI-5629 has exact independent GO and the active WI-5629 claim;
- no dependent WI-5626 implementation has started;
- PAUTH v4 remains active and covers the exact four-file scope.

WI-5626 remains prohibited from implementation until WI-5629 is independently
VERIFIED and its claim is absent.

## Requirement Sufficiency

Existing requirements are sufficient:

- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered files remain canonical; malformed
  state fails closed unless an exact append-only correction proves its
  disposition.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - Prime NO-ACTION rejects an invalid LO
  verdict and requests corrected review without authorizing implementation.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5629 precedes WI-5626.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - a corrected GO
  must mint and finalize the normal implementation-start packet.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - every decision is derived from current
  numbered files, claim, PAUTH, and project membership.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the repair does not restart,
  reconfigure, deploy, or replace the live dispatcher.
- `GOV-WORK-TREE-HYGIENE-001` - preserve foreign WI-5382 test bytes and isolate
  this exact hunk.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

No new owner decision is required. The accepted owner objective and PAUTH v4
already authorize this prerequisite repair.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## In-Root And Baseline Evidence

All targets are inside `E:\GT-KB`:

- `scripts/bridge_lifecycle_resolver.py` (new);
- `scripts/implementation_authorization.py` (tracked and clean);
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py` (new);
- `platform_tests/scripts/test_implementation_authorization.py` (tracked with
  53 foreign lines from terminal VERIFIED WI-5382).

The exact 53-line WI-5382 diff is captured before implementation and preserved
byte-for-byte. No other dirty path is in scope.

Direct implementation authorities:

- `bridge/gtkb-dispatch-malformed-status-token-quarantine-004.md`;
- `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md`;
- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-006.md`;
- `bridge/gtkb-dispatcher-next-foundation-spike-001.md` through `-004.md`.

## Proposed Scope

1. Add `scripts/bridge_lifecycle_resolver.py` with immutable
   `BridgeVersion`, `LifecycleDiagnostic`, and `BridgeLifecycleResolution`
   records plus `BridgeLifecycleResolutionError`.
2. Enumerate only exact `<slug>-NNN.md` files, require contiguous unique numeric
   versions, and reject exact-prefix siblings and duplicate versions.
3. Read UTF-8-SIG strictly. A strict version requires an exact canonical first
   nonblank status line.
4. Parse exact `Document`, `Version`, `Responds to`, and `author_identity`
   metadata needed for correction validation. Never treat metadata from a
   malformed file as authority; its first token is observed only to classify a
   possible LO-verdict-shaped envelope.
5. Resolve ordinary strict proposal, revision, review, implementation-report,
   and verification chains without changing their established behavior.
6. Recognize at most one pending correction only when:
   - malformed vN+1 immediately follows strict Prime NEW/REVISED vN;
   - the malformed first token is GO, NO-GO, or VERIFIED, never a Prime token;
   - strict Prime NO-ACTION vN+2 has the same Document and responds exactly to
     vN+1;
   - there is no skipped, duplicate, intervening, additional malformed, or
     later version.
7. Return pending correction with vN+2 as `latest_strict_state` and
   `review_artifact`, null implementation fields, empty `quarantined_paths`,
   and diagnostic `PENDING_CORRECTION_NO_IMPLEMENTATION_AUTHORITY`.
8. Complete correction quarantine only when strict LO GO/NO-GO/VERIFIED vN+3
   has the same Document, role-correct author, exact version, and responds
   exactly to vN+2.
9. For complete corrected GO, return the underlying Prime proposal and vN+3 GO
   as the implementation pair and record only vN+1 in `quarantined_paths`.
10. Refactor
    `implementation_authorization.bridge_entry_from_versioned_files` to consume
    the shared result while retaining the existing `BridgeEntry` public API.
    Authorization must use only the resolver's implementation pair and
    continue to enforce post-GO report, terminal, claim, PAUTH, target, packet,
    and operation-time gates.
11. Add isolated resolver tests and public `main begin` plus finalized-packet
    integration tests for TEST-11674.
12. Preserve WI-5382's 53 foreign test lines byte-for-byte.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applies": true,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; PAUTH-DISPATCHER-NEXT-PROGRAM-20260719 v4; WI-5629; TEST-11674; WI-5626 v006",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, DCL-PROJECT-DEPENDENCY-ORDERING-001, DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
  "primary_route": "Exact numbered bridge files -> one operation-neutral lifecycle result -> review or implementation consumer -> claim/start packet -> report -> independent verification.",
  "before_behavior": "Readers disagree: some tolerate or skip malformed history while implementation authorization rejects all malformed history; pending NO-ACTION cannot be represented without either stale fallback or total failure.",
  "after_behavior": "One strict result distinguishes audit state, reviewable Prime state, and implementation authority. Pending correction is reviewable but never implementation-authorizing; complete linked correction can quarantine exactly one malformed LO envelope.",
  "self_descriptive_naming": "BridgeLifecycleResolution fields name audit, review, implementation, quarantine, and blocking semantics directly.",
  "obsolete_guidance_disposition": "No blanket malformed skip, decorated-token normalization, local consumer parser, or historical rewrite remains.",
  "history_preservation": "Malformed bytes, NO-ACTION, corrected verdict, PAUTH, claims, packets, reports, and verdicts remain append-only.",
  "baseline": {
    "foundation_chain": "NEW v001, decorated malformed GO v002, strict Prime NO-ACTION v003, strict corrected LO GO v004",
    "implementation_authorization": "begin currently rejects malformed v002",
    "test_target": "53 foreign WI-5382 lines preserved",
    "live_runtime": "no daemon or route mutation in this slice"
  },
  "expected_result": {
    "pending_chain": "review_artifact is NO-ACTION; implementation pair is null; no quarantine",
    "complete_chain": "review artifact and implementation proposal resolve correctly; malformed path is explicit quarantine evidence",
    "arbitrary_malformed": "stable structural error; no stale fallback and no packet",
    "foundation_begin": "normal schema-v3 packet mints and finalizes from corrected GO v004"
  },
  "rollback": {
    "instructions": "Before VERIFIED, reverse only the hash-pinned WI-5629 hunks and remove only its two new files under separate rollback authority. Preserve WI-5382 bytes and all append-only records. After VERIFIED, use a governed follow-on correction.",
    "verification": "Rerun resolver, authorization, packet, work-intent, lint, and live foundation begin checks."
  },
  "hard_invariants": [
    "Malformed content never becomes a valid lifecycle status.",
    "Pending NO-ACTION never authorizes implementation and does not quarantine its malformed predecessor.",
    "Malformed Prime NEW or REVISED can never reactivate older Prime content.",
    "Complete correction requires adjacency, both Responds-to edges, matching document/version metadata, and role-correct authors.",
    "Schema-v3 named/current packet order and claim/PAUTH checks remain unchanged.",
    "No source edit occurs without exact GO, claim, and finalized start packet."
  ],
  "fail_closed_conditions": [
    "Unreadable, duplicate, skipped, non-adjacent, cross-thread, wrong-role, wrong-document, wrong-link, Prime-shaped malformed, or multiply malformed state.",
    "Implementation consumer receives a null implementation pair or an implementation-blocking diagnostic.",
    "Operation-time project order, PAUTH, claim, target, or packet evidence disagrees.",
    "Either dirty target changes after baseline capture."
  ],
  "essential_context_preservation": "Preserve WI-5629, TEST-11674, WI-5626 and v006, WI-5617 versions 001-004, PAUTH v4, owner authorization, malformed-quarantine precedent, WI-5382 packet contract, and the exact dirty-target attribution."
}
```

## Specification-Derived Verification Plan

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Ordinary lifecycle | Resolver fixtures for proposal GO/NO-GO, revised GO, post-implementation report NO-GO/VERIFIED, pending NO-ACTION, and terminal states | Existing strict chain behavior and numeric order remain unchanged. |
| Pending correction | `NEW -> malformed LO verdict -> NO-ACTION` with exact role/document/link | Result exposes strict NO-ACTION as latest/review artifact, null implementation pair, empty quarantine, and stable implementation blocker. |
| Complete corrected GO | `NEW -> malformed GO -> NO-ACTION -> GO` with both links | Result exposes proposal plus corrected GO as implementation pair and only malformed GO as quarantine evidence. |
| Complete corrected NO-GO/VERIFIED | Equivalent role-correct fixtures | Review/audit state is deterministic; no unauthorized implementation pair is exposed. |
| No stale fallback | Malformed NEW/REVISED, wrong token, missing NO-ACTION, malformed NO-ACTION/replacement, wrong role/document/link, non-adjacency, duplicate, multiple malformed, and prefix sibling fixtures | Stable structural error; no review/implementation artifact and no packet state. |
| Consumer contract | Resolver result-field assertions plus import-boundary checks | Both consumers can use named public fields without numbered-file reparsing. |
| Public authorization | Isolated root with active PAUTH, exact claim, corrected GO; invoke public `main begin`, then finalize | Exit 0; schema-v3 named packet precedes current packet; final packet authorizes exact targets. |
| Pending authorization denial | Same isolated root with pending correction | Nonzero stable denial; no named/current packet write. |
| WI-5382 preservation | Existing named/current, denial-no-write, `--no-write`, activate, list, and packet-hash tests | All pass; the pre-existing 53 lines remain byte-identical. |
| Work-intent consistency | Focused malformed/quarantine work-intent tests | Dispatch quarantine remains typed and does not silently skip arbitrary state. |
| Focused regression | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short` | Exit 0. |
| Static quality | `python -m ruff check scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py` | Exit 0. |
| Formatting | `python -m ruff format --check scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py` | Exit 0. |
| Live foundation proof | Retain WI-5617 claim and invoke `implementation_authorization.py begin` | Valid finalized packet identifies proposal v001, corrected GO v004, and quarantined v002. |
| Nonimpairment | `gt bridge dispatch health --json` before/after | No daemon restart or live route/cap/state mutation. |

## Acceptance Criteria

- One shared resolver is the only new numbered lifecycle authority in this
  slice.
- Its public result separates audit, review, implementation, quarantine, and
  blocking semantics.
- Pending correction is reviewable and never implementation-authorizing.
- Complete corrected GO authorizes the original proposal only after every
  structural predicate passes.
- Arbitrary malformed history cannot reactivate stale Prime content.
- Foundation WI-5617 can mint and finalize its normal packet.
- Existing strict lifecycle, claim, PAUTH, target, packet, and denial semantics
  remain unchanged.
- WI-5382 foreign test bytes remain byte-identical.

## Cross-Harness Disposition

The resolver is harness-neutral and uses canonical status, document,
Responds-to, author-role, and version evidence for A, B, C, D, E, F, and H.
No vendor/model route, role assignment, capability, invocation, or parity
configuration changes.

## Pre-Filing Preflight Subsection

Before filing, the governed revision helper must pass candidate applicability
and mandatory clause preflights with no missing required/advisory
specifications or blocking gaps.

## Risks And Rollback

- Risk: operation-neutral state could be mistaken for implementation authority.
  Mitigation: null implementation pair plus typed blocker, and authorization
  tests proving no packet write.
- Risk: pending correction could prematurely quarantine malformed evidence.
  Mitigation: quarantine is empty until the second exact link exists.
- Risk: ordinary report chains could regress. Mitigation: full lifecycle matrix
  and existing authorization suite.
- Risk: dirty test target could absorb WI-5382. Mitigation: operation-time
  hash/diff capture and byte-preservation assertion.
- Rollback: reverse only hash-pinned WI-5629 hunks before VERIFIED; after
  VERIFIED use a governed follow-on correction.

## Recommended Commit Type

`fix`
