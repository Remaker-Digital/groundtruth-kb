GO

author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 2026-06-22T20-25-18Z-loyal-opposition-A-c7bc2b
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex bridge auto-dispatch; approval_policy=never; workspace=E:\GT-KB
author_metadata_source: bridge auto-dispatch prompt plus canonical harness role reader

# Loyal Opposition GO Verdict - Orphan WI Per-Item Retire/Exclude Service

bridge_kind: lo_verdict
Document: gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
Version: 004
Date: 2026-06-22 UTC
Responds to: bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-003.md
Reviewed by: loyal-opposition/codex
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3464
status: GO

## Verdict

GO.

The revised proposal resolves both blockers from `bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-002.md`.
It strengthens the approval-packet gate so a merely valid packet is insufficient, and it narrows the bridge slice to the service, CLI, and tests that are actually listed in `target_paths`.

This GO authorizes only the three-file implementation scope in version 003:

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_projects_cli.py`

It does not authorize a canonical live drain of `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json`, a data-migration PAUTH execution, a `groundtruth.db` mutation, or edits to `scripts/resolve_orphan_wi_memberships.py`. Those remain follow-on work after this service/CLI surface is verified.

## First-Line Role Eligibility Check

- Canonical role command executed: `groundtruth-kb/.venv/Scripts/gt.exe harness roles`.
- `harness-state/harness-identities.json` maps Codex to durable harness ID `A`.
- The canonical role projection reports harness `A` is assigned `loyal-opposition`.
- Live latest bridge status before this verdict: `REVISED` at `bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-003.md`.
- Status authored here: `GO`.
- Eligibility result: Loyal Opposition is authorized to issue `GO` verdicts for latest `REVISED` implementation proposals.

## Review Independence

- Proposal author: `prime-builder/codex-automation`, harness `A`, session `019ef094-6d42-7541-a32f-0ae73d233921`.
- Reviewer context: `2026-06-22T20-25-18Z-loyal-opposition-A-c7bc2b`.
- Result: same harness ID, unrelated session contexts. The bridge rule permits same-harness review when author and reviewer sessions are unrelated and the reviewer is operating under a valid Loyal Opposition dispatch context.

## Prior Deliberations

- `DELIB-2509` - owner decision selecting "Per-WI PAUTH + assign-only scope" for the parent orphan-WI backfill driver and explicitly deferring retire/exclude execution to a follow-on slice.
- `DELIB-20265542` - prior Loyal Opposition NO-GO on this thread. Findings required exact approval-packet binding and removal or explicit deferral of the deferred-action drain claim.
- `DELIB-20261480` / `DELIB-2633` - orphan-WI membership backfill Slice 2 review context that surfaced the absent per-WI retire/exclude lifecycle surface.
- `DELIB-20261477` / `DELIB-2630` - prior Slice 2 verification context confirming deferred-action records remained intact for follow-on consumption.
- `DELIB-20260745` and `DELIB-20261322` - `gt projects remove-item` review precedent for append-only non-active project membership transitions and the non-active-status invariant.
- `DELIB-20265457` - owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch that includes WI-3464.

Deliberation search executed:

```powershell
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli deliberations search "WI-3464 orphan WI retire exclude ProjectLifecycleService retire-item approval packet" --limit 10
```

## Applicability Preflight

Command:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:a01436ec85feff7e0e7b3c56588e9f27034cdfe04cace0834dc1294eb0e5eb27`
- bridge_document_name: `gtkb-orphan-wi-backfill-per-wi-retire-exclude-service`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-003.md`
- operative_file: `bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
```

Result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-orphan-wi-backfill-per-wi-retire-exclude-service`
- Operative file: `bridge\gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-003.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Review Findings

No blocking findings remain.

### Confirmation 1 - Exact Approval-Packet Binding Is Now Required

Severity: P0 resolved.

Evidence:

- The prior NO-GO finding P1-001 required the approval evidence to bind to the exact project, work item, retire/exclude action, and requested non-active status.
- Version 003 requires `retire_project_work_item()` to parse the packet path, resolve it in-root, validate it, and then confirm exact `project_id`, exact `work_item_id`, exact lifecycle action, and exact requested non-active status.
- Version 003 also requires negative tests for different project, different work item, wrong action/status, missing packet, malformed packet, schema-invalid packet, and out-of-root packet, all without membership mutation.
- Live source inspection confirms the existing packet helper has `parse_packet_path_from_change_reason()`, `validate_packet()`, and the precedent helper `packet_covers_amendment()` for deterministic packet-content binding. The proposal's requested coverage helper is therefore implementable within the approved `lifecycle.py` and test surface.

Impact:

The governed retirement/exclusion surface will fail closed on generic or mismatched approval packets instead of treating a structurally valid packet as universal authority.

### Confirmation 2 - Deferred-Action Drain Claim Is No Longer In Scope

Severity: P0 resolved.

Evidence:

- The prior NO-GO finding P1-002 required the proposal either to include the deferred-action drain path and tests or to narrow the claim to service/CLI only.
- Version 003 narrows scope to `ProjectLifecycleService.retire_project_work_item()`, `gt projects retire-item`, and focused CLI tests.
- Version 003 explicitly excludes canonical live drain of `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json`, data-migration PAUTH execution, `groundtruth.db` mutation, and `scripts/resolve_orphan_wi_memberships.py` edits.
- The target path list is exactly the three files needed for that narrower service/CLI/test slice.

Impact:

The implementation can be verified without falsely claiming that the deferred-action backlog has been consumed or that WI-3464 is fully complete.

## Verification Expectations For Prime Builder

The post-implementation report must preserve this GO's narrowed scope. In particular:

- Report source/test changes only under the three approved target paths.
- Include exact-packet-match positive and mismatch negative tests.
- Show that no `groundtruth.db`, deferred-actions artifact, or drain script was mutated by this slice.
- Keep WI-3464 open, or otherwise avoid claiming full WI completion, until a follow-on bridge item handles the deferred-action drain and data-migration PAUTH work.

Expected evidence commands from the proposal are appropriate:

```powershell
python -m pytest platform_tests\scripts\test_projects_cli.py -q --tb=short
python -m ruff check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
python -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
git diff --name-only -- groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py scripts\resolve_orphan_wi_memberships.py groundtruth.db
```

## Methodology

Commands and inspections used:

```powershell
Get-Content -Path E:/GT-KB/.codex/skills/bridge/SKILL.md
Get-Content -Path harness-state/harness-identities.json
groundtruth-kb/.venv/Scripts/gt.exe harness roles
Get-Content -Path .claude/rules/file-bridge-protocol.md
Get-Content -Path .claude/rules/codex-review-gate.md
Get-Content -Path .claude/rules/deliberation-protocol.md
Get-Content -Path .claude/rules/loyal-opposition.md
Get-Content -Path .claude/rules/operating-model.md
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch health
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-orphan-wi-backfill-per-wi-retire-exclude-service --format json --preview-lines 400
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli deliberations search "WI-3464 orphan WI retire exclude ProjectLifecycleService retire-item approval packet" --limit 10
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli deliberations show DELIB-2509 --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli deliberations show DELIB-20265542 --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli backlog show WI-3464 --json
rg -n "retire_project_work_item|remove_project_item|approval_packet|parse_packet_path|validate_packet|retire-item|projects_remove_item|link_project_work_item" groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_projects_cli.py groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py
```

## Owner Action Required

None. This GO authorizes Prime Builder implementation within the narrowed target path scope above.

File bridge scan contribution: 1 selected eligible entry processed. The selected WI-4761 entry was not processed here because it became stale during this dispatch; its latest status is now `NO-GO` at `bridge/gtkb-wi4761-restore-ci-testing-integration-health-006.md`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
