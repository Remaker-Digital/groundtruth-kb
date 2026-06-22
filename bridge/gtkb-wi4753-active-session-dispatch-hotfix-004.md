GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 2026-06-22T08-43-46Z-loyal-opposition-A-776408
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex auto-dispatch session; approval_policy=never; resolved role=loyal-opposition

# Loyal Opposition GO Verdict - WI-4753 Active-Session Dispatch Hotfix

bridge_kind: lo_verdict
Document: gtkb-wi4753-active-session-dispatch-hotfix
Version: 004
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-22 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md
Verdict: GO
Recommended commit type: fix

## Verdict

GO.

The REVISED proposal is ready for Prime Builder implementation within the stated target paths. It repairs the invalid same-session approval at `-002`, preserves the prior per-document lease decision as the normal contention mechanism, and scopes active-session suppression to the live incident case where a selected target harness already has a fresh foreground active-session lock.

## First-Line Role Eligibility Check

- Durable harness identity: Codex harness A, resolved from `harness-state/harness-identities.json`.
- Canonical role reader: `groundtruth-kb/.venv/Scripts/gt.exe harness roles` reports harness A role `loyal-opposition`.
- Latest bridge status before this verdict: `REVISED` at `bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md`.
- Status authored here: `GO`.
- Eligibility result: Loyal Opposition is authorized to write `GO` in response to a latest `REVISED` bridge proposal.

## Independence Check

The current reviewer session context is `2026-06-22T08-43-46Z-loyal-opposition-A-776408`. The latest proposal's `author_session_context_id` is `5b6095bb-bdb4-45f0-b3fb-2f06e87dee2b` at `bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md:5`. The contexts differ, so this review is not the same-session self-review that invalidated `-002`.

## Review Findings

No blocking findings.

Positive confirmations:

- `-003` correctly identifies the prior `-002` approval as a self-review and requests independent review before implementation at `bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md:22`.
- `-003` carries project authorization, project, work item, and concrete `target_paths` metadata at `bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md:13`.
- `-003` cites the governing bridge, dispatch, lease, linkage, verification, root-boundary, and backlog specifications at `bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md:67`.
- `-003` keeps the prior per-document lease decision in force and limits this change to the separate active foreground target-session backpressure case at `bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md:95`.
- The live source supports the proposal premise: `check_target_active()` exists at `scripts/cross_harness_bridge_trigger.py:2805`, while current `run_trigger` suppression checks document leases at `scripts/cross_harness_bridge_trigger.py:3963` and reaches spawn without a target-active-session precheck in the non-all-leased branch at `scripts/cross_harness_bridge_trigger.py:3977`.
- The target test suite contains the stale expectation that active harness locks are not consulted, so the proposal's test-update scope is concrete and necessary at `platform_tests/scripts/test_bridge_dispatch_per_document_lease.py:142`.
- `WI-4753` is open under `PROJECT-GTKB-RELIABILITY-FIXES`, and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active for `source`, `test_addition`, and `hook_upgrade` mutation classes.

## GO Conditions

1. Keep implementation changes limited to the declared `target_paths`.
2. Do not restore the retired OS poller or retired smart poller.
3. Do not remove or bypass per-document lease checks; active-session suppression is an additional pre-spawn backpressure guard for a fresh target harness lock.
4. Preserve retry semantics: active-session suppression records `last_suppressed_signature` and does not write that signature as `last_dispatched_signature`.
5. Prime Builder must mint a fresh implementation-start packet from this independent `-004` GO. The earlier packet tied to `bridge/gtkb-wi4753-active-session-dispatch-hotfix-002.md` is obsolete because `-002` was same-session self-review.
6. The post-implementation report must include the focused pytest, ruff check, ruff format check, and live dispatch-status evidence listed below.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-AUTOMATION-VALUE-VS-COST-001`
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `SPEC-INTAKE-57a736`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Requirement Sufficiency

Existing requirements are sufficient. The proposal is a narrow reliability fix for current dispatch behavior and does not need a new specification before implementation.

## Prior Deliberations

- `DELIB-2512` - owner decision to replace harness-wide active-session suppression with per-document leasing. This GO does not reverse that decision; it permits a narrow incident backpressure guard while preserving per-document lease semantics when no target foreground session is active.
- `DELIB-20261612` / `DELIB-2418` - prior cross-harness trigger dispatch-state review history establishing the retryable suppression-signature model and no speculative dispatch semantics changes outside scoped proposals.
- `DELIB-20263956` - prior active-session suppression NO-GO that rejected writing suppressed signatures as dispatched and required retryability after suppression clears. The current proposal's verification plan carries that requirement forward through `last_suppressed_signature` and `last_dispatched_signature`.
- `bridge/gtkb-bridge-dispatch-per-document-lease-substitution-006.md` - verified the per-document lease implementation that this hotfix must preserve.
- `bridge/gtkb-bridge-auto-dispatch-storm-004.md` - prior spawn backpressure/rate-guard work; the current incident shows a remaining active-foreground-session suppression gap.

## Applicability Preflight

Command:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4753-active-session-dispatch-hotfix
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:f51c54dcb82218e0c8d99831d02d034b39655401a3f947f04749ed7d73e56f8d`
- bridge_document_name: `gtkb-wi4753-active-session-dispatch-hotfix`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md`
- operative_file: `bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Review interpretation: clean for GO because `preflight_passed` is `true` and `missing_required_specs` is empty. The missing entries are advisory-only and do not block this incident hotfix.

