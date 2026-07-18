REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder; transcript-defined ::init gtkb pb; approval_policy=never

# Revised Proposal - Undo non-spawn worker session envelopes after dependency closure

bridge_kind: prime_proposal
Document: gtkb-wi5314-nonspawn-session-envelope-suppression
Version: 007
Responds to: bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-006.md
Date: 2026-07-17 UTC
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5314
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]
implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

## Revision Claim

Reissue the previously approved WI-5314 compare-and-restore design after the
only blocking predecessor has reached terminal state. `WI-5255` is now latest
`VERIFIED` at `bridge/gtkb-wi5255-bc-telemetry-worker-provenance-008.md`, so
the peer implementation-report conflict cited in
`bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-006.md` no longer
blocks a fresh Loyal Opposition review.

The target paths were re-read before this revision and are clean for WI-5314:

```json
{
  "scripts/dispatcher_runtime.py": "sha256:dc67e8ada02a5cb20243fdf6634222139d23083049ac5fcda7fce51428bfb28c",
  "platform_tests/scripts/test_dispatcher_runtime.py": "sha256:44af13322cdd9bf3afc24d5f57cde65b6bb4933918097a8c542c628bb3a576d0"
}
```

`git diff --name-only -- scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`
produced no output before this revision. Existing unrelated worktree dirt in
non-target paths remains outside this proposal and does not authorize any
whole-file operation.

## Current-State Facts Checked Before Revision

- `WI-5255` latest status is `VERIFIED` at
  `bridge/gtkb-wi5255-bc-telemetry-worker-provenance-008.md`.
- `WI-5314` latest status is `NO-GO` at
  `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-006.md`.
- The version-006 NO-GO had one blocking finding: nonterminal `WI-5255`
  claimed the shared test path.
- The actual WI-5314 target paths are `scripts/dispatcher_runtime.py` and
  `platform_tests/scripts/test_dispatcher_runtime.py`; both have no current
  working-tree diff.
- An unrelated daemon module currently has foreign work but is not in this
  proposal's target set.

## Requirement Sufficiency

Existing requirements remain sufficient. This revision does not change the
session-envelope, dispatcher, role-authority, or work-intent requirements. It
only removes the obsolete predecessor-conflict premise and carries forward the
previously approved bounded source/test implementation after fresh target
baselines.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`

## Prior Deliberations And Bridge Evidence

- `DELIB-20266201` - bounded daemon process-lifecycle hardening authorization.
- `DELIB-20260658` - worker-envelope containment model.
- `DELIB-202666274` - modernization required-work authorization with bridge and mechanical gates retained.
- `DELIB-20260710-GTKB-RUNTIME-CHARTER-SESSION-ROLE-ENVELOPE` - worker authority must bind a real worker context.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-003.md` - prior substantive REVISED compare-and-restore proposal.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-004.md` - prior LO GO accepting that design before the peer-report conflict was discovered.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-006.md` - current NO-GO requiring terminal `WI-5255` and fresh revision.
- `bridge/gtkb-wi5255-bc-telemetry-worker-provenance-008.md` - terminal `VERIFIED` predecessor evidence.

## Owner Decisions / Input

No new owner decision is required. The active project authorization and prior
owner decisions cover this bounded source/test correction, and this revision
requests no dispatcher restart, runtime configuration change, database mutation,
Git operation, credential action, deployment, release, external-system effect,
or destructive cleanup.

## Findings Addressed

### F1 - Peer implementation report conflict

Closed by current state. The shared-path predecessor `WI-5255` is now terminal
`VERIFIED`; its implementation report no longer blocks the operation-time gate
for `platform_tests/scripts/test_dispatcher_runtime.py`. This revision still
requires a fresh independent `GO`, fresh implementation claim, and successful
implementation-start packet before any source/test mutation.

## Proposed Implementation

Repair both non-spawn leak paths while preserving worker authority before
spawn:

1. Allocate dispatch/session identifiers.
2. Acquire the complete Prime work-intent batch before authority issuance.
3. Snapshot the exact pre-issuance envelope path state.
4. Issue authority and retain an in-memory cleanup token describing only this
   dispatch's writes.
5. Attempt spawn.
6. If spawn returns `launched=True`, retain exactly one correlated worker
   envelope.
7. If spawn returns `launched=False`, release acquired intents and compare-and-
   restore or remove only the envelope state written by this dispatch.

