NEW
author_identity: loyal-opposition/antigravity/C
author_harness_id: C
author_session_context_id: antigravity-gtkb-lo-2026-06-02
author_model: Gemini 3.5 Flash (High)
author_model_version: 2026-06-01
author_model_configuration: reasoning=high

bridge_kind: implementation_proposal
Document: gtkb-bridge-reconciliation-correction-packets
Version: 001
Date: 2026-06-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4236

target_paths: ["scripts/bridge_reconciliation_correction_packet.py", "scripts/bridge_reconciliation_audit.py", "platform_tests/scripts/test_bridge_reconciliation_correction_packet.py", "groundtruth-kb/src/groundtruth_kb/cli.py"]

# Implementation Proposal - Generate governed bridge reconciliation correction packets by triage class

Implementation proposal for a bounded code or platform change.

## Claim

Implement a governed correction-packet generator for bridge/backlog reconciliation findings. The generator must consume read-only audit JSON, select exactly one triage class per invocation, prioritize non-terminal P1/P2 work items with VERIFIED bridge metadata, and produce a concrete dry-run packet for owner and bridge review. It must not mutate MemBase, bridge files, project rows, or status fields directly.

## Requirement Sufficiency

The owner rejected a broad, risky bulk status mutation under WI-4227 and directed one child correction work item or packet per triage class. WI-4236 is sufficient because it converts detector findings into bounded, auditable mutation packets while preserving owner decision gates, PAUTH scope, bridge GO, implementation-start, and post-implementation verification.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_reconciliation_correction_packet.py`, `scripts/bridge_reconciliation_audit.py`, `platform_tests/scripts/test_bridge_reconciliation_correction_packet.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`.

## Specification Links

- `GOV-STANDING-BACKLOG-001` - Packets propose backlog/work-item corrections without creating a second backlog authority.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Implementation is covered by the active project PAUTH.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - Packet generation is bounded to dry-run governance evidence and explicitly forbids bulk mutation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Packet classes map reconciliation findings to lifecycle-triggered correction reviews.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Bridge evidence cited in packets must come from live bridge history and `bridge/INDEX.md`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Each packet is a durable artifact with evidence, risk, and recommended action.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal carries concrete spec links and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification must prove one-class packet generation and no mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, and Work Item metadata are present.
- `SPEC-AUQ-POLICY-ENGINE-001` - The packet format must make any necessary owner decision explicit and one at a time.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are inside `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Packet generation should be harness-neutral.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Packet files and summaries preserve correction intent as artifacts before mutation.

## Prior Deliberations

- `DELIB-2358` - Loyal Opposition Review - Bridge Poller WI Retirement Disposition
- `DELIB-2696` - Loyal Opposition Verification - Platform Tests Ruff Cleanup
- `DELIB-2430` - Loyal Opposition Review - gt backlog add CLI REVISED-2
- `DELIB-2798` - GT-KB Bridge Review Verdict - gtkb-work-intent-registry-prime-write-integration - 014
- `DELIB-S365-WI-3418-OBSOLETED-BY-HYGIENE-SWEEP` - S365 AUQ D: retire WI-3418 (RC Gate seed fixture) as obsoleted by Layer A hygiene-sweep program

## Owner Decisions / Input

- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` - Owner directed correction packets one mutation class at a time.
- `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION` - Active project authorization; forbids broad bulk status mutation and automatic remediation without review.

## Proposed Scope

- Add `scripts/bridge_reconciliation_correction_packet.py`.
- Add a CLI surface, preferably `python -m groundtruth_kb bridge reconcile packet --class <class> --input <audit.json>`.
- Support one triage class per invocation; reject requests that combine multiple mutation classes.
- Include candidate work item ids, priority/stage/status, bridge evidence paths, proposed mutation type, exclusions, confidence/risk notes, and required gates.
- Prioritize non-terminal P1/P2 work items with VERIFIED bridge metadata.
- Emit dry-run markdown and JSON packet output only; do not call `backlog update`, `projects update`, `projects retire`, or bridge writer helpers.

## Specification-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-STANDING-BACKLOG-001` | Tests prove packets reference MemBase rows but do not update them. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Tests prove the generator rejects multi-class packet requests and records gate requirements. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Tests verify a packet surfaces at most one owner-decision prompt/decision slot. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tests map each supported audit class to a packet class and correction-review intent. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `python -m pytest platform_tests/scripts/test_bridge_reconciliation_correction_packet.py -q --tb=short`. |

## Acceptance Criteria

- CLI refuses combined triage classes in a single packet.
- Packet output includes candidate rows, evidence, proposed mutation class, exclusions, risk notes, and required gates.
- P1/P2 non-terminal work items with VERIFIED bridge metadata sort before lower-priority candidates.
- Tests prove no MemBase, bridge, project, or deliberation mutation occurs.
- Packet schema can consume the audit JSON emitted by WI-4234/WI-4235 commands.

## Risks / Rollback

Risk: operators could mistake a packet for approval to mutate. Mitigation: every packet must state `dry_run: true`, required gates, and forbidden automatic remediation.

Rollback: remove CLI registration and packet generator. Generated packet files, if any, are review artifacts and can be archived without data mutation.

## Files Expected To Change

- `scripts/bridge_reconciliation_correction_packet.py`
- `scripts/bridge_reconciliation_audit.py`
- `platform_tests/scripts/test_bridge_reconciliation_correction_packet.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`

## Recommended Commit Type

`feat`
