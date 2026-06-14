REVISED

# WI-4495 (re-cast): TAFE Live Implementation-Flow Pilot (parallel/shadow, parity-checked)

bridge_kind: prime_proposal
Document: gtkb-tafe-live-impl-flow-pilot
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-14 UTC
Responds to: bridge/gtkb-tafe-live-impl-flow-pilot-002.md (Loyal Opposition NO-GO)

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 896e79f0-533b-4f19-8034-449a0a2dda64
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code dispatched bridge auto-dispatch session via ::init gtkb pb; cross-harness event-driven trigger run 2026-06-14T00-20-14Z-prime-builder-B-2ced2d; owner pre-approved live-pilot design

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

## Revision Scope (addresses NO-GO at -002)

This REVISED supersedes the operative claims in `-001` that contradicted live
`bridge/INDEX.md` and live MemBase state. The technical design (live
parallel/shadow pilot + semantic parity via WI-4507's renderer + no
`bridge/INDEX.md` write) is unchanged; only the lifecycle/authorization framing
is corrected. Three findings, each addressed:

- **P1 (parked-draft language).** The `-001` "PARKED DRAFT — do not promote
  until WI-4507 VERIFIED" section and the "WITHOUT a `bridge/INDEX.md` entry /
  NOT yet actionable" language are removed from operative scope and preserved
  below as a clearly historical **Promotion History** section. This proposal is
  **live and actionable**: WI-4507 is VERIFIED and `bridge/INDEX.md` indexes
  this thread as latest `NEW` (now `REVISED`).
- **P1 (WI-4495 lifecycle).** The `-001` claims "re-form WI-4495 to an active
  resolution state" and "WI-4495 stays unresolved until terminal VERIFIED" are
  **withdrawn**. They are replaced with the live MemBase state: WI-4495 is
  terminal `stage=resolved` / `resolution_status=resolved`, owner-directed
  "Promote, keep WI-4495 resolved" (owner AUQ 2026-06-13), terminal per
  SPEC-1602 (no reopen path), `superseded_by=gtkb-tafe-backlog-reconciliation`,
  and serves as the **historical / re-cast authority** for this live pilot. No
  lifecycle transition of WI-4495 is expected or performed by this slice.
- **P1 (PAUTH breadth).** Resolved by the live PAUTH read-back and justification
  in the **Project Authorization (live read-back + justification)** section
  below, with `target_paths` shown to be the only implementation files the GO
  authorizes.

## Promotion History (historical — NOT operative guidance)

> Preserved per `.claude/rules/file-bridge-protocol.md` § "Parked-Draft
> Pattern". `-001` was authored as a parked draft (in `bridge/` without a
> `bridge/INDEX.md` entry) because its parity check imports
> `render_tafe_bridge_index_preview` from WI-4507, whose post-impl → VERIFIED
> was then pending. **That gate is now satisfied:** WI-4507
> (`gtkb-tafe-bridge-index-preview`) is latest `VERIFIED`, and the parked draft
> was promoted to a live `NEW` INDEX entry (git
> `c8cb00fcb chore(bridge): promote gtkb-tafe-live-impl-flow-pilot parked draft
> to NEW`). The promotion did not rewrite the internal parked-draft and
> WI-lifecycle language; this REVISED corrects that drift. No further owner
> approval gate is required to review or build — the design is owner
> pre-approved (`DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613`).

## Summary

Implement WI-4495 (re-cast) as the **live implementation-flow pilot**: TAFE
actively *drives* and *enforces* the lifecycle of ONE designated real bridge
thread, in **parallel/shadow** with the canonical bridge, and **parity-checks**
its TAFE projection against the canonical `bridge/INDEX.md` — producing the
evidence a future cutover would need WITHOUT any authority change.

This is NOT a "stage engine" (the `FlowRuntimeService` runtime is already
generic and flow-type-agnostic; the five flow definitions are seeded;
WI-4500–4503 lifecycle coverage is VERIFIED). It is the *live, enforcing,
parity-checking* layer over that substrate, operating on real bridge state
rather than test fixtures.

Single new module + an additive CLI command + tests:

1. **Live-pilot module** — `groundtruth-kb/src/groundtruth_kb/tafe_live_pilot.py`:
   given a designated real bridge thread slug, the live pilot (a) reads the
   thread's canonical latest status from `bridge/INDEX.md`; (b) gets-or-creates a
   TAFE `flow_instance` for it (subject_id = slug, implementation flow
   definition); (c) drives the TAFE flow to the stage that corresponds to the
   thread's current bridge status, ENFORCING the definition's declared
   constraints — legal `stage_sequence` transition order, `required_roles_by_stage`,
   and `never_self_review_stages` (checked against the real thread's per-version
   authors); (d) computes a **semantic parity verdict** (see below); (e) records
   a `flow_event` carrying the verdict + any findings. It performs NO write to
   `bridge/INDEX.md`.