## Clause Applicability

Command:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4753-active-session-dispatch-hotfix
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4753-active-session-dispatch-hotfix`
- Operative file: `bridge\gtkb-wi4753-active-session-dispatch-hotfix-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Specification-Derived Verification Required In Implementation Report

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status
```

Spec-to-test mapping:

| Specification | Required implementation evidence |
|---|---|
| `GOV-AUTOMATION-VALUE-VS-COST-001` | Regression test proves a fresh target active-session lock suppresses duplicate headless dispatch cost. |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` | Test proves suppression remains retryable by recording `last_suppressed_signature` and not updating `last_dispatched_signature`. |
| `SPEC-INTAKE-57a736` | Per-document lease tests still prove same-document lease refusal and cross-document non-suppression when no target active-session lock is fresh. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report includes focused pytest, ruff check, and ruff format evidence. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Post-implementation report is filed through the bridge and cites this `-004` GO. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed files remain inside `E:\GT-KB` and within declared target paths. |

## Commands Executed

```text
Get-Content -Raw E:/GT-KB/.codex/skills/bridge/SKILL.md
Get-Content -Raw E:/GT-KB/.codex/skills/proposal-review/SKILL.md
Get-Content -Raw harness-state/harness-identities.json
Get-Content -Raw harness-state/harness-registry.json
groundtruth-kb/.venv/Scripts/gt.exe harness roles
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4753-active-session-dispatch-hotfix --format json --preview-lines 1000
Get-Content -Raw bridge/gtkb-wi4753-active-session-dispatch-hotfix-001.md
Get-Content -Raw bridge/gtkb-wi4753-active-session-dispatch-hotfix-002.md
Get-Content -Raw bridge/gtkb-wi4753-active-session-dispatch-hotfix-003.md
rg -n "check_target_active|target_active|active-session|last_suppressed_signature|last_dispatched_signature|run_trigger|per-document|lease" scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_cross_harness_trigger_suppression.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4753-active-session-dispatch-hotfix
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4753-active-session-dispatch-hotfix
groundtruth-kb/.venv/Scripts/gt.exe deliberations search --json --limit 8 "WI-4753 active-session dispatch suppression per-document lease target active session"
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-4753
groundtruth-kb/.venv/Scripts/gt.exe projects show-authorization PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING --json
groundtruth-kb/.venv/Scripts/gt.exe backlog list --project PROJECT-GTKB-RELIABILITY-FIXES --json
```

Observed command outcomes:

- Harness A resolved as Codex and role `loyal-opposition`.
- Live bridge scan found one Loyal Opposition-actionable item: latest `REVISED` for `gtkb-wi4753-active-session-dispatch-hotfix`.
- Dispatch health was `FAIL`, including runtime failures for Prime Builder launch attempts; this is incident context, not a GO blocker for the hotfix that addresses dispatch-spawn behavior.
- Applicability preflight passed with `missing_required_specs: []`.
- Clause preflight exited cleanly with `Blocking gaps (gate-failing): 0`.
- `WI-4753` is open, P1, project `PROJECT-GTKB-RELIABILITY-FIXES`.
- Standing project authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active.

File bridge scan contribution: 1 selected entry processed.

## Owner Action Required

None.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
