NEW

# Defect-Fix Proposal - WI-4768 dispatcher live-state reporting and consistency reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4768-dispatch-live-state-reconcile
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-23 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef3a8-fefa-7382-a13c-c93e5ee51026
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive session; approval_policy=never; sandbox=danger-full-access; resolved Prime Builder by owner init keyword ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4768
Project: PROJECT-GTKB-DISPATCHER-CONTROL-CLI
Work Item: WI-4768
Fold-in Work Items: WI-4733, WI-4725

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implement WI-4768 by making `gt bridge dispatch status` and `gt bridge dispatch report` reflect live dispatcher runtime evidence instead of stale stored failure fields, and by surfacing dispatcher config drift between `config/dispatcher/rules.toml` and the generated harness-registry projection. This slice folds in stale-health defects WI-4733 and WI-4725 because WI-4768 explicitly depends on them and the dispatcher-control project scope includes their stale-health fix.

Current live evidence already demonstrates the drift class: `config/dispatcher/rules.toml` says harness F can receive dispatch, while `harness-state/harness-registry.json` still projects harness F with `can_receive_dispatch=false`. The current status/report code overlays dispatcher config onto the projection and hides that mismatch from operators. Separately, runtime health still treats persisted `last_result`, `failure_class`, and `last_launch.exit_failure_reason` as live failure evidence whenever pending work exists, even when the evidence is stale, orphaned, or contradicted by live worker/run state.

This proposal does not authorize raw editing of `config/dispatcher/rules.toml` or hand-editing `harness-state/harness-registry.json`. If a reconciliation action is implemented, it must be exposed as a governed CLI transaction under `gt bridge dispatch` and covered by temp-root tests; live project state remains unchanged unless a verified, governed CLI command is intentionally run later.

## First-Line Role Eligibility Check

Before filing this status-bearing `NEW` proposal, Prime Builder checked the status-token authority:

- `python -m groundtruth_kb.cli harness roles` confirmed durable harness `A` is active and carries `role=["prime-builder"]`.
- `.claude/session/role-019ef3a8-fefa-7382-a13c-c93e5ee51026.json` records this bridge session as `role="prime-builder"` from the init keyword.
- `python -m groundtruth_kb.cli bridge show gtkb-wi4768-dispatch-live-state-reconcile --json` returned `bridge_thread_not_found`, so `-001` is the correct first numbered file.

Prime Builder is authorized to write `NEW` proposal files; Loyal Opposition remains required for `GO` before protected implementation edits.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires dispatcher reporting and configuration control under the governed `gt bridge dispatch` CLI and skill surface.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - requires dispatcher configuration mutation to occur through governed CLI transactions and prohibits raw direct file edits.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge files and role-specific status tokens are the canonical proposal, review, report, and verification chain.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH bounds implementation authority for the selected project and included dependency work items.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - active PAUTH and proposal scope must cite the governing specifications.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge `GO`, target paths, implementation-start packet, implementation report, or Loyal Opposition verification.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves owner decision, requirement, DCL, project, WI, proposal, report, verification, and audit evidence as durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links governing specs and maps implementation tests to those specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must carry this spec-to-test mapping forward and report executed results.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this implementation proposal includes PAUTH, project, work item, and inline JSON `target_paths`.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner approval evidence comes from AUQ-backed owner decision `DELIB-20265795`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - implementation artifacts and tests must stay under `E:\GT-KB`; tests should use temp project roots.
- `GOV-STANDING-BACKLOG-001` - WI-4768, WI-4733, and WI-4725 are the MemBase work-item authorities for this slice and dependency fold-in.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use explicit fallback checks when hook parity or native hook support is uncertain.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - dispatcher operational findings are converted into durable proposal, implementation, report, and verification artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner requirement, defect fold-in, implementation plan, test mapping, report, and verification remain lifecycle-visible.

## Prior Deliberations

- `DELIB-20265795` - owner AUQ-backed decision requiring a dispatcher reporting/configuration control surface under `gt bridge dispatch`.
- `DELIB-20265540` - prior NO-GO showing dispatcher config mutation must be covered by cited authorization.
- `bridge/gtkb-wi4765-dispatch-report-cli-001.md` through `bridge/gtkb-wi4765-dispatch-report-cli-004.md` - predecessor project slice implementing and verifying the dispatcher reporting surface.
- `bridge/gtkb-wi4766-dispatch-config-transactions-001.md` through `bridge/gtkb-wi4766-dispatch-config-transactions-004.md` - predecessor project slice implementing and verifying governed dispatcher config transaction commands.
- `bridge/gtkb-wi4767-dispatch-config-file-edit-guard-001.md` through `bridge/gtkb-wi4767-dispatch-config-file-edit-guard-004.md` - predecessor project slice implementing and verifying the direct-edit guard and doctor check.
- WI-4733 - stale/orphaned dispatch-health `last_result` failure records should not produce live FAIL without live evidence.
- WI-4725 - stored failed-launch evidence should not read as a live FAIL while new dispatch is suppressed and no live failure remains.

Commands reviewed before proposal drafting:

```text
python -m groundtruth_kb.cli projects show PROJECT-GTKB-DISPATCHER-CONTROL-CLI --json
python -m groundtruth_kb.cli backlog show WI-4768 --json
python -m groundtruth_kb.cli backlog show WI-4733 --json
python -m groundtruth_kb.cli backlog show WI-4725 --json
python -m groundtruth_kb.cli bridge dispatch status --json
```

