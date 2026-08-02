REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=default; thread_source=automation
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5552-exited-worker-lease-reconciliation
Version: 007
Responds to: bridge/gtkb-wi5552-exited-worker-lease-reconciliation-006.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5552
related_work_items: ["WI-5208", "WI-5427", "WI-5429", "WI-5448", "WI-5549", "WI-5566"]

target_paths: ["platform_tests/scripts/test_wi5552_exited_worker_reconciliation.py"]
implementation_scope: isolated_test_first_residual_gap_admission
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
KB mutation: none; this proposal performs no KB mutation.

# WI-5552 Revised Implementation Proposal — Isolate the Mixed-Exit Residual-Gap Test Before Source Admission

## Revision Claim

Version 006 is correct: absence of a claim and age of a GO do not implement, withdraw, supersede, or verify the approved work. Versions 003 and 005 supplied no implementation evidence, and version 004's acceptance of disposition-close cannot substitute for the original implementation lifecycle. WI-5552 remains open.

The safe next step is a fresh, independently reviewed test-first slice. Current committed WI-5208 behavior already passes focused exact-once ledger, lease-release, daemon reconciliation, and generation-handoff tests, while one original source target is foreign-dirty and other source targets overlap open work. This revision therefore admits only the dedicated mixed-exit reproducer. It does not claim that current coverage proves WI-5552, does not authorize source modification, and does not convert the historical GO into current implementation authority.

## Requirement Sufficiency

