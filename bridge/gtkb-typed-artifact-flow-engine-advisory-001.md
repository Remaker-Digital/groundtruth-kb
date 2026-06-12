NEW

bridge_kind: governance_advisory
target_paths: []
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ab9e903c
author_model: claude-opus-4-6
author_model_version: 4.6
author_model_configuration: default

# Typed Artifact-Flow Engine — Advisory Synthesis Proposal

## Summary

This proposal synthesizes the owner's Bridge & Dispatch Architecture Overhaul
directive (7 requirements, R1-R7) with the Codex Loyal Opposition advisory
(`INSIGHTS-2026-06-12-bridge-dispatch-architecture-overhaul-advisory.md`) and
17 owner decisions (D1-D17) captured via structured AskUserQuestion grilling,
plus 7 net-new Codex contributions (CX1-CX7).

The target architecture replaces the current INDEX.md-based bridge dispatch
substrate with a MemBase-backed Typed Artifact-Flow Engine (TAFE) that
provides: typed flow definitions for 5 reviewed-task categories (R1);
single-claim contention elimination (R2); self-health and stuck-flow detection
(R3); policy-driven dispatch by role, capability, cost, and subject (R4);
need-driven activation only (R5); full flow auditability with quality/cost/
performance tracking (R6); and CLI+skills as the canonical data/service surface
(R7).

The existing bridge protocol (GO/NO-GO/VERIFIED discipline, append-only audit,
adversarial role pairing, AUQ gates, never-self-review invariant) remains
authoritative during construction. Migration uses a parallel-run strategy with
governed cutover only after VERIFIED evidence.

## Specification Links

- SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA — Umbrella architecture spec for the Typed Artifact-Flow Engine
- SPEC-TAFE-R1 — Controlled artifact routing across 5 reviewed-task flows
- SPEC-TAFE-R2 — Contention/duplication elimination (single-claim, no duplicate dispatch)
- SPEC-TAFE-R3 — Self-health-awareness, self-diagnosis, self-repair, stuck-flow detection
- SPEC-TAFE-R4 — Policy-driven dispatch (role, capability, cost, subject)
- SPEC-TAFE-R5 — Need-driven activation (never blind polling)
- SPEC-TAFE-R6 — Full flow auditability with quality/cost/performance tracking
- SPEC-TAFE-R7 — All canonical data/services via CLI+skills (not protocol-bearing markdown)
- GOV-ARTIFACT-APPROVAL-001 — Formal artifact approval gate
- GOV-STANDING-BACKLOG-001 — Standing backlog governance contract
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 — SoT freshness principle
- GOV-RELEASE-READINESS-GOVERNED-TESTING-001 — Release readiness governed testing
- GOV-FILE-BRIDGE-AUTHORITY-001 — Live bridge index authority and permanent bridge repair authority
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — Spec linkage mandate
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — Spec-derived testing mandate
- DCL-BRIDGE-KIND-TAXONOMY-ENUM-001 — Bridge kind enum taxonomy
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 — Single-harness operating mode architecture decision
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — Codex hook parity fallback
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — Application isolation placement decision
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001 — Single-harness bridge dispatcher contract
- SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001 — Canonical init keyword syntax
- SPEC-DISPATCH-ENVELOPE-ELEMENT-001 — Dispatch envelope element
- GOV-HARNESS-ONBOARDING-CONTRACT-001 — Harness onboarding contract
- GOV-SESSION-SELF-INITIALIZATION-001 — Session self-initialization
- GOV-SESSION-ROLE-AUTHORITY-001 — Session role authority split

## Prior Deliberations

The following Deliberation Archive records inform this proposal:

