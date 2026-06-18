NEW

# Harness B Interactive-Only Status Orthogonality Doctor Check (WI-4645)

bridge_kind: prime_proposal
Document: gtkb-harness-b-interactive-status-orthogonality
Version: 001 (NEW)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-18 UTC
Implements: WI-4645
Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4645
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_fab01_dispatch_substrate_revival.py"]
Recommended commit type: test:
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-automation-keep-working-2026-06-18T12-45Z
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop automation session; autonomous Prime Builder loop

## Claim

`WI-4645` should resolve as a deterministic visibility gap, not as a live
registry-state correction.

The live harness projection currently records harness B (`claude`) with
`role=["prime-builder"]`, `status="suspended"`, `can_fire_events=true`,
`can_receive_dispatch=false`, and dispatch tag `interactive-only`. That shape is
allowed by the role/status/dispatchability model: a harness may retain an
operating role without being eligible for headless dispatch, and inactive or
suspended harnesses retain their role set as lifecycle status changes. The
hygiene gap is that `gt doctor` has a dispatch-launchability check for active
headless targets but no visible check explaining the intentional interactive-only
role-holder state.

This proposal adds a narrow doctor check and focused tests so the state becomes
machine-visible: suspended interactive-only role holders are reported as an
expected orthogonal state, while ambiguous non-active role holders without an
explicit non-dispatchable or interactive-only signal produce a warning for
operator follow-up.

## Specification Links

- `REQ-HARNESS-REGISTRY-001` - harness roles, lifecycle status, invocation
  surfaces, and generated projection fields are registry data. The check reads
  the projection and does not hand-edit it.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - Prime Builder and Loyal Opposition are
  harness-assigned portable roles; the proposal preserves role portability by
  not treating a suspended lifecycle status as role erasure.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` - role sets and topology are derived
  from the registry; the proposal keeps lifecycle status and dispatchability as
  separate axes rather than collapsing them into one active-role test.
- `GOV-SESSION-ROLE-AUTHORITY-001` - interactive session authority and headless
  dispatch authority are separate. The check documents that a harness can remain
  an interactive role holder while not being a headless dispatch target.
- `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` - role resolution must not infer
  or override user-declared session authority solely from a registry lifecycle
  status. This proposal avoids any automatic role/status mutation.
- `DCL-SESSION-ROLE-RESOLUTION-001` - session role resolution is deterministic;
  this check is read-only visibility and does not become a second role resolver.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the bridge proposal and later implementation
  report remain the durable handoff and verification records for this change.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposal preserves the observed
  registry ambiguity as a governed artifact relationship instead of relying on
  transient chat interpretation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the work item remains open until the
  bridge implementation is verified; no lifecycle transition is claimed by this
  proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, work item,
  bridge proposal, implementation report, and tests remain linked as durable
  artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites
  the governing specifications for its implementation and tests.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the test plan maps each
  behavioral claim to an executable regression check before VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths and verification
  commands are inside `E:\GT-KB`.

## Authorization

This proposal uses active project authorization
`PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`, which
authorizes proposing implementation for all unimplemented work items linked to
`PROJECT-GTKB-MAY29-HYGIENE`. The authorizing owner decision is
`DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617`.

No formal-artifact mutation, harness-registry mutation, production deployment,
credential action, or external action is requested. The target paths are source
and test surfaces only.

## Prior Deliberations

- `DELIB-S378-ROLE-STATUS-ORTHOGONALITY-DISPATCH` - owner decision establishing
  role/status/dispatchability orthogonality. This proposal operationalizes that
  decision as a doctor-visible check for the observed harness B state.
- `DELIB-20263438` - role/status orthogonality follow-on context cited by the
  canonical terminology role-assignment entry; supports retaining role sets
  independently from lifecycle status.
- `DELIB-20263296` - GO for role-eligibility guard work; it distinguishes
  interactive session-role evidence from headless dispatch role checks.
- `DELIB-20261713` - GO for FAB-01 dispatch substrate revival; it approves the
  launchability and capability-axis split that this proposal builds on.
- `DELIB-20264419` - VERIFIED Ollama dispatch wiring; it keeps role/status
  eligibility separate from local dispatch readiness.
- `DELIB-20263440` - benchmark decision requiring disabled or non-selected
  harnesses to remain measurable without mutating durable roles, reinforcing
  that registry state and probe/interactive uses can be intentionally decoupled.

## Owner Decisions / Input

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` authorizes proposing
  implementation for all unimplemented work items linked to the May29 Hygiene
  project.
