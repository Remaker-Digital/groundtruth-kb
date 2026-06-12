REVISED

bridge_kind: governance_advisory_revision
Document: gtkb-typed-artifact-flow-engine-advisory
Version: 003
Responds-To: bridge/gtkb-typed-artifact-flow-engine-advisory-002.md

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebd61-0067-73d0-bc59-142681b70a9e
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

# Typed Artifact-Flow Engine - Corrected Advisory Synthesis

## Revision Claim

This revision corrects the NO-GO findings in
`bridge/gtkb-typed-artifact-flow-engine-advisory-002.md`.

The target architecture remains directionally the same: a MemBase-backed Typed
Artifact-Flow Engine (TAFE) should eventually replace protocol-bearing markdown
dispatch state, while preserving GO/NO-GO/VERIFIED discipline, append-only
audit, adversarial role pairing, AUQ gates, and never-self-review invariants.

The corrections are:

- owner decision D1-D17 mapping is now based on live MemBase deliberation records;
- the live pilot is limited to advisory/report verification, generated-view
  parity checks, and non-mutating bookkeeping;
- review routing is Codex mandatory plus one additional harness best-effort;
- existing project rows `WI-4495` and `WI-4496` are explicitly fenced as not
  implementation-ready until revised or separately owner-approved;
- advisory artifact-lifecycle citations are added.

No source/config/test implementation is included in this advisory.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`
- `SPEC-TAFE-R1`
- `SPEC-TAFE-R2`
- `SPEC-TAFE-R3`
- `SPEC-TAFE-R4`
- `SPEC-TAFE-R5`
- `SPEC-TAFE-R6`
- `SPEC-TAFE-R7`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-SESSION-SELF-INITIALIZATION-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Corrected Owner Decision Map

These summaries were read from live MemBase records on 2026-06-12 via
`python -m groundtruth_kb deliberations get`.

| ID | Live title / corrected decision |
|---|---|
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` | Never-self-review is session-scoped. A spawned worker is independent only when it receives the artifact and governed context, not creator scratchpad or session state. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D2-20260612` | The typed artifact-flow engine supersedes WI-4404 and `DELIB-BRIDGE-ORCHESTRATOR-VISION-20260610`; those remain historical context. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` | Spec capture is one umbrella candidate plus one child candidate per R1-R7. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D4-20260612` | Canonical flow state lives in MemBase behind CLI/services; markdown becomes generated presentation/compatibility view after cutover. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D5-20260612` | All work entering TAFE must be pre-classified into one of the five reviewed-task flows. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D6-20260612` | Activation is event-driven with watchdog fallback; watchdog evaluates need and must not blindly launch sessions. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D7-20260612` | Implementation flow AUQ gate sits before implementation begins, not before proposal/review. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D8-20260612` | Operation flow AUQ gate sits before execution. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D9-20260612` | Remediation flow AUQ gating is severity-tiered: low-risk bounded recovery can be autonomous; high-risk remediation is owner-gated. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D10-20260612` | Deliberation flow is owner-gated by definition. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D11-20260612` | Report flow has autonomous filing, but consumption/action is owner-gated. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D12-20260612` | Cost model is per-harness cost tier plus budget cap; cost is telemetry/tie-break evidence, not a quality override. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D13-20260612` | Dispatch policy is registry-driven capability matching: hard gates first, then calibrated precedence, cost as final tie-breaker only. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D14-20260612` | Telemetry is per-dispatch/stage-attempt outcome record plus periodic benchmark. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D15-20260612` | Migration is parallel-run with governed cutover; existing bridge governs construction and remains authoritative until cutover. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D16-20260612` | During coexistence, the old system is authoritative until the governed flip; `bridge/INDEX.md` remains canonical until cutover is VERIFIED. |
| `DELIB-BRIDGE-DISPATCH-OVERHAUL-D17-20260612` | Review route is Codex mandatory plus one additional harness best-effort; extra review is non-blocking. |

Additional controlling records:

- `DELIB-BRIDGE-DISPATCH-OVERHAUL-PILOT-ELIGIBILITY-20260612`: owner limited the live pilot to advisory/report verification, generated-view parity checks, and non-mutating bookkeeping.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-CX5-20260612`: Codex advisory recorded the same pilot limitation and kept governance-critical work on the existing bridge.

## Corrected Pilot Boundary

The earlier `-001` advisory incorrectly made an implementation-flow pilot the
first live pilot. That is withdrawn.

The live pilot is limited to:

- advisory/report verification;
- generated-view parity checks;
- non-mutating bookkeeping.

The live pilot excludes:

- implementation proposals;
- formal specifications;
- bridge-rule changes;
- destructive cleanup;
- release blockers;
- governance-critical artifacts.

Any live implementation-flow pilot requires a separate owner decision and bridge
proposal. Until then, implementation/governance/release-critical work remains on
the existing bridge.

## Corrected Review Route

Codex is the mandatory Loyal Opposition reviewer through the existing bridge.
One additional harness review is best-effort and non-blocking. Claude Code
review may be manually triggered by Mike as an additional perspective, but this
advisory does not require "all capable harnesses" to review.

## Backlog Fence

Live MemBase state currently shows:

```text
WI-4495: Implementation flow: full stage engine
stage: backlogged
resolution_status: open
approval_state: unapproved
subproject_name: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE/Phase-2-Implementation-Flow-Pilot
depends_on_work_items: WI-4489,WI-4493
blocks_work_items: WI-4496

WI-4496: Parallel-run comparator for Implementation flow
stage: backlogged
resolution_status: open
approval_state: unapproved
subproject_name: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE/Phase-2-Implementation-Flow-Pilot
depends_on_work_items: WI-4495
```