2. **Read-only CLI** — `gt flow pilot <thread-slug> [--stdout]` under the
   existing `flow` group: resolves the service, runs the pilot on the designated
   thread, writes the TAFE-side preview to the non-canonical
   `.gtkb-state/tafe-preview/` path (reusing WI-4507's renderer), prints the
   parity verdict + findings, and structurally REFUSES to write `bridge/INDEX.md`.
3. **Tests** — `groundtruth-kb/tests/test_tafe_live_pilot.py`: drive a controlled
   implementation-flow scenario and assert legal-transition enforcement,
   required-role enforcement, never-self-review violation detection (same actor
   reviewing own proposal is flagged), parity MATCH and parity DIVERGENCE
   detection, finding records, and an AST structural guard that the module never
   writes `bridge/INDEX.md`.

### Semantic parity check (grounded in WI-4507's actual renderer)

WI-4507's `render_tafe_bridge_index_preview(flow_instances, stage_instances, *, now)`
renders TAFE state per **stage** (`<status>: <stage_id> (role=…, claim=…)`), NOT
per bridge-version (`GO: bridge/<slug>-NNN.md`). So parity is **semantic, not a
text-diff**: map the bridge thread's canonical latest status to its expected
TAFE stage via a fixed `BRIDGE_STATUS_TO_STAGE` table for the implementation
flow (e.g. `NEW→propose`, `NO-GO→review`, `GO→implement`, post-impl
`NEW→verify`, `VERIFIED→complete`), then assert the pilot flow's current stage
equals the expected stage. The renderer produces the human-readable TAFE-side
projection for operator inspection; the verdict is computed from the structured
flow/stage rows. Divergence ⇒ a recorded finding, and **the canonical
`bridge/INDEX.md` wins** — TAFE never overrides it.

### Bounding (explicit out-of-scope)

This slice ships the live pilot bounded to parallel/shadow + parity evidence. It
MUST NOT:
- Write `bridge/INDEX.md`, change its authority, register an authoritative
  generated view, or dual-write. The PAUTH forbids `authoritative_generated_view`,
  `dual_write`, `cutover`; `GOV-FILE-BRIDGE-AUTHORITY-001` keeps `bridge/INDEX.md`
  canonical.
- Perform cutover (WI-4508/4510) or cutover-evidence gathering (WI-4509) — those
  remain reserved for a separate owner decision.
- Stand up a live dispatch substrate, mutate MemBase schema, or drive more than
  the single designated pilot thread.

## Project Authorization (live read-back + justification)

Per Required Revision 4, this REVISED takes option (b) of the NO-GO: justify the
existing PAUTH with current owner-backed evidence and the live read-back, rather
than mutate the authorization envelope from a dispatched (non-owner-interactive)
session. Live read-back of
`PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-2-REFORMATION-IMPL-FLOW-PILOT`
(`gt projects authorizations PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE --json`,
2026-06-14):

- `status`: `active`
- `allowed_mutation_classes`: `["source", "test"]`
- `forbidden_operations`: `["cutover", "dual_write", "live_dispatch_substrate", "authoritative_generated_view", "kb_schema_change"]`
- `included_work_item_ids`: `["WI-4495", "WI-4500", "WI-4501", "WI-4502", "WI-4503", "WI-4507"]`
- `owner_decision_deliberation_id`: `DELIB-TAFE-IMPL-FLOW-PILOT-SCOPE-EXPANSION-20260613`
- `scope_summary`: "Re-form the superseded implementation-flow stage engine
  (WI-4495) and implement the flow-type state machines WI-4500..WI-4503 plus the
  compatibility-view generator WI-4507, as a LIVE but PARALLEL/SHADOW
  implementation-flow pilot. bridge/INDEX.md remains canonical per
  GOV-FILE-BRIDGE-AUTHORITY-001 … Source+test only."

**Why the existing PAUTH is the correct authorization for this slice, and why no
duplicate-effort risk exists:**

1. **The envelope already fences this slice exactly.** Its `allowed_mutation_classes`
   are `source`/`test` only, and its `forbidden_operations`
   (`cutover`, `dual_write`, `live_dispatch_substrate`,
   `authoritative_generated_view`, `kb_schema_change`) are precisely the
   exclusions this proposal commits to. The authorization cannot license any
   operation this slice forswears.
2. **`target_paths` are the only implementation files the GO authorizes.** This
   proposal's `target_paths` are exactly
   `groundtruth-kb/src/groundtruth_kb/tafe_live_pilot.py` (new),
   `groundtruth-kb/src/groundtruth_kb/cli.py` (additive `gt flow pilot` block),
   and `groundtruth-kb/tests/test_tafe_live_pilot.py` (new). The
   implementation-start packet (`scripts/implementation_authorization.py begin`)
   binds the session to these paths and fails closed outside them, independent of
   the PAUTH's broader WI list.
3. **No duplicate effort against the sibling WIs.** `WI-4500`, `WI-4501`,
   `WI-4502`, `WI-4503` (flow-type state machines) and `WI-4507` (compatibility-
   view renderer) named in the PAUTH are already VERIFIED/complete. None of their
   deliverables overlap this slice's `target_paths`: the pilot module *consumes*
   WI-4507's `render_tafe_bridge_index_preview` and builds on the WI-4500–4503
   VERIFIED runtime — it does not re-implement them. The duplicate-effort check
   therefore resolves clean.
4. **PAUTH narrowing is an owner-expected governed follow-on, not a blocker.**
   `DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613` records the owner's intent
   to re-scope the PAUTH to the live-pilot-only slice after WI-4507 verifies.
   That re-scoping is a project-authorization mutation that must run through the
   governed `gt projects authorize` path with the precise narrowed scope, and is
   out of scope for this dispatched source/test revision. It is tracked as the
   owner-expected next step; it does not gate this bounded slice, which is already
   fenced by points 1–3.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` — TAFE governs reviewed-task flows
  as typed, staged artifacts in parallel-run while `bridge/INDEX.md` stays
  canonical until a separate governed cutover; this slice is the live, enforcing,
  parallel-run half.
- `SPEC-TAFE-R1` (Controlled Artifact Routing) — the implementation flow routes
  its subject through an ordered, role-gated stage sequence; the pilot drives +
  enforces exactly that against a real thread.
- `SPEC-TAFE-R7` (Interface Principle) — MemBase canonical; the pilot
  reads/writes TAFE state only through the public service API and reads
  `bridge/INDEX.md` read-only.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the live `bridge/INDEX.md` remains canonical;
  the pilot writes nothing to it (structural guard) and a divergence resolves in
  the canonical index's favor.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — PAUTH, project, work
  item, target paths, and governing specs are concretely linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — machine-readable
  project-authorization metadata is in the header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan maps
  the enforcement, parity, and no-write invariants to executed tests.
- `GOV-STANDING-BACKLOG-001` — WI-4495 (re-cast, terminal `resolved`) is the live
  backlog authority of record for this slice; WI-4508/4509/4510 remain excluded.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implementation proceeds under
  the cited PAUTH plus the forthcoming Loyal Opposition GO and implementation-start
  packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets are inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the pilot is a durable governed source
  artifact; WI-4495 remains terminal `resolved` (re-cast authority) and is not
  reopened by this slice.

## Prior Deliberations

- `DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613` — owner pre-approval of
  THIS design (parallel/shadow enforcement + semantic parity via WI-4507's
  renderer; no cutover); also records owner intent to re-scope the PAUTH to the
  live-pilot slice after WI-4507 verifies.
- `DELIB-TAFE-LIVE-PILOT-PURSUE-AND-PREMISE-CORRECTION-20260613` — owner decision
  to pursue the live pilot; corrects the earlier "flow types blocked / build a
  stage engine" premise (the runtime is generic; the flow types were never
  blocked).
- `DELIB-TAFE-IMPL-FLOW-PILOT-SCOPE-EXPANSION-20260613` — owner authorization
  expanding the implementation-flow pilot scope; the cited PAUTH's
  `owner_decision_deliberation_id`.
- `bridge/gtkb-typed-artifact-flow-engine-advisory-004.md` — constrained GO;
  Condition 2 reserved any live implementation-flow pilot for a separate owner
  decision (now satisfied by the three DELIBs above).
- `bridge/gtkb-tafe-backlog-reconciliation-004.md` — prior verification of the
  WI-4495/WI-4496 supersession state; the source of the live terminal-`resolved`
  WI-4495 record this REVISED aligns to.
- `bridge/gtkb-tafe-bridge-index-preview-004.md` (VERIFIED) — WI-4507 compat-view
  renderer (`render_tafe_bridge_index_preview`) the parity check consumes;
  build dependency now satisfied.
- `bridge/gtkb-tafe-flow-type-lifecycle-coverage-004.md` (VERIFIED) — WI-4500–4503
  flow-type lifecycle coverage proving the generic runtime advances each flow
  type; the pilot builds on that VERIFIED substrate.
- `bridge/gtkb-tafe-runtime-tables-schema-004.md` (VERIFIED) — `flow_instances`
  + `stage_instances` substrate the pilot drives.

## Owner Decisions / Input

This proposal depends on owner approval, which is already on record (no new
AskUserQuestion required to review or build):

- **`DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613`** — the owner
  PRE-APPROVED this specific design (parallel/shadow drive + enforce + semantic
  parity via WI-4507's renderer; `bridge/INDEX.md` canonical; no cutover). This
  is the owner-decision evidence authorizing Loyal Opposition review and build
  now that the WI-4507 build dependency is satisfied.
- **`DELIB-TAFE-IMPL-FLOW-PILOT-SCOPE-EXPANSION-20260613`** — owner authorization
  for the implementation-flow pilot scope; the cited PAUTH's owner decision.
- **WI-4495 lifecycle is owner-fixed.** Owner AUQ 2026-06-13 ("Promote, keep
  WI-4495 resolved") fixes WI-4495 as terminal `resolved`; this REVISED conforms
  and requests no lifecycle change.
- The slice stays within `source`/`test` mutation classes and respects every
  forbidden-operation clause (`cutover`, `dual_write`, `live_dispatch_substrate`,
  `authoritative_generated_view`, `kb_schema_change`). No expanded owner
  authorization is requested. PAUTH narrowing remains an owner-expected governed
  follow-on (above) and is not requested here.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` +
`SPEC-TAFE-R1` define the implementation flow as an ordered, role-gated,
never-self-review-constrained stage sequence; `SPEC-TAFE-R7` and
`GOV-FILE-BRIDGE-AUTHORITY-001` keep MemBase + `bridge/INDEX.md` canonical and
bound the pilot to non-authoritative parallel run. The owner pre-approval
(`DELIB-TAFE-LIVE-PILOT-DESIGN-PREAPPROVAL-20260613`) fixes the design. No new or
revised requirement is needed: this slice implements the specified live
parallel-run behavior over already-VERIFIED substrate and excludes any authority
change.

## Implementation Plan

1. **`tafe_live_pilot.py`** — `BRIDGE_STATUS_TO_STAGE` mapping;
   `parse_index_thread_status(index_text, slug)` (read-only parse of the
   canonical block's latest status); `run_live_pilot(slug, *, service, index_text,
   now, actors)` that gets-or-creates the flow instance, drives stage instances to
   the expected stage enforcing legal order + `required_roles_by_stage` +
   `never_self_review_stages` (using `actors` derived from the real thread's
   per-version authors), computes the semantic parity verdict, records a
   `flow_event`, and returns a frozen `LivePilotResult(slug, expected_stage,
   actual_stage, parity_ok, divergences, never_self_review_violations,
   preview_text)`. No `bridge/INDEX.md` write; `preview_text` comes from
   `render_tafe_bridge_index_preview`.
2. **`cli.py`** — additive `gt flow pilot <slug> [--stdout]`; writes the preview
   under `.gtkb-state/tafe-preview/`, prints the verdict, refuses an `INDEX.md`
   output target.
3. **Tests** — enforcement (legal/illegal transition, role, never-self-review
   violation), parity match + divergence, finding records, empty/edge inputs, and
   the AST no-`INDEX.md`-write structural guard.

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

Spec mapping: `SPEC-TAFE-R1` ⇒ transition/role enforcement tests;
`GOV-FILE-BRIDGE-AUTHORITY-001` ⇒ no-INDEX.md-write guard +
divergence-favors-canonical test; `SPEC-TAFE-R7` ⇒ public-API-only +
read-only-index assertions; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` ⇒
each linked spec maps to executed evidence.

## Risk / Rollback

Primary risk: scope creep toward authoritative/cutover behavior. Mitigation:
parallel/shadow only; no `bridge/INDEX.md` write (AST guard); divergence resolves
in the canonical index's favor; forbidden-operation clauses respected. Secondary
risk: building against an unstable renderer — mitigated because WI-4507 is now
VERIFIED. Rollback: single-commit revert of the new module + test + the additive
`gt flow pilot` block in `cli.py`; no KB mutation, no schema change.

## Recommended Commit Type

`feat:` — adds the live implementation-flow pilot module + an additive read-only
CLI surface + tests; no authority change, no cutover, no live dispatch substrate.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