- No new owner decision is required before Loyal Opposition review. If Loyal
  Opposition prefers changing harness B's live status instead of adding a doctor
  visibility check, that would be a different registry mutation and should be
  sent back as a NO-GO or a separate owner decision.

## Requirement Sufficiency

Existing requirements are sufficient. The canonical terminology already states
that inactive or suspended harnesses retain their role sets and that role,
lifecycle status, event-firing capability, and headless dispatchability are
orthogonal axes. The missing piece is deterministic visibility in the doctor
surface for the current harness B shape.

## Scope

### IP-1: Add a doctor check for interactive-only role/status orthogonality

Add a read-only doctor check near the existing harness dispatch launchability
check in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

The check reads `harness-state/harness-registry.json` through the existing
harness projection reader and classifies non-active role holders:

- PASS when every non-active role holder is explicitly non-dispatchable
  (`can_receive_dispatch=false`) or marked `interactive-only`. The message
  names each harness, lifecycle status, role set, and dispatchability axes so
  harness B's current state is visible and not mistaken for drift.
- WARNING when a non-active role holder has roles but lacks an explicit
  interactive-only or non-dispatchable signal. That condition is not an
  implementation blocker, but it is ambiguous enough to surface for registry
  hygiene follow-up.
- WARNING when the harness registry cannot be read, matching the existing
  launchability check's failure mode for read-only diagnostic surfaces.

The check must not change role resolution, target selection, dispatcher ranking,
work-intent claims, or `harness-state/harness-registry.json`.

### IP-2: Focused regression coverage

Extend `platform_tests/scripts/test_fab01_dispatch_substrate_revival.py` with
direct tests for the new doctor check:

- suspended harness B with `role=["prime-builder"]`, `can_receive_dispatch=false`,
  `can_fire_events=true`, and dispatch tag `interactive-only` returns PASS and
  names the orthogonal state in the message;
- suspended/non-active role holder with no explicit non-dispatchable or
  interactive-only signal returns WARNING;
- active dispatch targets continue to be covered by the existing launchability
  check and are not reclassified by this new visibility check.

## Out Of Scope

- No change to `harness-state/harness-registry.json`.
- No MemBase harness-table mutation or projection regeneration.
- No dispatcher target-selection, role-resolution, work-intent, or claim-gate
  behavior change.
- No narrative rule or formal artifact mutation.
- No production deployment or external credential action.

## Pre-Filing Checks

