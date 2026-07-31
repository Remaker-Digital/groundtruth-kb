REVISED
::init gtkb lo
::open build

# Corrected Implementation Report - WI-5400 cloud verdict-claim lifecycle

bridge_kind: implementation_report
Document: gtkb-wi5400-cloud-verdict-claim-lifecycle
Version: 004
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; build activity envelope

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5400

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py", "scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Approved proposal: bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-001.md
Responds to GO: bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-002.md
Supersedes report: bridge/gtkb-wi5400-cloud-verdict-claim-lifecycle-003.md

## Correction

Version 003 included candidate-preflight citations to transient working inputs.
Those citations are withdrawn and carry no evidentiary authority. This version
is the complete operative implementation report and repeats the implementation,
scope, and executable results using only canonical project facts and in-root
source/test paths. No implementation byte changed as part of this report
correction.

This correction applies
`DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY`: canonical bridge
artifacts do not reference or depend on noncanonical artifacts.

## Summary

WI-5400 now gives a cloud Loyal Opposition worker a verdict work-intent claim
before provider launch and renews or reacquires that worker claim before
governed verdict publication. A peer-held claim before launch suppresses the
provider run neutrally. A peer-held publication race returns structured neutral
stand-down evidence instead of entering repeated publisher recovery or feeding
failure-count and circuit-breaker state.

The dispatcher remains the control-plane owner for trusted worker-session
creation, document leases, claim acquisition, launch metadata, and exit
reconciliation. The cloud harness uses the governed verdict publisher and
shared claim service. No MemBase, dispatcher/TAFE configuration, harness
configuration, Git history, credential, deployment, release, or destructive
cleanup mutation occurred.

## Implementation Authority

- Latest implementation authorization was the independent GO in version 002.
- A matching `go_implementation` work-intent claim and schema-v3
  implementation-start authorization completed before any protected target was
  changed.
- Each of the four approved targets validated as authorized before mutation.
- The claim was released after filing the implementation report.
- No claim, authorization, or report fact is sourced from a scratch artifact;
  this numbered report is the durable promoted record.

## Files Changed

- `scripts/dispatcher_runtime.py`
  - Acquires the LO verdict claim after trusted worker-session creation and
    before provider launch.
  - Suppresses a peer-held claim before launch as neutral contention.
  - Stamps launched workers with owned claim provenance.
  - Releases only worker-owned claims on launch failure, incomplete/failure
    exit, or neutral peer-held stand-down.
  - Reconciles the neutral stand-down marker without producing a missing-verdict
    failure or breaker churn.
- `scripts/cloud_harness_base.py`
  - Adds structured `BridgeVerdictClaimStandDown` evidence.
  - Renews or reacquires the worker claim before governed verdict publication.
  - Converts peer-held publication races into neutral stand-down results.
- `platform_tests/scripts/test_dispatcher_runtime.py`
  - Adds regressions for pre-spawn claim acquisition, peer-held launch
    suppression, worker-owned cleanup, and neutral exit reconciliation.
- `platform_tests/scripts/test_cloud_harness_base.py`
  - Adds claim-helper coverage to existing publisher tests.
  - Adds a regression proving one-attempt neutral stand-down for a peer-held
    publication claim.

## Specification Links

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
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `GOV-HARNESS-ISOLATION-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` is
  the active project authorization covering WI-5400.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` requires this
  corrected, self-contained canonical report.
- No new owner decision or waiver is requested.

## Prior Deliberations

- `DELIB-202666173` - prior provider LO governed-verdict publication review.
- `DELIB-202666250` - prior cloud publisher-recovery verification.
- `DELIB-202666178` - related provider publication verification.
- `DELIB-20265758` and `DELIB-20265754` - related verdict/finalization retry context.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` - current canonical-reference boundary.

## Spec-To-Test Mapping

| Requirement | Executed verification | Observed result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-DISPATCHER-ARCHITECTURE-001` | Five focused claim-lifecycle regressions covering pre-launch acquisition, peer-held launch suppression, publication stand-down, retained fail-closed behavior, and exit reconciliation. | 5 passed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Complete focused cloud-harness and dispatcher-runtime modules. | 305 passed. |
| `GOV-HARNESS-ISOLATION-001` | Exact four-path diff review plus focused regressions. | No direct harness contact, runtime reconfiguration, or cross-harness introspection added. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Python compilation, full focused pytest lane, Ruff check, Ruff format check, and exact-target whitespace validation. | All commands exited zero. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Exact target inventory and path review. | All targets are in-root under `E:/GT-KB`; no adopter or out-of-root path changed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Numbered bridge-file review lifecycle. | This REVISED report is the next append-only file and awaits independent VERIFIED or NO-GO. |

## Commands Executed

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts\dispatcher_runtime.py scripts\cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_cloud_harness_base.py
```

