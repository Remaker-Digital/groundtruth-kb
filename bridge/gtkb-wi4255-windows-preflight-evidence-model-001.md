NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1078-0168-7573-8a31-a68af5b9842a
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: codex-desktop-prime-builder-auto-builder

# Implementation Proposal - Windows governance preflight evidence model

bridge_kind: prime_proposal
Document: gtkb-wi4255-windows-preflight-evidence-model
Version: 001
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE
Work Item: WI-4255

target_paths: ["groundtruth-kb/src/groundtruth_kb/governance/preflight_evidence.py", "platform_tests/groundtruth_kb/governance/test_preflight_evidence.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-4255` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: Define the evidence model for Windows-native governance preflights so failures produce durable human-readable and machine-readable evidence for owner-reviewed bypass instead of acting as a new unconditional blocking layer.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4255` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/governance/preflight_evidence.py`, `platform_tests/groundtruth_kb/governance/test_preflight_evidence.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266158` - Bridge Review — gtkb-wi4818-storm-watchdog-cursor-coverage-001
- `DELIB-20266361` - WI-4884 Daemon Resilience ADR/DCL Formalization Verdict
- `DELIB-20265894` - WI-4694 Validation-Through-Use Bar
- `DELIB-20266363` - Separation Check
- `DELIB-20266204` - Owner reconciliation decision batch 2: resolve 2 verified-done drift WIs (WI-3405, WI-4566)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4255`.

## Proposed Scope

- Add a reusable Windows governance preflight evidence model module; no command, hook, or CLI registration changes in this slice.
- Model preflight checks as hard, advisory, evidence-only, or inconclusive so later commit/push wrappers can report consistent severity.
- Provide deterministic JSON and readable Markdown/text summary helpers, including an evidence path field for owner-reviewed bypass prompts.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Evidence objects serialize with a stable schema containing status, checks, evidence path, generated timestamp, and summary fields.
- Failures distinguish hard existing governance gates from advisory/evidence-producing checks and inconclusive evidence states.
- Readable summaries include the evidence path when present so owner-reviewed bypass prompts can cite the durable artifact.
- Tests cover pass, fail, and partial/inconclusive evidence states without touching command wrappers or hooks.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/governance/preflight_evidence.py`
- `platform_tests/groundtruth_kb/governance/test_preflight_evidence.py`

## Recommended Commit Type

`feat`