Draft checks to run before filing:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-harness-b-interactive-status-orthogonality --content-file .gtkb-state\bridge-propose-drafts\gtkb-harness-b-interactive-status-orthogonality-001.md --json
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-harness-b-interactive-status-orthogonality --content-file .gtkb-state\bridge-propose-drafts\gtkb-harness-b-interactive-status-orthogonality-001.md
python scripts\proposal_target_paths_coverage_preflight.py --content-file .gtkb-state\bridge-propose-drafts\gtkb-harness-b-interactive-status-orthogonality-001.md --json --strict
python scripts\check_code_quality_baseline_parity.py .gtkb-state\bridge-propose-drafts\gtkb-harness-b-interactive-status-orthogonality-001.md
python .claude\hooks\bridge-compliance-gate.py --audit-only --audit-output .gtkb-state\bridge-propose-drafts\gtkb-harness-b-interactive-status-orthogonality-audit.json
```

Observed draft results:

- `bridge_applicability_preflight.py`: exit 0; `preflight_passed=true`;
  `packet_hash=sha256:19ec3eae6dc783bd77947663d482c618cff39e2e4af39476e6598d5cfbcd0159`;
  `missing_required_specs=[]`; `missing_advisory_specs=[]`; missing parent
  dirs `[]`.
- `adr_dcl_clause_preflight.py`: exit 0; clauses evaluated `5`; `must_apply=4`;
  `may_apply=1`; evidence gaps in must-apply clauses `0`; blocking gaps `0`.
- `proposal_target_paths_coverage_preflight.py --strict`: exit 0;
  `verdict=clean`; all implied paths covered; target paths are
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py` and
  `platform_tests/scripts/test_fab01_dispatch_substrate_revival.py`.
- `check_code_quality_baseline_parity.py`: exit 0; code-quality baseline
  parity clean for this draft.
- `bridge-compliance-gate.py --audit-only`: exit 0; audit decision `pass`;
  audit-mode preflight passed for
  `bridge/gtkb-harness-b-interactive-status-orthogonality-001.md`.

## Specification-To-Test Mapping

| Specification | Verification |
| --- | --- |
| `REQ-HARNESS-REGISTRY-001` | Unit test writes a temporary harness registry projection and verifies the doctor check reads status, role, and dispatchability without mutating the file. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Unit test proves a suspended harness can retain `role=["prime-builder"]` without the doctor treating that role as invalid. |
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001` | Unit test proves lifecycle status and dispatchability are handled as separate axes. |
| `GOV-SESSION-ROLE-AUTHORITY-001` / `DCL-ROLE-RESOLUTION-DECLARED-AUTHORITY-001` / `DCL-SESSION-ROLE-RESOLUTION-001` | Implementation contains no role resolver or registry mutation path; tests call the doctor check only. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Bridge thread remains append-only; post-implementation report will include command evidence, target-path diff, and work-item lifecycle evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight passes with `missing_required_specs: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report carries this mapping and exact command results. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Clause preflight validates all target paths are in-root. |

Implementation verification will run:

```text
python -m pytest platform_tests/scripts/test_fab01_dispatch_substrate_revival.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_fab01_dispatch_substrate_revival.py
python -m groundtruth_kb.cli doctor --profile harness-memory
```

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] The new doctor check reports the live harness B shape as an expected
  non-active interactive-only role-holder state rather than a failure.
- [ ] Ambiguous non-active role holders with roles but without an explicit
  non-dispatchable or interactive-only signal produce a warning.
- [ ] Existing launchability behavior remains scoped to active headless dispatch
  targets.
- [ ] No registry, dispatcher, role-resolution, or work-intent behavior changes.
- [ ] Focused pytest and ruff commands pass.
- [ ] Loyal Opposition returns VERIFIED before WI-4645 is treated as complete.

## Risk And Rollback

Risk is low because the implementation is read-only diagnostic visibility. The
main risk is confusing operators with another doctor message. The mitigation is
to use PASS for explicit interactive-only/non-dispatchable non-active role
holders and WARNING only for ambiguous records.

Rollback is a normal source/test revert of the added doctor check and tests. No
registry state, bridge history, MemBase row, credential, or deployment state is
mutated by the proposed implementation.

## Loyal Opposition Asks

1. Confirm that the correct resolution for WI-4645 is doctor-visible
   orthogonality, not live registry status mutation.
2. Confirm that PASS for explicit `interactive-only` / `can_receive_dispatch=false`
   non-active role holders and WARNING for ambiguous non-active role holders is
   the right severity split.
3. Confirm the target path scope is sufficient and should not include
   `harness-state/harness-registry.json`, since the registry is evidence only
   and not an implementation target.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
