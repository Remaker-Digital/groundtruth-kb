NEW

# Implementation Proposal - Unified dispatcher report CLI - fast cut (single command: status + in-flight work + PB/LO ready-to-work lists)

bridge_kind: prime_proposal
Document: gtkb-wi5174-dispatch-workflow-report
Version: 001
Date: 2026-07-10 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive session; approval_policy=never; role=prime-builder
author_metadata_source: Codex system runtime context plus explicit session document


Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5174-WORKFLOW-REPORT-20260710
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5174

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

Implementation proposal for a bounded code or platform change.

## Claim

Extend the existing `gt bridge dispatch report` command with a bounded,
read-only workflow view built exclusively from current bridge, dispatch-runtime,
project-authorization, and MemBase data. The existing full `--json` object is
preserved byte-for-contract in shape and semantics; only `--compact --json`
emits the new `gtkb.dispatch_workflow.v1` schema.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001` is owner-approved and sufficient
for the fast cut. It fixes the command surface, compact-schema fields, queue
categories, list bounds, source authorities, and explicit non-goals. The
approved source-spec backfill on WI-5174 is currently fail-closed pending the
independent document-role-writer verdict; this proposal cites the approved spec
and active PAUTH directly and does not bypass that backfill.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`.

## Specification Links

- `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001` - defines the only approved
  report command, compact schema, queue semantics, data authorities, bounds,
  and metrics-free fast-cut boundary.
- `ADR-DISPATCHER-COMPLEX-CLI-001` - keeps operational reporting on the
  established dispatcher command surface.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - provides the existing runtime
  dispatch facts consumed by the report without adding a competing data path.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `GOV-FILE-BRIDGE-AUTHORITY-001` - require the cited PAUTH, independent GO,
  claim, and implementation-start packet before protected changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` and
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - bind this proposal
  to its project, work item, authorization, and approved specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification
  against the compact-view acceptance criteria rather than only smoke output.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - preserve the approved requirement's
  formal lineage through PAUTH, bridge review, implementation, tests, and
  independent verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `GOV-STANDING-BACKLOG-001` - keep the work inside GT-KB platform paths and
  use the existing WI rather than creating a duplicate report backlog.

## Prior Deliberations

- `DELIB-20265795` - owner decision establishing a governed dispatcher
  reporting and configuration surface.
- `DELIB-202666075` - owner approval for the bounded WI-5174 implementation
  authorization.
- `DELIB-202665716` - dispatch-timer verification evidence relevant to keeping
  report data observational rather than selection-changing.

## Owner Decisions / Input

- `DELIB-202666075` - owner approved this bounded implementation authorization.
- `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-WI5174-WORKFLOW-REPORT-20260710`
  - active PAUTH; protected implementation still requires independent LO GO,
  matching claim, and implementation-start evidence.

## Proposed Scope

1. Add a pure compact-workflow projection beside the existing report builder.
   It may consume the existing full report for dispatch/runtime facts but must
   not alter the full report object returned to `--json` callers.
2. Obtain role actionability through `BridgeQueueSnapshot` and
   `compute_actionable_pending` or their shared successor. Do not duplicate
   status-to-role rules or infer worker authority from dispatcher configuration.
3. Join current MemBase work-item, source-specification, project-membership,
   PAUTH, and bridge-linkage facts only to classify records as
   `actionable_now`, `candidate_next`, or `blocked`. Missing facts become
   explicit reason codes; they are never guessed.
4. Render the bounded human workflow view by default and for `--compact`.
   Render `gtkb.dispatch_workflow.v1` only for `--compact --json`. Every list
   is capped at 20 records with truncation evidence.
5. Preserve read-only behavior and the fast-cut boundary: no telemetry,
   metrics, cost estimates, scoring, tuning, production-selection changes, or
   state writes.

## Specification-Derived Verification Plan

| Requirement | Automated evidence |
| --- | --- |
| Full JSON compatibility | Assert the exact existing top-level section set and representative existing semantics for `report --json`. |
| Compact JSON contract | Assert `report --compact --json` has `schema_version`, `status`, `in_flight`, role queues, and bounds. |
| Human contract | Assert default and explicit `--compact` output show status, in-flight work, and both role queues. |
| Canonical actionability | Fixture GO/NO-GO/NEW/REVISED threads and assert output follows the shared queue driver rather than locally reimplemented rules. |
| Candidate safety | Assert missing specification, PAUTH, bridge, or review prerequisites appear as `candidate_next` or `blocked`, never `actionable_now`. |
| Block evidence | Assert each surfaced blocked record has an evidence-backed reason code and unresolvable linkage is explicit. |
| Bounds | Seed more than 20 entries and assert fixed limits plus truncation indicators. |
| Read-only behavior | Snapshot report input files and MemBase state before all output variants and assert no changes. |

## Acceptance Criteria

- `gt bridge dispatch report --json` remains contract-compatible.
- Default human output, `--compact`, and `--compact --json` expose the required
  status, in-flight work, PB queue, and LO queue without a new command.
- Only canonically authorized items are described as ready; all candidates and
  blockers carry the specified distinction and reason evidence.
- All views are bounded and read-only.
- No WI-5175 metrics-enrichment or tuning behavior is introduced.

## Risks / Rollback

- Risk: a local actionability fork could drift from bridge routing. Mitigation:
  call the canonical queue driver directly and test canonical status fixtures.
- Risk: a compact projection could accidentally change `--json`. Mitigation:
  keep projection construction separate and lock the existing top-level
  contract in regression tests.
- Risk: incomplete MemBase linkage could be mistaken for readiness. Mitigation:
  classify unknowns only as candidate or blocked with explicit reason codes.
- Rollback: remove the compact projection and option handling while preserving
  the pre-existing report builder and full JSON contract; no persisted state
  requires migration.
- Filing uses the next numbered bridge file under `bridge/` and remains
  append-only; no prior bridge file is rewritten or deleted.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Recommended Commit Type

`feat`