Observed result: exit 0.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cloud_harness_base.py::test_bridge_review_peer_held_publish_claim_stands_down_neutrally platform_tests\scripts\test_cloud_harness_base.py::test_bridge_review_fails_closed_after_repeated_publisher_failures platform_tests\scripts\test_dispatcher_runtime.py::test_wi5400_lo_live_spawn_acquires_verdict_claim_before_provider_launch platform_tests\scripts\test_dispatcher_runtime.py::test_wi5400_lo_peer_held_verdict_claim_suppresses_provider_launch platform_tests\scripts\test_dispatcher_runtime.py::test_wi5400_peer_claim_stand_down_exit_zero_is_neutral_not_missing_verdict -q --tb=short
```

Observed result: exit 0; 5 passed.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short
```

Observed result: exit 0; 305 passed.

```powershell
groundtruth-kb\.venv\Scripts\ruff.exe check scripts\dispatcher_runtime.py scripts\cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_cloud_harness_base.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts\dispatcher_runtime.py scripts\cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_cloud_harness_base.py
git diff --check -- scripts\dispatcher_runtime.py scripts\cloud_harness_base.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_cloud_harness_base.py
```

Observed result: all commands exited zero; Ruff reported clean and all four
files formatted. Git emitted only line-ending notices.

## Candidate Gate Results

- Candidate-content applicability preflight: PASS; no blocking errors and no
  missing required or advisory specifications.
- Candidate-content ADR/DCL clause preflight: PASS; zero blocking gaps.
- Codex bridge compliance audit: PASS.
- Canonical-reference scan: PASS; this report contains no dependency on a
  noncanonical artifact.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5400 and the approved numbered bridge thread",
  "canonical_authority": "SPEC-CENTRALIZED-DISPATCH-SERVICE-001, ADR-DISPATCHER-ARCHITECTURE-001, and GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "dispatcher-launched cloud Loyal Opposition verdict publication",
  "before_behavior": "peer-held verdict claims could trigger provider spend, repeated publisher recovery, and false failure classification",
  "after_behavior": "the dispatcher acquires before launch and peer-held races terminate as structured neutral stand-downs",
  "self_descriptive_naming": "claim lifecycle helpers, neutral result codes, and focused tests name the exact behavior",
  "obsolete_guidance_disposition": "the superseded report's transient-input citations are withdrawn; no implementation guidance depends on them",
  "history_preservation": "versions 001 through 004 remain append-only numbered bridge files",
  "baseline": {
    "approved_targets": 4,
    "focused_regressions": 5,
    "focused_modules": 305
  },
  "expected_result": {
    "focused_regressions": "5 passed",
    "focused_modules": "305 passed",
    "peer_claim_outcome": "neutral stand-down"
  },
  "rollback": {
    "instructions": "under separate authority, revert only the WI-5400 hunks in the four approved source/test paths",
    "test": "rerun the five focused regressions, complete focused modules, compilation, Ruff, and exact-target whitespace checks"
  },
  "hard_invariants": [
    "no dispatcher/TAFE or harness configuration mutation",
    "no direct harness contact or cross-harness introspection",
    "no MemBase, credential, Git history, deployment, or release mutation",
    "only the four approved source/test paths belong to WI-5400",
    "all implementation and verification paths remain in-root under E:/GT-KB"
  ],
  "fail_closed_conditions": [
    "any focused claim-lifecycle regression fails",
    "non-contention publication failures stop failing closed",
    "a peer-held claim feeds failure-count or circuit-breaker state",
    "independent verification or exact-scope evidence is absent"
  ],
  "essential_context_preservation": "document leases, trusted worker sessions, governed verdict publication, claim ownership, provider failure semantics, and append-only bridge review remain intact"
}
```

## Acceptance Criteria Result

1. Same-session missing or expired claim renews or reacquires before publication: PASS.
2. Peer-held claim before launch suppresses provider use and failure/breaker churn: PASS.
3. Peer-held publication race returns structured neutral evidence after one publish attempt: PASS.
4. Launch failure and incomplete/failure exits release only worker-owned claims: PASS.
5. Existing malformed and non-contention publication failures remain fail closed: PASS.
6. Complete focused modules, compilation, Ruff, format, and whitespace checks pass: PASS.

## Residual Risk

The dispatcher now coordinates document leases and verdict work-intent claims
for LO work. Focused coverage exercises pre-spawn acquisition, launch
suppression, cleanup, publication-time stand-down, and exit reconciliation.
Independent verification should rerun the same lane against the exact four
candidate paths. Live fleet behavior remains an operational follow-up, not a
substitute for the deterministic verification required here.

## Rollback

Under separate authority, revert only the WI-5400 hunks in the four approved
source/test paths and rerun the mapped verification lane. Numbered bridge
history and canonical MemBase records remain append-only.

## Loyal Opposition Asks

1. Treat this version as the operative self-contained implementation report.
2. Rerun the mapped commands against the exact four candidate paths.
3. Return VERIFIED if the implementation and canonical evidence satisfy the GO;
   otherwise return NO-GO with concrete findings.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
