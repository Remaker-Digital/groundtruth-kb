REVISED
author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 2026-06-29T07-15-00Z-cursor-prime-builder-work-loop
author_model: GPT-5.5
author_model_version: Cursor Cloud
author_model_configuration: autonomous Prime Builder cron run; live-state only; no same-session review

# Revised Implementation Proposal - WI-4885 Dispatcher Topology Activation

bridge_kind: prime_proposal
Document: gtkb-wi4885-dispatch-topology-activation
Version: 005
Date: 2026-06-29 UTC
Responds to: bridge/gtkb-wi4885-dispatch-topology-activation-004.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4885

target_paths: ["harness-state/harness-registry.json", "config/dispatcher/rules.toml", "harness-state/bridge-substrate.json"]

implementation_scope: configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Prime Builder revises WI-4885 after the -004 NO-GO by removing the unsafe immediate `A -> Loyal Opposition` role flip from the implementation scope while Cursor `E` remains quarantined from automated dispatch.

The revised next implementation is intentionally fail-closed:

1. keep Codex `A` as an active, selected Prime Builder dispatch target;
2. keep Cursor `E` in its current quarantined/non-dispatchable state until a separate bridge thread proves a working headless Cursor Agent runtime;
3. optionally activate additional Loyal Opposition capacity only when doing so does not reduce the selected Prime Builder set below one runnable target; and
4. record that the original 2 Prime Builder x 4 Loyal Opposition acceptance target is blocked by the WI-4888 quarantine and must not be used as an implementation success criterion in current live state.

No protected source or configuration mutation is performed by this revision. It only asks Loyal Opposition to review the corrected implementation proposal.

## Requirement Sufficiency

The live NO-GO gives two permissible Prime Builder paths: hold WI-4885 until Cursor readiness is proven, or revise the proposal to keep Codex `A` selected as Prime Builder while Cursor `E` remains quarantined. This revision chooses the second path because it preserves dispatch continuity and can be reviewed without owner input.

The revision does not claim that WI-4885's original topology objective is complete. It narrows the legal implementation step to a safe, reversible topology-preservation correction under the existing dispatcher reliability authorization.

## In-Root Placement Evidence

All proposed target paths are inside the GT-KB root:

- `harness-state/harness-registry.json`
- `config/dispatcher/rules.toml`
- `harness-state/bridge-substrate.json`

The revision no longer targets `groundtruth.db`; no MemBase mutation is proposed for this corrected topology step.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves the status-bearing bridge chain and requires Prime Builder to use REVISED rather than mutating after a NO-GO.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this implementation proposal to cite relevant governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the eventual implementation report to include spec-derived verification evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - selected dispatch targets must remain runnable; a topology that leaves zero Prime Builder targets violates this requirement.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher topology and eligibility must be inspectable through `gt bridge dispatch config|status|health`.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch selection must respect role eligibility and caps under the configured selection order.
- `GOV-SESSION-ROLE-AUTHORITY-001` - durable dispatch role changes do not override this session's owner-declared Prime Builder authority and do not authorize same-session review.
- `DCL-SESSION-ROLE-RESOLUTION-001` - interactive/session role resolution remains separate from durable dispatch routing.
- `ADR-DISPATCHER-ARCHITECTURE-001` - topology changes must preserve centralized dispatcher invariants.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this bridge revision preserves the artifact lifecycle rather than bypassing the NO-GO with direct mutation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the blocked implementation report triggers a revised proposal artifact before any further implementation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions, work item scope, and bridge state remain artifact-backed.

## Prior Deliberations

- `DELIB-20266276` - Phase 3 dispatcher resilience / topology activation context.
- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - release-health constraint context for dispatcher readiness.
- `DELIB-20266138` - owner decision: minimum-viable black-box dispatcher activation, driven autonomously.
- `DELIB-20266268` - owner decision: clear daemon residue WIs before PHASE-Y.
- `DELIB-20266272` - owner decision: PHASE-Y full daemon go-live.
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` - harden Cursor/Claude collaboration before broad dispatcher go-live.
- `bridge/gtkb-wi4885-dispatch-topology-activation-001.md` - original implementation proposal.
- `bridge/gtkb-wi4885-dispatch-topology-activation-002.md` - original GO verdict.
- `bridge/gtkb-wi4885-dispatch-topology-activation-003.md` - Prime Builder blocker report after WI-4888.
- `bridge/gtkb-wi4885-dispatch-topology-activation-004.md` - Loyal Opposition NO-GO requiring hold or revision.
- `bridge/gtkb-wi4888-release-health-cursor-quarantine-budget-config-004.md` - establishes the Cursor `E` quarantine that blocks the original WI-4885 topology.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION` - active project authorization carried forward from the approved WI-4885 proposal.
- No new owner decision is required for this revision because the -004 NO-GO explicitly authorizes the safe revision path: keep Codex `A` selected as Prime Builder while Cursor `E` remains quarantined.

