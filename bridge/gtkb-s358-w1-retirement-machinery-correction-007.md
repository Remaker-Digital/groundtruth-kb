NEW

# Implementation Report - W1 Retirement-Machinery Correction (GTKB-GOVERNANCE-CORRECTION-S358-W1)

bridge_kind: implementation_report
Document: gtkb-s358-w1-retirement-machinery-correction
Version: 007
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-CORRECTION-S358-S358-COMBINED-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION
Project: PROJECT-GTKB-GOVERNANCE-CORRECTION-S358
Work Item: WI-3365

target_paths: ["groundtruth.db", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "scripts/project_verified_completion_scanner.py", ".claude/hooks/project-completion-surface.py", ".codex/gtkb-hooks/project-completion-surface.py", ".claude/settings.json", ".codex/hooks.json", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/hooks/test_project_completion_surface.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", ".groundtruth/formal-artifact-approvals/*-gov-project-verified-completion-retirement-001.json", ".groundtruth/formal-artifact-approvals/*-delib-s358-s350-manufactured-variant-provenance.json"]

## Summary

Post-implementation report for the W1 retirement-machinery correction, implementing the `-005` proposal under Codex GO at `-006`. All eight implementation points (IP-1 through IP-8) are complete and verified.

IP-1, IP-2, and IP-3 (the lifecycle service, the completion scanner, and the byte-identical surface hook pair) were implemented in the working tree under the prior `-004` GO; this session verified them against the `-005` proposal before continuing. IP-4 through IP-8 were implemented under the `-006` GO and a regenerated implementation-start packet (`expires_at` 2026-05-18T22:18:33Z, bound to `-006` / proposal `-005`).

The live project-completion and retirement machinery now matches GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2: completion is automatic on the all-membership-linked-work-items-VERIFIED condition with no owner-confirmation gate. The historical record is corrected (GOV v3), the provenance of the S350 manufactured-variant error is archived, and PROJECT-GTKB-LO-OPPORTUNITY-RADAR is retired.

## Specification Links

- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 - the primary governing specification; v2 is the rule the live machinery was made to match. W1 implemented machinery, a historical-record correction (v3), and a project retirement so the platform faithfully enforces v2.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 - v2's owner-AUQ boundary cites this: owner-AUQ gates project start, not completion. W1 stripped only the completion-side gate and left the start-side authorization workflow intact.
- GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 - cited by v2 alongside the implementation-authorization spec for the project-start owner-AUQ boundary; W1 did not change project start.
- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; this report is filed and reviewed through that workflow.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this report carries a complete, relevance-closed Specification Links section and every protected mutation surface is in target_paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - this report carries a spec-to-test mapping with executed verification evidence below.
- GOV-ARTIFACT-APPROVAL-001 - the v3 GOV spec and the provenance deliberation are formal artifacts; each MemBase mutation was gated by a formal-artifact-approval packet presented to and approved by the owner before insertion.
- PB-ARTIFACT-APPROVAL-001 - the protected-artifact approval discipline was applied to the v3 GOV spec and the provenance deliberation.
- DCL-ARTIFACT-APPROVAL-HOOK-001 - the formal-artifact-approval gate hook enforced the packet requirement on the GOV v3 and the deliberation insert; both inserts ran with a validated packet referenced via GTKB_FORMAL_APPROVAL_PACKET.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this report carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all changed files are in-root; no application path under applications/ was touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the correction is preserved as durable artifacts: WI-3365, the proposal chain, the v3 GOV spec, the provenance deliberation, the updated tests, and this report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, tests, GOV v3, deliberation, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3365 moves through open, in-progress, and verified lifecycle states.
- SPEC-AUQ-POLICY-ENGINE-001 - W1 removed the project-completion owner-AUQ gate; this does not weaken AUQ enforcement for any decision class that still requires it. Project completion is not an owner-decision point per v2.

## Prior Deliberations

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation authorizing the combined governance-correction project; records the W1 scope item by item. This report implements the W1 workstream.
- DELIB-S353-LO-OPPORTUNITY-RADAR-PROJECT-COMPLETION-2026-05-15 - the S353 keep-open choice for PROJECT-GTKB-LO-OPPORTUNITY-RADAR; IP-6 retired that project under the explicit DELIB-S358 supersession.
- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2 supersession record - v2's own description records the v1-to-v2 supersession; IP-7's v3 builds on it by re-framing v1 accurately as a Prime Builder error.
- DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE - the provenance deliberation created by IP-8 of this workstream; archives the chain by which the S350 manufactured-variant AskUserQuestion produced the incorrect v1.

## Owner Decisions / Input

- 2026-05-17, S357: the owner directed superseding GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 via a v2 (v1 preserved append-only), approved v2 as written, and folded the v1-record correction and the machinery correction into one combined project. Captured in DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION.
- 2026-05-17, S358: the owner directed standing up and running the combined governance-correction project; the W1 scope items are enumerated in DELIB-S358; W1-W4 sequencing was collected via AskUserQuestion.
- 2026-05-17, S358: the owner directed retiring PROJECT-GTKB-LO-OPPORTUNITY-RADAR (DELIB-S358 decision 4), superseding the DELIB-S353 keep-open choice.
- 2026-05-18, S358: the owner directed filing the `-005` REVISED (rather than an in-place override) to bring `platform_tests/scripts/test_project_verified_completion_scanner.py` into W1 scope after Prime Builder self-detected FINDING-F3. Collected via AskUserQuestion.
- 2026-05-18, S358: the owner approved GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v3 (IP-7) as drafted, after full native-format presentation. Collected via AskUserQuestion. Recorded in approval packet `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`.
- 2026-05-18, S358: the owner approved DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE (IP-8) as drafted, after full native-format presentation. Collected via AskUserQuestion. Recorded in approval packet `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json`.

## Implemented Changes

### IP-1: Owner-confirmation gate stripped from complete_project_authorization()

`groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`: the owner-confirmation gate (former Step 2) is removed from `complete_project_authorization()`; the mandatory `owner_decision_deliberation_id` parameter is dropped; the docstring states the v2 automatic model. The function retains the load-active-authorization step, the readiness check, the status transition, and the sole-active retirement step. The retirement `change_reason` no longer references an owner decision. `import json` is removed (the removed gate was its only consumer).

### IP-2: Work-item gating set reconciled to the v2 membership-link definition

`lifecycle.py`: the static `_authorization_work_item_ids()` (decoded the authorization envelope's `included_work_item_ids`) is replaced by `_project_membership_work_item_ids(project_id)`, which returns the project's active project-to-work-item membership-link work items via `db.list_project_work_items()`. `complete_project_authorization()` readiness now sources the gating set from membership links. `scripts/project_verified_completion_scanner.py`: the scanner's `_included_work_item_ids()` is likewise replaced by `_project_membership_work_item_ids(db, project_id)`; `scan()` builds a per-project membership-link gating map. Scanner and lifecycle service agree byte-for-byte on the gating definition.

### IP-3: Automatic-transition path added; surface hook pair repurposed

`lifecycle.py`: a new deterministic service method `auto_complete_ready_authorizations()` scans active authorizations and auto-completes every completion-ready one (all membership-linked work items VERIFIED) via the stripped `complete_project_authorization()`. It is idempotent - a completed authorization is no longer active. `.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` are repurposed from owner-confirmation advisory to automatic-transition trigger plus notification: the hook invokes `auto_complete_ready_authorizations()` and emits a notification of what was auto-completed and retired, with no AskUserQuestion instruction and no "Do NOT auto-transition" text. The two hook files remain byte-identical (see Hook Pair Byte-Identity below). `.codex/hooks.json`: the `project-completion-surface.py` registration `statusMessage` is corrected to "Auto-completing VERIFIED-ready project authorizations". `.claude/settings.json` requires no W1 change (the Claude-side hook entry carries no description field); see Files Changed for the scoping note.

### IP-4: gt projects complete-authorization CLI subcommand

`groundtruth-kb/src/groundtruth_kb/cli.py`: a `complete-authorization` subcommand is added to the `gt projects` group. It invokes the stripped `complete_project_authorization()` for an explicitly named authorization and does not gate on an owner decision (consistent with v2). It resolves `project_root` from the active config. The owner-directed `retire` subcommand is unchanged.

### IP-5: Covering tests updated

`groundtruth-kb/tests/test_project_artifacts.py`: the five v1 owner-confirmation-gate tests are deleted; the completion/retirement tests are re-signatured to the stripped function signature and the membership-link gating set; new tests cover the automatic-transition path (`auto_complete_ready_authorizations()`), the membership-link gating set, the scanner gating-set parity, and the `gt projects complete-authorization` CLI subcommand. `platform_tests/hooks/test_project_completion_surface.py`: the hook tests are rewritten to the repurposed automatic-transition-plus-notification behavior, asserting the transition is applied and the notification omits AskUserQuestion / "Do NOT auto-transition" language. `platform_tests/scripts/test_project_verified_completion_scanner.py` (in scope per FINDING-F3): the seed helper and tests are re-signatured to the v2 membership-link gating model, plus a new test proving the scanner gates on membership links rather than `included_work_item_ids`.

### IP-6: PROJECT-GTKB-LO-OPPORTUNITY-RADAR retired

`PROJECT-GTKB-LO-OPPORTUNITY-RADAR` is retired in MemBase via the project-lifecycle retirement path (v3 active -> v4 retired). The `change_reason` cites DELIB-S358 decision 4 and this bridge thread, and records the supersession of the DELIB-S353 keep-open choice.

### IP-7: GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v3 inserted

An append-only v3 of GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 is inserted into MemBase. v3 preserves the v2 behavioral rule byte-identically and rewrites only the Supersession paragraph to frame v1 accurately as a Prime Builder manufactured-variant error. The owner approved the v3 content as drafted (AskUserQuestion, 2026-05-18); the insert ran under a validated formal-artifact-approval packet.

### IP-8: DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE archived

A Deliberation Archive record capturing the provenance of the S350 manufactured-variant error is inserted into MemBase (`source_type=bridge_thread`, `outcome=informational`, linked to GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 and WI-3365). The owner approved the content as drafted (AskUserQuestion, 2026-05-18); the insert ran under a validated formal-artifact-approval packet.

## Specification-Derived Verification

| Specification | Behavior verified | Test / verification | Result |
|---|---|---|---|
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | completion succeeds with no owner_decision_deliberation_id and no owner-confirmation gate | test_project_artifacts.py::test_complete_succeeds_without_owner_decision | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | non-active authorization and unverified-work-item rejection still apply | test_project_artifacts.py::test_complete_rejects_non_active_authorization, ::test_complete_rejects_when_a_wi_not_verified | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | the gating set is the project's membership-linked work items, not included_work_item_ids | test_project_artifacts.py::test_complete_rejects_when_project_has_no_membership_links, ::test_complete_gating_set_is_membership_links_not_included_ids, ::test_scanner_gating_set_uses_membership_links | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | scanner gates on membership links (dedicated test file, FINDING-F3) | test_project_verified_completion_scanner.py (4 tests incl. ::test_scanner_gating_uses_membership_links_not_included_ids) | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | sole-active completion retires the project; other-active keeps it active | test_project_artifacts.py::test_complete_sole_active_authorization_retires_project, ::test_complete_with_other_active_authorization_keeps_project_active | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | auto_complete_ready_authorizations() auto-completes and auto-retires, idempotently, with no owner AUQ | test_project_artifacts.py::test_auto_complete_ready_authorizations_completes_and_retires, ::test_auto_complete_is_idempotent, ::test_auto_complete_skips_unready_authorization | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | the surface hook triggers the automatic transition and emits a notification with no AskUserQuestion instruction | test_project_completion_surface.py (4 tests: Claude + Codex auto-complete, notification-language, silent-when-not-ready) | PASS |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | the gt projects complete-authorization CLI subcommand invokes the stripped completion path | test_project_artifacts.py::test_projects_complete_authorization_cli | PASS |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | project start is unchanged - the existing project-schema and authorization tests still pass | test_project_artifacts.py (7 project-schema/CLI tests retained, all pass) | PASS |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | this report carries the spec-to-test mapping with executed commands and observed results | this section | PASS |
| GOV-ARTIFACT-APPROVAL-001 | the GOV v3 and the provenance deliberation each carry a validated formal-artifact-approval packet | see Formal-Artifact-Approval Packet Evidence | PASS |

Executed commands and observed results:

- `python -m pytest groundtruth-kb/tests/test_project_artifacts.py platform_tests/hooks/test_project_completion_surface.py platform_tests/scripts/test_project_verified_completion_scanner.py` -> `27 passed, 1 warning`. Breakdown: test_project_artifacts.py 19 (7 retained project-schema/CLI + 12 W1 completion), test_project_completion_surface.py 4, test_project_verified_completion_scanner.py 4.
- `python -m ruff check` over the eight W1 Python files (lifecycle.py, project_verified_completion_scanner.py, the two project-completion-surface.py hook copies, cli.py, the three test files) -> `All checks passed!`.

## MemBase Evidence (IP-6 / IP-7 / IP-8)

- IP-6: `db.get_project('PROJECT-GTKB-LO-OPPORTUNITY-RADAR')` -> `status=retired version=4`.
- IP-7: `db.get_spec('GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001')` -> `version=3 status=specified type=governance`. The PostToolUse KB-SPEC-EVENT confirmed the v3 insert.
- IP-8: `db.get_deliberation('DELIB-S358-S350-MANUFACTURED-VARIANT-PROVENANCE')` -> present, `version=1 source_type=bridge_thread outcome=informational`.

## Formal-Artifact-Approval Packet Evidence (IP-7 / IP-8)

- IP-7 packet: `.groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json`, `artifact_type=governance`, `action=update`, `approval_mode=approve`, `approved_by=owner`, `full_content_sha256=c9eded0438902c2d38c8fe5c14d43b8d3ce2269dd39c7348f30a27f390a4803d`. `python scripts/validate_formal_artifact_packet.py` -> `packet_valid`. The v3 insert ran with this packet referenced via GTKB_FORMAL_APPROVAL_PACKET; the formal-artifact-approval gate validated and allowed it.
- IP-8 packet: `.groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json`, `artifact_type=deliberation`, `action=insert`, `approval_mode=approve`, `approved_by=owner`, `full_content_sha256=f0dfde89aa89e7e13132bd8ca03fba4a2b4b39b549ab32c9b5087067fb52e386`. `python scripts/validate_formal_artifact_packet.py` -> `packet_valid`. The deliberation insert ran with this packet referenced via GTKB_FORMAL_APPROVAL_PACKET; the gate validated and allowed it.

## Hook Pair Byte-Identity

`.claude/hooks/project-completion-surface.py` and `.codex/gtkb-hooks/project-completion-surface.py` are byte-identical after the IP-3 repurposing: both files SHA-256 `292fb73230da7c200c5a048798e49717433fc17bd1dffee6a5c5e072043139cc` (ADR-CODEX-HOOK-PARITY-FALLBACK-001 parity).

## Bridge Preflights

Both mandatory bridge preflights are run on this `-007` operative file after its INDEX entry is filed:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-s358-w1-retirement-machinery-correction` - expected `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-s358-w1-retirement-machinery-correction` - expected exit 0, 0 blocking gaps.

Loyal Opposition reproduces the full preflight tables in the VERIFIED verdict per the file-bridge-protocol Mandatory Applicability Preflight Gate.

## Recommended Commit Type

`fix` - W1 repairs project-completion machinery that diverged from its governing specification (GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 v2). The new `auto_complete_ready_authorizations()` service method and the `gt projects complete-authorization` CLI subcommand are internal completions of the v2-mandated automatic-completion behavior, not a new external product capability; the behavior they expose is the rule v2 already mandates. The GOV v3 and the provenance deliberation are historical-record corrections. If Loyal Opposition assesses the new CLI subcommand and automatic-transition path as net-new capability surface warranting `feat`, that reassessment is welcomed; the diff stat is in Files Changed.

## Files Changed

W1 source / test / config files:
- groundtruth-kb/src/groundtruth_kb/project/lifecycle.py (IP-1, IP-2, IP-3)
- scripts/project_verified_completion_scanner.py (IP-2)
- .claude/hooks/project-completion-surface.py (IP-3)
- .codex/gtkb-hooks/project-completion-surface.py (IP-3)
- .codex/hooks.json (IP-3 - the project-completion-surface.py statusMessage hunk only)
- groundtruth-kb/src/groundtruth_kb/cli.py (IP-4)
- groundtruth-kb/tests/test_project_artifacts.py (IP-5)
- platform_tests/hooks/test_project_completion_surface.py (IP-5)
- platform_tests/scripts/test_project_verified_completion_scanner.py (IP-5)

MemBase + approval packets:
- groundtruth.db (IP-6 project retirement, IP-7 GOV v3 insert, IP-8 deliberation insert)
- .groundtruth/formal-artifact-approvals/2026-05-18-GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001-v3.json (IP-7)
- .groundtruth/formal-artifact-approvals/2026-05-18-delib-s358-s350-manufactured-variant-provenance.json (IP-8)

Bridge:
- bridge/gtkb-s358-w1-retirement-machinery-correction-005.md, -006.md, -007.md
- bridge/INDEX.md (W1 entry)

Commit-scope note: `.claude/settings.json` is in the proposal target_paths but W1 makes no change to it - the Claude-side `project-completion-surface.py` hook entry has no description field, so IP-3 leaves it untouched. The working tree's `.claude/settings.json` diff and the non-`statusMessage` portion of the `.codex/hooks.json` diff are unrelated parallel-session changes; the W1 commit excludes `.claude/settings.json` entirely and stages only the `project-completion-surface.py` statusMessage hunk of `.codex/hooks.json`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