- **DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610**: Owner vision to evolve bridge into active orchestrator routing work by stage, efficacy, cost, availability. This proposal is the direct architectural realization.
- **DELIB-REVIEW-INDEPENDENCE-INVARIANT-20260610**: Session-context scoping of never-self-review. Unit of independence is session context, not model identity.
- **DELIB-COST-WASTE-FRAMING-20260610**: Optimize value-per-spend; eliminate waste without sacrificing quality or independent verification.
- **DELIB-FAB10-REMEDIATION-20260610**: Dispatch telemetry, claim contract, INDEX integrity as prerequisites for orchestrator.
- **DELIB-20260612-REENABLE-AUTODISPATCH-WATCHDOG-OFF**: Auto-dispatch re-enabled after storm fixes.
- **DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612** through **D17**: 17 owner decisions from structured grilling session covering never-self-review scope (D1), formal-review stages (D2), typed flow engine selection (D3), AUQ gate semantics (D4), flow-state substrate (D5), testing/linting/formatting carve-outs (D6), workspace isolation (D7), stage-level leases (D8), migration strategy (D9), pilot flow (D10), cutover governance (D11), dispatch-policy model (D12), agent capability snapshots (D13), telemetry granularity (D14), reviewing harnesses (D15), WI-4404 disposition (D16), Codex advisory review route (D17).
- **DELIB-BRIDGE-DISPATCH-OVERHAUL-CX1-20260612** through **CX7**: 7 Codex net-new contributions — parallel-run compatibility views (CX1), stage-level leases with heartbeat/TTL/recovery (CX2), workspace isolation via worktrees (CX3), explicit AUQ blocking-transition semantics (CX4), rendered markdown bridge-view (CX5), phased CLI surface design (CX6), rollback/risk analysis (CX7).

## Owner Decisions / Input

All owner decisions were captured via AskUserQuestion during a structured
`/grill-me-for-clarification` session. Summary of key decisions:

- **D1 (Self-review scope):** Session-scoped. Same transcript = same context = cannot review. Spawned workers independent only with artifact + governed context, not creator scratchpad. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612)
- **D2 (Formal review stages):** All AI judgment gates require disjoint session context. Deterministic checks (lint, format, preflight) exempt. WI-4404 superseded by this overhaul. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D2-20260612)
- **D3 (Typed flow engine):** One engine, multiple typed flows — not separate one-off flows. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612)
- **D4 (AUQ gates):** AUQ is a blocking transition guard within flows. Flow waits for owner; cannot auto-advance past AUQ gates. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D4-20260612)
- **D5 (State substrate):** Canonical flow state in MemBase behind CLI/services. Markdown becomes generated presentation/compatibility view. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612)
- **D6 (Deterministic carve-outs):** Testing, linting, formatting run in-session without flow overhead. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D6-20260612)
- **D7 (Workspace isolation):** Mutating attempts use isolated worktrees. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D7-20260612)
- **D8 (Stage leases):** Stage-level leases with heartbeat, TTL, recovery, cleanup. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D8-20260612)
- **D9 (Migration):** Parallel-run. Existing bridge authoritative until governed cutover. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D9-20260612)
- **D10 (Pilot):** Implementation flow first pilot. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D10-20260612)
- **D11 (Cutover governance):** Cutover requires bridge proposal + LO review + owner AUQ. Not auto-promoted. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D11-20260612)
- **D12 (Dispatch policy):** Role + capability + cost + subject weighted scoring model. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D12-20260612)
- **D13 (Capability snapshots):** Agent capability snapshots at dispatch time for reproducibility. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612)
- **D14 (Telemetry):** Per-stage-attempt granularity. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D14-20260612)
- **D15 (Reviewing harnesses):** All capable harnesses beyond Codex should review the advisory. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D15-20260612)
- **D16 (WI-4404):** Superseded by this overhaul. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D16-20260612)
- **D17 (Codex advisory route):** Codex review through normal bridge protocol. (DELIB-BRIDGE-DISPATCH-OVERHAUL-D17-20260612)

## Requirement Sufficiency

