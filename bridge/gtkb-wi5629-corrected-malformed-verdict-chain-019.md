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

# Revised Implementation Proposal - Continue corrected chains through the strict lifecycle

bridge_kind: prime_proposal
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 019
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-018.md
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

Preserve the complete PAUTH packet integration reported in version 017 and
extend only the corrected-chain lifecycle adapter so that a single strictly
quarantined malformed Loyal Opposition verdict can continue through the same
post-verdict lifecycle as an ordinary strict chain.

The implementation will change only:

- `scripts/bridge_lifecycle_resolver.py`; and
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`.

The existing four-target WI-5629 authority boundary is retained because the
complete authorization and resolver matrices remain acceptance gates.
`scripts/implementation_authorization.py` and
`platform_tests/scripts/test_implementation_authorization.py` are verification
targets only in this revision; their bytes must remain unchanged.

The correction handshake remains narrow:

1. exactly one malformed, Loyal-Opposition-verdict-shaped version;
2. immediately preceded by a strict Prime `NEW` or `REVISED`;
3. immediately followed by a strict, role-correct Prime `NO-ACTION`;
4. followed by a strict, role-correct corrected `GO`, `NO-GO`, or `VERIFIED`;
5. all later versions parsed and linked under the ordinary strict rules.

The malformed file remains the only quarantined path. The physical numbered
chain remains complete in audit evidence. Only the malformed verdict and the
administrative `NO-ACTION` are omitted from logical transition evaluation.

## Finding Addressed

### F1 - P0 - A corrected GO becomes unreadable when normal implementation and verification continue

Version 017 proved the PAUTH packet integration with a green full matrix, then
withheld terminality because the public foundation chain still fails:

```text
NEW v001
-> malformed decorated GO v002
-> strict NO-ACTION v003
-> strict corrected GO v004
-> implementation report NEW v005
-> verification NO-GO v006
```

Current `_correction_resolution()` accepts only the `NO-ACTION` and at most
one corrected verdict. Version 005 therefore triggers
`MALFORMED_CORRECTION_INVALID_TAIL` even though versions 004 through 006 form
an ordinary strict post-GO lifecycle.

The defect is in lifecycle composition, not in parsing, metadata
compatibility, PAUTH evaluation, or the ordinary transition state machine.
The correction adapter must hand the strict logical sequence back to the
ordinary resolver after completing the correction handshake.

Version 018 independently reproduced this exact
`MALFORMED_CORRECTION_INVALID_TAIL` failure. Its narrow `NO-GO` accepts the
reported PAUTH progress and requires:

- strict post-corrected-GO continuation in the public resolver;
- preservation of the complete malformed-chain denial matrix;
- a fresh live foundation proof through report/verdict state; and
- a new implementation report that explicitly claims terminal readiness.

This revision accepts all four requirements without broadening into separate
historical metadata compatibility.

## Scope And Boundaries

In scope:

- corrected-chain composition inside `_correction_resolution()`;
- reuse of `_ordinary_resolution()` and
  `_validate_ordinary_transitions()` without weakening either;
- physical audit-version preservation;
- single malformed-path quarantine preservation;
- implementation-pair and review-artifact projections identical to ordinary
  lifecycle semantics;
- focused positive and negative resolver regressions;
- a live, read-only public foundation proof.

Out of scope:

- `Responds to GO:` compatibility, owned by WI-5636;
- decorated `Version:` compatibility, owned by WI-5637;
- changes to strict parsing, metadata names, response-link adjacency, version
  contiguity, role checks, status spelling, or terminality;
- PAUTH evaluator or taxonomy changes;
- bridge writer, provider, dispatcher configuration/runtime, harness caps,
  ranking, routing, claims, Git/index/ref/finalization, MemBase, credentials,
  deployment, release, and external systems;
- rewriting, renumbering, deleting, or normalizing any historical bridge file.

Read-only dependencies:

- `config/governance/project-authorization-operation-taxonomy.toml`;
- `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`;
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`;
- the public `gtkb-dispatcher-next-foundation-spike` bridge chain.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-NO-ACTION-STATUS-SEMANTICS-001`
already requires correction to be operation-neutral, while
`GOV-FILE-BRIDGE-AUTHORITY-001` and
`GOV-SOURCE-OF-TRUTH-FRESHNESS-001` require current strict lifecycle evidence.
The defect is an implementation gap in composing those existing rules.

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

`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` directs completion
of Dispatcher Next and all derived prerequisites under independent review.
Active `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` version 4 covers WI-5629 and
the preserved four-target boundary. No waiver or additional owner decision is
required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-011.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-014.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-015.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-016.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-017.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-018.md`
- `bridge/gtkb-wi5636-exact-responds-to-go-history-compatibility-002.md`

## Baseline And Ownership Evidence

Version 017 reported:

