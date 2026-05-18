REVISED

# Implementation Report - W1 Retirement-Machinery Correction (GTKB-GOVERNANCE-CORRECTION-S358-W1)

bridge_kind: implementation_report
Document: gtkb-s358-w1-retirement-machinery-correction
Version: 014
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3365

target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "scripts/project_verified_completion_scanner.py", ".claude/hooks/project-completion-surface.py", ".codex/gtkb-hooks/project-completion-surface.py", ".claude/settings.json", ".codex/hooks.json", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/hooks/test_project_completion_surface.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", ".groundtruth/formal-artifact-approvals/*-gov-project-verified-completion-retirement-001.json", ".groundtruth/formal-artifact-approvals/*-delib-s358-s350-manufactured-variant-provenance.json"]

## Revision Note

Version 014 (REVISED) supersedes the `-013` NO-GO. The `-013` verdict confirmed the `-012` package-availability remediation is correct: the in-root `groundtruth-kb/.venv` now has `pytest` 9.0.2, `ruff` 0.15.5, `pytest-asyncio` 1.3.0, and `pytest-timeout` 2.4.0; `ruff` passes; and the 30-test suite passes from the Codex auto-dispatch shell when the temp root is in-root. The sole remaining blocker was `-013` FINDING-F1 (P2): the `-012` command surface did not set an in-root temp root, so pytest's scratch directory resolved to the default Windows per-user temp location under the user profile, which the Codex auto-dispatch sandbox reports as access-denied, and all 30 tests errored at setup with `PermissionError: [WinError 5]`. `-014` updates the documented verification command surface to create a fresh, uniquely-named in-root temporary directory per run and point `TMP`/`TEMP` at it (see `## F2 Remediation`), and refreshes the executed-command evidence. `-014` makes no source, test, configuration, hook, or MemBase change: the `-012`/`-010` F1 collective-retirement remediation, the IP-1 through IP-8 implementation, and the passing bridge preflights are all preserved unchanged.

Version 012 (REVISED) supersaded the `-011` NO-GO. The `-011` verdict confirmed the F1 collective work-item retirement remediation is correct by runtime smoke and confirmed both mandatory bridge preflights pass on the `-010` operative file. The sole `-011` blocker was FINDING-F1 (P2): the `-010` verification command surface ran `C:\Python314\python.exe`, whose `pytest`/`ruff` resolve from a per-user site-packages location the Codex auto-dispatch sandbox cannot read. `-012` replaced that command surface with an in-root, network-free environment - the in-root `groundtruth-kb/.venv` provisioned with `pytest`, `ruff`, `pytest-asyncio`, and `pytest-timeout`.

Version 010 (REVISED) superseded `-009`. The `-009` `## F2 Remediation` section quoted a literal Windows per-user site-packages filesystem path (a path under the user profile directory). The mandatory `adr_dcl_clause_preflight.py` `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` detector flags any user-profile path token as an out-of-root output-path reference and failed the gate (exit 5) on `-009`. That was a false positive - the quoted path was a diagnostic tool-install location, not a GT-KB artifact output path - but `-010` removed the literal token and describes the per-user site-packages location in prose so the mandatory clause preflight passes.

Version 009 (REVISED) responded to the `-008` NO-GO on the `-007` post-implementation report. The `-008` verdict raised two findings:

- FINDING-F1 (P1): the implementation completed the project authorization and retired the project, but did not perform the collective work-item retirement clause of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001.
- FINDING-F2 (P2): the `-007` report's pytest/ruff commands were not reproducible in the Codex auto-dispatch environment.

`-009` implemented collective work-item retirement (see `## F1 Remediation`), extended the spec-derived tests with three covering tests, and updated the spec-to-test mapping. IP-1 through IP-8 were carried forward from `-007` unchanged.

## Summary

Post-implementation report for the W1 retirement-machinery correction, implementing the `-005` proposal under Codex GO at `-006`. All eight implementation points (IP-1 through IP-8) are complete, and the `-008` FINDING-F1 collective-retirement gap is remediated.

The live project-completion and retirement machinery now matches GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001: completion is automatic on the all-membership-linked-work-items-VERIFIED condition with no owner-confirmation gate, and retirement is collective - when a project's sole active authorization completes, the project, its associated VERIFIED work items, and their project membership links all retire together. The historical record is corrected (GOV v3), the provenance of the S350 manufactured-variant error is archived, and PROJECT-GTKB-LO-OPPORTUNITY-RADAR is retired.

## Specification Links

- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 - the primary governing specification. W1 implemented machinery, a historical-record correction (v3), and a project retirement so the platform faithfully enforces the rule. The F1 remediation implements the rule's collective work-item retirement clause.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 - the GOV rule's owner-AUQ boundary cites this: owner-AUQ gates project start, not completion. W1 stripped only the completion-side gate and left the start-side authorization workflow intact.
- GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 - cited alongside the implementation-authorization spec for the project-start owner-AUQ boundary; W1 did not change project start.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this report is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries a complete, relevance-closed Specification Links section and every protected mutation surface is in target_paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - this report carries a spec-to-test mapping with executed verification evidence below, including the F1 collective-retirement tests.
- GOV-ARTIFACT-APPROVAL-001 - the v3 GOV spec and the provenance deliberation are formal artifacts; each MemBase mutation was gated by a formal-artifact-approval packet presented to and approved by the owner before insertion.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline was applied to the v3 GOV spec and the provenance deliberation.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the formal-artifact-approval gate hook enforced the packet requirement on the GOV v3 and the deliberation insert; both inserts ran with a validated packet referenced via GTKB_FORMAL_APPROVAL_PACKET.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this report carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all changed files are in-root; no application path under applications/ was touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: WI-3365, the proposal chain, the v3 GOV spec, the provenance deliberation, the updated tests, and this report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, tests, GOV v3, deliberation, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3365 moves through open, in-progress, and verified lifecycle states.
- SPEC-AUQ-POLICY-ENGINE-001 - W1 removed the project-completion owner-AUQ gate; this does not weaken AUQ enforcement for any decision class that still requires it. Project completion and collective retirement are not owner-decision points per the GOV rule.

## Prior Deliberations

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation authorizing the combined governance-correction project; records the W1 scope item by item. This report implements the W1 workstream.
- DELIB-S353-LO-OPPORTUNITY-RADAR-PROJECT-COMPLETION-2026-05-15 - the S353 keep-open choice for PROJECT-GTKB-LO-OPPORTUNITY-RADAR; IP-6 retired that project under the explicit DELIB-S358 supersession.
- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 supersession record - v2's own description records the v1-to-v2 supersession; IP-7's v3 builds on it by re-framing v1 accurately as a Prime Builder error.
- DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE - the provenance deliberation created by IP-8 of this workstream; archives the chain by which the S350 manufactured-variant AskUserQuestion produced the incorrect v1.

## Owner Decisions / Input

- 2026-05-17, S357: the owner directed superseding GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 via a v2 (v1 preserved append-only), approved v2 as written, and folded the v1-record correction and the machinery correction into one combined project. Captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION.
- 2026-05-17, S358: the owner directed standing up and running the combined governance-correction project; the W1 scope items are enumerated in DELIB-S358; W1-W4 sequencing was collected via AskUserQuestion.
- 2026-05-17, S358: the owner directed retiring PROJECT-GTKB-LO-OPPORTUNITY-RADAR (DELIB-S358 decision 4), superseding the DELIB-S353 keep-open choice.
- 2026-05-18, S358: the owner directed filing the `-005` REVISED to bring `platform_tests/scripts/test_project_verified_completion_scanner.py` into W1 scope after Prime Builder self-detected FINDING-F3. Collected via AskUserQuestion.
- 2026-05-18, S358: the owner approved GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v3 (IP-7) as drafted, after full native-format presentation. Collected via AskUserQuestion. Recorded in approval packet `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`.
- 2026-05-18, S358: the owner approved DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE (IP-8) as drafted, after full native-format presentation. Collected via AskUserQuestion. Recorded in approval packet `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json`.
- The `-008` NO-GO introduced no new owner decision. Per the `-008` verdict's "Owner Action Required: None", the F1 collective-retirement gap is a Prime Builder revision requirement; this report implements the GOV rule's collective work-item retirement language as written.
- The `-011` NO-GO likewise introduced no new owner decision. Per the `-011` verdict's "Owner Action Required: None", the command-surface reproducibility blocker is a Prime Builder revision requirement, addressed in `## F2 Remediation`.
- The `-013` NO-GO likewise introduced no new owner decision. Per the `-013` verdict's "Owner Action Required: None", the command-surface temp-root reproducibility blocker is a Prime Builder report-revision requirement, addressed in `## F2 Remediation`.

## Implemented Changes

### IP-1: Owner-confirmation gate stripped from complete_project_authorization()

`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`: the owner-confirmation gate (former Step 2) is removed from `complete_project_authorization()`; the mandatory `owner_decision_deliberation_id` parameter is dropped; the docstring states the automatic model. The function retains the load-active-authorization step, the readiness check, the status transition, and the sole-active retirement step. `import json` is removed (the removed gate was its only consumer).

### IP-2: Work-item gating set reconciled to the membership-link definition

`lifecycle.py`: the static `_authorization_work_item_ids()` is replaced by `_project_membership_work_item_ids(project_id)`, which returns the project's active project-to-work-item membership-link work items via `db.list_project_work_items()`. `scripts/project_verified_completion_scanner.py`: the scanner's `_included_work_item_ids()` is likewise replaced by `_project_membership_work_item_ids(db, project_id)`. Scanner and lifecycle service agree byte-for-byte on the gating definition.

### IP-3: Automatic-transition path added; surface hook pair repurposed

`lifecycle.py`: a new deterministic service method `auto_complete_ready_authorizations()` scans active authorizations and auto-completes every completion-ready one via the stripped `complete_project_authorization()`. It is idempotent. `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` are repurposed from owner-confirmation advisory to automatic-transition trigger plus notification; the two hook files remain byte-identical. `.codex/hooks.json`: the `project-completion-surface.py` registration `statusMessage` is corrected. `.claude/settings.json` requires no W1 change. The F1 remediation below extends this IP-3 automatic-transition path so retirement is collective.

### IP-4: gt projects complete-authorization CLI subcommand

`groundtruth-kb/src/groundtruth_kb/cli.py`: a `complete-authorization` subcommand is added to the `gt projects` group. It invokes the stripped `complete_project_authorization()` for an explicitly named authorization and does not gate on an owner decision.

### IP-5: Covering tests updated

`groundtruth-kb/tests/test_project_artifacts.py`: the five v1 owner-confirmation-gate tests are deleted; the completion/retirement tests are re-signatured to the stripped function signature and the membership-link gating set; new tests cover the automatic-transition path, the membership-link gating set, the scanner gating-set parity, and the `gt projects complete-authorization` CLI subcommand. `platform_tests/hooks/test_project_completion_surface.py`: the hook tests are rewritten to the repurposed automatic-transition-plus-notification behavior. `platform_tests/scripts/test_project_verified_completion_scanner.py` (FINDING-F3): the seed helper and tests are re-signatured to the membership-link gating model.

### IP-6: PROJECT-GTKB-LO-OPPORTUNITY-RADAR retired

`PROJECT-GTKB-LO-OPPORTUNITY-RADAR` is retired in MemBase via the project-lifecycle retirement path (v3 active -> v4 retired). The `change_reason` cites DELIB-S358 decision 4 and this bridge thread.

### IP-7: GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v3 inserted

An append-only v3 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 is inserted into MemBase. v3 preserves the v2 behavioral rule byte-identically and rewrites only the Supersession paragraph to frame v1 accurately as a Prime Builder manufactured-variant error. The owner approved the v3 content as drafted (AskUserQuestion, 2026-05-18); the insert ran under a validated formal-artifact-approval packet.

### IP-8: DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE archived

A Deliberation Archive record capturing the provenance of the S350 manufactured-variant error is inserted into MemBase (`source_type=bridge_thread`, `outcome=informational`, linked to GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 and WI-3365). The owner approved the content as drafted (AskUserQuestion, 2026-05-18); the insert ran under a validated formal-artifact-approval packet.

## F1 Remediation: Collective Work-Item Retirement

The `-008` NO-GO FINDING-F1 established that `complete_project_authorization()` completed the authorization and retired the project but left the associated VERIFIED work items and their membership links active - the GOV rule's "retirement is collective: the project and its VERIFIED work items retire together" clause was unimplemented. This revision closes that gap in `lifecycle.py`:

- A new helper `_retire_project_work_items(project_id, *, completed_authorization_id, changed_by)` is added. When invoked, it iterates the retiring project's active membership-linked work items and, for each: (a) retires this project's membership link by writing a new membership version with `status="retired"` (non-active, so the link drops out of the active project-to-work-item set while remaining on the append-only record); (b) transitions the work item to `resolution_status="retired"` via `db.update_work_item()`.
- A new helper `_work_item_in_other_active_project(work_item_id, exclude_project_id)` implements the shared-work-item rule: it returns True when the work item has an active membership link in some non-terminal project other than the retiring one. When True, `_retire_project_work_items()` retires only the retiring project's membership link and leaves the work item active for its other project(s). This is the safe shared-work-item shape the `-008` verdict prescribed.
- `complete_project_authorization()` Step 4 now calls `_retire_project_work_items()` immediately after `retire_project()` when the project is retired (sole-active-authorization case), and returns the new `retired_work_items` list alongside `authorization` and `project_retired`.
- `auto_complete_ready_authorizations()` carries the `retired_work_items` list into each per-authorization result dict, so the automatic-transition hook path also performs and reports collective retirement.

Design note: collective retirement changes only the work item's `resolution_status` (to `retired`, a member of `WORK_ITEM_TERMINAL_RESOLUTION_STATUSES`). It deliberately does not change the work item's `stage` field. Moving `stage` to `resolved` would trip the GOV-15 owner-approval gate in `db._validate_stage_transition()` (`run_pre_resolve_work_item`), and GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 makes completion and collective retirement automatic with no owner AskUserQuestion. Setting `resolution_status` only keeps automatic collective retirement gate-clean. `"retired"` is a valid terminal `resolution_status` per `db.WORK_ITEM_TERMINAL_RESOLUTION_STATUSES = ("verified", "resolved", "retired", "wont_fix", "not_a_defect")`.

## F2 Remediation: Reproducible Command Surface

`-011` FINDING-F1 (P2) recorded that the `-010` verification command surface was not reproducible in the Codex auto-dispatch environment. `-012` provisioned the in-root `groundtruth-kb/.venv` with `pytest`, `ruff`, `pytest-asyncio`, and `pytest-timeout`. The `-013` NO-GO confirmed that package-availability remediation is correct - the in-root venv has the tools, `ruff` passes, and the 30-test suite passes from the Codex shell with an in-root temp root - but found one remaining defect: the `-012` command surface omitted the temp-root environment. Pytest derives its scratch directory from `TMP`/`TEMP`; with the default Windows per-user temp location (under the user profile's AppData tree), pytest's `pytest-of-<user>` directory is access-denied from the Codex auto-dispatch sandbox, and all 30 tests error before setup with `PermissionError: [WinError 5]`.

`-014` resolves this. The verification command surface now creates a fresh, uniquely-named in-root temporary directory and points `TMP` and `TEMP` at it before running pytest:

- The directory is created under the in-root scratch root `E:\GT-KB\.tmp`, which is under the GT-KB project root and is writable by each harness.
- A fresh per-run directory is used rather than a fixed shared one because `E:\GT-KB\.tmp` is shared across more than one AI harness. Pytest's temp root is `<TMP>/pytest-of-<username>` - keyed on the username, not the process - so the first harness to run creates `pytest-of-micha`, and a second harness running under a different sandbox security context is then ACL-denied on that directory (observed directly during `-014` preparation: `Access is denied: E:\GT-KB\.tmp\pytest-of-micha`). A fresh uniquely-named directory per invocation (`E:\GT-KB\.tmp\w1-pytest-<guid>`) eliminates the collision: each run owns its own temp root. This is the "equivalent in-root temp-root mechanism" the `-013` NO-GO authorized in place of a bare `TMP`/`TEMP` setting.
- No network access and no per-user profile path is involved; every input - interpreter, packages, and temp root - is in-root.

The exact runnable command surface and observed results are in the Specification-Derived Verification section below. This command-surface change is the only difference between `-014` and `-012`. No source, test, configuration, hook, or MemBase artifact is changed; the F1 collective-retirement remediation, the IP-1 through IP-8 implementation, and the two passing bridge preflights are carried forward from `-012`/`-010` unchanged.

## Specification-Derived Verification

| Specification | Behavior verified | Test / verification | Result |
|---|---|---|---|
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | completion succeeds with no owner_decision_deliberation_id and no owner-confirmation gate | test_project_artifacts.py::test_complete_succeeds_without_owner_decision | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | non-active authorization and unverified-work-item rejection still apply | test_project_artifacts.py::test_complete_rejects_non_active_authorization, ::test_complete_rejects_when_a_wi_not_verified | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | the gating set is the project's membership-linked work items, not included_work_item_ids | test_project_artifacts.py::test_complete_rejects_when_project_has_no_membership_links, ::test_complete_gating_set_is_membership_links_not_included_ids, ::test_scanner_gating_set_uses_membership_links | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | scanner gates on membership links (dedicated test file, FINDING-F3) | test_project_verified_completion_scanner.py (4 tests) | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | sole-active completion retires the project; other-active keeps it active | test_project_artifacts.py::test_complete_sole_active_authorization_retires_project, ::test_complete_with_other_active_authorization_keeps_project_active | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (FINDING-F1: collective retirement) | project retirement collectively retires the associated membership-linked work items (resolution_status=retired) and retires the membership links | test_project_artifacts.py::test_complete_retires_membership_linked_work_items | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (FINDING-F1: shared work item) | a work item also linked to another non-terminal project is left active; only the retiring project's membership link retires | test_project_artifacts.py::test_complete_shared_work_item_is_not_retired | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 (FINDING-F1: auto-transition path) | auto_complete_ready_authorizations() applies collective retirement and reports retired work items | test_project_artifacts.py::test_auto_complete_retires_membership_linked_work_items | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | auto_complete_ready_authorizations() auto-completes and auto-retires, idempotently, with no owner AUQ | test_project_artifacts.py::test_auto_complete_ready_authorizations_completes_and_retires, ::test_auto_complete_is_idempotent, ::test_auto_complete_skips_unready_authorization | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | the surface hook triggers the automatic transition and emits a notification with no AskUserQuestion instruction | test_project_completion_surface.py (4 tests) | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | the gt projects complete-authorization CLI subcommand invokes the stripped completion path | test_project_artifacts.py::test_projects_complete_authorization_cli | PASS |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | project start is unchanged - the existing project-schema and authorization tests still pass | test_project_artifacts.py (7 project-schema/CLI tests retained) | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries the spec-to-test mapping with executed commands and observed results | this section | PASS |
| GOV-ARTIFACT-APPROVAL-001 | the GOV v3 and the provenance deliberation each carry a validated formal-artifact-approval packet | see Formal-Artifact-Approval Packet Evidence | PASS |

Executed commands and observed results (in-root `groundtruth-kb/.venv` environment with a fresh per-run in-root temp root - see `## F2 Remediation`; run from the GT-KB project root in PowerShell):

    $bt = Join-Path 'E:\GT-KB\.tmp' ("w1-pytest-" + [System.Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $bt -Force | Out-Null
    $env:TMP = $bt
    $env:TEMP = $bt
    groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_project_artifacts.py platform_tests/hooks/test_project_completion_surface.py platform_tests/scripts/test_project_verified_completion_scanner.py -q --tb=short
    groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/tests/test_project_artifacts.py

- The pytest command -> `30 passed in 6.76s` (exit 0). Breakdown: test_project_artifacts.py 22 (7 retained project-schema/CLI + 12 completion/retirement + 3 F1 collective-retirement), test_project_completion_surface.py 4, test_project_verified_completion_scanner.py 4.
- The ruff command -> `All checks passed!` (exit 0).
- The `-013` NO-GO independently reran the suite from the Codex auto-dispatch shell with an in-root temp root and observed `30 passed, 1 warning in 6.21s`. The single warning is an environment-dependent optional-dependency `DeprecationWarning`; it does not fire in `groundtruth-kb/.venv`, which lacks the optional `chromadb` (`search` extra). The 30-test pass set is identical.

## MemBase Evidence (IP-6 / IP-7 / IP-8)

- IP-6: `db.get_project('PROJECT-GTKB-LO-OPPORTUNITY-RADAR')` -> `status=retired version=4`.
- IP-7: `db.get_spec('GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001')` -> `version=3 status=specified type=governance`.
- IP-8: `db.get_deliberation('DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE')` -> present, `version=1 source_type=bridge_thread outcome=informational`.

## Formal-Artifact-Approval Packet Evidence (IP-7 / IP-8)

- IP-7 packet: `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`, `artifact_type=governance`, `action=update`, `approval_mode=approve`, `approved_by=owner`, `full_content_sha256=c9eded0438902c2d38c8fe5c14d43b8d3ce2269dd39c7348f30a27f390a4803d`. The `-008` and `-013` verdicts independently confirmed this packet hash matches the GOV v3 MemBase `description`.
- IP-8 packet: `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json`, `artifact_type=deliberation`, `action=insert`, `approval_mode=approve`, `approved_by=owner`, `full_content_sha256=f0dfde89aa89e7e13132bd8ca03fba4a2b4b39b549ab32c9b5087067fb52e386`. The `-008` and `-013` verdicts independently confirmed this packet hash matches the deliberation MemBase `content`.

## Hook Pair Byte-Identity

`.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` are byte-identical after the IP-3 repurposing: both files SHA-256 `292fb73230da7c200c5a048798e49717433fc17bd1dffee6a5c5e072043139cc` (ADR-CODEX-HOOK-PARITY-FALLBACK-001 parity). `-014` changes neither hook file.

## Bridge Preflights

Both mandatory bridge preflights are run on this `-014` operative file after its INDEX entry is filed:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w1-retirement-machinery-correction` - expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w1-retirement-machinery-correction` - expected exit 0, 0 blocking gaps.

`-011` and `-013` independently confirmed both preflights pass on `-012`. `-014` changes only the `## Revision Note`, `## Owner Decisions / Input`, `## F2 Remediation`, and executed-command lines; the only new path tokens are the in-root `E:\GT-KB\.tmp` temp-root paths, and no user-profile path literal is introduced, so applicability and clause results are unchanged.

Loyal Opposition reproduces the full preflight tables in the VERIFIED verdict per the file-bridge-protocol Mandatory Applicability Preflight Gate.

## Recommended Commit Type

`fix` - W1 repairs project-completion/retirement machinery that diverged from its governing specification. The F1 remediation completes the collective-retirement behavior the GOV rule already mandates; the new `_retire_project_work_items()` / `_work_item_in_other_active_project()` helpers are internal completions of that mandated behavior, not a new external product capability. The GOV v3 and the provenance deliberation are historical-record corrections. `-014` adds no code change and does not alter the recommended type.

## Files Changed

W1 source / test / config files:
- groundtruth-kb/src/groundtruth_kb/project/lifecycle.py (IP-1, IP-2, IP-3; F1 remediation - `_retire_project_work_items()`, `_work_item_in_other_active_project()`, Step 4 collective retirement, `auto_complete_ready_authorizations()` result)
- scripts/project_verified_completion_scanner.py (IP-2)
- .claude/hooks/project-completion-surface.py (IP-3)
- .codex/gtkb-hooks/project-completion-surface.py (IP-3)
- .codex/hooks.json (IP-3 - the project-completion-surface.py statusMessage hunk only)
- groundtruth-kb/src/groundtruth_kb/cli.py (IP-4)
- groundtruth-kb/tests/test_project_artifacts.py (IP-5; F1 remediation - 3 new collective-retirement tests)
- platform_tests/hooks/test_project_completion_surface.py (IP-5)
- platform_tests/scripts/test_project_verified_completion_scanner.py (IP-5)

MemBase + approval packets:
- groundtruth.db (IP-6 project retirement, IP-7 GOV v3 insert, IP-8 deliberation insert)
- .groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json (IP-7)
- .groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json (IP-8)

Bridge:
- bridge/gtkb-s358-w1-retirement-machinery-correction-005.md, -006.md, -007.md, -008.md, -009.md, -010.md, -011.md, -012.md, -013.md, -014.md
- bridge/INDEX.md (W1 entry)

Commit-scope note: `.claude/settings.json` is in the proposal target_paths but W1 makes no change to it. The working tree's `.claude/settings.json` diff and the non-`statusMessage` portion of the `.codex/hooks.json` diff are unrelated parallel-session changes; the W1 commit excludes `.claude/settings.json` entirely and stages only the `project-completion-surface.py` statusMessage hunk of `.codex/hooks.json` (via `git add -p`; never `git add -A`). The `-012` command-surface remediation provisioned the gitignored in-root `groundtruth-kb/.venv` environment, and `-014` verification used a gitignored in-root directory under `E:\GT-KB\.tmp`; neither is part of the W1 commit. The W1 commit type is `fix`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
