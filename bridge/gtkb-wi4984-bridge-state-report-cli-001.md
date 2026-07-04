NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; role=Prime Builder; sandbox=danger-full-access; approval=never
author_metadata_source: codex-interactive

# Implementation Proposal - Deterministic bridge/dispatcher/harness state-report CLI (gt bridge state-report)

bridge_kind: prime_proposal
Document: gtkb-wi4984-bridge-state-report-cli
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4984-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4984

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement deterministic read-only gt bridge state-report for bridge/dispatcher/harness status.

Work item description: Deterministic read-only CLI 'gt bridge state-report [--json] [--markdown]' emitting the owner-standard bridge/dispatcher/harness report (owner-affirmed 2026-07-03). Per DELIB-S312 (Deterministic Services Principle) it replaces AI re-derivation of this report each loop fire. Authorized via DELIB-202665301 (owner AUQ: "keep me LO; route to Codex-A"); LO verifies.

--markdown output MUST be three markdown TABLES (owner explicitly requires tables, not inline bullets):

(1) BRIDGE: total thread count + the LO-actionable (latest NEW/REVISED) list, plus a status-mix table with columns "Status | Count". Compute latest status via exact <slug>-NNN.md indexing by reusing scripts/bridge_thread_files.py (WI-4977) so drafts, prefix-siblings, and non-canonical files are excluded consistently.

(2) DISPATCHER: an aspect/value table with rows Health, PB selected, LO selected, Findings — sourced from `gt bridge dispatch health` / status (not cached artifacts).

(3) HARNESSES: a table whose columns are EXACTLY "ID | Harness | Model / Config | Role | Active | Dispatchable | Events". The Model / Config column sits immediately to the right of Harness and shows the model label plus key headless-invocation config (reasoning / effort / approval_policy / skill / route), read from harness-state/harness-registry.json (headless invocation_surfaces argv) and config/dispatcher/rules.toml (budget.harnesses.*.model).

Deterministic computation only; no AI judgment. --json emits the same data machine-readably. Scope is the report tool + focused tests; no dispatcher-behavior or topology changes.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4984` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`, `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`.

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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-202665295` - WI-4977 Headless Dispatch Stability — Implementation Verification
- `DELIB-202665187` - Verdict: NO-GO
- `DELIB-202665146` - Verdict: NO-GO
- `DELIB-202665297` - WI-4977 Headless Dispatch Stability — REVISED Proposal Review Verdict
- `DELIB-202665174` - Verdict Summary

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4984-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4984`.

## Proposed Scope

- Add read-only gt bridge state-report with JSON and Markdown output.
- Report current bridge latest-status mix, Prime/LO actionable queues, dispatcher health/selected candidates/findings, and harness role/dispatchability table from canonical readers.
- Do not change dispatcher behavior, routing, topology, or eligibility.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused tests verify bridge latest-status/actionable derivation uses canonical bridge readers. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused CLI tests verify dispatcher health/selected candidate fields and read-only behavior. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- CLI returns deterministic JSON and Markdown summaries without mutating bridge, dispatcher, registry, or runtime state.
- Report derives bridge state from numbered bridge files and dispatcher state, not cached startup summaries.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`

## Recommended Commit Type

`feat`