New specifications are required. 8 candidate specifications have been captured
in MemBase as `candidate` status specs:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` (umbrella architecture)
- `SPEC-TAFE-R1` through `SPEC-TAFE-R7` (one per owner requirement)

These candidate specs will be promoted through the governed approval path
as part of the project formation step. No source/config/test implementation
is proposed in this advisory.

## Proposed Architecture

### Core Substrate: MemBase Tables

The Typed Artifact-Flow Engine adds the following tables to `groundtruth.db`:

| Table | Purpose |
|-------|---------|
| `flow_definitions` | Typed flow templates (Implementation, Operation, Remediation, Deliberation, Report) |
| `flow_instances` | Active flow instances with artifact references |
| `stage_instances` | Per-stage state within a flow (Propose, Review, Implement, Verify, etc.) |
| `stage_leases` | Heartbeat/TTL-based stage claims replacing bridge_claim_cli.py |
| `stage_attempts` | Per-attempt records (worktree, harness, result, duration) |
| `flow_events` | Append-only event log for auditability (R6) |
| `flow_artifacts` | Artifact-to-flow linkage (specs, tests, bridge files, reports) |
| `agent_capability_snapshots` | Harness capability state at dispatch time (R4) |
| `compatibility_views` | Generated INDEX.md / bridge-view compatibility layer (CX1, CX5) |

### 5 Typed Flows (R1)

1. **Implementation Flow:** Propose → (AUQ?) → Review → (AUQ?) → Implement → Verify → (AUQ?) → Complete
2. **Operation Flow:** Plan → (AUQ?) → Execute → Verify → Complete
3. **Remediation Flow:** Diagnose → (AUQ?) → Propose-Fix → Review → Implement → Verify → Complete
4. **Deliberation Flow:** Surface → Investigate → (AUQ?) → Decide → Record → Complete
5. **Report Flow:** Investigate → Draft → Review → Finalize → Complete

Each flow definition specifies: stages, required-role per stage,
AUQ-gate positions (D4), never-self-review enforcement points (D1, D2),
deterministic-carve-out stages (D6), and workspace-isolation requirements (D7).

### Dispatch Policy Engine (R4)

Weighted scoring model (D12) evaluating:
- Role match (harness holds required role for target stage)
- Capability match (agent_capability_snapshots record supports required tools)
- Cost efficiency (value-per-spend optimization per D3/DELIB-COST-WASTE-FRAMING)
- Subject affinity (work-subject match for context relevance)

### CLI Surface (R7)

Proposed `gt flow` subcommand tree:

```
gt flow define    — register/update flow definitions
gt flow list      — list active flow instances
gt flow show      — display flow instance detail
gt flow start     — create new flow instance from definition
gt flow status    — per-stage status with lease/health info
gt flow claim     — acquire stage lease (replaces bridge_claim_cli.py)
gt flow release   — release stage lease
gt flow heartbeat — renew stage lease TTL
gt flow advance   — transition stage (with validation)
gt flow dispatch  — dispatch subsystem commands
  gt flow dispatch tick    — single dispatch evaluation cycle
  gt flow dispatch health  — dispatcher health report
gt flow render    — generated view commands
  gt flow render bridge-view  — generate INDEX.md-compatible view
