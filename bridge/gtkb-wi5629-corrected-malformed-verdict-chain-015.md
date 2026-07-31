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

# Revised Implementation Proposal - Complete WI-5629 through bounded PAUTH packet integration

bridge_kind: prime_proposal
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 015
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-014.md
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

Preserve the already-implemented exact-thread malformed-verdict resolver and
complete the operation-time project-authorization integration that blocks its
terminal verification.

The correction remains confined to WI-5629's existing four target paths.
`scripts/implementation_authorization.py` will consume the canonical,
already-present WI-5178 evaluator at
`groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
without modifying that module, its taxonomy, or its standalone tests. The
packet adapter will:

1. convert the current PAUTH row into the evaluator's structured envelope;
2. evaluate every exact target and requested operation before packet creation;
3. bind the normalized envelope, target classifications, evaluator identity,
   evaluator bytes, taxonomy identity, taxonomy bytes, and decision evidence
   into the packet;
4. re-evaluate current PAUTH state at implementation start and packet load;
5. reject envelope, target, operation, evaluator, or taxonomy drift before any
   protected effect.

This is a cycle-breaking integration step, not a substitute for the broader
WI-5178 governed-predecessor-closure program. WI-5178 retains ownership of its
taxonomy, evaluator, envelope carrier, outer gates, work-intent consumers, and
full 24-path verification. WI-5629 remains non-terminal until the fresh
verification matrix passes and an independent Loyal Opposition issues
VERIFIED.

## Finding Addressed

### F1 - P0 - Terminal VERIFIED is blocked by operation-time authorization failures

Accepted. Version 014 correctly withheld VERIFIED. A fresh authoritative run
on the current tree produced five failures in 77.94 seconds:

- the positive packet omitted `allowed_mutation_classes`;
- bridge/metadata-only authority accepted a source target;
- an explicitly forbidden operation was accepted;
- packet load accepted a changed PAUTH envelope;
- packet load accepted changed taxonomy bytes.

The failure cluster is concentrated in the adapter and packet-revalidation
logic already owned by `scripts/implementation_authorization.py`, plus its
existing WI-5629 test target. The canonical evaluator itself passes its
standalone tests and is not changed by this proposal.

The corrected sequence is:

1. integrate and prove the canonical evaluator through this fresh WI-5629
   proposal and GO;
2. use the now-working implementation-start path to complete the currently
   blocked WI-5554, WI-5425, and WI-5166 frontier;
3. complete the sole broad WI-5178 24-path carrier and stand down the narrower
   sibling carrier;
4. rerun the full WI-5629 matrix and submit one unambiguous implementation
   report for independent terminal verification;
5. only then allow WI-5633 and dependent protected-finalization work to start.

No owner waiver is requested or inferred.

## Scope Changes

The target-path set is unchanged from the independently approved version 011:

- `scripts/bridge_lifecycle_resolver.py`;
- `scripts/implementation_authorization.py`;
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`;
- `platform_tests/scripts/test_implementation_authorization.py`.

The behavioral scope expands only inside the existing implementation-
authorization target: version 011 required operation-time PAUTH gates to remain
enforced, while version 014 proved the current adapter did not satisfy that
requirement. This revision makes the missing integration explicit and
testable.

Read-only dependencies, excluded from mutation:

