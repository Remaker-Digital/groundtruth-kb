NEW

# WI-4505: TAFE Stuck-Flow Detection and Self-Diagnosis (read-only detector)

bridge_kind: prime_proposal
Document: gtkb-tafe-stuck-flow-detection
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 869ade5b-58a4-4261-b2cb-98fcbecb8c0e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder declared via ::init gtkb pb; explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-OBSERVABILITY-TRACK-WI-4504-4505
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4505

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_stuck_flow.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_stuck_flow.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

---

## Summary

Implement WI-4505, the TAFE R3 **stuck-flow detection and self-diagnosis** surface, as a pure, injected-service detector module (`groundtruth-kb/src/groundtruth_kb/tafe_stuck_flow.py`) plus a thin read-only CLI command. The detector reads current flow/stage/lease state and the WI-4504 per-stage-attempt telemetry, classifies each active flow's stuck conditions, and attaches a self-diagnosis derived from the recorded failure-class / outcome / recovery-action telemetry. It mirrors the functional-core / imperative-shell shape of the VERIFIED WI-4498 policy engine and the WI-4499 dispatch-tick runtime.

This is the **canonical structured stuck-flow detector** — the primitive a later slice can have the WI-4499 dispatch tick consume. It is intentionally **read-only**: it computes and reports findings; it performs **no recovery actuation** (no lease release, re-dispatch, stage mutation, or flow restart), which the active observability-track PAUTH forbids (`autonomous_recovery_actuation`).

### De-duplication boundary vs WI-4499 (dispatch tick/health)

WI-4499's `gt flow dispatch health` surfaces **aggregate dispatch-readiness counts** (pending stages, eligible candidates by role, stale-lease indicators) for the R5 need-evaluation path. WI-4505 is different and non-overlapping: it produces **per-flow structured stuck findings + R3 self-diagnosis** (which flow, which stage, why stuck, what the telemetry says about the failure). WI-4505 does not re-implement dispatch readiness, does not dispatch, and does not aggregate for need-evaluation. WI-4499 may later consume `detect_stuck_flows(...)` as its stuck-input primitive; that wiring is out of scope here.

### Bounding (explicit out-of-scope)

This slice is bounded to read-only detection + diagnosis + a read-only CLI. It MUST NOT:

- Perform any **recovery actuation** — no lease release/expiry, re-dispatch, stage/flow mutation, session spawn, subprocess, or flow restart. The PAUTH forbids `autonomous_recovery_actuation`; the detector emits findings and advisory diagnosis text only. Lease recovery is WI-4494; dispatch is WI-4498/4499.
- Mutate MemBase, `stage_leases`, owner-gate state, `bridge/INDEX.md`, or any flow/stage/telemetry row. Reads only; `mutated=False` always.
- Create a new table or schema (the `schema_table_creation` class is unused; the detector reads existing flow/stage/lease/telemetry rows).
- Create a dispatch substrate, scheduled task, hook, poller, generated view, dual-write, pilot expansion, or cutover.

## Specification Links

