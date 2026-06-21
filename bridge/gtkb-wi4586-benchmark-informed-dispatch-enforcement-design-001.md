NEW

# Benchmark-Informed Dispatch Enforcement Design for WI-4586

bridge_kind: prime_proposal
Document: gtkb-wi4586-benchmark-informed-dispatch-enforcement-design
Version: 001
Author: Prime Builder (Codex, harness A via interactive session-role override)
Date: 2026-06-21 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eec0d-db60-7a02-b3bf-85d24df55e76
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder override via ::init gtkb pb; approval_policy=never

Project Authorization: PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL
Project: PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1
Work Item: WI-4586

target_paths: []

implementation_scope: design-only benchmark-informed dispatcher enforcement path
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

---

## Summary

This design proposal moves `WI-4586` to its next bridge step by defining a gated future path for benchmark-informed dispatcher eligibility and ranking. It does not activate enforcement, mutate dispatcher config, update harness quality scores, create benchmark runner code, or change MemBase. It answers how benchmark evidence should eventually feed the quality-first dispatch policy without violating the project rule that benchmark results remain advisory until later explicit owner approval.

The core design is a two-stage boundary. Benchmark slices produce advisory evidence and candidate quality signals. A later, separate owner-approved activation bridge may promote mature, calibrated signals into dispatcher inputs, where they can set or update a harness's effective quality for a specific task class and support minimum requisite quality matching. Until that activation bridge exists, benchmark results may appear in reports and dry-run/explain surfaces only.

## First-Line Role Eligibility Check

- Owner session init: `::init gtkb pb`.
- Resolved interactive role for this session: Prime Builder.
- Durable registry note: harness `A` may remain durably assigned Loyal Opposition for headless routing; this filing uses the transcript-defined interactive Prime Builder override allowed by the session-role authority rules and does not change the durable registry.
- Existing bridge thread for `WI-4586`: none (`gt bridge threads --wi WI-4586` returned no thread).
- Status authored here: `NEW`.
- Eligibility result: Prime Builder is authorized to file a new design proposal under the active benchmark-project PAUTH.

## Design Claim

Benchmark-informed dispatch must be deliberately gated. Benchmark scores are valuable because they can make `dispatch_quality` less static and more task-specific, but premature enforcement would be dangerous: a noisy benchmark could silently down-rank or exclude a useful harness, or over-promote a cheap harness that has not proven governance-grade reliability. The correct design is advisory-first measurement, then explicit activation after thresholds mature.

This proposal also preserves the owner's current quality-first dispatch direction: once activated, benchmark-derived quality participates as a hard eligibility and ranking input. Work items may carry a minimum requisite quality; harnesses below that threshold are ineligible; sufficient candidates rank by quality, then cost, then availability. Benchmark evidence should help compute or justify those quality values, not bypass the bridge protocol or broadcast work to every harness.

## Proposed Enforcement Path

1. **Advisory evidence phase (current and near-term benchmark slices).**
   - Benchmark runs produce evidence records, deterministic scores, adjudicated scores when available, reliability/cost/latency telemetry, and failure classes.
   - Results remain advisory. They may be displayed in reports and used by humans or bridge proposals as evidence, but they do not automatically change dispatcher behavior.
2. **Calibration maturity gate.**
   - A score family becomes eligible for enforcement only after repeated runs across the relevant harnesses and task classes show stable thresholds, documented false-positive/false-negative behavior, and no unresolved scoring-pipeline or telemetry NO-GO.
   - Maturity evidence must cite the manifest/rubric, fixture corpus, runner, scoring, telemetry, and reporting slices that produced the data.
3. **Activation proposal gate.**
   - Dispatcher influence requires a future bridge proposal with explicit owner approval or PAUTH for enforcement activation.
   - The activation proposal must name the affected roles, task classes, minimum quality thresholds, score freshness bounds, fallback behavior, and rollback plan.
   - Activation must include an explain/dry-run surface so the owner can see how a benchmark score would affect routing before it becomes live.
4. **Runtime policy after activation.**
   - Benchmark-derived quality is an input to dispatch eligibility/ranking, not an independent dispatcher.
   - A work item's minimum requisite quality filters candidates before ranking.
   - Sufficient candidates rank by quality, cost, availability, then deterministic tie-breakers.
   - Missing, stale, or untrusted benchmark quality fails closed to the static configured quality or to no benchmark-derived override, depending on the activation proposal's explicit rule.