- resolver: 36 passed;
- implementation authorization: 161 passed;
- work intent: 34 passed;
- standalone evaluator: 13 passed;
- expanded operation-time cluster: 10 passed;
- Ruff check, Ruff format check, and compile: PASS;
- current PAUTH packet creation and start: PASS;
- live foundation progression: FAIL with
  `MALFORMED_CORRECTION_INVALID_TAIL`.

Version 017 final hashes:

- `scripts/bridge_lifecycle_resolver.py`:
  `0AEE86CFA377CAEDEDA7D57914891C63A2415F766FD4D93003EC8FBFC95C6854`;
- `scripts/implementation_authorization.py`:
  `A13B6CDE9DEA029996E8E8B724C20BB71168C074078835894733BA55DDF07371`;
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`:
  `539894A7B406C3D9E76A43B7252F593BA93A75CAAC5C38E40A04D8F786E504A4`;
- `platform_tests/scripts/test_implementation_authorization.py`:
  `D7C3597096175694F2DD442894954E6C5BF301F95A805E07E6EC152D3A4F18CB`.

Before filing, recheck those hashes, latest v018 disposition, null WI-5629
claim, PAUTH v4, and target ownership. Any unexplained drift requires
attribution or a new revision.

## Proposed Implementation

1. In `_correction_resolution()`, replace the two-version tail ceiling with a
   lower bound requiring at least the strict Prime `NO-ACTION`.
2. Preserve the existing exact predecessor, malformed shape, `NO-ACTION`,
   corrected-verdict status, and author-role checks.
3. Preserve the existing pending-correction result when the tail contains only
   `NO-ACTION`; implementation authority remains unavailable.
4. Preserve the existing completed-correction projection when no version
   follows the corrected verdict.
5. When versions follow a corrected verdict:
   - reject any version after corrected `VERIFIED` with
     `VERSION_AFTER_TERMINAL_STATUS`;
   - construct the logical strict sequence from the original strict prefix,
     corrected verdict, and every later strict version;
   - omit only the malformed verdict and corrective `NO-ACTION` from logical
     transition evaluation;
   - pass that logical sequence to `_ordinary_resolution()`;
   - copy its latest-state, review-artifact, implementation-artifact,
     implementation-verdict, and blocking-diagnostic projections;
   - restore the complete physical tuple as `audit_versions`;
   - retain exactly the malformed path in `quarantined_paths`.
6. Do not add a second transition table, fallback resolver, metadata alias, or
   compatibility parser.
7. Add focused tests for:
   - the exact public v001-v006 foundation chain;
   - corrected `GO` followed by pending report `NEW`;
   - report `NO-GO` followed by `REVISED` and a fresh `GO`;
   - a second report followed by terminal `VERIFIED`;
   - invalid direct `GO -> VERIFIED`;
   - versions after corrected `VERIFIED`;
   - strict rejection of `Responds to GO:`;
   - strict rejection of decorated `Version:`.
8. Keep both implementation-authorization targets byte-identical and rerun
   their full reported matrix as nonimpairment evidence.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5629 v017 report and live foundation MALFORMED_CORRECTION_INVALID_TAIL evidence",
  "canonical_authority": "DCL-NO-ACTION-STATUS-SEMANTICS-001, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
  "primary_route": "Physical exact chain -> strict parse/link/role validation -> bounded malformed-correction handshake -> logical ordinary lifecycle -> public resolution",
  "before_behavior": "A corrected GO authorizes implementation but any later report makes the entire thread unreadable.",
  "after_behavior": "The correction handshake removes only its malformed verdict and administrative NO-ACTION from logical transition evaluation; all later versions use the ordinary strict lifecycle while full physical audit history and single-path quarantine remain visible.",
  "self_descriptive_naming": "Existing correction and ordinary resolver names remain; no parallel compatibility abstraction is introduced.",
  "obsolete_guidance_disposition": "No historical file is rewritten and no stale fallback, aggregate projection, metadata alias, or second state machine is added.",
  "history_preservation": "Every numbered version remains parsed, linked, audited, and append-only; only the malformed file is quarantined.",
  "baseline": {
    "resolver": "36 passed",
    "authorization": "161 passed",
    "work_intent": "34 passed",
    "evaluator": "13 passed",
    "live_foundation": "MALFORMED_CORRECTION_INVALID_TAIL at v005"
  },
  "expected_result": {
    "live_foundation": "latest v006 NO-GO, implementation pair v001/v004, audit versions v001-v006, only v002 quarantined",
    "ordinary_lifecycle": "all existing strict transition and terminal rules reused unchanged",
    "separate_compatibility": "WI-5636 and WI-5637 remain failing and separately owned until their own governed implementations"
  },
  "rollback": {
    "instructions": "Under fresh GO, exact claim, and start authority, reverse only the WI-5629 resolver/test hunks and rerun the complete matrix.",
    "verification": "Restore the v017 hashes for the two changed files and preserve both authorization target hashes."
  },
  "hard_invariants": [
    "Only one exact malformed LO-verdict-shaped version may enter correction handling.",
    "The strict Prime NO-ACTION is mandatory, adjacent, and operation-neutral.",
    "Every later version is still parsed against physical version, document, response-link, status, and role metadata.",
    "Ordinary transition and terminal rules are reused, not duplicated.",
    "Only the malformed path is quarantined after correction completes.",
    "WI-5636 and WI-5637 compatibility behavior is unchanged."
  ],
  "fail_closed_conditions": [
    "The malformed version is missing, duplicated, wrong-shaped, or has the wrong predecessor.",
    "NO-ACTION or the corrected verdict is missing, non-adjacent, wrong-status, or wrong-role.",
    "Any later strict metadata or ordinary transition is invalid.",
    "A version follows terminal VERIFIED.",
    "Any change requires a target outside the four-file WI-5629 boundary."
  ],
  "essential_context_preservation": "Preserve WI-5629 v001-v019, PAUTH v4 packet evidence, the exact public foundation v001-v006 chain, all existing strict negative tests, and the separate WI-5636/WI-5637 sequencing."
}
```