- `SPEC-TAFE-R3` — the governing requirement: stuck/failed-flow detection and self-diagnosis over the recorded failure-class, cleanup-result, and recovery-action telemetry. WI-4505 is the detection/diagnosis surface; it reasons over the durable inputs without actuating recovery.
- `SPEC-TAFE-R6` — the detector consumes the per-stage-attempt telemetry (`outcome`, `failure_class`, `cleanup_result`, `recovery_actions`) recorded by WI-4504 for the self-diagnosis facet.
- `SPEC-TAFE-R2` — expired/stale-lease detection reads stage-lease state (single-claim contention context); lease state is read, never mutated.
- `SPEC-TAFE-R5` — stuck/failed/expired-lease detection is one of the need-evaluation inputs R5 enumerates; WI-4505 provides the canonical detector the R5 dispatch tick can later consume, but WI-4505 itself initiates nothing.
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — Phase 1 parallel-run substrate; `bridge/INDEX.md` remains canonical until a later governed cutover; this slice adds an observability surface only.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` remains the canonical workflow state; this slice writes nothing to the index at runtime.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — PAUTH, project, work item, target paths, and governing specs are concretely linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable project-authorization metadata is present in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps R3 detection/diagnosis, R6 telemetry consumption, R2 lease-read, the non-mutating bound, and the no-recovery-actuation bound to executed tests.
- `GOV-STANDING-BACKLOG-001` — WI-4505 is the backlog authority for this slice; WI-4506 (dashboard) and the cutover items remain out of scope.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds under the active bounded observability-track PAUTH (which includes WI-4505) plus the forthcoming Loyal Opposition GO and implementation-start packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all source and test changes are inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the detector is a durable governed source artifact with a preserved evidence trail; WI-4505 stays unresolved until terminal VERIFIED.

## Prior Deliberations

<!-- Reviewed and pruned by author. -->

- `DELIB-TAFE-PHASE-1-OBSERVABILITY-TRACK-PAUTH-20260613` — owner-decision basis for the observability-track PAUTH that authorizes WI-4504 (telemetry) and WI-4505 (this slice), and which forbids `autonomous_recovery_actuation`.
- `DELIB-20263164` — owner decision backing the tranche-3 PAUTH that also includes WI-4505.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` — owner approval promoting the TAFE R-specs (including SPEC-TAFE-R3/R6) to `specified`.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` — owner choice of the TAFE overhaul direction that produced SPEC-TAFE-R3/R5/R6.
- `bridge/gtkb-tafe-stage-attempt-telemetry-002.md` — the GO'd WI-4504 telemetry contract (`stage_attempt_telemetry` + `list_stage_attempt_telemetry`) this detector consumes for the diagnosis facet; implementation is in flight and this slice recommends landing after WI-4504 reaches VERIFIED.
- `bridge/gtkb-tafe-dispatch-tick-health-003.md` — the in-flight WI-4499 dispatch tick/health; this proposal documents the explicit de-duplication boundary (WI-4505 = canonical structured detector; WI-4499 = aggregate dispatch-readiness health).
- No prior deliberations found for TAFE stuck-flow detection / self-diagnosis: `search_deliberations("stuck flow detection self-diagnosis dispatch tick expired lease TAFE")` and `search_deliberations("stuck flow detection self-diagnosis failure class recovery TAFE R3")` returned no matches on 2026-06-13. This is the first implementation of the R3 detection surface, not a revisit of a rejected approach.

## Owner Decisions / Input

No new owner decision is required to file or implement this proposal.

- **Implementation authority:** the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-OBSERVABILITY-TRACK-WI-4504-4505`, backed by owner decision `DELIB-TAFE-PHASE-1-OBSERVABILITY-TRACK-PAUTH-20260613`, which explicitly includes WI-4505 and forbids `autonomous_recovery_actuation`, `dual_write`, `pilot_eligibility_expansion`, `phase_2_reformation`, `generated_view_authority`, `index_authority_change`, and `bridge_rule_cutover`. This slice stays within `source_code_addition` + `test_addition` and respects every forbidden bound (read-only, no recovery actuation).
- **Work selection:** the owner directed the autonomous TAFE drive and, via AskUserQuestion on 2026-06-13 (S438), reaffirmed driving TAFE to completion. WI-4505 is the next observability-track item after WI-4504.
- No expanded authorization is requested; the read-only/no-actuation bound is enforced by a structural test.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TAFE-R3` specifies stuck/failed-flow detection and self-diagnosis; `SPEC-TAFE-R6` specifies the telemetry fields the diagnosis reasons over; `SPEC-TAFE-R2` specifies the lease state read for expired-lease detection; `SPEC-TAFE-R5` enumerates stuck detection as a need-evaluation input. No new or revised requirement is needed because this slice implements the specified detection/diagnosis surface as a non-mutating read/compute/report layer and explicitly excludes recovery actuation, dispatch, and persistence.

## Implementation Plan

New module `groundtruth-kb/src/groundtruth_kb/tafe_stuck_flow.py`:

1. **Frozen value objects:** `StuckThresholds` (configurable `stalled_seconds`, `owner_gate_stalled_seconds`, `lease_expiry_grace_seconds`, with defaults), `StuckFlowFinding` (`flow_instance_id`, `stage_instance_id`, `reason`, `diagnosis`, evidence fields, `age_seconds`), and `StuckFlowReport` (frozen list of findings + aggregate counts by reason + `mutated=False`).
2. **`detect_stuck_flows(service, *, now=None, thresholds=StuckThresholds()) -> StuckFlowReport`** — a pure, injected-service function. Reads active (non-terminal) flow instances (`service.list_flow_instances`), their stage instances (`service.list_stage_instances`), stage-lease state (existing read surface), and per-stage-attempt telemetry (`service.list_stage_attempt_telemetry`, WI-4504). For each active flow it classifies stuck conditions:
   - `expired_lease` — a stage holds an active lease whose lifecycle/heartbeat is expired relative to `now` (+ grace). **Read-only detection**; recovery is WI-4494, not actuated here.
   - `stalled_pending` — a non-terminal stage is unclaimed (no active lease) with no progress (no recent attempt/event) beyond `stalled_seconds`.
   - `owner_gate_stalled` — a stage blocked on an owner gate beyond `owner_gate_stalled_seconds`.
   - `failed_unrecovered` — the latest telemetry attempt for a stage has `outcome` failed with a `failure_class` set, and no subsequent successful attempt or recorded `recovery_actions` (R3 self-diagnosis over R6 telemetry).
3. **`diagnose_stuck_flow(finding, telemetry_rows) -> str`** — attaches a self-diagnosis string derived from the telemetry (`failure_class`, last `outcome`, `cleanup_result`, and an **advisory-only** recovery hint). The hint is text; it is never actuated.
4. The module exposes `__all__` with the value objects + functions. It imports nothing that mutates, has **no** `subprocess`/spawn, no `bridge/INDEX.md` write, no MemBase write, and no lease-release / re-dispatch / flow-mutation surface. Telemetry-dependent classification (`failed_unrecovered` + diagnosis enrichment) degrades gracefully (empty telemetry → those facets simply produce no findings), so the lease/stall/owner-gate facets work on the already-VERIFIED runtime substrate even before WI-4504 lands.

CLI wiring in `groundtruth-kb/src/groundtruth_kb/cli.py`:

5. Add a read-only `gt flow stuck` command (under the existing `flow` group) that resolves the service via the existing helper, calls `detect_stuck_flows`, and emits the JSON/summary report (`{"findings": [...], "counts": {...}, "mutated": false, "status": "phase1_detect_only"}`). `--json` and threshold-override options mirror sibling `flow` commands. No actuation.

New tests `groundtruth-kb/tests/test_tafe_stuck_flow.py`:

6. Cover each stuck reason produced against a temp MemBase (expired-lease, stalled-pending, owner-gate-stalled, failed-unrecovered); a healthy flow producing no findings; `failed_unrecovered` diagnosis maps the telemetry `failure_class`; the `mutated=False` invariant (assert no row changes after `detect`); a **structural test** asserting the module source contains no `subprocess`, no lease-release / re-dispatch / flow-mutation / MemBase-write surface, and no `bridge/INDEX.md` write (enforcing the no-recovery-actuation bound); and CLI tests (`CliRunner`) for `gt flow stuck` JSON output.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
python -m pytest groundtruth-kb/tests/test_tafe_stuck_flow.py -q --tb=short
Expected: pass; exercises R3 stuck detection (expired-lease / stalled-pending / owner-gate / failed-unrecovered), R6 telemetry-driven diagnosis, R2 lease-read, the healthy-flow negative case, the mutated=False invariant, the no-recovery-actuation structural guard, and the CLI command.

python -m pytest groundtruth-kb/tests/test_tafe_stuck_flow.py groundtruth-kb/tests/test_tafe_stage_attempt_telemetry.py -q --tb=short
Expected: pass; verifies WI-4505 reads the WI-4504 telemetry surface as recorded (additive, read-only).

python -m ruff check groundtruth-kb/src/groundtruth_kb/tafe_stuck_flow.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_stuck_flow.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/tafe_stuck_flow.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_stuck_flow.py
Expected: pass.

git diff --check -- groundtruth-kb/src/groundtruth_kb/tafe_stuck_flow.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_tafe_stuck_flow.py
Expected: no output, exit 0.
```

