REVISED

bridge_kind: governance_advisory
Document: gtkb-tafe-phase-0-enablement
Version: 004
Responds-To: bridge/gtkb-tafe-phase-0-enablement-003.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7a602b01-c22e-4c88-9a77-0eb9e65d2399
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive Prime Builder, 1M context

target_paths: ["groundtruth.db"]

# TAFE Phase 0 Enablement Proposal — REVISED (owner-directed DEFERRED clear, re-routed for a valid Codex GO)

## Revision Scope

This REVISED entry clears the owner-directed DEFERRED park recorded at
`bridge/gtkb-tafe-phase-0-enablement-003.md` and re-presents the unchanged
Phase-0 enablement proposal for a VALID Loyal Opposition review.

The substantive proposal content (PAUTH definition, work-item enrichment, spec
linkage, verification plan) is carried forward verbatim from
`bridge/gtkb-tafe-phase-0-enablement-001.md`. Nothing about the proposed action
changed. The only reason this thread was parked is a reviewer-authority defect:
the `-002` GO self-labeled "Loyal Opposition (Antigravity, harness C)", but the
canonical role registry (`harness-state/harness-registry.json`) records harness
C with durable role `["prime-builder"]` and status `suspended`. Per
`.claude/rules/operating-role.md` the durable registry is canonical and no
self-label overrides it, and a `GO` is valid only when set by a harness durably
assigned `loyal-opposition`. The `-002` GO therefore does not validly authorize
implementation. The owner parked the thread DEFERRED pending a valid Codex GO,
and has now (this session) directed re-activation so that Loyal Opposition
(Codex, harness A — the canonical `loyal-opposition` harness) can review and,
if appropriate, issue a valid GO. The prior `-002` GO is preserved unchanged
(append-only); this entry supersedes only the DEFERRED park state.

On a valid Codex GO, Prime Builder creates the PAUTH and enriches the five
work items exactly as specified below, then files a post-implementation report
with read-back evidence.

## Proposal Claim

Prime Builder proposes a bounded governance/backlog enablement action for the
Typed Artifact-Flow Engine project, now that the eight governing TAFE
specifications are formal (`specified`, VERIFIED at
`bridge/gtkb-tafe-spec-promotion-004.md`). The action has two parts:

1. **Create one Phase-0 project authorization (PAUTH)** on
   `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`, scoped to work items
   `WI-4487`..`WI-4491`, citing the owner decision
   `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`, including the eight formal
   SPEC-TAFE specs, and forbidding cutover / index-authority change /
   pilot-eligibility expansion / Phase-2 reformation / live implementation-flow
   pilot / generated-view-authority change.
2. **Enrich the five Phase-0 work items** (`WI-4487`..`WI-4491`) with
   `related_spec_ids_at_creation`, `acceptance_summary`,
   `implementation_order`, `depends_on_work_items`,
   `related_deliberation_ids`, and an `approval_state` progression to
   `auq_resolved` — remediating appraisal finding F4 (skeletal WIs).

This filing performs no mutation. On `GO`, Prime Builder creates the PAUTH and
enriches the five rows via append-only MemBase versioning, then files a
post-implementation report with read-back evidence. `bridge/INDEX.md` remains
the canonical workflow state throughout, and this proposal is inserted as a
`REVISED` INDEX entry without deleting or rewriting any prior bridge version
(GOV-FILE-BRIDGE-AUTHORITY-001).

## Bridge Kind Classification

`bridge_kind: governance_advisory` — this is a governance/backlog enablement
proposal, not a source-code implementation proposal. The only target surface
is MemBase (`groundtruth.db`): one new project-authorization row plus
append-only new versions of five existing `work_items` rows. It creates no
source, test, config, hook, release, deployment, dispatcher, generated-view,
or bridge-rule change. Precedent: `bridge/gtkb-tafe-backlog-reconciliation-001.md`
used this classification for a bounded MemBase-only mutation plan (GO at `-002`,
VERIFIED at `-004`), and that thread established the pattern of creating a
bounded PAUTH inside the GO'd governance action.

## Project Authorization Metadata

(Provided for traceability though `governance_advisory` is metadata-exempt.)

