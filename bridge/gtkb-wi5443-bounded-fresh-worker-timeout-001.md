NEW
::init gtkb lo
::open build

# Defect-Fix Proposal - Recover and finalize missing WI-5336 bounded fresh-worker timeout source

bridge_kind: prime_proposal
Document: gtkb-wi5443-bounded-fresh-worker-timeout
Version: 001 (NEW)
Date: 2026-07-17 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: interactive desktop Prime Builder A


Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5443

target_paths: ["platform_tests/scripts/test_modernization_fresh_worker.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

Recover the independently specified but never finalized WI-5336 timeout marker
on top of the now-committed WI-5407 fresh-worker baseline. Add one test-local
timeout decorator so the real isolated-wheel proof is bounded as a
multi-process acceptance test rather than incorrectly inheriting the
repository's 30-second unit-test ceiling.

Filing creates `bridge/gtkb-wi5443-bounded-fresh-worker-timeout-001.md` as the
next append-only numbered bridge file; no prior bridge version is deleted or
rewritten.

## Requirement Sufficiency

**Existing requirements sufficient.** `DCL-ACTIVITY-CONTEXT-MANIFEST-001`,
the frozen `AT-FRESH-WORKER` contract, and the linked governance authorities
already specify the required isolation behavior, bounded verification, and
nonimpairment constraints. This proposal restores a missing test-local
execution bound and does not introduce or alter product requirements.

## Defect / Reproduction

At diagnostic HEAD `c0497fce9aa8506b71e6e372dec5520e2cb18c56`, the exact frozen
`AT-FRESH-WORKER` command passed its first two tests and then pytest's global
30-second watchdog interrupted
`test_built_wheel_assembles_context_without_source_tree_or_root_config` while
the test was creating its isolated virtual environment. A focused rerun
reproduced the same timeout later in the isolated `pip install` subprocess.
The changing interruption point proves the node is making progress but cannot
reliably complete its legitimate build, virtualenv, install, and subprocess
work within the unit-test ceiling.

WI-5336 specified `@pytest.mark.timeout(180)` for this exact node and received
independent verification, but the marker is absent from every reachable
committed version. WI-5407's separate installed-wheel source-exclusion repair
was committed at that diagnostic HEAD, which is an ancestor of current HEAD
`9271fa1056b60acde4175f0e1a4d7656ad0db207`; the target file remains clean and
the shared-file sequencing prerequisite recorded by WI-5443 is satisfied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/scripts/test_modernization_fresh_worker.py`.

## Specification Links

- `DCL-ACTIVITY-CONTEXT-MANIFEST-001` - governs the packaged fresh-worker
  context proof whose isolation assertions must remain unchanged.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent GO, matching claim,
  and implementation-start authority before the protected test edit.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - forbids solving the timing
  defect by impairing harnesses, reducing coverage, or weakening isolation.
- `GOV-WORK-TREE-HYGIENE-001` - limits implementation and finalization to the
  exact one-line hunk in the already-dirty shared test file.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the recovered defect,
  proposal, executable evidence, and independent verdict as durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this
  proposal to cite every governing specification concretely.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires repeated
  execution of the exact node and frozen acceptance lanes before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds WI-5443, its
  modernization-assurance project, and the active project PAUTH.
- `SPEC-AUQ-POLICY-ENGINE-001` - the existing project-wide owner
  authorization is cited explicitly; no synthetic owner approval is inferred.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the isolated wheel, virtualenv,
  and generated test state remain inside the mandatory GT-KB root.
- `GOV-STANDING-BACKLOG-001` - WI-5443 remains the durable recovery owner
  instead of rewriting the falsely terminal WI-5336 record.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - native Windows Codex self-enforces
  the bridge, claim, target, and implementation-start gates.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation and verification
  remain linked to the exact recovery artifact lifecycle.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the missing committed marker and
  reproduced acceptance failure trigger this successor proposal.

## Prior Deliberations

- `DELIB-202666540` - Loyal Opposition Proposal Review - GO - WI-5336 Fresh Worker Built-Wheel Timeout
- `DELIB-202666538` - Loyal Opposition Proposal Review - GO - WI-5335 Loading Graph Repeatability Timeout
- `DELIB-202666539` - Loyal Opposition review_no_action — WI-5336 Fresh Worker Built Wheel Timeout

## Owner Decisions / Input

- The owner authorized the full modernization program and directed that every
  discovered flaw be added as hygiene work while implementation continues.
- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`
  is the active bounded project authorization resolved by the governed
  proposal scaffold. No Git staging, commit, push, release, deployment,
  credential change, dispatcher/TAFE mutation, or harness manipulation is
  requested by this proposal.

## Proposed Scope

1. Add only `@pytest.mark.timeout(180)` immediately above
   `test_built_wheel_assembles_context_without_source_tree_or_root_config`.
2. Preserve every existing build, virtualenv, wheel-install, isolated-Python,
   package-origin, source-checkout exclusion, root-config absence, and
   no-host-authority assertion.
3. Preserve the repository-wide 30-second timeout for ordinary tests.
4. Exclude production source, configuration, global timeout policy,
   dispatcher/TAFE/harness state, and every unrelated dirty hunk.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5443 and DELIB-202666540",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "one test-local pytest timeout marker on the exact built-wheel acceptance node",
  "before_behavior": "the multi-process built-wheel proof inherits the 30-second unit-test ceiling and is interrupted during legitimate virtualenv or package-install progress",
  "after_behavior": "the same unchanged isolation proof receives a 180-second node-local bound while all ordinary tests retain the 30-second repository ceiling",
  "self_descriptive_naming": "the existing test name continues to identify the built-wheel, source-tree, and root-config isolation contract; the standard pytest timeout marker exposes its execution bound",
  "obsolete_guidance_disposition": "no guidance is replaced or retained; this proposal restores the previously reviewed bounded-test behavior",
  "history_preservation": "WI-5336 deliberations and WI-5443 successor evidence remain append-only and independently reviewable",
  "baseline": {
    "node_timeout_seconds": 30,
    "observed_interruptions": [
      "isolated virtualenv creation",
      "isolated pip install"
    ]
  },
  "expected_result": {
    "node_timeout_seconds": 180,
    "full_activity_passes_required": 3,
    "assertions_changed": 0
  },
  "rollback": {
    "instructions": "governed removal of the single node-local decorator after measured optimization proves equivalent margin",
    "test": "run the exact node and full AT-FRESH-WORKER activity three consecutive times"
  },
  "hard_invariants": [
    "all wheel isolation and source-exclusion assertions remain byte-for-byte unchanged",
    "the repository-wide timeout remains 30 seconds",
    "no dispatcher, TAFE, harness, production source, or configuration state changes"
  ],
  "fail_closed_conditions": [
    "missing independent GO or matching claim/start authority",
    "target file differs from the reviewed clean baseline",
    "any assertion or global timeout change appears in the implementation diff"
  ],
  "essential_context_preservation": "the proposal preserves the exact frozen activity, authoritative specifications, historical deliberations, target identity, rollback, and repeated-verification obligations"
}
```

## Specification-Derived Verification Plan

| Spec / contract | Verification |
| --- | --- |
| `DCL-ACTIVITY-CONTEXT-MANIFEST-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run the exact built-wheel node three consecutive times without a command-line timeout override; verify all isolation assertions execute unchanged. |
| Frozen `AT-FRESH-WORKER` | Run `python -m pytest platform_tests/scripts/test_modernization_fresh_worker.py -q --tb=short` three consecutive times and require 4/4 each time. |
| Frozen `AT-SCOPE-SEMANTICS` | Run `python scripts/check_modernization_scope_semantics.py run --phase clean-suite`; distinguish any unrelated governed failures from `MSA-MOD-AS03`. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`; `GOV-WORK-TREE-HYGIENE-001` | Confirm one insertion only, no assertion deletion or process/harness change, exact target authorization, Ruff check/format, compilation, and `git diff --check`. |
| Bridge/spec-linkage/project-linkage authorities | Run mandatory applicability and clause preflights before filing, then require live GO, matching claim/start packet, post-implementation report, and independent VERIFIED. |

## Acceptance Criteria

- The exact built-wheel test passes three consecutive repetitions under its own
  marker without a CLI timeout override.
- The full frozen `AT-FRESH-WORKER` activity passes 4/4 three consecutive
  repetitions under supported concurrent workstation load.
- `MSA-MOD-AS03` no longer fails because of the repository-wide 30-second
  watchdog.
- All wheel isolation, source-checkout exclusion, packaged-registry origin,
  absent-root-config, and no-host-authority assertions remain byte-for-byte
  unchanged.
- The diff is exactly one decorator insertion in the approved target; global
  timeout policy and all production/runtime surfaces are unchanged.
- Independent LO returns VERIFIED before exact mechanical finalization.

## Risks / Rollback

The bounded risk is that a genuinely hung node can now occupy a worker for up
to 180 seconds instead of 30. That remains well below the frozen activity's
900-second outer bound and is narrow to one multi-process proof. Rollback is
the governed removal of the single decorator after a measured optimization
demonstrates equivalent margin. No unrelated shared-file byte may be included
in implementation or rollback.

## Files Expected To Change

- `platform_tests/scripts/test_modernization_fresh_worker.py`

## Recommended Commit Type

`test:`