5. **Audit and rollback.**
   - Every activated benchmark-derived quality decision must be explainable from a current benchmark record, a scoring version, a task-class mapping, and the active activation bridge.
   - Rollback must be able to disable benchmark-derived dispatch influence while preserving advisory reports.

## Relationship To Related Work

- `WI-4579` is VERIFIED for the manifest/rubric. It defines the benchmark contract and advisory safety invariants.
- The scoring pipeline thread is currently DEFERRED, so no enforcement design may depend on a live scoring implementation being available today.
- `WI-4586` remains design-only; it creates the activation boundary that later scoring/telemetry/reporting slices must satisfy.
- `WI-4691` is the dispatcher-side quality-first spillover policy proposal. `WI-4586` is the benchmark-side evidence/activation path that can eventually feed that policy.
- `WI-4698` is already VERIFIED for the governance-grade LO quality floor. `WI-4586` does not change that floor; it defines how future benchmark evidence might justify quality metadata or per-task quality thresholds.

## Explicit Non-Activation Commitments

- No source, test, script, hook, prompt, dispatcher, cloud, deployment, credential, production, or application mutation is requested by this proposal.
- No benchmark result changes dispatcher ranking or eligibility as part of this bridge.
- No durable harness role, status, dispatchability, configured cost, configured quality, or configured availability is changed.
- No MemBase record is created, updated, resolved, or promoted by this bridge.
- No live benchmark runner is executed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the design is reviewed through the bridge before any future enforcement proposal can mutate dispatcher behavior.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this design cites the benchmark, dispatch, and bridge governance surfaces that constrain it.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries PAUTH, Project, Work Item, and target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - future activation must include spec-derived tests; this design maps verification to preflight and evidence-review checks.
- `GOV-STANDING-BACKLOG-001` - `WI-4586` is open backlog work in the benchmark project and should not be silently bypassed.
- `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` - benchmark-informed quality influences dispatch-envelope routing only through governed dispatcher policy.
- `DCL-DISPATCH-ENVELOPE-SCHEMA-001` - benchmark dispatch envelopes and result records must preserve structured envelope fields.
- `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` - live bridge state remains TAFE/dispatcher/versioned bridge state; benchmark fixtures and outputs do not become bridge authority.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - any future enforcement belongs in the centralized dispatch service, not ad hoc benchmark scripts.
- `REQ-HARNESS-REGISTRY-001` - benchmark-derived quality may eventually inform harness quality metadata or task-class overlays only through a governed activation path.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - eligibility/ranking rules remain declarative and explainable.
- `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` - benchmark evidence does not change which bridge statuses are actionable for each role.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - score evidence, activation decisions, and rollback plans must be durable artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - benchmark enforcement crosses the threshold from evidence to policy and therefore requires explicit artifact governance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - advisory evidence, maturity, activation, rollback, and supersession states must be explicit.

## Prior Deliberations