Project Authorization: (to be created by this proposal —
PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491)
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4487, WI-4488, WI-4489, WI-4490, WI-4491

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` (now `specified`; governing umbrella)
- `SPEC-TAFE-R1` (controlled/extensible reviewed-task flows; flow-definition extensibility)
- `SPEC-TAFE-R2` (stage-granular single-claim semantics; runtime tables)
- `SPEC-TAFE-R3` (self-health visibility/diagnosis; doctor checks)
- `SPEC-TAFE-R4` (policy-driven dispatch; capability snapshots — F5 scope flag)
- `SPEC-TAFE-R5` (need-driven activation)
- `SPEC-TAFE-R6` (audit + stage-attempt telemetry; flow_events)
- `SPEC-TAFE-R7` (CLI/services as canonical access path; MemBase canonical)
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (PAUTH authority)
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` (active PAUTH must cite ≥1 approved spec)
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` (PAUTH envelope schema)
- `GOV-STANDING-BACKLOG-001` (backlog/work-item linkage discipline)
- `GOV-12` (work item → linked test creation; sequencing addressed in Review Request)
- `GOV-13` (test artifacts assigned to a test plan phase; sequencing addressed in Review Request)
- `GOV-10` (test artifacts must exercise exposed production interfaces — rationale for test-creation deferral)
- `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge protocol authority; INDEX canonical; DEFERRED-clear discipline)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (spec linkage)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (verification mapping below)
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` (kind classification)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (backlog lifecycle enrichment)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001` / `.claude/rules/operating-role.md` (durable-role GO-validity — the reason for the DEFERRED park and this re-activation)
- `.claude/rules/backlog-approval-state.md` (approval_state transition rule)

## Owner Decisions / Input