- `config/governance/project-authorization-operation-taxonomy.toml`;
- `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`;
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`.

The following remain out of scope: dispatcher configuration or restart,
provider routing, harness caps, Git/index/ref/finalization, bridge writer and
protected-commit surfaces, work-intent or start-gate consumers, MemBase
mutation, credentials, deployment, release, and external systems.

## Requirement Sufficiency

Existing requirements are sufficient. The defect is failure to connect an
already-specified and already-present canonical evaluator to the existing
packet authority path.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` directs the Master
Prime Builder to complete Dispatcher Next and every derived or upstream
prerequisite without bypassing independent review. Active
`PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` version 4 includes WI-5629 and all four
declared source/test targets. No additional owner decision is required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-011.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-012.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-013.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-014.md`
- `bridge/gtkb-wi5178-operation-time-authority-enforcement-012.md`
- `bridge/gtkb-wi5178-governed-predecessor-closure-008.md`
- `bridge/gtkb-wi5633-protected-commit-corrected-chain-evidence-002.md`

## Baseline And Ownership Evidence

- WI-5629, the narrow WI-5178 thread, and the broad WI-5178 thread have no
  live claim. The broad thread has only an expired draft claim.
- Current hashes:
  - `scripts/implementation_authorization.py`:
    `8B9BF2A27A5A4A07CCEA3C2821EA78078386652D6B6C6F112E4758E6694AEEB8`;
  - `platform_tests/scripts/test_implementation_authorization.py`:
    `EC569799585EEFC63DB7D4D7A0DD84BD57CE548771C8466E45EE1463EC17486C`;
  - read-only evaluator:
    `5EAB50B26F0EAC3E99C1670007983D7DFFF071B758D062B215FBDDBF3379A9CA`;
  - read-only taxonomy:
    `E726688AC19484CB1105EC4965C53F3F1CC4E6198E28F71D66D79838878387D8`.
- `scripts/bridge_lifecycle_resolver.py` and its test remain the untracked
  WI-5629 implementation from version 013.
- The tracked source/test diffs remain the WI-5629 resolver integration and
  fixture updates. Any byte drift after GO requires a fresh attribution check.
- The WI-5178 evaluator is an untracked predecessor artifact. This proposal
  may import and test it but must not edit, stage, finalize, or claim it.

## Proposed Implementation

1. Add one private row-to-envelope adapter in
   `scripts/implementation_authorization.py`. Decode every list-valued PAUTH
   column with the existing strict JSON-list helper and preserve ID, version,
   project, status, owner decision, expiry, supersession, included/excluded WI
   IDs, and included/excluded spec IDs.
2. Import the canonical evaluator through the project-root-bound
   `groundtruth_kb` package. Import or taxonomy failure is a stable
   `AuthorizationError`; no local fallback taxonomy is allowed.
3. After current lifecycle, project, membership, and excluded-spec checks,
   evaluate each requested operation against the exact target path set.
   Empty targets or operations retain existing behavior only where the caller
   is explicitly performing a metadata-only validation. Every supplied
   operation must receive an allow decision; the first denial raises with its
   stable reason code and detail.
4. Return a complete packet envelope containing the decoded authorization
   bounds, authorization version, normalized envelope hash, classified
   targets, normalized operations, operation-time decisions, evaluator
   ID/version/hash, and taxonomy version/hash.
5. Pass proposal `target_paths` and
   `implementation_packet_create` into project-authorization extraction during
   packet creation.
6. At packet start/load, reevaluate the current row with the exact requested
   operation and packet targets. Reject a changed project, normalized envelope
   hash, evaluator identity/hash, taxonomy identity/hash, or target
   classification before returning the current decision.
7. Preserve schema-v3 named-before-current packet ordering, claim authority,
   corrected-chain resolution, terminal behavior, and every existing
   no-write denial.
8. Extend only `platform_tests/scripts/test_implementation_authorization.py`
   as needed for the five reproduced assertions and focused negative drift
   coverage. Do not change the read-only evaluator or its tests.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; PAUTH-DISPATCHER-NEXT-PROGRAM-20260719 v4; WI-5629 v014 NO-GO; authoritative five-failure operation-time cluster",
  "canonical_authority": "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
  "primary_route": "Exact bridge chain -> current PAUTH row -> canonical operation-time evaluator and taxonomy -> packet-bound evidence -> claim/start/load revalidation -> protected effect",
  "before_behavior": "The corrected bridge chain resolves, but implementation authorization copies only basic PAUTH metadata and ignores supplied targets and operations, so disallowed targets, forbidden operations, envelope drift, and taxonomy drift can pass.",
  "after_behavior": "One canonical evaluator classifies exact targets and operations at packet creation, start, and load; the packet binds stable PAUTH, evaluator, taxonomy, and classification evidence; any denial or drift fails before a protected effect.",
  "self_descriptive_naming": "The existing validate_project_authorization_row and validate_packet_project_authorization_operation surfaces remain the public gates; private adapter names identify row conversion and bound-evidence comparison.",
  "obsolete_guidance_disposition": "No parallel taxonomy, local path classifier, string-prefix permission rule, legacy packet broadening, or second authorization carrier is introduced.",
  "history_preservation": "All numbered WI-5629 and WI-5178 bridge files, current source diffs, claims, packets, and test evidence remain append-only or preserved; no prior artifact is rewritten.",
  "baseline": {
    "resolver_tests": "36 passed",
    "operation_time_cluster": "5 failed in 77.94 seconds",
    "target_scope": "the same four WI-5629 paths approved at v011",
    "read_only_dependencies": "canonical WI-5178 evaluator, taxonomy, and standalone tests"
  },
  "expected_result": {
    "operation_time_cluster": "5 passed in one run",
    "resolver_behavior": "unchanged",
    "packet_contract": "normalized envelope plus evaluator/taxonomy hashes and classifications are bound and rechecked",
    "runtime_effect": "no dispatcher, route, provider, harness, Git, credential, deployment, release, or external-system mutation"
  },
  "rollback": {
    "instructions": "Under a fresh authorized packet, restore only hash-pinned WI-5629 hunks in its four target paths. Preserve the canonical evaluator, taxonomy, WI-5178 artifacts, and all bridge history.",
    "verification": "Rerun the resolver, focused five-test cluster, full implementation-authorization/work-intent matrix, standalone evaluator tests, Ruff, format, compile, and live no-write foundation proof."
  },
  "hard_invariants": [
    "A PAUTH may never authorize a target class outside its allowed mutation classes.",
    "An exact forbidden operation always wins over an otherwise allowed target class.",
    "Packet reuse may not outlive current PAUTH, evaluator, or taxonomy bytes.",
    "Corrected malformed-verdict resolution remains fail closed and operation neutral.",
    "No protected mutation occurs without independent GO, exact claim, and implementation-start authorization."
  ],
  "fail_closed_conditions": [
    "PAUTH row, target, requested operation, evaluator, or taxonomy is absent, malformed, unknown, denied, or drifted.",
    "Any declared WI-5629 target changes after the GO baseline without attribution.",
    "Any read-only WI-5178 dependency would need mutation.",
    "Any preflight, focused test, full regression, or independent verification gate fails."
  ],
  "essential_context_preservation": "Preserve WI-5629 versions 001 through 015, WI-5178's two current NO-GOs, PAUTH v4, TEST-11674, the five authoritative failures, the 36 passing resolver tests, the read-only canonical evaluator and taxonomy, WI-5633 dependency, and the live foundation corrected-GO proof."
}
```