## Specification-Derived Verification Plan

| Requirement | Command or test | Acceptance predicate |
| --- | --- | --- |
| Existing correction behavior | `pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py` | Existing 36 tests remain green. |
| Exact public continuation | New exact v001-v006 fixture plus live public read | Latest state is v006 `NO-GO`; implementation pair is v001/v004; all six versions are audited; only v002 is quarantined. |
| Pending report projection | Corrected `GO` plus report `NEW` test | Report is the review artifact and no stale implementation pair is exposed. |
| Resumable NO-GO | Corrected `GO`, report `NEW`, `NO-GO` test | Original proposal/corrected GO pair is exposed for revision. |
| Revised implementation pair | Add `REVISED` and fresh `GO` | Pair switches to revised proposal and fresh GO. |
| Terminal continuation | Add second report `NEW` and `VERIFIED` | Latest is terminal VERIFIED; no review or implementation pair remains. |
| Invalid transition denial | Corrected `GO -> VERIFIED` direct test | Fails `INVALID_BRIDGE_TRANSITION`. |
| Terminal denial | Corrected `VERIFIED` plus later version | Fails `VERSION_AFTER_TERMINAL_STATUS`. |
| WI-5636 boundary | `Responds to GO:` negative fixture | Remains `WRONG_RESPONDS_TO_LINK`. |
| WI-5637 boundary | Decorated `Version:` negative fixture | Remains `WRONG_BRIDGE_VERSION_METADATA`. |
| Authorization nonimpairment | `pytest platform_tests/scripts/test_implementation_authorization.py` | All 161 tests pass and both authorization targets retain v017 hashes. |
| Work-intent nonimpairment | `pytest platform_tests/scripts/test_bridge_work_intent_registry.py` | All 34 tests pass. |
| Evaluator nonimpairment | `pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py` | All 13 tests pass. |
| Static quality | Ruff check/format and `py_compile` on four targets | PASS. |

The complete resolver, authorization, work-intent, and evaluator suites must
pass in fresh runs without global short timeouts. The live public proof is
read-only and must not issue a packet, claim, or protected effect.

## Acceptance Criteria

- The exact public foundation chain resolves through v006.
- Every physical numbered version remains in audit order.
- Only the malformed v002 path is quarantined.
- The ordinary strict resolver remains the sole post-correction transition
  authority.
- Review and implementation projections match ordinary lifecycle semantics.
- Existing missing, wrong-link, cross-thread, wrong-role, wrong-document,
  duplicate, gap, non-adjacent, terminal, and multiple-malformed denials pass.
- `Responds to GO:` and decorated `Version:` remain rejected for WI-5636 and
  WI-5637.
- Both authorization targets remain byte-identical to v017.
- Full reported test and static-quality matrices pass.
- No dispatcher, provider, harness, Git, credential, deployment, release,
  MemBase, or external-system state changes.

## Pre-Filing Preflight

Before filing the canonical revision:

1. confirm v018 is the latest `NO-GO`;
2. confirm WI-5629 has no live claim;
3. recheck exact target hashes and ownership;
4. run candidate applicability preflight against the completed draft;
5. run mandatory ADR/DCL clause preflight against the completed draft;
6. require zero blocking errors, zero missing required specs, and zero blocking
   clause gaps.

## Risks And Rollback

- Risk: removing administrative correction versions from logical transition
  evaluation could hide them from audit consumers. Mitigation: return the
  complete original physical tuple in `audit_versions` and retain the malformed
  path in `quarantined_paths`.
- Risk: a bespoke corrected-tail transition table could drift from ordinary
  semantics. Mitigation: compose a logical strict sequence and call the
  existing `_ordinary_resolution()` unchanged.
- Risk: the revision could accidentally absorb historical metadata aliases.
  Mitigation: parsing remains unchanged and explicit WI-5636/WI-5637 negative
  tests are acceptance gates.
- Rollback before VERIFIED requires a fresh governed claim/start and restores
  only the two changed resolver/test hashes. Preserve authorization files,
  public bridge history, and all foreign bytes.

## Recommended Commit Type

`fix`