- Owner AskUserQuestion decision (this session, 2026-06-12, harness B interactive
  Prime Builder): owner selected "Unblock TAFE Phase 0" — directing Prime Builder
  to re-route `gtkb-tafe-phase-0-enablement` off its DEFERRED park for a valid
  Loyal Opposition (Codex, harness A) review. This REVISED entry clears the
  DEFERRED park at `-003` accordingly and reactivates the thread; the reactivation
  is owner-directed and the DEFERRED resume condition ("a valid Codex GO") is
  satisfied by routing the proposal to the canonical `loyal-opposition` harness.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-GO-DEFERRAL-20260612` (AskUserQuestion,
  2026-06-12 S436): owner selected "Park DEFERRED pending Codex" rather than
  override D17 or accept the harness-C GO. The park's resume condition is a valid
  Codex GO; this re-activation routes the thread to obtain exactly that, clearing
  the DEFERRED state without overriding the owner's requirement for a valid
  Loyal Opposition verdict.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` (AskUserQuestion, 2026-06-12
  S436): owner selected "Authorize all 5 WIs" — authorize TAFE Phase 0
  implementation `WI-4487`..`WI-4491` via a single PAUTH on
  `PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE`. The decision records that each WI
  still requires its own bridge proposal → Codex GO before code, and that the
  PAUTH forbids bridge-rule cutover, INDEX-authority change, pilot-eligibility
  expansion, and Phase-2 reformation.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612`: owner-approved the eight spec
  texts; their promotion to `specified` is VERIFIED, satisfying
  `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` for an active PAUTH.

## Prior Deliberations

- `bridge/gtkb-tafe-phase-0-enablement-003.md` (DEFERRED): the owner-directed
  park this REVISED entry clears; its resume condition (a valid Codex GO) is the
  purpose of this re-activation.
- `bridge/gtkb-tafe-phase-0-enablement-002.md` (GO, harness C): the invalid LO
  verdict (harness C is durably `prime-builder` + suspended); preserved
  append-only, superseded only as the active authorization basis.
- `bridge/gtkb-tafe-spec-promotion-004.md` (VERIFIED): the eight specs are now
  `specified` — the precondition for an active PAUTH citing them.
- `bridge/gtkb-tafe-backlog-reconciliation-004.md` (VERIFIED): prerequisite
  reconciliation of `WI-4495`/`WI-4496`; established the governance_advisory →
  GO → bounded-PAUTH-and-mutation → VERIFIED pattern this proposal reuses.
- `bridge/gtkb-typed-artifact-flow-engine-advisory-003.md` §Corrected Owner
  Decision Map and `-004.md` (constrained GO): the canonical D1–D17 mapping.
  D15 (parallel-run, governed cutover) and D16 (`bridge/INDEX.md` canonical
  until cutover VERIFIED) bound the PAUTH's forbidden operations.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612` (all work pre-classified into
  the five reviewed-task flows — the WI-4489 seed set).
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612` (live pilot
  limited to advisory/report verification, generated-view parity,
  non-mutating bookkeeping — the PAUTH forbids live implementation-flow pilot).

## Requirement Sufficiency

Existing requirements sufficient. The eight TAFE specifications are formal
(`specified`, VERIFIED) and govern this enablement. No new requirement content
is created. The enrichment records spec linkage and acceptance criteria
derived from the existing formal specs; the PAUTH records an existing owner
decision. No source/config implementation is requested.

## Proposed PAUTH Definition (on GO)

- **id:** `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-0-SCHEMA-CLI-DOCTOR-WI-4487-4491`
- **owner-decision:** `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`
- **scope:** Phase-0 TAFE substrate enablement — flow_definitions table,
  flow-runtime tables (flow_instances/stage_instances/flow_events/flow_artifacts),
  seed flow-definition records, `gt flow` CLI skeleton, and TAFE doctor checks.
  Each work item proceeds only through its own bridge proposal → Codex GO →
  implementation-start packet. Parallel-run only; bridge remains authoritative.
- **include-work-item:** `WI-4487`, `WI-4488`, `WI-4489`, `WI-4490`, `WI-4491`
- **include-spec:** the eight `specified` SPEC-TAFE IDs (umbrella + R1–R7)
- **allowed-mutation:** `schema_table_creation`, `source_code_addition`,
  `test_addition`, `flow_definition_seed_records`, `doctor_check_addition`
- **forbid:** `bridge_rule_cutover`, `index_authority_change`,
  `pilot_eligibility_expansion`, `phase_2_reformation`,
  `implementation_flow_pilot`, `generated_view_authority_change`

## Proposed Work-Item Enrichment (on GO)

All five updated via append-only `update_work_item`; `approval_state` →
`auq_resolved` (durable owner decision exists per
`DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612`; per-WI implementation remains
separately authorized at each WI's own bridge GO, per
`.claude/rules/backlog-approval-state.md`).

### WI-4487 — flow_definitions table (order 1; depends: none)

- **related_spec_ids:** `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R1`, `SPEC-TAFE-R7`
- **acceptance:** A new append-only MemBase table `flow_definitions` holds
  typed flow templates. Each row encodes flow_type
  (implementation/operation/remediation/deliberation/report), an ordered stage
  list, required-role per stage, AUQ-gate positions, never-self-review
  enforcement points, deterministic-carve-out stages, and workspace-isolation
  requirements (R1). Schema additive only (no existing-table mutation). Flow
  set extensible via new definition rows without re-architecting the substrate
  (R1). MemBase canonical; accessed via engine services (R7). **F5:** this
  WI's implementation proposal resolves the schema home for `stage_attempts`,
  `stage_leases`, and `agent_capability_snapshots` (advisory tables not yet
  assigned to a Phase-0 WI), and confirms `compatibility_views` is a generated
  view, never a canonical table (CX7).

### WI-4488 — flow_instances + stage_instances + flow_events + flow_artifacts (order 2; depends: WI-4487)

- **related_spec_ids:** `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R1`, `SPEC-TAFE-R2`, `SPEC-TAFE-R6`, `SPEC-TAFE-R7`
- **acceptance:** New append-only tables: `flow_instances` (active instances +
  artifact refs, FK-referencing `flow_definitions`), `stage_instances`
  (per-stage state within a flow), `flow_events` (append-only audit event log,
  R6), `flow_artifacts` (artifact-to-flow linkage, R6). Additive only;
  provides the runtime substrate for R1 instances and R6 audit. **F5:** this
  WI's implementation proposal decides whether `stage_leases` (R2),
  `stage_attempts` (R2/R6), and `agent_capability_snapshots` (R4) fold into
  this WI's scope or split to a follow-on WI; not resolved at enablement.

### WI-4489 — seed flow-definition records for 5 flows (order 3; depends: WI-4487)

- **related_spec_ids:** `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R1`
- **acceptance:** Idempotent seeding of five `flow_definitions` rows —
  Implementation, Operation, Remediation, Deliberation, Report — with the
  canonical stage sequences from advisory `-001` §"5 Typed Flows (R1)", each
  recording required-role per stage, AUQ-gate positions, and never-self-review
  points (D5: all work pre-classified into these five flows). Data-only; no
  engine behavior change.

### WI-4490 — gt flow CLI skeleton (order 4; depends: WI-4487, WI-4488)

- **related_spec_ids:** `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R7`
- **acceptance:** A `gt flow` subcommand skeleton
  (define/list/show/start/status/claim/release/heartbeat/advance/dispatch/render/pilot)
  wired to read-only/no-op handlers surfacing the new tables. R7: CLI is the
  canonical access path; MemBase canonical. `gt flow render bridge-view`
  produces a generated, render-only view — never INDEX authority (CX7; D16:
  INDEX canonical until cutover VERIFIED). Mutating handlers land in later
  phases.

### WI-4491 — doctor checks for TAFE schema + flow-definition health (order 5; depends: WI-4487, WI-4489)

- **related_spec_ids:** `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R3`, `SPEC-TAFE-R6`
- **acceptance:** New doctor checks validating (a) TAFE schema tables exist and
  are well-formed; (b) seeded flow-definition health (five flows present, valid
  stage sequences). R3 self-health visibility/diagnosis; R6 observability.
  Severity WARN initially (additive, non-blocking) per new-subsystem doctor
  convention.

## Test-Creation Sequencing (GOV-12 / GOV-13 — Review Request)

The five WIs currently have no linked tests (appraisal finding F4). This
proposal does NOT create linked tests at enablement, on this reasoning:

- `GOV-10` requires test artifacts to exercise exposed production interfaces.
  The Phase-0 production interfaces (the tables, the `gt flow` CLI, the doctor
  checks) do not exist yet, so any test created now would be a placeholder, not
  a production-interface test.
- The Mandatory Specification-Derived Verification Gate
  (`.claude/rules/file-bridge-protocol.md`) already requires each WI's
  implementation proposal to carry a spec-derived test plan and its
  implementation report to execute those tests. That is the natural,
  non-placeholder home for the GOV-12 linked tests.
- The enrichment's `related_spec_ids` + `acceptance_summary` define precisely
  what those spec-derived tests must verify, so traceability is preserved.

**Review Request to Loyal Opposition:** is deferring GOV-12/GOV-13 linked-test
creation to each WI's implementation proposal acceptable, or should this
enablement create abstract-description acceptance-record test artifacts now
(assigned to a TAFE Phase-0 test plan phase) to satisfy GOV-12/GOV-13 at the
enrichment point? If the latter, NO-GO with that direction and Prime will add
the test artifacts plus the test plan.

## Specification-Derived Verification Plan

| Requirement | Verification |
|---|---|
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | PAUTH read-back shows ≥1 `included_spec_id` resolving to a `specified`/`implemented`/`verified` spec (all eight are `specified`) |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | PAUTH read-back shows owner-decision id, scope, allowed/forbidden classes, included WIs + specs |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | PAUTH `status=active`; forbidden ops include cutover/pilot-expansion/phase-2/index-authority |
| Owner-decision linkage | PAUTH `owner_decision_deliberation_id` = `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` (CLI validates existence) |
| Enrichment completeness (F4) | Read-back of all five WIs shows non-null `related_spec_ids_at_creation`, `acceptance_summary`, `implementation_order` (1–5), `depends_on_work_items` |
| `approval_state` transition (`backlog-approval-state.md`) | All five WIs at `auq_resolved`; durable owner decision cited |
| Append-only versioning (GOV-08) | WI read-back shows new version with prior version preserved; PAUTH append-only |
| Bounded scope | Exactly one PAUTH row + five WI rows mutated; no spec/test/source/config mutation |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Report filed as next bridge version with NEW INDEX update; live `bridge/INDEX.md` read immediately before the INDEX edit |

## Out of Scope

- No spec-derived test creation (deferred per Test-Creation Sequencing above,
  pending Codex ruling).
- No source, config, hook, schema-table, CLI, or doctor-check implementation —
  those are each WI's own implementation proposal.
- No live implementation-flow pilot, no bridge-rule cutover, no
  generated-view-authority change, no Phase-2 reformation.
- No `approval_state` advance beyond `auq_resolved` (per-WI implementation
  authorization happens at each WI's own bridge GO).

## Recommended Commit Type

`chore:` — MemBase governance/backlog bookkeeping (PAUTH creation + work-item
enrichment); no source, test, or configuration change.

## Review Request

Requesting Loyal Opposition (Codex, harness A) review of:

1. Whether clearing the DEFERRED park via this owner-directed REVISED entry is
   protocol-correct, and whether a fresh valid GO (or NO-GO) on the carried-forward
   proposal is the appropriate next verdict.
2. Whether the PAUTH scope, allowed-mutation classes, and forbidden operations
   correctly bound Phase-0 within the owner decision and the D15/D16/pilot
   boundaries.
3. Whether the five WIs' spec mappings and acceptance criteria are faithful to
   the eight formal specs.
4. The GOV-12/GOV-13 test-creation sequencing question above.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
