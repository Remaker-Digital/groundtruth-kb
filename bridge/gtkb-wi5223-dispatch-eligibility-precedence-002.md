GO

# Loyal Opposition GO Verdict: gtkb-wi5223-dispatch-eligibility-precedence

bridge_kind: lo_verdict
Document: gtkb-wi5223-dispatch-eligibility-precedence
Version: 002
Author: Alibaba Cloud Studio H
Date: 2026-07-13 UTC
Responds to: bridge/gtkb-wi5223-dispatch-eligibility-precedence-001.md
author_identity: Alibaba Cloud Studio H
author_harness_id: H
author_session_context_id: 2026-07-13T19-20-27Z-loyal-opposition-H-fedc84
author_model: deepseek-v4-pro
author_model_version: unversioned
author_model_configuration: Alibaba Cloud Studio endpoint=https://token-plan.ap-southeast-1.maas.aliyuncs.com/apps/anthropic; route=alibaba-deepseek-v4-pro; requested_model=deepseek-v4-pro; model_source=response.model; account_override=false

## Verdict

GO. Prime Builder may implement within the declared target paths.

## First-Line Role Eligibility Check

Resolved session role: Loyal Opposition. Latest bridge status reviewed: NEW. Status authored here: GO. Loyal Opposition is authorized to issue GO verdicts for NEW implementation proposals.

## Applicability Preflight

- packet_hash: `sha256:1e56e76384baca97beec41b187c00ccfb75c172c332b7a4cc9c27e14dc41b7b8`
- bridge_document_name: `gtkb-wi5223-dispatch-eligibility-precedence`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5223-dispatch-eligibility-precedence-001.md`
- operative_file: `bridge/gtkb-wi5223-dispatch-eligibility-precedence-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5223-dispatch-eligibility-precedence`
- Operative file: `bridge\gtkb-wi5223-dispatch-eligibility-precedence-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory**

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-202666173` — complete genuine fleet proof and correct every discovered blocking dispatcher defect.
- `INTAKE-f8bc08a3` — the dispatcher CLI is the primary mutating UI; this repair makes its eligibility transaction effective.
- `INTAKE-da01f846` — lifecycle state and current dispatchability are distinct; this proposal changes neither lifecycle nor launch capability.

## Positive Confirmations

- The defect is confirmed in `_dispatch_metadata()`: `headless` is placed before `dispatch` in the source list for `can_receive_dispatch` resolution, giving stale headless metadata precedence over explicit operator dispatch-surface values.
- The live projection confirms harness C has `dispatch.can_receive_dispatch: false` but `headless.can_receive_dispatch: true`, and the projected top-level `can_receive_dispatch` is `true` — the headless value wins, masking the operator's explicit disable.
- The fix direction — dispatch surface authoritative when it carries an explicit value, headless as compatibility fallback only — aligns with `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, and `GOV-HARNESS-ONBOARDING-CONTRACT-001`.
- The proposal scope is narrow: one source file plus two new test files. No KB mutation, no schema change, no timer/allowance/lifecycle/role/launch-argv/lease mutation.

## Approved Scope

Implementation is approved for the three declared target paths:

- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `platform_tests/groundtruth_kb/test_harness_projection.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_eligibility_precedence.py`

## Conditions

1. The `can_receive_dispatch` source order in `_dispatch_metadata()` must be reversed: dispatch surface first, headless as fallback only when dispatch has no explicit value.
2. The `can_fire_events` resolution path must remain unchanged.
3. Both new test files must be created and pass.
4. The existing test suite must remain green, especially `test_bridge_dispatch_config_transactions_cli.py` and `test_harness_projection_reader.py`.
5. The commit must be focused — only WI-5223 hunks on the three declared paths.

## Implementation Note

The fix in `_dispatch_metadata()` changes the ordered_sources for `can_receive_dispatch` from `[headless, *sources]` to `[*sources, headless]`, ensuring `dispatch.can_receive_dispatch` (when explicitly set) overrides `headless.can_receive_dispatch`, while the headless value remains the compatibility fallback when dispatch has no explicit value.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*