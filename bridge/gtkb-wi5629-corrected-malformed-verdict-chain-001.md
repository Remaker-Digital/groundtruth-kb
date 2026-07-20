NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Link-validated corrected malformed-verdict chains

bridge_kind: prime_proposal
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629

target_paths: ["scripts/bridge_lifecycle_resolver.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_lifecycle_resolver.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Create one strict, reusable lifecycle resolver for exact numbered bridge files
and use it in implementation authorization. The resolver continues to reject
malformed or unreadable numbered state except for one append-only correction
shape whose links and author roles prove that a malformed Loyal Opposition
verdict was explicitly rejected and replaced:

```text
strict Prime NEW/REVISED vN
-> malformed LO-verdict-shaped vN+1
-> strict Prime NO-ACTION vN+2 responding exactly to vN+1
-> strict corrected LO GO/NO-GO/VERIFIED vN+3 responding exactly to vN+2
```

Only the malformed vN+1 envelope is quarantined from lifecycle authority.
The correction and replacement remain in the returned audit chain. Any
non-adjacent, cross-thread, wrong-role, wrong-document, ambiguous, unreadable,
unlinked, pending, or Prime-shaped malformed file remains a blocking error.

This repair is required because WI-5617 has exact corrected `GO` at version
004, but `implementation_authorization.py begin` rejects its malformed
historical version 002 before it can recognize versions 003 and 004.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` requires
malformed numbered state to fail closed, while
`DCL-NO-ACTION-STATUS-SEMANTICS-001` defines the append-only correction route.
The proposal does not make malformed content valid; it requires a fully linked,
role-correct correction sequence and preserves the malformed file as
quarantined audit evidence.

## In-Root Placement Evidence

All four targets are inside `E:\GT-KB`:

- `scripts/bridge_lifecycle_resolver.py` (new)
- `scripts/implementation_authorization.py` (tracked and clean)
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py` (new)
- `platform_tests/scripts/test_implementation_authorization.py` (tracked with
  53 foreign lines from terminal VERIFIED WI-5382)

The WI-5382 test bytes are outside WI-5629 ownership and must be preserved.
Before mutation, Prime Builder must record operation-time hashes and diff
attribution for both tracked targets. If either changes after capture,
implementation stops and returns for revision.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - exact numbered files remain canonical;
  malformed state fails closed unless a complete append-only correction chain
  structurally supersedes one malformed LO verdict.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - Prime NO-ACTION is the explicit route
  for rejecting an invalid LO publication and requesting a corrected verdict.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - the corrected
  chain must mint and finalize the same implementation-start packet as an
  ordinary exact GO chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - resolution reads fresh exact numbered
  files for each decision.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

Direct implementation authorities:

- `bridge/gtkb-dispatch-malformed-status-token-quarantine-004.md` - terminal
  VERIFIED precedent that malformed statuses are typed quarantine evidence,
  not silently accepted state.
- `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md` - terminal
  VERIFIED schema-v3 named/current packet contract that this repair must
  preserve.

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` directs the Master
Prime Builder to preserve and complete derived or upstream-dependent work
needed to execute Dispatcher Next. PAUTH version 4 explicitly includes
WI-5629 while retaining independent GO, claim, and implementation-start gates.
No additional owner decision is required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-20265221` - owner priority behind the VERIFIED malformed-status
  quarantine precedent.
- `bridge/gtkb-dispatch-malformed-status-token-quarantine-004.md`
- `bridge/gtkb-wi5382-implementation-start-packet-contract-004.md`
- `bridge/gtkb-dispatcher-next-foundation-spike-001.md` through `-004.md`
- `bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-004.md`

## Proposed Scope

1. Add `scripts/bridge_lifecycle_resolver.py` with immutable version and
   resolution records.
2. Enumerate only exact `<slug>-NNN.md` files and reject duplicate versions.
3. Read UTF-8-SIG explicitly and require a strict canonical first-line status.
4. Capture, but do not trust, the first token of malformed content only to
   prove that the one quarantined envelope is LO-verdict-shaped
   (`GO`, `NO-GO`, or `VERIFIED`).
5. Parse exact `Document`, `Responds to`, `author_identity`, and version
   metadata from strict correction files.
6. Quarantine one malformed file only when all of these predicates hold:
   - its version is exactly one greater than a strict Prime `NEW`/`REVISED`;
   - its first token is an LO verdict token, never a Prime status;
   - the next exact version is strict `NO-ACTION`, has the same document,
     declares Prime author identity, and responds exactly to the malformed
     path;
   - the next exact version is strict corrected LO verdict, has the same
     document, declares Loyal Opposition author identity, and responds exactly
     to the NO-ACTION path;
   - no additional malformed, unreadable, duplicate, skipped, or intervening
     version exists in the four-version sequence.
7. Return strict versions plus explicit quarantined-path evidence; never
   rewrite or delete the malformed file.
8. Refactor `implementation_authorization.bridge_entry_from_versioned_files`
   to consume the shared resolver and retain the existing `BridgeEntry` API.
9. Add isolated resolver tests plus a public `begin` and finalized-packet
   integration test for TEST-11674.
10. Preserve WI-5382's existing foreign test hunk byte-for-byte.

The new resolver is intentionally reusable by the dependent WI-5626 clause
preflight repair. WI-5626 must receive its own revised GO before importing it.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; PAUTH-DISPATCHER-NEXT-PROGRAM-20260719 v4; WI-5629; TEST-11674; bridge/gtkb-wi5626-lifecycle-aware-clause-preflight-004.md",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001, DCL-NO-ACTION-STATUS-SEMANTICS-001, DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Exact numbered bridge files, shared strict lifecycle resolver, link-validated correction quarantine, implementation authorization, claim, finalized start packet, implementation report, independent verification.",
  "before_behavior": "Implementation authorization rejects every malformed historical file, including an explicitly rejected and corrected LO verdict, so WI-5617 cannot mint its required start packet.",
  "after_behavior": "Only one adjacent, link-complete, role-correct malformed LO verdict correction sequence is traversable; every other malformed state remains a blocking error.",
  "self_descriptive_naming": "bridge_lifecycle_resolver and corrected-malformed-verdict tests name the exact authority and exception.",
  "obsolete_guidance_disposition": "No reader becomes tolerant of decorated status lines and no historical artifact is rewritten. Blanket malformed-file skipping is explicitly rejected.",
  "history_preservation": "The malformed file, NO-ACTION, corrected verdict, work item, test, PAUTH, packets, and verification evidence remain append-only.",
  "baseline": {
    "foundation_chain": "NEW v001, malformed decorated LO GO v002, strict Prime NO-ACTION v003 responding to v002, strict corrected LO GO v004 responding to v003",
    "implementation_authorization": "source target clean; begin rejects v002 before resolving corrected state",
    "test_target": "contains 53 foreign lines from terminal VERIFIED WI-5382 that must be preserved",
    "new_targets": 2
  },
  "expected_result": {
    "corrected_foundation_chain": "resolves strict v001, v003, and v004 with v002 recorded as quarantined correction evidence",
    "implementation_start": "public begin plus packet finalization succeeds with ordinary claim and PAUTH checks intact",
    "invalid_chains": "all fail before packet state is written",
    "runtime_effect": "no dispatcher restart, routing, cap, registry, TAFE, lease, credential, deployment, release, push, or history mutation"
  },
  "rollback": {
    "instructions": "Before VERIFIED, restore only the WI-5629 hash-pinned hunks and remove only its two new targets under separate rollback authority. Preserve WI-5382 bytes and all bridge history. After VERIFIED, use a governed follow-on correction.",
    "verification": "Run resolver, implementation-authorization, packet-contract, work-intent, lint, and live foundation begin checks."
  },
  "hard_invariants": [
    "Malformed status content never becomes a valid lifecycle status.",
    "Malformed Prime NEW or REVISED can never fall back to older Prime content.",
    "Both Responds-to edges, document names, author roles, adjacency, and exact versions must agree.",
    "Pending NO-ACTION never authorizes implementation.",
    "Schema-v3 named/current packet ordering and claim checks remain unchanged.",
    "No implementation occurs without independent GO, exact claim, and implementation-start authorization."
  ],
  "fail_closed_conditions": [
    "Malformed first token is not an LO verdict token.",
    "Correction or replacement version is missing, non-adjacent, unreadable, or malformed.",
    "Document, Responds-to path, author role, or version metadata disagrees.",
    "Any duplicate, additional malformed, skipped, or intervening version exists.",
    "Latest strict lifecycle state does not independently authorize the requested operation.",
    "Either tracked target changes after operation-time baseline capture."
  ],
  "essential_context_preservation": "Preserve WI-5629, TEST-11674, PAUTH v4, the owner program decision, WI-4658 quarantine precedent, WI-5382 packet contract and foreign hunk, WI-5626 consumer dependency, foundation versions 001 through 004, and exact failure diagnostics."
}
```

## Specification-Derived Verification

| Requirement | Test or command | Acceptance predicate |
| --- | --- | --- |
| Strict ordinary chain | Shared-resolver fixtures for exact NEW/REVISED/GO/NO-GO/NO-ACTION/VERIFIED | Existing strict chains preserve numeric order and statuses byte-for-byte. |
| Corrected malformed LO verdict | Fixture `NEW -> decorated GO -> NO-ACTION -> GO` with exact document, roles, versions, and Responds-to links | Resolver returns strict v001/v003/v004, records only v002 as quarantined, and implementation authorization selects v001 under v004. |
| No stale fallback | Fixtures with malformed NEW, malformed REVISED, wrong first token, missing correction, pending NO-ACTION, non-adjacent versions, cross-thread link, wrong document, wrong author role, wrong Responds-to path, malformed replacement, and multiple malformed files | Resolver raises a stable fail-closed error and writes no packet state. |
| Public authorization path | Isolated-root test seeds active PAUTH, exact GO implementation claim, and corrected chain; invokes public `main begin`, then finalizes the packet | Exit 0; schema-v3 named packet is written before current packet; finalized implementation-start evidence authorizes the declared target. |
| WI-5382 preservation | Existing named/current packet order, denial-no-write, `--no-write`, activate, list, and packet-hash tests | All pass unchanged; the 53 foreign test lines remain byte-identical. |
| Work-intent consistency | Focused work-intent malformed/quarantine tests | Typed malformed diagnostics and dispatch quarantine behavior remain green. |
| Focused regression | `python -m pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short` | Exit 0. |
| Static quality | `python -m ruff check scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py` | Exit 0. |
| Formatting | `python -m ruff format --check scripts/bridge_lifecycle_resolver.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py` | Exit 0. |
| Live foundation proof | Acquire/retain the exact WI-5617 claim and run `implementation_authorization.py begin` for the foundation thread | A valid packet is produced from corrected GO v004; output explicitly identifies quarantined v002 and approved proposal v001. |
| Live nonimpairment | `gt bridge dispatch health --json` before and after | No daemon restart or live configuration/state mutation occurs. |

## Acceptance Criteria

- One shared resolver is the only new status-chain authority in this slice.
- The foundation's exact four-version correction chain can mint and finalize a
  normal implementation-start packet.
- Arbitrary malformed state cannot reactivate stale Prime content.
- Correction traversal requires exact adjacency, two Responds-to edges,
  matching document/version metadata, and role-correct authorship.
- Malformed bytes remain preserved and explicitly reported as quarantine
  evidence.
- Existing strict lifecycle, claim, PAUTH, packet, and denial semantics remain
  unchanged.
- WI-5382's foreign test hunk is preserved exactly.
- Only the four declared targets change.
- The live dispatcher is neither restarted nor reconfigured.

## Cross-Harness Disposition

The resolver is harness-neutral and applies identically to bridge artifacts
authored by A, B, C, D, E, F, or H. It uses canonical status, document,
Responds-to, and role provenance rather than vendor/model names. No harness
invocation, role assignment, route, capability, or parity configuration changes
in this slice.

## Risks and Rollback

- Risk: a broad exception could authorize stale content. Mitigation: exact
  four-version adjacency, two directed links, role/document/version checks,
  one quarantined LO-shaped file maximum, and negative fixtures for every
  omitted predicate.
- Risk: shared resolver adoption could alter ordinary chains. Mitigation:
  retain the existing `BridgeEntry` API and run the full implementation
  authorization suite.
- Risk: the dirty test target could absorb WI-5382 work. Mitigation:
  operation-time hash/diff attribution and append-only disjoint tests.
- Rollback: before VERIFIED, restore only the hash-pinned WI-5629 hunks and
  remove its two new files under separate rollback authority. Do not revert
  WI-5382 or any unrelated bytes. After VERIFIED, use a governed follow-on
  proposal.

## Recommended Commit Type

`fix`