The project state shows WI-4765, WI-4766, and WI-4767 resolved; WI-4768 is the next open project work item. WI-4733 and WI-4725 are open dependency defects and are explicitly included in `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4768`.

## Owner Decisions / Input

- `DELIB-20265795` - owner AUQ-backed decision requiring the dispatcher control/reporting surface.
- `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4768` - active project authorization for WI-4768 with dependency fold-in of WI-4733 and WI-4725, allowing `cli_extension`, `source`, `test_addition`, and `config` while forbidding production deployment and credential lifecycle work.

No new owner decision is required before implementation because WI-4768 is directly inside the captured dispatcher-control project, its stale-health dependencies are explicitly folded into the active PAUTH, and implementation still requires Loyal Opposition `GO`.

## Requirement Sufficiency

Existing requirements sufficient.

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` specifies the dispatcher reporting/configuration control surface under `gt bridge dispatch`.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` specifies governed CLI transactions for dispatcher config mutation and prohibits raw file edits.
- WI-4768 specifies live-state reporting plus rules.toml/registry consistency surfacing and reconciliation.
- WI-4733 and WI-4725 specify the stale-health failure modes that WI-4768 depends on.
- `DELIB-20265795` is the AUQ-backed owner decision that created this workstream.
- `PAUTH-PROJECT-GTKB-DISPATCHER-CONTROL-CLI-WI-4768` is active and bounds this WI and dependency fold-in.

## Proposed Scope

In scope:

- Extend dispatcher status/report collection so runtime health distinguishes live failure evidence from stale or orphaned stored fields.
- Recompute or annotate live worker/run evidence so a persisted `last_result`, `failure_class`, or `last_launch.exit_failure_reason` does not create a live FAIL when no current runtime condition supports it.
- Preserve genuine FAIL behavior for active pending work with live blocker evidence, including current launch/readiness failures, circuit breakers with pending work, and exit-zero/no-verdict evidence when still operationally current.
- Add status/report consistency findings for drift between raw harness-registry projection fields and the dispatcher config overlay, including the current class where a harness is suspended or registry-disabled while `rules.toml` still marks it dispatchable.
- Add a governed reconciliation path under `gt bridge dispatch` if implementation needs an explicit operator command; any such command must write through an audited transaction/helper and must not require raw file edits.
- Add focused tests for stale-health discounting, genuine live-failure preservation, config/projection drift surfacing, report JSON exposure, and CLI read-only behavior.

Out of scope:

- No raw direct edit to live `config/dispatcher/rules.toml`.
- No hand edit to `harness-state/harness-registry.json`; it remains generated projection state.
- No change to dispatcher ranking, caps, scheduling, queue selection, provider invocation, bridge status semantics, or role assignment.
- No dispatcher-control skill work; that remains WI-4769.
- No production deployment, credential lifecycle, force-push, or external service action.

## Spec-Derived Verification Plan

| Specification / requirement | Proposed verification |
| --- | --- |
| WI-4768 live-state reporting | Add tests proving stale stored failed-launch or last-result rows without live supporting evidence produce WARN/annotation or no failure, not FAIL. |
| WI-4733 stale/orphaned health fold-in | Add tests for stale recipient records and orphaned/role-inactive recipient records so they do not keep dispatch health red indefinitely. |
| WI-4725 suppressed stale failure fold-in | Add tests for stored `last_launch.exit_failure_reason` plus suppression/no-live-dispatch evidence so the stale failure is discounted or clearly annotated. |
| WI-4768 genuine failures preserved | Add tests proving active pending work with live launch/readiness blocker evidence still reports FAIL. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` report visibility | Add or update `gt bridge dispatch report --json` tests so consistency findings and live-state fields are machine-readable. |
| `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` reconciliation path | If a reconciliation command is added, test that it writes only through the governed dispatcher transaction/helper path and records audit evidence in temp roots. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This proposal carries PAUTH, project, work item, fold-in work items, and inline JSON `target_paths` metadata. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal links governing specs and maps tests back to the linked requirements. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report must carry this mapping forward and include executed pytest, ruff check, and ruff format evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests use pytest temp roots/synthetic payloads and all implementation target paths remain under `E:\GT-KB`. |

Required verification commands after implementation:

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py groundtruth-kb/src/groundtruth_kb/cli.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
```

## Acceptance Criteria

- `gt bridge dispatch status --json` exposes live-state-aware health and does not hide config/projection consistency drift behind the overlay.
- `gt bridge dispatch report --json` exposes the same consistency findings and live-state classification details.
- Stale stored failure fields no longer produce `health_status=FAIL` without current runtime support.
- Genuine live failures still produce `health_status=FAIL`.
- The current rules.toml/registry mismatch class is surfaced in findings with enough detail for an operator to reconcile it through governed CLI commands.
- No live direct file mutation of dispatcher config or harness-registry projection is required to implement or verify the slice.

## Risk / Rollback

Primary risk: discounting stale runtime failures too aggressively could hide a genuine dispatch outage. Mitigation: stale-discounting must require explicit stale/orphaned/no-live evidence and tests must preserve active live-failure FAIL behavior.

Secondary risk: reporting config/projection drift as FAIL could make already-degraded dispatch lanes noisier. Mitigation: classify drift findings separately from runtime launch failure findings and make the health severity deterministic in tests.

Rollback: remove the live-state classification helpers, consistency findings, optional reconciliation command, and focused tests. Existing WI-4765 reporting and WI-4766 transaction behavior would remain intact.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4768-dispatch-live-state-reconcile`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

Recommended commit type: `fix:`. The implementation corrects dispatcher-health false FAIL behavior and exposes dispatcher control-plane consistency drift.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