Spec mapping:

- `SPEC-TAFE-R3` — tests prove each stuck reason is detected and a self-diagnosis is produced from telemetry, with no recovery actuation (structural guard + `mutated=False`).
- `SPEC-TAFE-R6` — tests prove `failed_unrecovered` + diagnosis consume the `outcome`/`failure_class`/`recovery_actions` telemetry fields.
- `SPEC-TAFE-R2` — tests prove expired-lease detection reads lease state and never mutates it.
- `SPEC-TAFE-R5` — tests prove the detector returns a structured report consumable by a future tick, while initiating nothing.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — each linked spec maps to executed test evidence.

## Sequencing

This slice consumes the WI-4504 `stage_attempt_telemetry` surface for the `failed_unrecovered` + diagnosis facets. WI-4504 is GO'd (`bridge/gtkb-tafe-stage-attempt-telemetry-002.md`) with implementation in flight. This proposal recommends WI-4505 **implementation land after WI-4504 reaches VERIFIED**, so the consumed telemetry contract is verified first — the same discipline applied to WI-4499 consuming the WI-4498 engine. Filing the proposal in parallel keeps the authorized observability-track pipeline moving without pre-committing implementation. The non-telemetry facets (expired-lease / stalled-pending / owner-gate) build only on the already-VERIFIED runtime + lease substrate.

## Risk / Rollback

Primary risk is scope creep into recovery actuation (forbidden by the PAUTH). Mitigation: the detector is read/compute/report only; a structural test asserts the absence of any lease-release / re-dispatch / flow-mutation / subprocess / MemBase-write / index-write surface, and `mutated=False` is asserted against a temp DB.

A second risk is duplicating the in-flight WI-4499 dispatch health. Mitigation: the explicit de-duplication boundary above (WI-4505 = per-flow structured detector + R3 diagnosis; WI-4499 = aggregate dispatch-readiness). WI-4505 adds no dispatch/readiness logic.

A third risk is building on the WI-4504 telemetry before it is VERIFIED. Mitigation: the telemetry contract is fixed by WI-4504's GO'd proposal; the proposal recommends implementation after WI-4504 VERIFIED, and the telemetry-dependent facets degrade gracefully if telemetry is absent.

Rollback is a single-commit revert of the new module + test plus the additive `gt flow stuck` CLI block (no removal of existing commands). No KB mutation, no schema change, no integration to unwind.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of a new `gtkb-tafe-stuck-flow-detection` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`, and this slice changes no bridge-authority behavior.

## Recommended Commit Type

`feat:` — adds a new pure TAFE R3 stuck-flow detection/diagnosis module plus an additive read-only `gt flow stuck` CLI surface with comprehensive tests; no behavior change to existing commands, no recovery actuation, and no live dispatch.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