These rows are not implementation-ready under the corrected owner-decision map.
They are fenced as planning artifacts pending reconciliation. They must not be
selected for execution as a live implementation-flow pilot unless one of these
happens first:

1. the rows are revised/replaced to describe non-mutating schema/model/shadow
   parity work only; or
2. Mike makes a new owner decision expanding live pilot eligibility beyond
   advisory/report verification and non-mutating bookkeeping, followed by a
   bridge proposal and LO review.

This advisory does not mutate MemBase backlog rows. It records the execution
fence so future sessions do not treat `WI-4495` / `WI-4496` as approved live
implementation-flow pilot work.

## Corrected Migration Plan

| Phase | Corrected scope | Authority boundary |
|---|---|---|
| 0 | Advisory review, candidate-spec review, project-plan reconciliation | Existing bridge authoritative |
| 1 | Read-only schema/model and CLI skeleton for flow definitions/instances/views | No dispatch; no live bridge mutation |
| 2 | Generated bridge-view parity and non-mutating bookkeeping shadow checks | Existing bridge authoritative |
| 3 | Stage-attempt telemetry and health diagnosis in shadow/dry-run mode | Existing bridge authoritative |
| 4 | Deterministic dispatch policy and need evaluator in dry-run mode | No blind launch; no governance-critical routing |
| 5 | Parallel live pilot limited to advisory/report verification, generated-view parity, and non-mutating bookkeeping | Existing bridge authoritative |
| 6 | Mutating-attempt workspace isolation built and tested behind explicit gates | Not live for implementation flow without separate approval |
| 7 | Governed cutover proposal with parity evidence, rollback plan, LO review, and owner AUQ | Only after VERIFIED cutover may `bridge/INDEX.md` stop being canonical |

## Architecture Recommendation

Proceed toward the MemBase-backed TAFE target, but only through the corrected
migration boundary above.

Core canonical entities remain:

- `flow_definitions`
- `flow_instances`
- `flow_artifacts`
- `stage_instances`
- `stage_leases`
- `stage_attempts`
- `flow_events`
- `agent_capability_snapshots`
- `compatibility_views`

Initial CLI/service surface remains:

- `gt flow define/list/show`
- `gt flow start`
- `gt flow status`
- `gt flow claim/release/heartbeat`
- `gt flow advance`
- `gt flow dispatch tick`
- `gt flow health`
- `gt flow render bridge-view`
- `gt flow pilot`

Skills and MCP/plugin surfaces may wrap these commands, but canonical state
must remain behind the CLI/service layer.

## Requirement Sufficiency

Candidate specs already exist for `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`
and `SPEC-TAFE-R1` through `SPEC-TAFE-R7`. This advisory revision does not
promote those specs or implement code. Future implementation proposals must
derive tests from the relevant candidate/promoted specs and from the owner
decision records cited above.

## Artifact Lifecycle Traceability

This revision adds the advisory lifecycle citations requested by LO:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`: owner decisions, requirements, specs,
  work items, reports, and bridge verdicts remain governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`: TAFE construction must proceed
  through durable artifact flow rather than ad hoc dispatcher edits.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: requirement/spec/backlog/report
  lifecycle transitions remain explicit during migration, pilot, and cutover.

During coexistence, `bridge/INDEX.md` remains canonical per D16. Generated TAFE
views are compatibility/projection artifacts only until a cutover proposal is
VERIFIED.

## Pre-Filing Preflight Subsection

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-typed-artifact-flow-engine-advisory --content-file .gtkb-state\bridge-revisions\drafts\gtkb-typed-artifact-flow-engine-advisory-003.md
```

Observed result:

```text
preflight_passed: true
packet_hash: sha256:13a30327377d547f1f4d7c6edee5a615ea449aafbb057242f272b2e7ab88894a
missing_required_specs: []
missing_advisory_specs: []
warnings.missing_parent_dirs: []
```

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-typed-artifact-flow-engine-advisory --content-file .gtkb-state\bridge-revisions\drafts\gtkb-typed-artifact-flow-engine-advisory-003.md
```

Observed result:

```text
must_apply: 3
may_apply: 2
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Verification / Review Plan

This is a governance advisory, not a code implementation. Verification is:

- direct MemBase read of D1-D17, pilot eligibility, CX5, and WI-4495/WI-4496;
- bridge applicability preflight;
- ADR/DCL clause preflight;
- Loyal Opposition review of the corrected advisory.

Future implementation proposals must include source-level tests and ruff/format
checks for their own target paths.

## Risk And Rollback

- Risk: future sessions pick up stale Phase-2 implementation-pilot rows. Mitigation: this advisory explicitly fences WI-4495/WI-4496 until revised or separately owner-approved.
- Risk: generated views become treated as canonical too early. Mitigation: D16 is cited and the migration plan keeps `bridge/INDEX.md` authoritative until VERIFIED cutover.
- Risk: cost optimization overrides review quality. Mitigation: D12/D13 keep cost as a tie-break after hard gates and capability/quality routing.
- Rollback: because this is an advisory-only revision, rollback is to withdraw or supersede this bridge advisory; no source/config/data mutation is performed here.

## Required Follow-Up If Accepted

Before implementation work begins, Prime Builder should file a project/backlog
reconciliation proposal that revises or replaces `WI-4495` and `WI-4496` to
match the corrected pilot boundary.
