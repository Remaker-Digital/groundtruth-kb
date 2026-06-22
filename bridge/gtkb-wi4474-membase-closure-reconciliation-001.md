NEW

# WI-4474 MemBase Closure Reconciliation Proposal

bridge_kind: prime_proposal
Document: gtkb-wi4474-membase-closure-reconciliation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-22 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eecf8-f9c0-7652-a2ab-d36df80757a8
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop interactive session; Prime Builder session role from `::init gtkb pb`

Project Authorization: PAUTH-WI-4474-MEMBASE-CLOSURE-RECONCILIATION
Project: PROJECT-GTKB-COST-OPTIMIZED-AUTODISPATCH
Work Item: WI-4474

target_paths: ["groundtruth.db", "bridge/gtkb-wi4474-membase-closure-reconciliation-*.md"]

implementation_scope: membase_work_item_closure_reconciliation
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

`WI-4474` remains open/backlogged in MemBase, but its requested tracked
watchdog promotion has already been implemented and VERIFIED in the bridge
thread `gtkb-storm-watchdog-detect-noncodex-process-families`, latest
`VERIFIED` at `bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md`.
That verified implementation landed the watchdog at the tracked path
`scripts/ops/harness_storm_watchdog.ps1` and added
`platform_tests/scripts/test_harness_storm_watchdog.py`, satisfying WI-4474's
requirement to promote the emergency `.gtkb-state/ops` watchdog into a
versioned, reviewable, and testable `scripts/ops/` surface.

This proposal requests a closure-only reconciliation: after Loyal Opposition
returns GO, update only the `WI-4474` MemBase lifecycle fields and related
bridge evidence so the standing backlog reflects the already-verified bridge
outcome. No source, test, dispatcher configuration, harness registry,
invocation surface, host scheduled task, deployment, credential, formal
artifact, or bridge-runtime mutation is in scope.

## Current Live State Snapshot

Current backlog row from `gt backlog show WI-4474 --json`:

- `id`: `WI-4474`
- `rowid`: `6433`
- `version`: `1`
- `resolution_status`: `open`
- `stage`: `backlogged`
- `related_bridge_threads`: `null`
- `status_detail`: `null`
- `completion_evidence`: `null`
- `changed_by`: `prime-builder/claude`
- `changed_at`: `2026-06-12T00:49:43+00:00`

Current verified promotion evidence:

- `gtkb-storm-watchdog-detect-noncodex-process-families` latest status is
  `VERIFIED` at `bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md`.
- The VERIFIED verdict states that the implementation correctly adds the
  tracked watchdog script `scripts/ops/harness_storm_watchdog.ps1` and
  regression test `platform_tests/scripts/test_harness_storm_watchdog.py`.
- Focused verification command run in this session:
  `python -m pytest platform_tests/scripts/test_harness_storm_watchdog.py -q --tb=short -o addopts= --basetemp .gtkb-state/pytest-wi4474-watchdog`
  returned `6 passed, 1 warning in 2.61s`.

Current closure-specific PAUTH readback:

- `id`: `PAUTH-WI-4474-MEMBASE-CLOSURE-RECONCILIATION`
- `status`: `active`
- `owner_decision_deliberation_id`: `DELIB-20260622-WI4474-CLOSURE-RECONCILIATION`
- `included_work_item_ids`: `["WI-4474"]`
- `allowed_mutation_classes`: `["membase_work_item_update","project_artifact_link","governance_evidence"]`
- `forbidden_operations`: `["source_change","test_change","dispatcher_config_change","harness_registry_mutation","invocation_surface_mutation","production_deployment","credential_lifecycle_change","formal_artifact_mutation","retired_poller_restore","bridge_protocol_bypass","self_review"]`

## Exact Implementation Contract

Implementation after GO must preserve the current interactive Prime Builder
session marker so attribution resolves to `prime-builder/codex`, then run the
following MemBase update:

