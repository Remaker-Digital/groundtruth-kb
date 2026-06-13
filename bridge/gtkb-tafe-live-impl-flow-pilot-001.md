NEW

# WI-4495 (re-cast): TAFE Live Implementation-Flow Pilot (parallel/shadow, parity-checked)

bridge_kind: prime_proposal
Document: gtkb-tafe-live-impl-flow-pilot
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 09c03e33-cc0f-4d57-8c6d-523d79c19ff7
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; autonomous Prime Builder via ::init gtkb pb; owner-authorized /loop drive; owner pre-approved live-pilot design

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-2-REFORMATION-IMPL-FLOW-PILOT
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4495

target_paths: ["groundtruth-kb/src/groundtruth_kb/tafe_live_pilot.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_tafe_live_pilot.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

---

## PARKED DRAFT — do not promote until WI-4507 VERIFIED

This is a **parked draft** per `.claude/rules/file-bridge-protocol.md` § "Parked-Draft Pattern": it is intentionally written to `bridge/` WITHOUT a `bridge/INDEX.md` entry, so it is NOT yet actionable for Loyal Opposition review. The applicability preflight will return `ERR_NO_INDEX_ENTRY` for this file; that is expected and not a defect.

**Promotion gate.** This draft becomes a live `NEW` proposal only when **WI-4507 (`gtkb-tafe-bridge-index-preview`, the compatibility-view renderer) reaches VERIFIED**, because the parity check below imports `render_tafe_bridge_index_preview`. WI-4507's implementation is already committed (`f9268f07`); only its post-impl report → VERIFIED is pending. On WI-4507 VERIFIED the promoter must: (1) re-form WI-4495 to an active resolution state (re-cast from the superseded "full stage engine" to this live pilot), citing `DELIB-TAFE-LIVE-PILOT-PURSUE-AND-PREMISE-CORRECTION-20260613`; (2) optionally narrow the cited PAUTH to the live pilot; (3) add the `NEW` INDEX entry via the serialized index writer; (4) run `bridge_applicability_preflight.py` + `adr_dcl_clause_preflight.py` and revise if any required spec/blocking gap surfaces; (5) commit the promotion tagged `gtkb-tafe-live-impl-flow-pilot: parked draft promoted to NEW`. Owner has PRE-APPROVED this design (`DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613`), so no further owner-approval gate is required to promote, review, or build.

## Summary

Implement WI-4495 (re-cast) as the **live implementation-flow pilot**: TAFE actively *drives* and *enforces* the lifecycle of ONE designated real bridge thread, in **parallel/shadow** with the canonical bridge, and **parity-checks** its TAFE projection against the canonical `bridge/INDEX.md` — producing the evidence a future cutover would need WITHOUT any authority change.

This is NOT a "stage engine" (the `FlowRuntimeService` runtime is already generic and flow-type-agnostic; the five flow definitions are seeded; WI-4500-4503 lifecycle coverage is VERIFIED). It is the *live, enforcing, parity-checking* layer over that substrate, operating on real bridge state rather than test fixtures.

Single new module + an additive CLI command + tests:

1. **Live-pilot module** — `groundtruth-kb/src/groundtruth_kb/tafe_live_pilot.py`: given a designated real bridge thread slug, the live pilot (a) reads the thread's canonical latest status from `bridge/INDEX.md`; (b) gets-or-creates a TAFE `flow_instance` for it (subject_id = slug, implementation flow definition); (c) drives the TAFE flow to the stage that corresponds to the thread's current bridge status, ENFORCING the definition's declared constraints — legal `stage_sequence` transition order, `required_roles_by_stage`, and `never_self_review_stages` (checked against the real thread's per-version authors); (d) computes a **semantic parity verdict** (see below); (e) records a `flow_event` carrying the verdict + any findings. It performs NO write to `bridge/INDEX.md`.
2. **Read-only CLI** — `gt flow pilot <thread-slug> [--stdout]` under the existing `flow` group: resolves the service, runs the pilot on the designated thread, writes the TAFE-side preview to the non-canonical `.gtkb-state/tafe-preview/` path (reusing WI-4507's renderer), prints the parity verdict + findings, and structurally REFUSES to write `bridge/INDEX.md`.
3. **Tests** — `groundtruth-kb/tests/test_tafe_live_pilot.py`: drive a controlled implementation-flow scenario and assert legal-transition enforcement, required-role enforcement, never-self-review violation detection (same actor reviewing own proposal is flagged), parity MATCH and parity DIVERGENCE detection, finding records, and an AST structural guard that the module never writes `bridge/INDEX.md`.

### Semantic parity check (grounded in WI-4507's actual renderer)

WI-4507's `render_tafe_bridge_index_preview(flow_instances, stage_instances, *, now)` renders TAFE state per **stage** (`<status>: <stage_id> (role=…, claim=…)`), NOT per bridge-version (`GO: bridge/<slug>-NNN.md`). So parity is **semantic, not a text-diff**: map the bridge thread's canonical latest status to its expected TAFE stage via a fixed `BRIDGE_STATUS_TO_STAGE` table for the implementation flow (e.g. `NEW→propose`, `NO-GO→review`, `GO→implement`, post-impl `NEW→verify`, `VERIFIED→complete`), then assert the pilot flow's current stage equals the expected stage. The renderer produces the human-readable TAFE-side projection for operator inspection; the verdict is computed from the structured flow/stage rows. Divergence ⇒ a recorded finding, and **the canonical `bridge/INDEX.md` wins** — TAFE never overrides it.

### Bounding (explicit out-of-scope)

This slice ships the live pilot bounded to parallel/shadow + parity evidence. It MUST NOT:
- Write `bridge/INDEX.md`, change its authority, register an authoritative generated view, or dual-write. The PAUTH forbids `authoritative_generated_view`, `dual_write`, `cutover`; `GOV-FILE-BRIDGE-AUTHORITY-001` keeps `bridge/INDEX.md` canonical.
- Perform cutover (WI-4508/4510) or cutover-evidence gathering (WI-4509) — those remain reserved for a separate owner decision.
- Stand up a live dispatch substrate, mutate MemBase schema, or drive more than the single designated pilot thread.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — TAFE governs reviewed-task flows as typed, staged artifacts in parallel-run while `bridge/INDEX.md` stays canonical until a separate governed cutover; this slice is the live, enforcing, parallel-run half.
- `SPEC-TAFE-R1` (Controlled Artifact Routing) — the implementation flow routes its subject through an ordered, role-gated stage sequence; the pilot drives + enforces exactly that against a real thread.
- `SPEC-TAFE-R7` (Interface Principle) — MemBase canonical; the pilot reads/writes TAFE state only through the public service API and reads `bridge/INDEX.md` read-only.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the live `bridge/INDEX.md` remains canonical; the pilot writes nothing to it (structural guard) and a divergence resolves in the canonical index's favor.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — PAUTH, project, work item, target paths, and governing specs are concretely linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable project-authorization metadata is in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps the enforcement, parity, and no-write invariants to executed tests.
- `GOV-STANDING-BACKLOG-001` — WI-4495 (re-cast) is the backlog authority for this slice; WI-4508/4509/4510 remain excluded.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds under the cited PAUTH plus the forthcoming Loyal Opposition GO and implementation-start packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets are inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the pilot is a durable governed source artifact; WI-4495 stays unresolved until terminal VERIFIED.

## Prior Deliberations

- `DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613` — owner pre-approval of THIS design (parallel/shadow enforcement + semantic parity via WI-4507's renderer; no cutover).
- `DELIB-TAFE-LIVE-PILOT-PURSUE-AND-PREMISE-CORRECTION-20260613` — owner decision to pursue the live pilot; corrects the earlier "flow types blocked / build a stage engine" premise (the runtime is generic; the flow types were never blocked).
- `DELIB-TAFE-IMPL-FLOW-PILOT-SCOPE-EXPANSION-20260613` — owner authorization expanding the implementation-flow pilot scope.
- `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` — constrained GO; Condition 2 reserved any live implementation-flow pilot for a separate owner decision (now satisfied by the three DELIBs above).
- `bridge/gtkb-tafe-bridge-index-preview-001.md` — WI-4507 compat-view renderer (`render_tafe_bridge_index_preview`) the parity check consumes; build dependency.
- `bridge/gtkb-tafe-flow-type-lifecycle-coverage-004.md` (VERIFIED) — WI-4500-4503 flow-type lifecycle coverage proving the generic runtime advances each flow type; the pilot builds on that VERIFIED substrate.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` (VERIFIED) — `flow_instances` + `stage_instances` substrate the pilot drives.

## Owner Decisions / Input

This proposal depends on owner approval, which is already on record (no new AskUserQuestion required to promote or build):

- **`DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613`** — the owner PRE-APPROVED this specific design (parallel/shadow drive + enforce + semantic parity via WI-4507's renderer; `bridge/INDEX.md` canonical; no cutover). This is the owner-decision evidence authorizing promotion, Loyal Opposition review, and build once the WI-4507 build dependency is satisfied.
- **`DELIB-TAFE-IMPL-FLOW-PILOT-SCOPE-EXPANSION-20260613`** — owner authorization for the implementation-flow pilot scope.
- The slice stays within `source`/`test` mutation classes and respects every forbidden-operation clause (`cutover`, `dual_write`, `live_dispatch_substrate`, `authoritative_generated_view`, `kb_schema_change`). No expanded owner authorization is requested.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` + `SPEC-TAFE-R1` define the implementation flow as an ordered, role-gated, never-self-review-constrained stage sequence; `SPEC-TAFE-R7` and `GOV-FILE-BRIDGE-AUTHORITY-001` keep MemBase + `bridge/INDEX.md` canonical and bound the pilot to non-authoritative parallel run. The owner pre-approval (`DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613`) fixes the design. No new or revised requirement is needed: this slice implements the specified live parallel-run behavior over already-VERIFIED substrate and excludes any authority change.

## Implementation Plan

1. **`tafe_live_pilot.py`** — `BRIDGE_STATUS_TO_STAGE` mapping; `parse_index_thread_status(index_text, slug)` (read-only parse of the canonical block's latest status); `run_live_pilot(slug, *, service, index_text, now, actors)` that gets-or-creates the flow instance, drives stage instances to the expected stage enforcing legal order + `required_roles_by_stage` + `never_self_review_stages` (using `actors` derived from the real thread's per-version authors), computes the semantic parity verdict, records a `flow_event`, and returns a frozen `LivePilotResult(slug, expected_stage, actual_stage, parity_ok, divergences, never_self_review_violations, preview_text)`. No `bridge/INDEX.md` write; `preview_text` comes from `render_tafe_bridge_index_preview`.
2. **`cli.py`** — additive `gt flow pilot <slug> [--stdout]`; writes the preview under `.gtkb-state/tafe-preview/`, prints the verdict, refuses an `INDEX.md` output target.
3. **Tests** — enforcement (legal/illegal transition, role, never-self-review violation), parity match + divergence, finding records, empty/edge inputs, and the AST no-`INDEX.md`-write structural guard.

## Spec-Derived Verification Plan

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_live_pilot.py -q --tb=short
Expected: pass; exercises enforcement (transition/role/never-self-review), semantic parity match+divergence, finding records, and the no-INDEX.md-write structural guard.

groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_tafe_index_preview.py -q --tb=short
Expected: pass; confirms the consumed WI-4507 renderer remains green under the new caller.

ruff check + ruff format --check on the three target files
Expected: pass.

git status --short bridge/INDEX.md
Expected: empty (the pilot never mutates the canonical index).
```

Spec mapping: `SPEC-TAFE-R1` ⇒ transition/role enforcement tests; `GOV-FILE-BRIDGE-AUTHORITY-001` ⇒ no-INDEX.md-write guard + divergence-favors-canonical test; `SPEC-TAFE-R7` ⇒ public-API-only + read-only-index assertions; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` ⇒ each linked spec maps to executed evidence.

## Risk / Rollback

Primary risk: scope creep toward authoritative/cutover behavior. Mitigation: parallel/shadow only; no `bridge/INDEX.md` write (AST guard); divergence resolves in the canonical index's favor; forbidden-operation clauses respected. Secondary risk: building against an unstable renderer — mitigated by the promotion gate (build only after WI-4507 VERIFIED). Rollback: single-commit revert of the new module + test + the additive `gt flow pilot` block in `cli.py`; no KB mutation, no schema change.

## Recommended Commit Type

`feat:` — adds the live implementation-flow pilot module + an additive read-only CLI surface + tests; no authority change, no cutover, no live dispatch substrate.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
