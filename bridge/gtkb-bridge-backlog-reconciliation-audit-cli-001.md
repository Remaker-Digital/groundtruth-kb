NEW
author_identity: loyal-opposition/antigravity/C
author_harness_id: C
author_session_context_id: antigravity-gtkb-lo-2026-06-02
author_model: Gemini 3.5 Flash (High)
author_model_version: 2026-06-01
author_model_configuration: reasoning=high

bridge_kind: implementation_proposal
Document: gtkb-bridge-backlog-reconciliation-audit-cli
Version: 001
Date: 2026-06-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4234

target_paths: ["scripts/bridge_backlog_terminal_reconciliation.py", "scripts/bridge_reconciliation_audit.py", "platform_tests/scripts/test_bridge_reconciliation_audit.py", "groundtruth-kb/src/groundtruth_kb/cli.py"]

# Implementation Proposal - Reusable sanity gate for bridge/backlog terminal-state reconciliation

Implementation proposal for a bounded code or platform change.

## Claim

Implement a reusable, read-only bridge/backlog reconciliation audit command that compares live `bridge/INDEX.md`, on-disk bridge history, and MemBase work-item/project state to surface the six WI-4227 terminal-state drift buckets. The command must produce deterministic JSON plus a concise operator summary and must not mutate bridge, backlog, project, or deliberation state.

## Requirement Sufficiency

The owner identified a recurring detection/remediation gap: VERIFIED bridge work and retired backlog state can diverge without a routine check. WI-4234 already scopes the reusable sanity gate for the WI-4227 reconciliation logic. This proposal is sufficient because it turns the completed one-off reconciliation report into a repeatable command surface, preserves the existing six drift classes, and explicitly leaves remediation to later correction packets and governed mutation gates.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_backlog_terminal_reconciliation.py`, `scripts/bridge_reconciliation_audit.py`, `platform_tests/scripts/test_bridge_reconciliation_audit.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The audit treats live `bridge/INDEX.md` as authoritative for bridge queue state and does not create an alternate queue.
- `GOV-STANDING-BACKLOG-001` - The audit compares bridge evidence against MemBase backlog/work-item state without using `MEMORY.md` as a second backlog authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - The command must read fresh live sources instead of cached startup reports or stale generated summaries.
- `DCL-REPORTING-SURFACE-FRESH-READ-001` - The operator summary must disclose that it came from fresh bridge and MemBase reads.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Implementation is covered by the bounded project authorization named above.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - Scope stays inside read-only detection and explicitly excludes broad bulk mutation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The command preserves deviation findings as durable artifacts suitable for follow-up work items and correction packets.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The six drift buckets map to lifecycle trigger categories for later correction review.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal carries concrete spec links and target paths before bridge review.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must include tests mapped to these specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, and Work Item metadata are present.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner approval is already captured for this proposal batch; future correction decisions remain one-at-a-time.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are inside `E:\GT-KB`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - The check should be usable by either harness through the same deterministic command.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Detection produces durable artifacts rather than transient chat-only findings.

## Prior Deliberations

- `DELIB-2430` - Loyal Opposition Review - gt backlog add CLI REVISED-2
- `DELIB-2737` - S381 owner decision: PROJECT-GTKB-DETERMINISTIC-SERVICES-001 close-out Path B
- `DELIB-0621` - S279 WI Bulk Resolution And Deliberation Archive Advisory
- `DELIB-2762` - Loyal Opposition Review - Deterministic Services Stale Status Reconciliation REVISED-3
- `DELIB-S365-WI-3418-OBSOLETED-BY-HYGIENE-SWEEP` - S365 AUQ D: retire WI-3418 (RC Gate seed fixture) as obsoleted by Layer A hygiene-sweep program

## Owner Decisions / Input

- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` - Owner directed creation of the bridge reconciliation project, work items, and implementation proposals.
- `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION` - Active project authorization for WI-4234 through WI-4238; forbids broad bulk status mutation and automatic remediation without review.

## Proposed Scope

- Add `scripts/bridge_reconciliation_audit.py` as the shared read-only audit implementation.
- Add or wrap `scripts/bridge_backlog_terminal_reconciliation.py` for the WI-4227 six-bucket terminal-state reconciliation.
- Expose the command through the repo CLI, preferably as `python -m groundtruth_kb bridge reconcile audit --json`.
- Preserve these six drift classes: `bridge_index_drift`, `missing_or_incorrect_related_bridge_threads`, `stale_backlog_status`, `terminal_backlog_without_evidence`, `verified_bridge_missing_terminal_backlog_state`, and `verified_bridge_without_backlog_match`.
- Emit deterministic JSON detail plus a concise markdown/operator summary.
- Do not apply corrections, update MemBase, edit `bridge/INDEX.md`, or retire work items from this command.

## Specification-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Unit tests load fixture `bridge/INDEX.md` content as the only bridge queue authority and prove no alternate queue is used. |
| `GOV-STANDING-BACKLOG-001` | Unit tests compare fixture MemBase-like work-item rows against bridge evidence and preserve backlog as the single mutable authority. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Tests exercise fresh-read inputs and reject cached/generated report inputs as authoritative sources. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tests cover all six WI-4227 drift classes and classify them deterministically. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Implementation report cites the active PAUTH and verifies the command is read-only. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `python -m pytest platform_tests/scripts/test_bridge_reconciliation_audit.py -q --tb=short`. |

## Acceptance Criteria

- Command emits JSON counts and row-level detail for all six WI-4227 reconciliation buckets.
- Command emits a concise markdown/operator summary suitable for hygiene-sweep or session-wrap surfacing.
- Tests prove no bridge file, `bridge/INDEX.md`, MemBase row, or project authorization row is mutated.
- Output ordering is deterministic and stable across repeated runs against the same inputs.
- Existing one-off WI-4227 report data can be represented by the new schema.

## Risks / Rollback

Risk: false positives from bridge/backlog parsing could create noisy correction candidates. Mitigation: fixture-driven tests for each bucket and read-only default behavior.

Rollback: remove the CLI registration and audit script changes. No state rollback should be required because the command is detection-only.

## Files Expected To Change

- `scripts/bridge_backlog_terminal_reconciliation.py`
- `scripts/bridge_reconciliation_audit.py`
- `platform_tests/scripts/test_bridge_reconciliation_audit.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`

## Recommended Commit Type

`feat`
