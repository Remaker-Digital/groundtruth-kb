NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3d79-c37d-7432-8c82-a66b675a389a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; reasoning=xhigh; approval_policy=never

# WI-5033 - Dispatch ranking flattening after uniform-random tiebreak

bridge_kind: prime_proposal
Document: gtkb-wi5033-dispatch-ranking-flattening
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5033-DISPATCH-RANKING-FLATTENING-20260707
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5033

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/harness_ops.py", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/skills/test_dispatcher_control_skill.py", "groundtruth.db", "harness-state/harness-registry.json"]

implementation_scope: source-and-operational-state
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

WI-5033 is the owner-approved follow-on to WI-5032. WI-5032 has reached latest
`VERIFIED`, so the prerequisite uniform-random terminal tiebreak is in place.
This proposal normalizes the remaining dispatcher ranking dimensions so
harnesses B, C, D, E, and F all use the Codex baseline values:

- `dispatch_quality = 90`
- `dispatch_cost = 60`
- `dispatch_availability = 90`
- `reviewer_precedence = 20`

The implementation must preserve each harness's role, lifecycle status, and
`can_receive_dispatch` value. It must not restart the dispatcher daemon, change
provider/model credentials, activate or suspend harnesses, or mutate dispatcher
configuration or registry tables by hand.

Current dispatcher status on 2026-07-07 confirms the work remains applicable:
B/C/D/E/F still carry mixed ranking values and `gt bridge threads --wi WI-5033
--json --compact` returns `match_count: 0` before this filing.

## Implementation Direction

Use governed dispatcher-control transactions for the whole change.

1. Extend `gt bridge dispatch config set-weights` with
   `--reviewer-precedence INTEGER`, or add an equivalent sibling transaction
   under `gt bridge dispatch config`, so reviewer precedence is no longer a raw
   registry-table edit. The preferred shape is to extend `set-weights` because
   `SPEC-DISPATCHER-CONTROL-SURFACE-001` treats quality, cost, availability,
   and reviewer precedence as one dispatcher ranking surface.
2. Keep the transaction append-only through `harness_ops`; do not edit
   the MemBase database, the generated harness-registry projection, or the
   dispatcher TOML directly.
3. After the transaction surface exists and implementation-start is active, run
   the governed normalization transactions for B, C, D, E, and F.
4. Verify through `gt bridge dispatch config --json`, `gt bridge dispatch
   status --json`, and `gt bridge dispatch health --json`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the implementation proposal must enter the numbered bridge chain through the governed writer and wait for a latest `GO`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites the dispatcher-control, project-authorization, and verification requirements that constrain the work.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries `Project Authorization`, `Project`, and `Work Item` metadata for implementation-start validation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map this proposal's requirements to executed tests and dispatcher status evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the bounded PAUTH is owner approval evidence for WI-5033 only and does not permit unrelated dispatcher or harness work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the PAUTH does not bypass Loyal Opposition `GO`, target paths, implementation-start, implementation report, or verification.
- `GOV-STANDING-BACKLOG-001` - WI-5033 remains visible in the MemBase backlog until bridge completion or another terminal disposition.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - all dispatcher reporting and configuration changes must flow through governed `gt bridge dispatch` commands rather than direct file or runtime-state mutation.
- `DCL-DISPATCHER-CONFIG-CLI-ONLY-001` - direct dispatcher configuration or runtime/config mutation outside the transaction path is prohibited.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatch target selection remains a GT-KB-owned service behavior and must preserve role/status routing and auditability.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the dispatcher remains daemon-owned; harnesses remain dispatch consumers rather than control-plane actors.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - the change must preserve kind-aware dispatchability and dispatcher routing semantics.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, PAUTH, proposal, implementation report, and verification remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation should preserve traceability from owner decision to work item, proposal, tests, report, and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5033 moves from owner-gated backlog work into a governed implementation proposal path without silent resolution or supersession.

## Prior Deliberations

- `DELIB-DISPATCH-RANKING-NORMALIZATION-20260705` - owner AUQ decision: flatten ranking values after the uniform-random tiebreak; leave role and dispatchability unchanged.
- `DELIB-20260707-WI5033-IMPLEMENTATION-APPROVAL` - owner authorized Prime Builder to attach WI-5033 to the dispatcher modernization project, create bounded PAUTH evidence, and file this NEW implementation proposal.
- The latest WI-5032 bridge verdict is `VERIFIED`, satisfying the prerequisite tiebreak behavior before this proposal is filed.

## Owner Decisions / Input