```powershell
$env:GTKB_HARNESS_NAME = 'codex'
$threads = '["bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md","bridge/gtkb-wi4474-membase-closure-reconciliation-001.md"]'
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog update WI-4474 `
  --resolution-status resolved `
  --stage resolved `
  --related-bridge-threads $threads `
  --status-detail 'Resolved after closure reconciliation: tracked watchdog promotion is VERIFIED at bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md; verified implementation landed scripts/ops/harness_storm_watchdog.ps1 and platform_tests/scripts/test_harness_storm_watchdog.py, satisfying WI-4474 tracked scripts/ops promotion requirement; closure bridge gtkb-wi4474-membase-closure-reconciliation received GO and implementation report.' `
  --owner-approved `
  --change-reason 'WI-4474 closure reconciliation after verified watchdog-promotion bridge; closure-specific PAUTH PAUTH-WI-4474-MEMBASE-CLOSURE-RECONCILIATION and owner decision DELIB-20260622-WI4474-CLOSURE-RECONCILIATION authorize the MemBase lifecycle update.' `
  --json
```

The same command with `--dry-run --json` was executed before filing and
returned:

```json
{
  "dry_run": true,
  "fields": {
    "related_bridge_threads": "[\"bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md\",\"bridge/gtkb-wi4474-membase-closure-reconciliation-001.md\"]",
    "resolution_status": "resolved",
    "stage": "resolved",
    "status_detail": "Resolved after closure reconciliation: tracked watchdog promotion is VERIFIED at bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md; verified implementation landed scripts/ops/harness_storm_watchdog.ps1 and platform_tests/scripts/test_harness_storm_watchdog.py, satisfying WI-4474 tracked scripts/ops promotion requirement; closure bridge gtkb-wi4474-membase-closure-reconciliation received GO and implementation report."
  },
  "updated": false,
  "work_item_id": "WI-4474"
}
```

## Field-Level Readback Contract

After implementation, `gt backlog show WI-4474 --json` must show:

| Field | Expected value |
| --- | --- |
| `id` | `WI-4474` |
| `resolution_status` | `resolved` |
| `stage` | `resolved` |
| `related_bridge_threads` | `["bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md","bridge/gtkb-wi4474-membase-closure-reconciliation-001.md"]` |
| `status_detail` | `Resolved after closure reconciliation: tracked watchdog promotion is VERIFIED at bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md; verified implementation landed scripts/ops/harness_storm_watchdog.ps1 and platform_tests/scripts/test_harness_storm_watchdog.py, satisfying WI-4474 tracked scripts/ops promotion requirement; closure bridge gtkb-wi4474-membase-closure-reconciliation received GO and implementation report.` |
| `changed_by` | `prime-builder/codex` |
| `change_reason` | `WI-4474 closure reconciliation after verified watchdog-promotion bridge; closure-specific PAUTH PAUTH-WI-4474-MEMBASE-CLOSURE-RECONCILIATION and owner decision DELIB-20260622-WI4474-CLOSURE-RECONCILIATION authorize the MemBase lifecycle update.` |

The update must not change `title`, `description`, `priority`, `origin`,
`component`, `project_name`, `subproject_name`, `source_owner_directive`,
`source_deliberation_query`, `acceptance_summary`, `related_deliberation_ids`,
`source_spec_id`, `source_test_id`, `supersedes`, `superseded_by`, or
`completion_evidence`. `version` and `changed_at` are expected to advance as
normal MemBase row-history fields.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the closure mutation must be gated by a
  numbered bridge proposal, Loyal Opposition GO, implementation-start packet,
  implementation report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal
  carries concrete PAUTH, project, work item, target paths, prior evidence, and
  verification mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the required project
  authorization, project, and work-item metadata are present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps to the
  already-VERIFIED implementation bridge, focused watchdog tests, and exact
  MemBase readback.
- `GOV-STANDING-BACKLOG-001` - WI-4474 should not remain open once the tracked
  promotion has terminal verified evidence.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the PAUTH grants bounded
  eligibility only; it does not bypass LO GO, implementation start, report, or
  VERIFIED.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the owner decision, PAUTH, work
  item, verified promotion bridge, closure bridge, and MemBase row should form
  a consistent artifact graph.

## Prior Deliberations

- `DELIB-20260622-WI4474-CLOSURE-RECONCILIATION` - owner project-completion
  directive captured as closure-only MemBase authorization for WI-4474.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D6-20260612` - owner decision selecting
  event-driven dispatch with watchdog fallback; the emergency watchdog was the
  runtime artifact later promoted.
