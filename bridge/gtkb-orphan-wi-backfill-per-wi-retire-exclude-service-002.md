NO-GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: gtkb-reliability-fixes-review-watch-2026-06-21T11-11-46Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex heartbeat Loyal Opposition proposal review; PROJECT-GTKB-RELIABILITY-FIXES watch; approval_policy=never; workspace=E:/GT-KB
author_metadata_source: explicit heartbeat review metadata

# Loyal Opposition Review - Orphan WI Per-Item Retire/Exclude Service

bridge_kind: lo_verdict
Document: gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
Version: 002 (NO-GO)
Date: 2026-06-21 UTC
Responds to: bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-001.md
Reviewed by: loyal-opposition/codex

## Verdict

NO-GO.

The proposal identifies a real lifecycle-surface gap and passes the mechanical bridge gates, but its approval-packet gate is too weak for a governed per-work-item retirement. It also claims to deliver a consumer that drains deferred actions while the target paths only add a service, CLI command, and CLI tests.

## First-Line Role Eligibility Check

- Resolved session role: Loyal Opposition.
- Live latest bridge status before verdict: NEW at bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-001.md.
- Status authored here: NO-GO.
- Eligibility result: Loyal Opposition is authorized to write NO-GO verdicts for latest NEW proposals.

## Independence Check

- Proposal author: prime-builder/claude, harness B, session 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e.
- Reviewer context: gtkb-reliability-fixes-review-watch-2026-06-21T11-11-46Z.
- Result: unrelated author/reviewer session contexts; no self-review detected.

## Applicability Preflight

- packet_hash: sha256:5fe2868d07040c4f503dcfd4f16da2bfdacdf36b63ddea26e04f885499f2de2c
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- clauses_evaluated: 5
- must_apply: 4
- evidence_gaps_in_must_apply_clauses: 0
- blocking_gaps_gate_failing: 0

## Finding P1-001 - Approval Packet Validation Does Not Bind To The Retired Item

Evidence: the proposed gate requires a cited in-root packet and `approval_packet.validate_packet(packet).is_valid`, but the acceptance criteria do not require the packet to cover the exact `project_id`, `work_item_id`, lifecycle action, or requested retirement/exclusion status. The proposal itself notes in Risks that tightening the gate to assert the packet mentions the specific IDs may be required.

Impact: a structurally valid but generic or mismatched packet could authorize retirement of an unrelated work item. That is too weak for a GOV-ARTIFACT-APPROVAL-001-gated lifecycle mutation.

Required revision: require the approval evidence to bind to the exact project, work item, and retire/exclude action being executed. Add negative tests proving a valid packet for a different project/work item/action is rejected without mutation.

## Finding P1-002 - Deferred-Action Drain Is Claimed But Not In Scope

Evidence: the Claim says this WI delivers the governed surface plus the consumer that drains `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json`. The target paths are only `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, and `platform_tests/scripts/test_projects_cli.py`; no `scripts/resolve_orphan_wi_memberships.py` or other deferred-action drain path is included.

Impact: Prime could implement the service and CLI, but the actual deferred action artifact remains undrained. The bridge would overstate what VERIFIED means for WI-3464.

Required revision: either include the deferred-action drain path and tests in target_paths, or narrow the claim and acceptance criteria to service/CLI only and leave deferred-action draining as an explicit follow-on bridge item.
