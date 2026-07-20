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

# Revised Implementation Proposal - Normalize the WI-5629 Static-Quality Baseline

bridge_kind: prime_proposal
Document: gtkb-wi5629-corrected-malformed-verdict-chain
Version: 023
Responds to: bridge/gtkb-wi5629-corrected-malformed-verdict-chain-022.md
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5629

target_paths: ["platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Resolve the sole version 022 terminal blocker through a format-only
normalization of
`platform_tests/scripts/test_implementation_authorization.py`.

The mutation is restricted to the exact Ruff diff already reproduced by Prime
Builder and Loyal Opposition: convert the mixed LF block at lines 984-998 to
the file's CRLF convention. No Python token, assertion, fixture, function
signature, test order, or behavior may change.

The accepted corrected-chain implementation remains unchanged. The following
three files are verification-only dependencies and must retain their version
021 hashes:

- `scripts/bridge_lifecycle_resolver.py`:
  `9F9AAF48A0712F93DB778D0934E21CC344A00C433D690B07A9AC6981A768F1F1`;
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`:
  `247731D41A7D54641E38A57DD41A77AF9B739993D8686902EFCC63B0C3CE0C40`;
- `scripts/implementation_authorization.py`:
  `A13B6CDE9DEA029996E8E8B724C20BB71168C074078835894733BA55DDF07371`.

The pre-normalization test hash is
`D7C3597096175694F2DD442894954E6C5BF301F95A805E07E6EC152D3A4F18CB`.
The implementation report must record its new post-Ruff SHA256.

## Finding Addressed

### F1 - Required four-target Ruff format evidence is red

Version 022 independently accepted the resolver behavior and found one
remaining terminal blocker: version 020 required a four-target
`ruff format --check`, while also freezing the only file Ruff would normalize.

This revision explicitly supersedes only that frozen-byte condition. It permits
mechanical formatting of the one test file and keeps the original full
four-target static-quality gate. It does not request a waiver or narrow
acceptance to changed files.

The authorized pre-mutation Ruff diff is exactly:

```text
platform_tests/scripts/test_implementation_authorization.py lines 984-998:
LF line endings -> CRLF line endings
```

Any token-level diff, any second formatted region, or any change to another
file fails closed and requires a new revision.

## Scope And Boundaries

In scope:

- run the repository Ruff formatter against only
  `platform_tests/scripts/test_implementation_authorization.py`;
- verify the resulting Git diff is line-ending-only in the exact identified
  block;
- update the reported expected SHA256 for that test;
- rerun the full WI-5629 functional and static-quality matrix;
- file a fresh terminal-readiness implementation report.

Out of scope:

- resolver or resolver-test changes;
- implementation-authorization source changes;
- assertion, fixture, import, function-signature, test-order, or test-content
  changes;
- WI-5636 `Responds to GO:` compatibility;
- WI-5637 decorated `Version:` compatibility;
- WI-5633 protected-commit integration;
- WI-5474 finalization;
- bridge writer/provider behavior;
- dispatcher configuration/runtime, capacity, ranking, routing, or claims;
- harness registry, Git index/refs/finalization, MemBase, credentials,
  deployment, release, or external-system mutation.

Read-only verification dependencies:

- `scripts/bridge_lifecycle_resolver.py`;
- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`;
- `scripts/implementation_authorization.py`;
- `platform_tests/scripts/test_bridge_work_intent_registry.py`;
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`;
- the public `gtkb-dispatcher-next-foundation-spike` bridge chain.

## Requirement Sufficiency

Existing requirements are sufficient. This revision reconciles two conditions
inside the accepted WI-5629 verification contract; it does not change bridge
lifecycle semantics or project authorization policy.

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
Active `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` version 4 includes WI-5629
and permits test mutation after an independent GO, exact claim, and
implementation-start authorization. No waiver or additional owner decision is
required.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`
- `DELIB-20260708-NO-ACTION-CANONICAL-SEMANTICS`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-017.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-018.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-019.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-020.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-021.md`
- `bridge/gtkb-wi5629-corrected-malformed-verdict-chain-022.md`
- `bridge/gtkb-wi5636-exact-responds-to-go-history-compatibility-002.md`
- `bridge/gtkb-wi5637-bounded-decorated-version-history-compatibility-002.md`

## Baseline And Ownership Evidence

Current canonical state before filing:

- latest bridge status: `NO-GO` v022;
- WI-5629 claim: `null`;
- PAUTH: active version 4 and includes WI-5629 plus `test` mutation;
- four-target Ruff format: one file would be reformatted;
- exact Ruff diff: only the 15-line mixed-ending block at lines 984-998;
- resolver suite: 44 passed;
- authorization suite: 161 passed;
- work-intent suite: 34 passed;
- operation-time evaluator suite: 13 passed;
- Ruff lint, `py_compile`, and `git diff --check`: PASS.

The WI-5629 behavioral targets currently match version 021 and version 022.
WI-5636, WI-5637, WI-5633, WI-5474, dispatcher, provider, and Git surfaces
remain separately owned.

## Proposed Implementation

1. Acquire an exact WI-5629 implementation claim after a fresh independent GO.
2. Create and finalize a fresh schema-v3 implementation-start packet for only
   `platform_tests/scripts/test_implementation_authorization.py`.
3. Recheck the pre-normalization hash and the exact `ruff format --diff`.
4. Run:
   `ruff format platform_tests/scripts/test_implementation_authorization.py`.
5. Prove the resulting diff changes only line endings in the identified block
   and produces no Python-token or behavior change.
6. Recheck the three frozen dependency hashes.
7. Run the full verification matrix below.
8. Record the new test hash and file a fresh implementation report claiming
   terminal readiness.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5629 v021 implementation report and independent format-only NO-GO v022",
  "canonical_authority": "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Fresh GO -> exact claim/start -> Ruff normalization of one declared test -> full fresh verification matrix -> independent terminal review",
  "before_behavior": "The corrected-chain implementation passes every executable test, but terminal verification is blocked by a mixed-line-ending baseline in one declared verification test.",
  "after_behavior": "The test file follows one consistent Ruff formatting convention and the full four-target static-quality gate is green.",
  "behavior_change": "none",
  "self_descriptive_naming": "No code identifiers or test names change; the revision name states the static-quality normalization scope.",
  "obsolete_guidance_disposition": "The contradictory v020 frozen-test-byte condition is superseded only for the exact formatter normalization; all behavioral guidance remains operative.",
  "history_preservation": "All bridge versions remain append-only and every public lifecycle artifact remains byte-preserved.",
  "authorized_mutation": "newline normalization only in platform_tests/scripts/test_implementation_authorization.py lines 984-998",
  "frozen_dependencies": [
    "scripts/bridge_lifecycle_resolver.py",
    "platform_tests/scripts/test_bridge_lifecycle_resolver.py",
    "scripts/implementation_authorization.py"
  ],
  "separate_compatibility": "WI-5636, WI-5637, WI-5633, and WI-5474 remain separate",
  "baseline": {
    "resolver": "44 passed",
    "authorization": "161 passed",
    "work_intent": "34 passed",
    "evaluator": "13 passed",
    "static_format": "one mixed-ending test block prevents the four-target check from passing"
  },
  "expected_result": {
    "behavior": "unchanged",
    "executable_tests": "252 passed",
    "static_format": "all four declared WI-5629 targets already formatted",
    "changed_path_count": 1
  },
  "rollback": "Under fresh GO, claim, and start authority, restore only the pre-normalization test bytes and rerun the same matrix.",
  "hard_invariants": [
    "Only platform_tests/scripts/test_implementation_authorization.py may change.",
    "The formatter diff is newline-only in the preidentified block.",
    "Resolver, resolver-test, and authorization-source hashes remain exact.",
    "All executable and static-quality gates pass after normalization.",
    "WI-5636, WI-5637, WI-5633, WI-5474, dispatcher, provider, harness, Git, and MemBase boundaries remain untouched."
  ],
  "essential_context_preservation": "Preserve the full WI-5629 v001-v023 history, v021/v022 functional evidence, public foundation chain, PAUTH v4, strict compatibility denials, and exact three-file frozen hash ledger.",
  "fail_closed_conditions": [
    "The pre-normalization hash differs from v021/v022.",
    "Ruff proposes any token-level or second-region change.",
    "Any frozen dependency hash changes.",
    "Any executable or static-quality check fails.",
    "Any mutation requires a path outside the one declared target."
  ]
}
```

## Specification-Derived Verification Plan

| Requirement | Command or proof | Acceptance predicate |
| --- | --- | --- |
| Exact format-only scope | Pre/post token comparison plus `git diff --word-diff=porcelain` and exact Ruff diff review | No Python token or semantic content changes; only identified line endings normalize. |
| Corrected-chain behavior | `pytest platform_tests/scripts/test_bridge_lifecycle_resolver.py -q --tb=short --timeout=120` | All 44 tests pass; resolver and test hashes remain exact. |
| Public continuation | Direct read-only `resolve_bridge_lifecycle(..., "gtkb-dispatcher-next-foundation-spike")` | Latest v006 `NO-GO`; pair v001/v004; audit v001-v006; only malformed v002 quarantined; no diagnostics. |
| Authorization nonimpairment | `pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short --timeout=120` | All 161 tests pass after normalization. |
| Work-intent nonimpairment | `pytest platform_tests/scripts/test_bridge_work_intent_registry.py -q --tb=short --timeout=120` | All 34 tests pass. |
| Evaluator nonimpairment | `pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py -q --tb=short --timeout=120` | All 13 tests pass. |
| Static lint | Ruff check on all four WI-5629 targets | PASS. |
| Static format | Ruff format check on all four WI-5629 targets | PASS: all four already formatted. |
| Syntax | `py_compile` on all four WI-5629 targets | PASS. |
| Whitespace | `git diff --check --` on all four WI-5629 targets | PASS, exit 0 without mixed-ending warning. |
| Boundary preservation | SHA256 comparison | Three verification-only dependencies retain v021 hashes; normalized test receives one new reported hash. |

The full test matrix must run fresh. No prior passing result substitutes for a
post-normalization run.

## Acceptance Criteria

- The only mutated protected path is
  `platform_tests/scripts/test_implementation_authorization.py`.
- The diff is newline-only in the exact lines 984-998 block already shown by
  Ruff.
- Python tokens, assertions, fixtures, signatures, imports, ordering, and
  behavior remain unchanged.
- Resolver, resolver-test, and authorization-source hashes stay exact.
- All 252 executable tests pass: 44 resolver, 161 authorization, 34
  work-intent, and 13 evaluator.
- Ruff check, four-target Ruff format check, `py_compile`, and
  `git diff --check` all pass.
- Live foundation resolution remains unchanged and correct.
- WI-5636/WI-5637 strict negative boundaries remain passing.
- No dispatcher, provider, harness, Git index/ref/finalization, MemBase,
  credential, deployment, release, or external-system mutation occurs.

## Pre-Filing Preflight

Before filing the canonical revision:

1. confirm v022 is the latest `NO-GO`;
2. confirm WI-5629 has no live claim;
3. confirm PAUTH v4 includes WI-5629 and test mutation;
4. confirm the four target hashes match v021/v022;
5. confirm the exact Ruff diff remains newline-only;
6. run candidate applicability preflight against this completed draft;
7. run mandatory ADR/DCL clause preflight against this completed draft;
8. require zero blocking errors, zero missing required specs, and zero
   blocking clause gaps.

## Risks And Rollback

- Risk: formatter output could include a token-level change. Mitigation:
  preflight and post-mutation diff/token comparisons fail closed.
- Risk: normalization could mask a behavioral regression. Mitigation: rerun
  all 252 executable tests plus live foundation proof.
- Risk: the narrow revision could be used to alter resolver behavior.
  Mitigation: three exact dependency hashes are hard acceptance predicates.
- Rollback before VERIFIED requires fresh governed claim/start authority and
  restores only the test's pre-normalization hash
  `D7C3597096175694F2DD442894954E6C5BF301F95A805E07E6EC152D3A4F18CB`.

## Recommended Commit Type

`test`
