NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-2026-06-29T00-18-00Z
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Codex bridge Bash adapters classify writes versus references

bridge_kind: prime_proposal
Document: gtkb-wi4254-codex-bridge-bash-adapter-write-classification
Version: 001
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY-BRIDGE-SIGNAL-QUALITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY
Work Item: WI-4254

target_paths: [".codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py", ".codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py", "platform_tests/scripts/test_sdk_bridge_bash_guard.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File governed proposal for WI-4254 to classify Codex Bash adapter bridge commands as definite writes, benign references, or unsupported likely writes.

Work item description: Codex bridge Bash adapters currently write skipped diagnostics for benign bridge path references, including staging/status commands, and return success when they cannot extract content. Distinguish definite bridge content writes, benign bridge path references, and unsupported likely writes; unsupported likely writes must fail closed per owner decision.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4254` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`, `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py`, `platform_tests/scripts/test_sdk_bridge_bash_guard.py`.

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
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266368` - Separation Check
- `DELIB-20266004` - Verdict
- `DELIB-20266102` - Owner Decision - WI-4813 Skill Catalog-Contract Test: Prioritization + Bundled Scenarios Reconciliation
- `DELIB-20266288` - Per-artifact approval needed for the PAUTH amendment per GOV-ARTIFACT-APPROVAL-001. Proposed PAUTH v3 amends `PAUTH-PROJ
- `DELIB-20266206` - Owner reconciliation decision: repair 10 corrupted related_bridge_threads links

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-BRIDGE-SIGNAL-QUALITY-BRIDGE-SIGNAL-QUALITY-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4254`.

## Proposed Scope

- Distinguish benign bridge path references such as git status, git add, git log, and bridge file reads from bridge content writes.
- Keep supported bridge writes routed through the canonical Claude hook payloads for bridge compliance and WI-ID collision checks.
- Fail closed for unsupported likely bridge writes, including malformed or unclosed heredoc writes, instead of returning success after writing skipped diagnostics.

## Cross-Harness Disposition

- Codex adapter behavior is intentionally Codex-specific for `.codex/gtkb-hooks/**`; this proposal changes only the Codex Bash adapter path and preserves canonical Claude hook enforcement by routing supported writes into `.claude/hooks/bridge-compliance-gate.py` and `.claude/hooks/bridge-proposal-wi-id-collision-gate.py`.
- Claude native Write/Edit bridge behavior remains authoritative and unchanged; no `.claude/hooks/**`, `.claude/settings.json`, or Claude skill behavior is in scope.
- Cross-harness parity is verified by targeted tests covering Codex adapter classification against the canonical hook expectations; no typed waiver is requested.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run bridge applicability preflight and targeted Bash-adapter tests proving bridge writes remain governed. |
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
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run targeted adapter parity tests for both bridge-compliance and WI-ID collision Bash adapters. |

## Acceptance Criteria

- Benign bridge path references do not create skipped diagnostics or fail the Bash adapters.
- Supported bridge writes still invoke canonical hooks and preserve existing enforcement behavior.
- Unsupported likely bridge writes fail closed with targeted tests for both bridge-compliance and WI-ID collision adapters.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.codex/gtkb-hooks/bridge-compliance-gate-bash-adapter.py`
- `.codex/gtkb-hooks/wi-id-collision-gate-bash-adapter.py`
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py`

## Recommended Commit Type

`feat`
