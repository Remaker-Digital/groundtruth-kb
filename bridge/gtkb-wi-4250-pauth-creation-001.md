NEW
author_identity: Claude Code
author_harness_id: B
author_session_context_id: 544b584c-7392-4d40-81d8-dba187ba11eb
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder; /loop dynamic
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# gtkb-wi-4250-pauth-creation - Create the narrow WI-4250 stale-status reconciliation authorization

bridge_kind: governance_advisory
Document: gtkb-wi-4250-pauth-creation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC
Responds-To: `bridge/gtkb-wi-4250-status-reconciliation-authorization-002.md` (Codex LO GO)

Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4250

target_paths: ["groundtruth.db", ".groundtruth/formal-artifact-approvals/**"]

implementation_scope: governance_mutation
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This proposal implements the approved governance pre-step for WI-4250: create one new project authorization that allows only `work_item_status_promotion` for `WI-4250` inside `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`. It does not reconcile the stale backlog row yet. It only creates the missing PAUTH so the later row-reconciliation thread can mint a valid implementation-start packet instead of reusing the adjacent stale-status batch authorization that excludes `WI-4250`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `bridge/gtkb-wi-4250-status-reconciliation-authorization-002.md` - GO review approving this PAUTH-creation step.
- `bridge/gtkb-wi-4250-backlog-reconciliation-002.md` - NO-GO showing the direct stale-row repair could not proceed without a WI-specific `work_item_status_promotion` authorization.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md` - VERIFIED evidence for the first WI-4250 slice.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md` - VERIFIED evidence completing WI-4250 implementation scope.
- `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECONCILIATION` - adjacent active stale-status PAUTH pattern that excludes `WI-4250`.

## Owner Decisions / Input

Owner directive on 2026-06-12: "Please proceed with the cleanup plan and WI-4250 and WI-4251." That is sufficient owner direction for this narrow authorization-creation step; the formal-artifact approval packets created in this implementation supply the governed mutation evidence for the deliberation and PAUTH records.

## Requirement Sufficiency

Existing requirements are sufficient for this scoped governance correction. The approved governance-prestep thread, the direct-reconciliation NO-GO, and the verified WI-4250 child threads already define the needed outcome precisely: create a narrow `work_item_status_promotion` authorization for `WI-4250` only, then stop.

## Planned Authorization Record

The implementation creates one new active PAUTH with these fields:

- id: `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION`
- project_id: `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`
- allowed_mutation_classes: `["work_item_status_promotion"]`
- included_work_item_ids: `["WI-4250"]`
- included_spec_ids: `["GOV-08", "GOV-15", "GOV-STANDING-BACKLOG-001", "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001", "GOV-FILE-BRIDGE-AUTHORITY-001", "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001"]`
- forbidden_operations: `["source", "test_addition", "spec_status_promotion", "hook_upgrade", "cli_extension", "deploy", "git_push_force"]`

## Specification-Derived Verification Plan

| Specification | Verification command or artifact | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-wi-4250-pauth-creation --format json --preview-lines 120` | Thread files and `bridge/INDEX.md` agree with no drift. |
| `GOV-ARTIFACT-APPROVAL-001` | Inspect the new files under `.groundtruth/formal-artifact-approvals/` cited by the deliberation and authorization writes. | Owner-approved formal-artifact packets exist for both governed inserts before the DB mutation. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` | New PAUTH appears active, scoped to `WI-4250`, with only `work_item_status_promotion` allowed. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Verify the new row's `included_work_item_ids`, `allowed_mutation_classes`, and `forbidden_operations` fields in the command output above. | Envelope matches the narrow WI-4250 reconciliation scope exactly. |
| `GOV-STANDING-BACKLOG-001` | `$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb backlog show WI-4250 --json` | `WI-4250` remains unchanged by this thread; only authorization state changes. |

## Risk / Rollback

The primary risk is accidentally broadening the stale-status reconciliation authority beyond `WI-4250`. Mitigation: use a WI-specific authorization id, include only `WI-4250`, and verify the row after creation before filing any reconciliation implementation. Rollback is a separate governed authorization-status mutation if the inserted PAUTH shape is wrong.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry in `bridge/INDEX.md`. `bridge/INDEX.md` remains the canonical workflow state.

## Recommended Commit Type

`docs` - this thread authorizes a later governance mutation; no source or test implementation occurs here.