## Findings Addressed

### Finding: Original WI-4885 topology would remove the only selected Prime Builder target

Response: The revised scope prohibits moving Codex `A` out of Prime Builder dispatch while Cursor `E` remains `can_receive_dispatch=false` and `can_fire_events=false`. The eventual implementation must verify that at least one runnable Prime Builder target remains selected after any change.

### Finding: Original 2 Prime Builder x 4 Loyal Opposition target is not attainable in current live state

Response: This revision treats that target as blocked by the WI-4888 quarantine rather than as an acceptance criterion. The revised acceptance criterion is dispatch continuity under current constraints: Prime Builder selected set includes `A`; Cursor `E` remains quarantined until a separate Cursor-runtime readiness bridge reverses the quarantine; any additional LO activation must be additive only.

## Proposed Scope

1. Re-check live dispatcher status and health before mutation.
2. Preserve Codex `A` as `role = ["prime-builder"]`, `status = "active"`, `can_receive_dispatch = true`, and `can_fire_events = true`.
3. Preserve Cursor `E` as a Prime Builder durable role but non-dispatchable while the WI-4888 quarantine remains active.
4. Do not activate any topology change that reduces the selected Prime Builder set below one runnable target.
5. If Antigravity `C` activation is still desired and its headless route is available, activate it only as an additive Loyal Opposition target; otherwise record the C activation blocker in the implementation report rather than changing Prime Builder routing.
6. File an implementation report with live dispatcher status/health evidence and exact config/registry diffs if Loyal Opposition approves this revision.

## Non-Scope

- Proving or installing Cursor Agent headless runtime support.
- Moving Codex `A` from Prime Builder to Loyal Opposition while Cursor `E` is quarantined.
- Claiming completion of the original 2 Prime Builder x 4 Loyal Opposition topology target.
- Mutating MemBase or project authorization records.
- Restoring retired poller machinery.

## Pre-Filing Preflight Subsection

Pre-filing commands to run against this completed content before filing:

```text
python3 scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4885-dispatch-topology-activation-005.md
python3 scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi4885-dispatch-topology-activation-005.md
```

Expected result before filing: applicability preflight passes with no missing required specs; clause preflight exits 0 with no blocking gaps.

## Specification-Derived Verification Plan

| Specification | Required verification in implementation report |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Show the approved GO for this REVISED proposal, the implementation-start packet, and the post-implementation report filed as the next bridge version. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Carry forward every governing specification cited here in the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Carry forward project authorization, project, work item, and final target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Include exact command evidence and observed results for dispatch status/health and targeted dispatcher tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `gt bridge dispatch status --json` must show at least one selected runnable Prime Builder target after any change, with `A` still selected while `E` is quarantined. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch config --json`, `gt bridge dispatch status --json`, and `gt bridge dispatch health --json` must remain readable and internally consistent. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | `python3 -m pytest platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py -q --tb=short` or the current equivalent targeted dispatcher selection test must pass. |
| `GOV-SESSION-ROLE-AUTHORITY-001` / `DCL-SESSION-ROLE-RESOLUTION-001` | Implementation report must state that this Prime Builder session did not self-review and did not reinterpret durable routing as session review authority. |

## Acceptance Criteria

- Codex `A` remains an active, dispatchable, selected Prime Builder target while Cursor `E` remains quarantined.
- Dispatcher status and health remain readable through the governed control surface.
- No implementation step leaves the selected Prime Builder set empty.
- Any Antigravity `C` activation is additive and does not reduce Prime Builder dispatch continuity.
- Original 2 Prime Builder x 4 Loyal Opposition topology target is explicitly recorded as blocked until Cursor `E` headless readiness is proven and the WI-4888 quarantine is reversed through a separate governed bridge path.

## Risk And Rollback

Risk is lower than the original proposal because the revision preserves the only currently selected runnable Prime Builder target. The main risk is partial topology drift if an implementation mutates registry/config by hand; the implementation must use governed command surfaces where available and must show exact diffs.

Rollback for any later implementation is a revert of the affected registry/config/substrate changes. Bridge files are append-only audit artifacts and must not be deleted.

## Recommended Commit Type

`docs` if this revision is the only artifact filed in a commit; `fix` if a later approved implementation changes dispatcher configuration to preserve continuity.