Undo is not `close_session`. The cleanup token records prior and issued bytes
for the authoritative worker document, harness current envelope, and shared
projection written by `ensure_worker_session`. Each path is derived through
canonical envelope helpers. Undo restores or removes a path only if its current
bytes still equal this issuance's bytes. A mismatch records
`worker_session_undo_conflict`, preserves newer bytes, and fails closed instead
of overwriting a concurrent writer. Partial undo is a hard failure.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5314 revision 007 after WI-5255 VERIFIED at bridge/gtkb-wi5255-bc-telemetry-worker-provenance-008.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, SPEC-CENTRALIZED-DISPATCH-SERVICE-001, GOV-SESSION-ROLE-AUTHORITY-001, DCL-SESSION-ROLE-RESOLUTION-001",
  "primary_route": "dispatcher_runtime Prime work-intent and worker-session spawn path",
  "before_behavior": "Failed acquisition or failed spawn can leave dispatcher-composed authority for a worker that never launched.",
  "after_behavior": "Failed acquisition writes no envelope; failed spawn restores this dispatch's exact pre-issuance envelope state; successful launch retains one correlated envelope.",
  "self_descriptive_naming": "Cleanup-token and worker-session-undo-conflict names expose the non-spawn rollback boundary.",
  "obsolete_guidance_disposition": "The obsolete nonterminal WI-5255 blocker is closed by terminal verification; no public guidance changes.",
  "history_preservation": "No phantom worker envelope is archived and no unrelated or concurrent envelope bytes are overwritten.",
  "baseline": {
    "target_hashes": {
      "scripts/dispatcher_runtime.py": "sha256:dc67e8ada02a5cb20243fdf6634222139d23083049ac5fcda7fce51428bfb28c",
      "platform_tests/scripts/test_dispatcher_runtime.py": "sha256:44af13322cdd9bf3afc24d5f57cde65b6bb4933918097a8c542c628bb3a576d0"
    },
    "predecessor": "WI-5255 VERIFIED",
    "target_diff": "git diff --name-only over the two target paths produced no output"
  },
  "expected_result": {
    "failed_acquisition_net_new_envelopes": 0,
    "failed_spawn_net_new_envelopes": 0,
    "successful_launch_envelopes": 1,
    "concurrent_overwrites": 0
  },
  "essential_context_preservation": "Dispatch id, worker session id, harness, role, provenance, selected work, intents, telemetry, document leases, and all foreign hunks remain available at their existing boundaries.",
  "hard_invariants": [
    "No worker authority remains for a decision that launches no worker.",
    "Worker authority exists before a real subprocess consumes it.",
    "Successful launch retains exactly one correlated envelope.",
    "Acquired Prime intents are released when issuance or spawn fails.",
    "Undo never overwrites concurrent bytes.",
    "Loyal Opposition leases and foreign hunks remain unchanged."
  ],
  "fail_closed_conditions": [
    "pre-start target hash drift",
    "implementation-start packet missing or outside target paths",
    "undo path escapes project root",
    "issued bytes no longer match at undo time",
    "partial rollback",
    "non-spawn leaves net-new envelope state",
    "focused dispatcher regression"
  ],
  "rollback": "Reverse only the exact WI-5314 source and test hunks; never restore either whole target."
}
```

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Snapshot target path hashes, run failed-acquisition and failed-spawn cycles in disposable in-root test fixtures, and require zero net envelope changes for non-spawns. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Assert order: acquire work intents, issue authority, spawn, then retain or undo. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Successful launch retains one correlated worker envelope; every non-spawn retains none. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Assert exact harness, role, dispatch id, session id, and dispatcher composition provenance. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Prove exact new hunks preserve all foreign pre-start hunks and do not rewrite whole target files. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` and `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Require fresh independent GO, fresh claim, and successful implementation-start packet before mutation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused dispatcher tests, Ruff check/format, and scope/hash checks before implementation report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run mutations only in disposable in-root test repositories. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use only append-only bridge proposal, GO, implementation report, and independent verification states. |

Expected commands after GO:

- `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short`
- `python -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`
- `python -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`
- exact pre/post target hash and hunk-isolation checks.

## Acceptance Criteria

1. Repeated acquisition failures create zero new worker documents or projections.
2. Issuance failure releases every acquired Prime intent and launches nothing.
3. Successful acquisition plus `launched=False` releases intents and restores the exact pre-issuance path set and bytes.
4. Undo conflict records `worker_session_undo_conflict` and preserves newer bytes.
5. Successful launch retains exactly one correlated worker envelope.
6. Loyal Opposition lease and successful-dispatch tests remain green.
7. Exact WI-5314 hunks preserve all foreign edits; no whole-file Git operation occurs.
8. No daemon, config, database, Git, credential, deployment, release, or external effect occurs.

## Risk And Rollback

Rollback can race with a newer envelope writer. Byte-level compare-and-restore
turns that into a visible non-destructive conflict. Revert only the exact
independently reviewed WI-5314 source and test hunks.

## Pre-Filing Self-Check Evidence

The completed content was prepared after a Prime drafting claim for this
thread. The filing helper will rerun the mandatory applicability and ADR/DCL
clause preflights against this exact candidate before writing the live bridge
file, and filing must fail on any nonzero result, credential hit, chain
conflict, or metadata failure.