- `DELIB-20262481` - dispatch concurrency-cap context; preserved because the
  watchdog is a complementary emergency control.
- `DELIB-20265232` and `DELIB-20265231` - dispatch-storm incident and terminal
  remediation context.
- `DELIB-20265457` - owner authorization for the reliability-fixes batch that
  produced the verified watchdog-promotion bridge.
- `bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md` -
  Loyal Opposition VERIFIED verdict proving the tracked script/test promotion
  is complete.

## Owner Decisions / Input

No additional owner action is required. The current project-completion
directive has been captured as
`DELIB-20260622-WI4474-CLOSURE-RECONCILIATION`, and active PAUTH
`PAUTH-WI-4474-MEMBASE-CLOSURE-RECONCILIATION` explicitly authorizes the
closure-only MemBase update for `WI-4474`.

This is a single-row closure reconciliation, not a bulk operation; this bridge
proposal is the GOV-STANDING-BACKLOG-001 review packet for the lifecycle
update, and the owner-approval evidence is the deliberation/PAUTH pair above.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4474 defines the desired tracked
watchdog promotion; `bridge/gtkb-storm-watchdog-detect-noncodex-process-families-004.md`
proves that the tracked `scripts/ops/` script and test landed and were
VERIFIED; backlog and artifact-lifecycle requirements require MemBase to
reflect that durable completion evidence. No new specification is required for
this closure-only reconciliation.

## Spec-Derived Verification Plan

| Spec / governing surface | Verification command or evidence | Expected outcome |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge.py gtkb-wi4474-membase-closure-reconciliation --format json` after report filing | Chain shows `001 NEW`, then GO, then implementation report before VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `gt projects show-authorization PAUTH-WI-4474-MEMBASE-CLOSURE-RECONCILIATION --json` | PAUTH is active, includes `WI-4474`, and allows only `membase_work_item_update`, `project_artifact_link`, and `governance_evidence`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `show_thread_bridge.py gtkb-storm-watchdog-detect-noncodex-process-families --format json --preview-lines 20` and `python -m pytest platform_tests/scripts/test_harness_storm_watchdog.py -q --tb=short -o addopts=` | Implementation bridge latest status is `VERIFIED` at `-004`; focused test returns `6 passed`. |
| `GOV-STANDING-BACKLOG-001` | `gt backlog show WI-4474 --json` after implementation | Field-level readback matches the table above. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Readback of DELIB, PAUTH, verified promotion bridge, closure bridge, and resolved MemBase row | Artifact graph consistently links owner decision, authorization, verified implementation evidence, and closure. |

## Risk / Rollback

Risk is limited to one MemBase lifecycle row. The exact row key is `WI-4474`;
implementation must use the stable lookup command `gt backlog show WI-4474 --json`
before and after mutation. Rollback, if LO later rejects the closure evidence,
is a follow-up governed backlog update returning `resolution_status` to `open`,
`stage` to `backlogged`, and replacing or clearing `status_detail`. No source,
test, dispatcher config, host scheduled task, deployment, or credential rollback
is needed because none is authorized or changed by this reconciliation.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4474-membase-closure-reconciliation`; no prior version
is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are
the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

chore: backlog reconciliation only; no product/source behavior change.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
