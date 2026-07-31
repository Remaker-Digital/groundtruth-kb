NEW

# WI-5223 - Honor canonical dispatcher eligibility over stale headless metadata

bridge_kind: prime_proposal
Document: gtkb-wi5223-dispatch-eligibility-precedence
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-13 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; governed dispatcher recovery

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5223-ELIGIBILITY-PRECEDENCE-20260713
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5223

target_paths: ["groundtruth-kb/src/groundtruth_kb/harness_projection.py", "platform_tests/groundtruth_kb/test_harness_projection.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_eligibility_precedence.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The canonical `gt bridge dispatch config set-eligibility` transaction reports a
successful append-only MemBase/registry update, but the current projection gives
`invocation_surfaces.headless.can_receive_dispatch` precedence over the
transaction-owned `invocation_surfaces.dispatch.can_receive_dispatch`. A stale
headless `true` therefore keeps an unavailable harness selected after the
operator explicitly disables it. This was reproduced on A and C while routing
WI-5220 to the owner-authorized available reviewer D.

Make the dispatch surface authoritative when it carries an explicit eligibility
value, while retaining headless receive metadata as a compatibility fallback
only when the canonical dispatch value is absent. Add projection and CLI-level
regressions. Preserve launch argv, lifecycle state, role, model, allowance,
runtime state, leases, and every unrelated dirty hunk.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - operator eligibility must determine which harness the centralized dispatcher may launch.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - `gt bridge dispatch config` is the canonical mutating control surface and must report effective changes truthfully.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - installed headless capability is distinct from current dispatcher eligibility.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the correction requires proposal, independent review, implementation report, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the behavioral authority is linked before source mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, WI, PAUTH, and exact targets are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must execute both projection and CLI control-path regressions.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the live routing defect is preserved as WI-5223 and TEST-11377.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - evidence remains linked across the work item, test, PAUTH, bridge, implementation, and commit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - a reproducible canonical-control failure triggers governed correction.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all source, tests, and evidence remain within `E:/GT-KB`.

## Prior Deliberations

- `DELIB-202666173` - complete genuine fleet proof and correct every discovered blocking dispatcher defect.
- `INTAKE-f8bc08a3` - the dispatcher CLI is the primary mutating UI; this repair makes its eligibility transaction effective.
- `INTAKE-da01f846` - lifecycle state and current dispatchability are distinct; this proposal changes neither lifecycle nor launch capability.
- `bridge/gtkb-wi5020-retire-event-source-config-006.md` - VERIFIED authority for separate event-source and dispatch-target axes.
- `bridge/gtkb-wi5200-5202-generous-harness-repair-narrow-008.md` - VERIFIED generous provider limits that remain untouched.

## Owner Decisions / Input

- `DELIB-202666173` authorizes correction of every defect discovered while proving genuine A/B/C/D/F/H operation.
- On 2026-07-13 the owner stated that C is out of budget and that only D, H, and F are available reviewers. The failed canonical C disable made that availability constraint unenforceable and exposed this defect.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5223-ELIGIBILITY-PRECEDENCE-20260713` limits implementation to the three declared paths after independent GO.

## Requirement Sufficiency

Existing requirements sufficient - `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`SPEC-DISPATCHER-CONTROL-SURFACE-001`, and
`GOV-HARNESS-ONBOARDING-CONTRACT-001` already separate installed launch
capability from current operator-controlled eligibility.

## Spec-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| Centralized dispatch eligibility | Projection fixture with `headless=true`, `dispatch=false` | Projected top-level eligibility is `false`; the unavailable harness is not selectable. |
| Headless capability compatibility | Projection fixture with headless receive metadata and no dispatch override | Existing launch-capability fallback remains `true`. |
| Canonical control surface | New CLI integration invokes `set-eligibility false`, reads the regenerated projection, then invokes `true` | Disable and re-enable are both effective and append-only without direct JSON mutation. |
| Harness onboarding separation | Inspect projected invocation surfaces and top-level fields | Headless argv/capability metadata is retained; roles, lifecycle, and model metadata are unchanged. |
| Focused regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_harness_projection.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_eligibility_precedence.py -q --tb=short` | Both focused modules pass. |
| Existing transaction coverage | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_config_transactions_cli.py -q --tb=short` | Existing canonical transaction behavior remains green against the staged patch. |
| Static quality | Ruff check and format-check on the three targets | Clean. |

## Acceptance Criteria

- An explicit dispatch-surface eligibility value overrides stale headless receive metadata.
- Headless receive metadata remains a compatibility fallback when no dispatch override exists.
- Canonical disable excludes the harness from the projected dispatcher population; canonical re-enable restores it.
- The transaction remains append-only and no runtime JSON or lease file is edited.
- The focused commit stages only WI-5223 hunks from the dirty projection path plus the two approved tests.
- D/F/H retain 600 turns, 900-second operations, and the owner-calibrated 60-minute model window; WI-5223 changes no timer.

## Risk / Rollback

The primary risk is hiding a launchable harness when an old dispatch override is
stale. That is the intended operator-control contract: headless capability says
the harness can be launched, while explicit dispatch eligibility says whether
it may be launched now. Tests preserve the no-override compatibility fallback.
Rollback reverts the single focused source/test commit; append-only registry
history and bridge evidence remain intact.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5223-dispatch-eligibility-precedence`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - restores the effective semantics of the canonical dispatcher eligibility control.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