## Specification-Derived Verification Plan

| Requirement | Command or test | Acceptance predicate |
| --- | --- | --- |
| Exact malformed-chain resolution | `pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py` | All 36 resolver tests pass unchanged. |
| Allowed packet envelope | `test_project_authorization_accepts_active_project_without_retirement_class` and retired-reconciliation positive test | Packet carries bounds, classifications, and 64-character evaluator/taxonomy hashes. |
| Target-class denial | `test_project_authorization_rejects_source_target_for_bridge_metadata_only` | Source target is denied with path and `source` class in the error. |
| Forbidden-operation precedence | `test_project_authorization_rejects_explicit_forbidden_operation` | Exact forbidden operation fails with `forbidden_operation`. |
| Live envelope freshness | `test_packet_load_rejects_project_authorization_envelope_drift` | Changed current PAUTH cannot reuse the cached packet. |
| Evaluator/taxonomy freshness | taxonomy drift test plus one evaluator-hash comparison | Byte drift fails before protected effect. |
| Full WI-5629 regression | `pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_bridge_work_intent_registry.py` | Full command passes with no deselected WI-5629 assertions. |
| Canonical evaluator nonimpairment | `pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py` | Standalone evaluator suite passes without modifying its files. |
| Static quality | Ruff check, Ruff format check, and `py_compile` on the four WI-5629 targets | All pass. |
| Live corrected-chain proof | public foundation `begin --no-write` after the correction | Corrected v004 GO resolves; no packet or runtime mutation occurs. |
| Dependency closure | CLI checks for WI-5178, WI-5629, WI-5633, and WI-5474 | WI-5629 is not declared terminal until WI-5178 completes and the full matrix is green. |

The five-test blocker cluster must pass 5/5 in one run. The full matrix must
then run without a short global timeout; per-test timeouts may remain fail
closed.

## Acceptance Criteria

- The five independently reproduced failures pass.
- No mutation occurs outside the four declared WI-5629 paths.
- Packet creation, implementation start, and packet load all evaluate the
  exact current PAUTH envelope against exact operations and targets.
- Cached packets bind and recheck envelope, evaluator, and taxonomy bytes.
- The existing resolver's 36 tests and live corrected-chain proof remain
  green.
- No dispatcher, provider, harness, Git, credential, deployment, or release
  state changes.
- WI-5178 remains the sole owner of its broader evaluator/taxonomy/gate
  program and must still complete independently before WI-5629 VERIFIED.

## Pre-Filing Preflight Subsection

Before filing the live version:

1. run `bridge_applicability_preflight.py` against this completed draft;
2. run `adr_dcl_clause_preflight.py` against this completed draft;
3. require no blocking errors, no missing required specs, and no blocking
   clause gaps;
4. recheck latest thread status is version 014 NO-GO and all three relevant
   claims are absent or expired.

## Risks And Rollback

- Risk: operation-time evaluation could reject legacy PAUTH rows that relied
  on free-form mutation classes. Mitigation: the permanent taxonomy already
  defines canonical aliases; unknown values fail closed with a recovery code,
  and focused legacy tests remain in the full matrix.
- Risk: comparing operation-specific decisions could falsely treat a packet
  load as drift from packet creation. Mitigation: bind and compare stable
  envelope/evaluator/taxonomy evidence, then evaluate the current requested
  operation separately.
- Risk: the cycle breaker could accidentally absorb WI-5178. Mitigation: exact
  unchanged four-path scope and an explicit prohibition on modifying its
  evaluator, taxonomy, standalone tests, envelope carrier, or outer consumers.
- Rollback before VERIFIED restores only hash-pinned WI-5629 hunks in its four
  target paths under a fresh authorized packet. Preserve all foreign and
  predecessor bytes. After VERIFIED, use a governed follow-on correction.

## Recommended Commit Type

`fix`
