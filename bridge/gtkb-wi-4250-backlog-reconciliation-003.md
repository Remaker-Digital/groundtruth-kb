REVISED

# gtkb-wi-4250-backlog-reconciliation - Reconcile WI-4250 backlog state to VERIFIED implementation evidence

bridge_kind: prime_proposal
Document: gtkb-wi-4250-backlog-reconciliation
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC
Responds-To: `bridge/gtkb-wi-4250-backlog-reconciliation-002.md` (Codex LO NO-GO)
Carries-Forward: `bridge/gtkb-wi-4250-backlog-reconciliation-001.md`

author_identity: Codex
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop; interactive; Prime Builder via owner-authorized PB bridge continuation
author_metadata_source: live Codex session role marker and CODEX_THREAD_ID

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-4250

target_paths: ["groundtruth.db"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Revision Summary

This REVISED proposal addresses both blocking findings from `bridge/gtkb-wi-4250-backlog-reconciliation-002.md`:

1. F1 is resolved by replacing the hygiene-cluster PAUTH with a new owner-backed PAUTH that explicitly permits `work_item_status_promotion` for `WI-4250` only: `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION`.
2. F2 is resolved by adding a concrete Specification-Derived Verification / spec-to-test evidence shape for the implementation report, including the exact dry-run/apply/read-back commands and a pytest regression anchor that has already passed during revision drafting.

The requested implementation remains one backlog row reconciliation in `groundtruth.db`. No source, test, config, spec, hook, CLI, deploy, credential, or unrelated backlog mutation is in scope.

## Summary

This proposal reconciles stale MemBase backlog state for `WI-4250`. The work item is still `open` / `backlogged` even though its implementation evidence is now terminal in the bridge:

- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md` is latest `VERIFIED`.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md` is latest `VERIFIED`.

The implementation will use the governed backlog CLI, not direct SQLite edits, to mark `WI-4250` resolved and attach the complete bridge provenance set:

- `bridge/gtkb-hygiene-sweep-cli-004.md`
- `bridge/gtkb-hygiene-sweep-skill-008.md`
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md`
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the backlog reconciliation is implementation work and must be approved through a canonical bridge thread with `bridge/INDEX.md` as the operative queue state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specs for a KB-only lifecycle reconciliation and makes the approved mutation explicit.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries concrete `Project Authorization`, `Project`, and `Work Item` metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must include Specification-Derived Verification / spec-to-test mapping, command evidence, and observed results.
- `GOV-STANDING-BACKLOG-001` - the MemBase backlog is the governed cross-session work authority, so terminal lifecycle state must be reconciled when verified implementation evidence exists.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the new WI-specific PAUTH is the authorization envelope for this reconciliation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the implementation stays inside the declared project/work-item/target-path envelope.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this is an artifact lifecycle/status reconciliation, not source implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - verified implementation evidence must be reflected in the durable backlog artifact rather than left contradictory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this preserves one durable authority chain from owner decision to PAUTH to bridge proposal to implementation report.

## Prior Deliberations

- `DELIB-20262517` - owner authorization for the new WI-4250 PAUTH, recorded from Mike's 2026-06-12 Codex reply: "Authorize WI-4250 PAUTH".
- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` - project-scoped implementation authorization model; PAUTH does not bypass bridge review, target-path scoping, reports, or verification.
- `DELIB-20260630` - earlier owner authorization for WI-4250 Slice 2 documentation guidance; relevant implementation lineage, but not sufficient for this backlog-row reconciliation.
- `DELIB-20260621` - batch-2 stale-status reconciliation decision; explicitly treated WI-4250 as genuinely open at that time, so this proposal does not rely on it as authorization.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md` - VERIFIED child implementation evidence for the UTF-8 / module-entrypoint slice.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md` - VERIFIED child implementation evidence for fallback-guidance / regression-coverage slice.

## Owner Decisions / Input

Owner decision recorded as `DELIB-20262517`:

- Source ref: `AUQ-WI-4250-PAUTH-20260612`
- Owner answer: "Authorize WI-4250 PAUTH"
- Outcome: `owner_decision`
- Work item: `WI-4250`

This decision authorized only a narrow PAUTH for one-time `WI-4250` backlog lifecycle/linkage reconciliation. It did not authorize source, test, spec, hook, CLI, deploy, credential, or unrelated backlog mutation.

## Authorization Envelope

The revised authorization basis is:

- PAUTH: `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION`
- Status: `active`
- Project: `PROJECT-GTKB-DETERMINISTIC-SERVICES-001`
- Included work items: `["WI-4250"]`
- Allowed mutation classes: `["work_item_status_promotion"]`
- Forbidden operations: `["source", "test_addition", "spec_status_promotion", "hook_upgrade", "cli_extension", "deployment"]`
- Owner decision: `DELIB-20262517`

Dry-run creation evidence:

```text
python -m groundtruth_kb backlog authorize-implementation WI-4250 ... --dry-run --json
```

Observed result during revision drafting: dry-run proposed `DELIB-20262517` and `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION` without writing durable state.

Creation evidence:

```text
python -m groundtruth_kb backlog authorize-implementation WI-4250 ... --json
```

Observed result during revision drafting: created `DELIB-20262517` and active PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION`.

## Findings Addressed

### F1 - Blocking (P1): The cited PAUTH does not authorize the requested KB mutation

Response: corrected. The proposal no longer cites `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER` as the mutation authority. It cites the new owner-backed PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION`, whose only allowed mutation class is `work_item_status_promotion` and whose only included work item is `WI-4250`.

### F2 - Blocking (P1): The proposal fails the mandatory spec-to-test clause gate

Response: corrected. This revision adds an explicit Specification-Derived Verification / spec-to-test evidence plan with command evidence and observed-result requirements. It includes:

- dry-run of the exact future `python -m groundtruth_kb backlog resolve WI-4250 ... --dry-run --json` command;
- actual apply command only after GO and implementation authorization;
- post-apply `python -m groundtruth_kb backlog show WI-4250 --json` read-back;
- `python -m pytest platform_tests\cli\test_backlog_update_title_desc.py platform_tests\scripts\test_cli_backlog_authorize_implementation.py -q --tb=short` regression evidence.

During revision drafting, the pytest anchor already passed: 22 passed in 5.63s.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4250` defines the portability and UTF-8 regression coverage closure condition, and the two verified child bridge threads provide the terminal implementation evidence. The only remaining work is a governed lifecycle reconciliation of the backlog row to the verified bridge record.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | KB-only reconciliation; no credentials or copied secrets in scope. | CLI output review and credential-scanned bridge filing. | |
| CQ-PATHS-001 | Yes | Limit mutation to `groundtruth.db`; use governed CLI rather than direct SQLite. | Target-path review plus row read-back. | |
| CQ-COMPLEXITY-001 | Yes | Use existing `backlog resolve` command; no new service logic. | Dry-run/apply/read-back evidence. | |
| CQ-CONSTANTS-001 | Yes | Reuse existing WI id, PAUTH id, project id, and verified bridge ids verbatim. | Post-change row read-back. | |
| CQ-SECURITY-001 | Yes | No network calls or external side effects beyond one approved KB row update. | Local-only verification commands. | |
| CQ-DOCS-001 | Yes | Record the reconciliation through the bridge thread and `status_detail`. | Implementation report and row read-back. | |
| CQ-TESTS-001 | Yes | Use CLI dry-run/read-back plus existing pytest regression anchor for backlog update/authorization surfaces. | Commands in the verification plan. | |
| CQ-LOGGING-001 | Yes | No runtime logging changes. | Source scope inspection: no source edits. | |
| CQ-VERIFICATION-001 | Yes | Require observed results for dry-run, apply, read-back, and regression anchor. | Implementation report must carry exact command results. | |

## Files Expected To Change

| Path | Status | Purpose |
|---|---|---|
| `groundtruth.db` | modified | Append a new `WI-4250` work-item version with terminal lifecycle/linkage reconciliation. |

No source, test, config, rule, hook, CLI, or deployment file is expected to change during implementation.

## Specification-Derived Verification Plan

| Specification / surface | Command evidence required in implementation report | Expected observed result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-wi-4250-backlog-reconciliation --format json --preview-lines 80` | Thread files and `bridge/INDEX.md` agree; no drift before implementation report filing. |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-4250 --json` before and after apply | Before: `resolution_status` is `open`, `stage` is `backlogged`; after: both are `resolved`, and `status_detail` cites the verified bridge evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `python -m groundtruth_kb projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` | Active PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION` includes only `WI-4250` and allows only `work_item_status_promotion`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests\cli\test_backlog_update_title_desc.py platform_tests\scripts\test_cli_backlog_authorize_implementation.py -q --tb=short` | Existing backlog update/resolve and authorization regression suites pass; revision drafting observed 22 passed in 5.63s. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `python -m groundtruth_kb backlog resolve WI-4250 --related-bridge-threads '["bridge/gtkb-hygiene-sweep-cli-004.md", "bridge/gtkb-hygiene-sweep-skill-008.md", "bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md", "bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md"]' --status-detail "Resolved by verified WI-4250 implementation evidence: UTF-8 portability slice 1 VERIFIED at bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md and slice 2 guidance VERIFIED at bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md; reconciled under PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION." --owner-approved --change-reason "Resolve WI-4250 stale backlog row under GO for gtkb-wi-4250-backlog-reconciliation and PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION." --dry-run --json` | Dry-run reports `updated: false`, `dry_run: true`, and only the intended `resolution_status`, `stage`, `related_bridge_threads`, and `status_detail` fields. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Same command without `--dry-run`, followed by read-back and implementation report | One durable artifact chain: owner decision -> PAUTH -> GO -> backlog row update -> implementation report -> LO verification. |

## Implementation Command

After GO and implementation authorization, run the dry-run command above, then run the same command without `--dry-run` if the dry-run output matches the expected field set.

The dry-run already passed during this revision draft:

```json
{
  "dry_run": true,
  "fields": {
    "related_bridge_threads": "[\"bridge/gtkb-hygiene-sweep-cli-004.md\", \"bridge/gtkb-hygiene-sweep-skill-008.md\", \"bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md\", \"bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md\"]",
    "resolution_status": "resolved",
    "stage": "resolved",
    "status_detail": "Resolved by verified WI-4250 implementation evidence: UTF-8 portability slice 1 VERIFIED at bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md and slice 2 guidance VERIFIED at bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-005.md; reconciled under PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION."
  },
  "updated": false,
  "work_item_id": "WI-4250"
}
```

## Risk / Rollback

Risk is low because the implementation is one governed backlog row update. The main failure mode is incorrect provenance linkage or status detail. Mitigation: preserve the existing related bridge threads and append the two verified WI-4250 child threads; use `backlog resolve --dry-run --json` before apply; verify exact read-back after apply.

Rollback is one inverse `backlog update` restoring the pre-change `resolution_status`, `stage`, `related_bridge_threads`, and `status_detail` values if the read-back does not match the approved reconciliation.

## Bridge Filing (INDEX-Canonical)

This REVISED proposal is filed under `bridge/` and inserted into the existing `gtkb-wi-4250-backlog-reconciliation` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten. `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`fix` - this repairs contradictory durable backlog state without changing the implemented feature surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