gt flow pilot     — pilot mode commands for parallel-run
```

### Migration Plan (D9, D11)

| Phase | Scope | Bridge Status |
|-------|-------|---------------|
| 0 | Schema tables, flow-definition records, CLI skeleton, doctor checks | Bridge authoritative |
| 1 | Lease subsystem (replaces bridge_claim_cli.py) | Bridge authoritative |
| 2 | Implementation flow pilot (parallel-run) | Bridge authoritative; TAFE shadow |
| 3 | Dispatch policy engine | Bridge authoritative; TAFE shadow |
| 4 | Remaining 4 flow types | Bridge authoritative; TAFE shadow |
| 5 | Telemetry + health subsystem | Bridge authoritative; TAFE shadow |
| 6 | Compatibility view generator | Dual-write; bridge generated from TAFE |
| 7 | Governed cutover (bridge proposal + LO review + owner AUQ) | TAFE authoritative |

Phase 7 cutover requires its own bridge proposal, LO review, and owner
AUQ approval (D11). The cutover is not auto-promoted.

## §5 Constraint Survival

All §5 constraints from the owner directive survive:

| Constraint | How Preserved |
|-----------|--------------|
| Never-self-review (§1) | Session-context scoping (D1); enforced at stage transitions |
| GO/NO-GO discipline | Stage-transition validation in flow engine; LO verdict required |
| Append-only audit trail | flow_events table; stage_attempts immutable records |
| Adversarial role pairing | Required-role per stage in flow_definitions |
| Project root boundary | All TAFE code within E:\GT-KB |
| MemBase as canonical store | TAFE tables are MemBase tables |
| Formal-artifact approval | Approval gates preserved as AUQ-blocking transitions |
| AUQ as owner-decision channel | AUQ gates are blocking transition guards (D4) |

## Risk and Rollback

- **Risk:** Schema migration complexity. **Mitigation:** Phase 0 adds new tables only; no existing table mutations.
- **Risk:** Parallel-run divergence. **Mitigation:** Compatibility view generator (Phase 6) keeps INDEX.md synchronized; Phase 7 cutover requires explicit evidence of parity.
- **Risk:** Dispatch policy regression. **Mitigation:** Agent capability snapshots (D13) provide reproducible dispatch decisions.
- **Rollback:** Any phase can revert to bridge-authoritative by stopping TAFE writes. Phase 7 cutover is the only irreversible step and requires governed approval.

## Success Metrics

Per owner requirement R6 and D14:
- Flow completion rate by type
- Stage attempt success/failure rate
- Dispatch decision quality (capability match accuracy)
- Contention/duplicate dispatch incidents (target: zero after Phase 1)
- Mean time through flow by type
- Stuck-flow detection latency (target: < 5 minutes)

## Proposed Project Structure

**Project:** PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE

Phases 0-7 as defined in Migration Plan above. Work items to be created during
project formation (Step 5 of the owner directive).

Candidate WI groupings from Codex advisory (WI-A0-1 through WI-A7-3):
- Phase 0: Schema tables, flow-definition records, CLI skeleton, doctor checks
- Phase 1: Lease subsystem, heartbeat service, recovery service
- Phase 2: Implementation flow pilot, parallel-run comparator
- Phase 3: Policy engine, capability snapshots, scoring model
- Phase 4: Operation + Remediation + Deliberation + Report flows
- Phase 5: Telemetry tables, per-attempt recording, dashboard integration
- Phase 6: Compatibility view generator, dual-write mode
- Phase 7: Cutover proposal, evidence gathering, governed transition

## Superseded Artifacts

- **WI-4404** (scheduled-poller restoration) — superseded per D16
- **bridge_claim_cli.py** — replaced by stage-lease subsystem (Phase 1)
- **bridge/INDEX.md** — becomes generated compatibility view (Phase 6-7)
- **cross_harness_bridge_trigger.py** — replaced by dispatch policy engine (Phase 3)
- **single_harness_bridge_dispatcher.py** — replaced by dispatch policy engine (Phase 3)

## Recommended Commit Type

`docs:` — This advisory synthesis proposes architecture and captures decisions.
No source code, tests, or configuration changes are included.

## Clause Waivers

Owner waiver: DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING — DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612 — This is a governance advisory proposing architecture and capturing owner decisions; no source/config/test implementation is included (see Requirement Sufficiency). Spec-to-test mapping will be required in each phase's implementation proposal, not in this advisory.

Owner waiver: GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS — DELIB-BRIDGE-DISPATCH-OVERHAUL-D11-20260612 — This advisory does not perform bulk operations on work items; it proposes candidate WI groupings for Step 5 (project formation). Actual WI creation will follow governed project formation with inventory and review packets.

## Review Request

Requesting Loyal Opposition review of:

1. Architectural soundness of the TAFE substrate design
2. Completeness of §5 constraint preservation
3. Migration strategy risk assessment
4. Phase ordering and dependency analysis
5. CLI surface design adequacy for R7
6. Whether candidate specs (SPEC-TAFE-R1 through R7) capture the owner requirements faithfully
