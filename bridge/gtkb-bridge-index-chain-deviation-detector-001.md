NEW
author_identity: loyal-opposition/antigravity/C
author_harness_id: C
author_session_context_id: antigravity-gtkb-lo-2026-06-02
author_model: Gemini 3.5 Flash (High)
author_model_version: 2026-06-01
author_model_configuration: reasoning=high

bridge_kind: prime_proposal
Document: gtkb-bridge-index-chain-deviation-detector
Version: 001
Date: 2026-06-02 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION
Project: PROJECT-GTKB-BRIDGE-RECONCILIATION
Work Item: WI-4235

target_paths: ["scripts/bridge_index_chain_audit.py", "scripts/bridge_reconciliation_audit.py", "platform_tests/scripts/test_bridge_index_chain_audit.py", "groundtruth-kb/src/groundtruth_kb/cli.py"]

# Implementation Proposal - Detect bridge INDEX/file-chain deviations and prepare repair packets

Implementation proposal for a bounded code or platform change.

## Claim

Implement a deterministic bridge INDEX/file-chain deviation detector that finds bridge-artifact drift before it causes stale dispatch or hidden completed work. The detector must identify missing INDEX entries, INDEX entries whose files are absent, skipped or duplicated version chains, responds-to mismatches, latest-status disagreements, and unindexed live bridge files. It must produce reviewable repair packets but must not edit bridge files or `bridge/INDEX.md` by default.

## Requirement Sufficiency

The session already surfaced a live bridge-chain defect: a verified bridge thread had a missing intermediate `REVISED` line in `bridge/INDEX.md`. That class of problem is distinct from terminal backlog reconciliation and must be detected at the bridge artifact layer. WI-4235 is sufficient because it scopes both detection and packet preparation while preserving the rule that live bridge state remains `bridge/INDEX.md` and repairs happen only through governed writer paths.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_index_chain_audit.py`, `scripts/bridge_reconciliation_audit.py`, `platform_tests/scripts/test_bridge_index_chain_audit.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - The detector checks bridge files and `bridge/INDEX.md` while preserving `bridge/INDEX.md` as the queue authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Deviations become durable reviewable repair packets instead of ad hoc chat memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Chain defects affect artifact lifecycle state and must be classified before correction.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal carries concrete spec links and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification must include spec-mapped tests for each deviation class.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, and Work Item metadata are present.
- `SPEC-AUQ-POLICY-ENGINE-001` - Repair packets may surface owner decisions one at a time; the detector itself needs no further owner input.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All target paths are inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - Bridge-chain detection is separate from backlog mutation and must not modify backlog state.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - The same detector should be runnable from Codex and Claude.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Repair packets are artifacts suitable for bridge review.

## Prior Deliberations

- `DELIB-2421` - Loyal Opposition Review - Proposal-Standards WI-ID Collision Gate
- `DELIB-2425` - Loyal Opposition Review - Proposal-Standards WI-ID Collision Gate
- `DELIB-2552` - Loyal Opposition Review - WITHDRAWN Latest-Status Reconciliation
- `DELIB-2358` - Loyal Opposition Review - Bridge Poller WI Retirement Disposition
- `DELIB-2422` - Loyal Opposition Review - Proposal-Standards WI-ID Collision Gate

## Owner Decisions / Input

- `DELIB-2026-06-02-BRIDGE-RECONCILIATION-PROJECT` - Owner directed bridge deviation checking/correction project work and implementation proposals.
- `PAUTH-PROJECT-GTKB-BRIDGE-RECONCILIATION-DETECTION-CORRECTION` - Active project authorization for WI-4234 through WI-4238; forbids automatic remediation without review.

## Proposed Scope

- Add `scripts/bridge_index_chain_audit.py` for bridge-internal chain integrity checks.
- Add shared aggregation or hooks in `scripts/bridge_reconciliation_audit.py` where useful.
- Expose the detector through the repo CLI, preferably as `python -m groundtruth_kb bridge reconcile index-chain --json`.
- Detect absent files referenced by INDEX, bridge files not referenced by INDEX, duplicate status entries, missing intermediate versions, latest-status mismatch, and `Responds to:` chain mismatches.
- Emit a correction-packet-ready JSON shape with candidate repair actions, evidence paths, and risk notes.
- Do not edit `bridge/INDEX.md` or bridge documents from this detector.

## Specification-Derived Verification Plan

| Specification | Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fixture tests validate that the detector reads live-like INDEX content and never substitutes a cached queue surface. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tests classify missing INDEX entries, missing files, skipped versions, duplicate status lines, latest-status mismatch, and responds-to mismatch. |
| `GOV-STANDING-BACKLOG-001` | Tests prove the detector does not inspect or mutate backlog rows except through explicit audit input in the shared aggregator. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests use only in-root fixture paths and target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `python -m pytest platform_tests/scripts/test_bridge_index_chain_audit.py -q --tb=short`. |

## Acceptance Criteria

- JSON output includes issue type, bridge document slug, affected files, INDEX line evidence when available, and candidate repair action.
- Tests cover at least one fixture for each bridge-internal deviation class.
- Detector output is deterministic and sorted.
- No default command path mutates bridge files, `bridge/INDEX.md`, MemBase, or reports.
- Repair packets are reviewable text/JSON outputs that can be filed separately through governed bridge paths.

## Risks / Rollback

Risk: version parsing may incorrectly flag historically unusual bridge threads. Mitigation: classify uncertain cases separately and include file evidence for review.

Rollback: remove CLI registration and the detector module. Since detection is read-only, rollback should not require data repair.

## Files Expected To Change

- `scripts/bridge_index_chain_audit.py`
- `scripts/bridge_reconciliation_audit.py`
- `platform_tests/scripts/test_bridge_index_chain_audit.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`

## Recommended Commit Type

`feat`