- The owner authorized WI-5033 in the current Prime Builder session.
- `DELIB-20260707-WI5033-IMPLEMENTATION-APPROVAL` records the approved scope: normalize B/C/D/E/F to `90/60/90/20`, preserve role/status/dispatchability, and avoid raw config or registry edits.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5033-DISPATCH-RANKING-FLATTENING-20260707` bounds this proposal and any later GO-gated implementation. It forbids implementation without live bridge `GO` and implementation-start, direct `rules.toml` or registry-table edits outside governed dispatcher-control transactions, harness role or dispatchability changes, lifecycle status changes, daemon restart, topology activation/deactivation, production deployment, credential/provider changes, external spend, unrelated cleanup, destructive cleanup, history rewrite, and unrelated sweep commits.

## Requirement Sufficiency

Existing requirements are sufficient. WI-5033 states the exact desired ranking
values, the exact harness set, the dependency on WI-5032, and the preservation
constraints. `SPEC-DISPATCHER-CONTROL-SURFACE-001` and
`DCL-DISPATCHER-CONFIG-CLI-ONLY-001` supersede the older work-item note that
`reviewer_precedence` would require a registry-table edit: the implementation
must close that transaction-surface gap instead of bypassing it.

No new requirement is needed before implementation, provided the source slice
only exposes reviewer precedence through the governed dispatcher-control
surface and the operational slice only normalizes B/C/D/E/F ranking values.

## Cross-Harness Disposition

This proposal targets dispatcher-owned control-plane source, tests, MemBase
dispatch metadata, and the generated harness registry projection. It does not
add or remove harness-local hooks, skills, commands, invocation shims, or
permissions.

- Claude/B: affected only as a dispatcher target whose ranking metadata is
  normalized; no Claude-local surface changes.
- Antigravity/C: affected only as a dispatcher target whose ranking metadata is
  normalized; no Antigravity-local surface changes.
- Ollama/D: affected only as a dispatcher target whose ranking metadata is
  normalized; no provider route/model/credential changes.
- Cursor/E: affected only as a dispatcher target whose ranking metadata is
  normalized; suspended status and dispatchability are preserved.
- OpenRouter/F: affected only as a dispatcher target whose ranking metadata is
  normalized; PB role and dispatchability are preserved.

## Spec-Derived Verification Plan

The implementation report must run and report the exact commands below,
adjusting only to the repo-native interpreter if the venv path is unavailable:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_transactions.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/skills/test_dispatcher_control_skill.py -q --no-header
gt bridge dispatch config --json
gt bridge dispatch status --json
gt bridge dispatch health --json
```

Expected coverage:

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` and `DCL-DISPATCHER-CONFIG-CLI-ONLY-001`: tests prove reviewer precedence can be changed through `gt bridge dispatch config` without direct TOML, runtime JSON, or raw registry-table edits, and that `set-weights` still supports dry-run and JSON output.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, and `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`: status evidence proves the dispatcher still owns selection and routing; roles, lifecycle status, and `can_receive_dispatch` are unchanged while ranking metadata changes.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: implementation-start must accept only the target paths in this proposal and the active PAUTH; no implementation begins before that packet exists.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: bridge preflights must pass before filing and before `GO`/verification; the implementation report must carry forward specification links and this spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: MemBase/project/bridge evidence must show WI-5033 linked to this proposal without resolving the work before verification evidence exists.

Operational acceptance after implementation:

- `gt bridge dispatch status --json` reports B, C, D, E, and F with
  `dispatch_quality=90`, `dispatch_cost=60`, `dispatch_availability=90`, and
  `reviewer_precedence=20`.
- The same status evidence shows each harness's role, status, and
  `can_receive_dispatch` value preserved relative to the pre-implementation
  status evidence captured on 2026-07-07.
- Selection among fully tied candidates remains uniform-random by inheritance
  from verified WI-5032 behavior.

## Risk / Rollback

Main risk: changing reviewer precedence through the same command family as
quality/cost/availability could accidentally conflate top-level harness
precedence with dispatch metadata under `invocation_surfaces.dispatch`.
Mitigation: source tests must assert the append-only harness version preserves
role, lifecycle status, dispatchability, invocation surfaces, and unrelated
metadata while updating only the requested ranking fields.

Secondary risk: normalizing suspended or currently non-dispatchable harnesses
could be mistaken for activation. Mitigation: verification explicitly compares
role/status/`can_receive_dispatch` before and after; this proposal forbids any
activation, suspension, or role reassignment.

Rollback is one focused rollback of the WI-5033 source/test changes plus a
governed dispatcher-control transaction restoring the prior B/C/D/E/F ranking
metadata captured in the implementation report. Append-only PAUTH, bridge,
deliberation, transaction-audit, and MemBase history remain as durable evidence.

## Pre-Filing Checks

- Applicability preflight on the completed draft must pass with no required or advisory spec gaps.
- ADR/DCL clause preflight on the completed draft must report zero blocking gaps.
- Phantom-spec sweep must find no missing `SPEC` / `GOV` / `ADR` / `DCL` / `PB` IDs.
- Draft scaffold-marker sweep must find no unfinished template markers.

## Bridge Filing

This proposal will be filed in the bridge directory as the next status-bearing
numbered bridge file for `gtkb-wi5033-dispatch-ranking-flattening`; no prior
version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file
chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat(dispatch): add governed reviewer-precedence transaction support and
normalize dispatcher ranking metadata for WI-5033.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