**Existing requirements sufficient.** `WI-5552`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`, and the original independently approved test-first acceptance behavior are sufficient for the single isolated test target declared here. This revision narrows implementation admission to producing missing evidence; it does not create or revise product behavior. If the fixture exposes a residual source defect outside the stated requirements, implementation must stop and a later proposal must reassess requirement sufficiency before requesting source authority.

## Current Evidence and Preimages

- `scripts/dispatcher_runtime.py` is tracked, Git-clean, and currently SHA-256 `02A54EA1E819157C6C41C2232E7244D73AAFEFF3D1BA47FD3F53A89DE9FE4189` (worktree/HEAD blob `4d54b8a658a2d6e3af5e9275dd367370c91b4bc4`).
- `scripts/gtkb_dispatcher_daemon.py` is tracked, Git-clean, and currently SHA-256 `E9A9DFB96D94D6623ACE9110A861AA901DFFC38864187C5D10B21BD3BFD2DE1C` (worktree/HEAD blob `143e4018a9490b9238c2bff311b823c9df2e9654`).
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py` is foreign-dirty under WI-5549 at SHA-256 `DDE66052C4556CBD0D175FE7B32B5F1EB9E09C725A84FD2F0A3A6E86FC35F7E6`, worktree blob `494005615cfd39f2e45e5b0b98a270cf00197eb3`, versus HEAD/index blob `51408720b0c07977da0e1edb743b96809c911936`. This proposal neither edits nor adopts those bytes.
- The original hyphenated test path is absent. This revision corrects it to the repository's import-safe underscore convention: `platform_tests/scripts/test_wi5552_exited_worker_reconciliation.py`, also currently absent.
- The original patch-carrier path is absent and removed from this revision. A speculative patch is not an implementation outcome and cannot safely own foreign-dirty source.
- On 2026-08-01, the following synthetic focused nodes passed together in 1.84 seconds: WI-5208 concurrent launches reconcile out of order and release exactly once; legacy last-launch migration; daemon nonzero-exit reconciliation; generation-handoff live-work deferral; and supervisor-commit-before-exit. These are baseline evidence only. They do not cover the exact WI-5552 mixed D/F scenario and are not terminal evidence.
- WI-5552 is an active member of active `PROJECT-GTKB-RELIABILITY-FIXES`. Active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` v1 covers eligible project-member source/test work. Deprecated WI approval fields are not operation-time authority.

## Scope and Ordering

### Slice A — One deterministic synthetic integration fixture

Create only `platform_tests/scripts/test_wi5552_exited_worker_reconciliation.py`. The fixture must use isolated temporary state and monkeypatched process/lease surfaces; it must not start, stop, activate, quiesce, configure, or otherwise mutate TAFE, the dispatcher daemon, live workers, live leases, live run state, or provider state.

The fixture creates at least two concurrent launch-ledger entries:

1. one launch has an authoritative parseable exit sidecar and recorded document leases;
2. one separate launch remains live with matching PID plus create-time provenance and its own leases; and
3. the exited launch's PID is dead, reused, or otherwise non-authoritative for live classification.

Invoke the canonical reconciliation and daemon-tick/quiescence seams deterministically. Prove the exited launch becomes terminal exactly once, only its leases are released exactly once, the provenance-valid live launch and leases are preserved, active/completed counts converge, and generation-handoff readiness is not blocked by the already-exited launch.

### Slice B — Fail closed on source admission

If the new fixture passes against the exact preimages above, WI-5552's implementation report is test-only and must state that no source repair was needed. If it fails, stop after preserving the exact failing assertion and current source hashes. Do not patch any source in this implementation cycle.

A residual failure requires a subsequent substantive `REVISED` proposal that declares only the exact failed source surfaces, incorporates the observed failure, revalidates current PAUTH/overlaps/preimages, and obtains a fresh independent GO and exact implementation claim. No failure grants implicit source authority.

### Slice C — Collision and dependency discipline

- WI-5208 is the committed baseline, not a substitute for the new reproducer.
- WI-5427's historical generation-handoff lane is withdrawn. WI-5429 remains a separate runtime-generation admission lane and is not duplicated here.
- WI-5448 owns dead-daemon lease restart semantics; this fixture may assert compatible invariants but must not implement that lane.
- WI-5549 owns the present foreign-dirty `bridge_dispatch_report.py` bytes. Preserve them byte-for-byte.
- WI-5566 remains an open daemon overlap. Preserve its scope and bytes.
- Any future source revision must serialize only the exact overlapping paths after their owners reach a current disposition. Unrelated preparation and isolated test work remain parallel.

## Acceptance Criteria

1. The new underscore-named test module is the only implementation target in this revision.
2. The fixture proves authoritative exited-sidecar precedence, PID/create-time provenance for live classification, exact-once exited-launch reconciliation, lease isolation, deterministic ledger counts, and generation-handoff unblocking.
3. Running the fixture twice against fresh isolated state produces the same result and no residue outside pytest temporary directories.
4. Repeated reconciliation in one fixture releases the exited launch's leases once and never releases the live launch's leases.
5. No source, configuration, live runtime, TAFE/dispatcher state, provider state, bridge hunk, or foreign-dirty byte is modified.
6. A passing fixture yields a factual test-only implementation report. A failing fixture yields no source edit and requires a new exact-surface proposal.
7. Normal current GO, exact claim, schema-v3 implementation-start, independent verification, and governed finalization gates remain mandatory.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5552; DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION; PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; bridge/gtkb-wi5552-exited-worker-lease-reconciliation-006.md",
  "canonical_authority": "SPEC-CENTRALIZED-DISPATCH-SERVICE-001 with DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001 and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Independent bridge GO, exact work-intent claim, schema-v3 implementation-start packet, one isolated test addition, test-only implementation report, and independent VERIFIED.",
  "before_behavior": "Committed WI-5208 and daemon tests cover adjacent exact-once and handoff behavior, but no dedicated fixture proves WI-5552's mixed exited/live D/F launch, PID-reuse, lease-isolation, and generation-handoff scenario as one invariant set.",
  "after_behavior": "One synthetic fixture deterministically proves the complete WI-5552 invariant set without touching live dispatcher, TAFE, worker, lease, provider, or runtime state; any residual source failure stops for a separately reviewed exact-surface proposal.",
  "self_descriptive_naming": "test_wi5552_exited_worker_reconciliation.py names the work item and behavior using the repository's import-safe underscore convention.",
  "obsolete_guidance_disposition": "The stale-carrier NO-ACTION closure claim and original hyphenated test filename are rejected; prior numbered evidence is preserved and no source guidance is changed.",
  "history_preservation": "All bridge, project, PAUTH, MemBase, test-baseline, foreign-dirty, and Git evidence remains preserved; no prior version or foreign byte is rewritten.",
  "baseline": {
    "runtime_sha256": "02A54EA1E819157C6C41C2232E7244D73AAFEFF3D1BA47FD3F53A89DE9FE4189",
    "daemon_sha256": "E9A9DFB96D94D6623ACE9110A861AA901DFFC38864187C5D10B21BD3BFD2DE1C",
    "foreign_dirty_report_sha256": "DDE66052C4556CBD0D175FE7B32B5F1EB9E09C725A84FD2F0A3A6E86FC35F7E6",
    "focused_baseline": "5 adjacent synthetic nodes passed in 1.84 seconds; dedicated WI-5552 module absent"
  },
  "expected_result": {
    "fixture": "Mixed exited/live launches converge deterministically with exact-once exited-lease release and live-lease preservation.",
    "provenance": "Only PID plus create-time agreement classifies the no-exit launch as live; an authoritative parseable exit sidecar makes its exact launch terminal.",
    "admission": "Pass yields a test-only report; fail yields preserved evidence and no source edit."
  },
  "rollback": {
    "instructions": "Remove only the approved new test file through the governed lifecycle.",
    "verification": "Re-run the focused WI-5208 and daemon baseline nodes and confirm no live or foreign target changed."
  },
  "hard_invariants": [
    "No TAFE or dispatcher activation, configuration, live-run, live-worker, live-lease, provider, Git, index-lock, deployment, release, or external-system mutation.",
    "Only the single declared test target may be created; every source and foreign-dirty byte is preserved.",
    "A fixture failure cannot authorize a source patch and must return through a fresh exact-surface proposal.",
    "Independent GO, exact claim, schema-v3 start, verification, and governed finalization remain load-bearing."
  ],
  "fail_closed_conditions": [
    "Missing, stale, or mismatched GO, claim, PAUTH, start packet, PB role, target absence, or source preimage.",
    "The fixture reads or mutates non-temporary dispatcher, TAFE, worker, lease, provider, or runtime state.",
    "Any implementation attempts to modify source, create the obsolete hyphenated path, or adopt WI-5549 foreign-dirty bytes.",
    "Any acceptance result is inferred without executing the dedicated fixture."
  ],
  "essential_context_preservation": "The revision preserves the original defect and approval, v006 correction, current preimages, WI-5208 baseline, WI-5448/WI-5549/WI-5566 ownership, active project PAUTH, the disabled live dispatcher/TAFE posture, and the full independent bridge lifecycle."
}
```

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — canonical dispatcher behavior and reconciliation authority.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` — daemon liveness, provenance, and reconciliation constraints.
- `ADR-DISPATCHER-ARCHITECTURE-001` — preserves the existing dispatcher substrate and forbids an alternate reconciler.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — the test cannot impair live dispatcher behavior or mutate runtime state.
- `GOV-RELIABILITY-FAST-LANE-001` — bounds the active Reliability Fixes implementation lane.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active project membership and PAUTH govern implementation authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — re-evaluate active PAUTH at proposal and implementation start.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered files are canonical; fresh GO/claim/start remain mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — independent verification derives from the linked behavior.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — preserves exact project, PAUTH, WI, and target linkage.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the single test target remains within `E:/GT-KB` and outside adopter scope.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — preserves test, proposal, result, and review traceability.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserves the unresolved defect and its evidence as durable governed artifacts instead of a stale-carrier no-op.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — no terminal state is asserted without implementation and verification evidence.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run the new exact mixed-exit fixture and the focused WI-5208 reconciliation nodes. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Assert exited-sidecar precedence, live PID/create-time agreement, exact lease isolation, and daemon-tick/quiescence convergence. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Static review proves the fixture invokes only existing canonical runtime/daemon seams and introduces no alternate dispatcher substrate. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Assert all filesystem/process/lease inputs are isolated or monkeypatched and no live daemon/provider operation occurs. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Re-run schema-v3 applicability and authorization evaluation before implementation start. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require canonical current GO, exact claim, schema-v3 start, independent verdict, and governed finalization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Map the executed fixture and focused baseline nodes to every acceptance criterion in the implementation report. |

## Risks and Rollback

Risk is low because the admitted implementation is a new isolated test only. The primary risk is a fixture that accidentally consults or mutates live state; fail closed by requiring temporary roots and monkeypatched process/lease surfaces. Rollback removes only the new test file under separate governed authority. Append-only bridge evidence remains preserved.

## Owner Decisions / Input

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` established the active Reliability Fixes standing project/authorization. No new owner decision is required for this proposal.
- No owner disposition withdraws or supersedes WI-5552; this revision therefore keeps the work open and returns it to a fresh implementation-review cycle.

## In-Root and Append-Only Evidence

The only declared implementation target is inside `E:/GT-KB`: `platform_tests/scripts/test_wi5552_exited_worker_reconciliation.py`. Numbered bridge history remains append-only and canonical. No prior version is rewritten or deleted.

## Essential Context Preservation

This proposal preserves the original defect, the v002 test-first approval, v006's rejection of stale-GO closure, current source/test preimages, foreign-dirty ownership, related WI ordering, project authorization, acceptance behavior, test mapping, rollback, and the explicit prohibition on source admission without a new failing-evidence proposal.