- `DELIB-20263444` - owner selected advisory-first benchmark consequences; dispatcher enforcement/ranking is gated behind later explicit owner approval.
- `DELIB-20263440` through `DELIB-20263447` - owner decisions for harness benchmark mode coverage, deterministic/adjudicated scoring, safety boundaries, GT-KB-native challenge cases, cadence, fixture isolation, and Dispatcher/Bridge CLI-first operation.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-V1-DISPATCH-POLICY-20260612` - conservative dispatch policy uses hard eligibility gates and cost only as an optimizer inside capable tiers.
- `DELIB-20260620-BRIDGE-DISPATCHER-FABRIC-DELIBERATION` - strategic dispatcher-fabric framing: reliability and quality are hard eligibility gates.
- `bridge/harness-testing-quality-benchmarking-umbrella-005.md` - VERIFIED umbrella sequencing; later slices require their own bridge review and do not inherit implementation authorization.
- `bridge/harness-testing-quality-benchmarking-manifest-rubric-004.md` - VERIFIED manifest/rubric; benchmark evidence is advisory and safety-scoped.
- `bridge/gtkb-wi4691-quality-first-spillover-dispatch-001.md` - current related dispatcher policy proposal; benchmark enforcement should feed that policy only after activation.

## Owner Decisions / Input

- `DELIB-20263444` is the controlling owner decision: benchmark results are advisory first, and dispatcher ranking or eligibility enforcement requires later explicit owner approval.
- `PAUTH-HARNESS-TESTING-QUALITY-BENCHMARKING-1-UMBRELLA-PROPOSAL` authorizes proposal filing and backlog/project metadata for `WI-4579` through `WI-4587`; it forbids automatic dispatcher ranking or eligibility enforcement based on benchmark results before explicit later owner approval.
- Current owner clarification in this session establishes the target policy shape for any future activation: minimum requisite quality, quality-first ranking, cost tie-breaks among equal-quality candidates, availability after cost, and spillover only when higher-quality queues are saturated.
- No additional owner decision is needed for this design-only proposal because it does not activate enforcement or mutate protected artifacts.

## Requirement Sufficiency

Existing requirements sufficient. `WI-4586` explicitly says to design, but not activate, a future enforcement path where mature benchmark thresholds may affect dispatcher ranking or eligibility only after explicit owner approval. The benchmark PAUTH and `DELIB-20263444` supply the advisory-first boundary. The current owner clarification supplies the dispatch-policy shape that future benchmark activation must support.

## Specification-Derived Verification Plan

| Governing surface | Verification evidence for this design proposal |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread is append-only and latest `NEW` until Loyal Opposition review. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability preflight passes with no missing required specs and the proposal carries PAUTH, Project, Work Item, and `target_paths: []`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Clause preflight reports zero blocking gaps; future activation requirements include spec-derived tests before any enforcement. |
| `DELIB-20263444` / benchmark PAUTH | Proposal explicitly preserves advisory-only behavior and forbids live dispatcher influence in this bridge. |
| `ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001` / `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Future enforcement is routed through dispatcher policy and activation bridge, not benchmark scripts. |
| `REQ-HARNESS-REGISTRY-001` / `DCL-DISPATCH-ENVELOPE-RULES-001` | Benchmark-derived quality is framed as a governed input to quality/rule metadata, with missing/stale/untrusted values fail-closed per activation design. |
| `ADR-TAFE-AUTHORITATIVE-BRIDGE-STATE-001` | Proposal states benchmark fixtures/outputs never replace bridge state authority. |

Because this is a design-only bridge with `target_paths: []`, no `pytest` or
`ruff` command is required for implementation verification in this thread.
Future activation or source-bearing enforcement bridges must add concrete
pytest/ruff coverage for the files they mutate.

Review commands:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4586-benchmark-informed-dispatch-enforcement-design
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4586-benchmark-informed-dispatch-enforcement-design
gt bridge show gtkb-wi4586-benchmark-informed-dispatch-enforcement-design
gt bridge threads --wi WI-4586
```

## Acceptance Criteria

1. The proposal defines advisory evidence, maturity, activation, runtime policy, audit, and rollback stages.
2. It explicitly prevents benchmark results from changing dispatcher eligibility or ranking in this bridge.
3. It aligns future benchmark activation with minimum requisite quality and quality-first dispatch ranking.
4. It identifies the relationship to WI-4579, WI-4583, WI-4691, and WI-4698 without duplicating their implementation scopes.
5. It gives Loyal Opposition a clear basis to GO or NO-GO the design without requiring owner input or protected file mutation.

## Risk / Rollback

- Risk: the design is too abstract to constrain future activation. Mitigation: activation requirements name task classes, thresholds, freshness, fallback, explain/dry-run, audit, and rollback as mandatory future bridge contents.
- Risk: benchmark-derived quality could be confused with live dispatcher policy. Mitigation: this proposal repeats the non-activation commitments and cites the PAUTH prohibition.
- Rollback: if this design receives GO and is later found wrong, file a superseding WI-4586 revision or follow-on design bridge; no source, config, or database state is changed by this proposal.

## Bridge Filing

This proposal is filed as the first status-bearing numbered bridge file for `gtkb-wi4586-benchmark-informed-dispatch-enforcement-design`; no prior version is deleted or rewritten. Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs` - design-only bridge artifact; no source, test, config, hook, or MemBase mutation is requested.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
