REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f69a3-25dd-75e1-83d6-8c4aa29fb912
author_model: GPT-5 Codex
author_model_version: 2026-07-16 runtime
author_model_configuration: Codex Desktop interactive Prime Builder A; user-directed PB bridge auto-process

# Revised Proposal - Undo non-spawn worker session envelopes

bridge_kind: prime_proposal
Document: gtkb-wi5314-nonspawn-session-envelope-suppression
Version: 003
Responds to: bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-002.md
Date: 2026-07-16 UTC
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5314
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]
Recommended commit type: fix

## Revision Claim

Repair both non-spawn leak paths while preserving worker authority before spawn. Prime work intents are acquired before authority issuance. Issuance returns a bounded compare-and-restore token. When `_spawn_harness` returns `launched=False`, the dispatcher releases acquired intents and undoes only the envelope state written by that dispatch. A successful launch retains exactly one correlated envelope.

## Requirement Sufficiency

Existing requirements are sufficient. Version 002 requests complete enforcement of the existing WI, centralized-dispatch, session-authority, and hygiene contracts. No new owner choice is required.

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

## Prior Deliberations

- `DELIB-20266201`
- `DELIB-20260658`
- `DELIB-202666274`
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-001.md`
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-002.md`

## Owner Decisions / Input

No new owner decision is required. The preferred correction from version 002 is inside the active PAUTH and unchanged target paths. No daemon restart, runtime configuration, Git, database, credential, deployment, release, or external mutation is requested.

## Findings Addressed

### P1: successful acquisition plus failed spawn leaves authority behind

Accepted. The revised order is: allocate ids; acquire the complete Prime intent batch; snapshot the exact pre-issuance envelope path state; issue authority; spawn; then either retain on `launched=True` or release intents and undo on `launched=False`.

Undo is not `close_session`. The dispatcher token records the prior and issued bytes for the authoritative worker document, harness current envelope, and shared projection written by `ensure_worker_session`. Each path is derived through canonical envelope helpers. Undo restores or removes a path only if its current bytes still equal this issuance's bytes. A mismatch records `worker_session_undo_conflict` and never overwrites a newer writer. The worker document must match the exact session id, dispatch id, harness id, role, and `dispatcher_composition` provenance before removal. Partial undo is a hard failure.

### P3: terminal close coordination

No change. Closing workers that actually launched remains with its existing lifecycle owner. WI-5314 covers acquisition, authority issuance, spawn acceptance, and symmetric undo when no worker launches.

## Scope Changes

Target paths remain unchanged. Version 003 adds failed-spawn symmetry to version 001:

- acquire Prime intents before authority issuance;
- release acquired intents if issuance fails;
- return an in-memory cleanup token from issuance;
- on failed spawn, release intents and compare-and-restore this dispatch's envelope artifacts;
- test acquisition failure, issuance failure, failed spawn after acquisition, undo conflict, and successful launch;
- preserve Loyal Opposition document leases and foreign pre-start hunks;
- perform no whole-file stage or commit.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5314; TEST-11457; bridge versions 001-003",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "dispatcher run_dispatch_cycle Prime work-intent and spawn path",
  "before_behavior": "Failed acquisition or failed spawn can leave dispatcher-composed authority for a worker that never launched.",
  "after_behavior": "Failed acquisition writes no envelope; failed spawn restores this dispatch's exact pre-issuance envelope state; successful launch retains one envelope.",
  "self_descriptive_naming": "Cleanup-token and worker-session-undo-conflict names expose the non-spawn rollback boundary.",
  "obsolete_guidance_disposition": "No public guidance changes; incomplete creation discipline is corrected.",
  "history_preservation": "No phantom is archived and no unrelated or concurrent envelope bytes are overwritten.",
  "baseline": {
    "failed_acquisition_net_new_envelopes": 1,
    "failed_spawn_net_new_envelopes": 1,
    "successful_launch_envelopes": 1
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
    "undo path escapes project root",
    "issued bytes no longer match at undo time",
    "partial rollback",
    "non-spawn leaves net-new envelope state",
    "focused dispatcher regression"
  ],
  "rollback": "Reverse only the exact WI-5314 source and test hunks; never restore either whole target."
}
```

## Pre-Filing Preflight Subsection

The governed revision helper runs mandatory applicability and ADR/DCL clause preflights against this exact candidate. Filing fails on any nonzero result, credential hit, chain conflict, or metadata failure.

## Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Snapshot path existence and hashes, repeat acquisition-failure and failed-spawn cycles, require zero net changes. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Assert order: acquire, issue, spawn, then retain or undo. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Successful launch retains one correlated envelope; every non-spawn retains none. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Assert exact harness, role, dispatch id, session id, and provenance. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Prove exact new hunks preserve all foreign pre-start hunks. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run complete dispatcher tests, Ruff check/format, and scope/hash checks. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run mutations only in disposable in-root test repositories. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require fresh independent GO, claim, and start packet before edits. |

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

Rollback can race with a newer envelope writer. Byte-level compare-and-restore turns that into a visible non-destructive conflict. Revert only the exact independently reviewed WI-5314 hunks and tests.

## Recommended Commit Type

`fix`
