author_identity: Claude Loyal Opposition
author_harness_id: B
author_session_context_id: 901d970b-b437-4794-83bc-b84ac044f8d9
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo + ::open build

# LO Advisory — Data-Derived Harness Dispatch-Attribute Calibration and a Role / Activity / Diligence-Stage Selection Model

bridge_kind: loyal_opposition_advisory
Classification: adapt (tasks Prime Builder to file a fresh umbrella project proposal)
Advisory-status: ADVISORY (non-dispatchable; interactive PB disposition)
Date: 2026-07-04
Author: Loyal Opposition (Claude, harness B), interactive session
Specs / components touched: config/dispatcher/rules.toml; harness-state/harness-registry.json; config/agent-control/harness-capability-registry.toml; scripts/dispatcher_runtime.py; groundtruth_kb/dispatcher/lane_scoring.py; groundtruth_kb/dispatcher/rules_loader.py; groundtruth_kb/harness_projection.py; scripts/benchmarks/harness_quality_manifest.py; scripts/benchmarks/harness_quality_reporting.py
Governance in scope: GOV-HARNESS-STATE-SOT-CONSOLIDATION-001 (blocking); GOV-SOURCE-OF-TRUTH-FRESHNESS-001; REQ-HARNESS-REGISTRY-001
Related WIs: WI-4969 / WI-4791 (harness quality/token accounting scaffold); WI-4983 (dispatch reliability cluster)

---

## 1. Executive Summary

The owner has determined that the dispatcher's `dispatch_cost`, `dispatch_quality`, and `dispatch_availability` values in `config/dispatcher/rules.toml` are arbitrary example placeholders, and wants two things:

1. **A method** to make those values meaningful and correct — derived from observed differences in capability, cost, and responsiveness — so the dispatcher produces a desirable, fit-for-purpose work distribution.
2. **A redesigned attribute model** that best describes a harness from the dispatcher's perspective, so the dispatcher can make good dispatch decisions across **all roles** and **all activity-envelope types**, at **each stage of the adversarial diligence workflow** (proposal review vs implementation verification vs ops verification), producing sufficiently consistent fit-for-purpose artifacts.

The owner further specifies this must be delivered as a **repeatable, ~weekly "harness capability adjustment" procedure** (skill + CLI) — because models and harnesses are expected to release roughly weekly — whose output is an **implementation proposal** that may drive both harness re-parity work and attribute-value updates. Regular data-driven self-optimization is intended to be a **core GT-KB capability**; it is only lightly implemented today.

**This advisory tasks Prime Builder to create a fresh umbrella project proposal** that (a) states the unifying design and overall architecture, (b) breaks the work into constituent work items each suitable for an individual implementation proposal, and (c) is scoped so the result is a defined project with clear WIs implementable under the normal adversarial-diligence (bridge) process.

**Most important finding (developed in §3):** the placeholder attribute values are not merely un-calibrated — **they are not consumed by the live selection path at all.** There are three disconnected "how to pick a harness" representations in the codebase, and the live daemon path keys on `reviewer_precedence` + `harness_id`, not on quality/cost/availability. Therefore the owner's step-1 ("adjust the values so they are meaningful") has a hard prerequisite: **bind the attributes to live selection**, or the calibration tunes dead knobs. This reframing strengthens the case for the dedicated project rather than a quick value edit.

**Second structural finding (§3 Finding F):** the five dispatch/eligibility fields are duplicated across two *persistent* artifacts — `harness-registry.json` (harness-state SoT) and `rules.toml` (dispatcher policy) — with no single authority. Under the owner's SoT-singleton principle (§3, Governing Principle), persistent duplication of the same information is a Source-of-Truth violation, not a convenience. Consolidating these fields to one authoritative home is a **prerequisite** for calibration (you cannot make a value "correct" until it lives in exactly one place), and is folded into WI-1.

---

## 2. Method Note (how this advisory was produced)

Read-only investigation, this session:

- Read `config/dispatcher/rules.toml` (global `selection_order` line 2; per-harness score blocks lines 42-95; rules `bridge-prime-builder-default` line 99 and `bridge-loyal-opposition-cheap-fast-default` line 105).
- Read the live selection sort in `scripts/dispatcher_runtime.py` (`active_matching` sorted by `(_reviewer_precedence_for_record, harness_id)`, ~lines 4026-4035).
- Read `groundtruth_kb/dispatcher/lane_scoring.py` in full (shadow/non-activating lane model; `_utility_score = quality + availability - cost`).
- Read the harness registry `reviewer_precedence` values (A=20, B=10, C=30, D=10).
- Reviewed 24 h of bridge authorship distribution (A=120 PB artifacts; LO verdicts D=46, C=26, B=2) and `.gtkb-state/bridge-poller/dispatch-failures.jsonl`.
- Confirmed the `harness_quality_*` benchmark scaffold exists (`scripts/benchmarks/harness_quality_manifest.py`, `harness_quality_reporting.py`).
- Deliberation search (3 queries: dispatch selection attributes; dispatcher self-optimization data-driven; harness capability adjustment weekly) — **0 matches**. See §9.

---

## 3. Current-State Findings (evidence-first)

### Finding A — Three disconnected selection representations that disagree

| Representation | Location | Ordering / formula |
| --- | --- | --- |
| Global `selection_order` | `rules.toml` line 2 | `[quality, cost, availability, reviewer_precedence, harness_id]` (quality first) |
| Per-rule `prefer` (LO rule) | `rules.toml` line 105 | `[availability, quality, cost]` (availability first) |
| Shadow utility scorer | `lane_scoring.py` `_utility_score` | `quality + availability − cost` (equal-weight linear) |

These three cannot all be authoritative; they encode different objective functions. Any calibration effort must first choose (or unify) the authoritative representation.

### Finding B — The live selection path consumes none of the attribute values

The live daemon selection in `dispatcher_runtime.py` (`active_matching`) sorts candidates by `(_reviewer_precedence_for_record(record), harness_id)`. It does **not** read `dispatch_quality`, `dispatch_availability`, or `dispatch_cost`. `lane_scoring.py` — the only module that turns those attributes into a utility — declares itself in its own docstring: *"deliberately non-activating: it ... does not change runtime dispatcher target selection or write harness-state/config files."* It is a shadow/advisory projection.

**Consequence:** the placeholder attribute values are currently cosmetic with respect to live dispatch. Editing them (the owner's step 1) will not change behavior until they are bound to live selection. This must be stated plainly so the owner does not expect a value edit alone to shift distribution.

### Finding C — Correcting my own earlier explanation (interrogative-default discipline)

Earlier this session I told the owner "C beats B because C's availability (80) exceeds B's (75)." That explanation was drawn from the rule's `prefer` field — which the live path does not use. The **actual** live driver is `reviewer_precedence`: A=20, B=10, C=30, D=10. With D quiesced (`can_receive_dispatch=false`) and B vs C decided by precedence, the effective selection is precedence-governed, not attribute-governed. The exact precedence direction and the full candidate-filter chain (why C is chosen over B when B's precedence is numerically lower) is itself under-documented and is a required output of the selection-binding audit WI (§6, WI-1). I flag this correction because it is the strongest possible evidence for the owner's core point: the current selection is not describing harnesses by capability at all.

### Finding D — The owner's role/activity vision already has a shadow foundation

`lane_scoring.py` already models **lanes = harness × role × activity_type** over `DEFAULT_ACTIVITY_TYPES = (build, test, spec, ops, project, deliberation)`, computes a per-lane utility, and gates a *production* projection on **fresh required evidence** (`parity`, `readiness`, `benchmark`) with fail-closed blockage reasons. This is not greenfield: the project should **activate and extend** this shadow foundation, not reinvent it. The `harness_quality_*` benchmark scaffold is the intended evidence feeder (the `benchmark` evidence type is already named in the production gate).

### Finding E — Observed distribution today (why this matters)

Over 24 h: LO verdicts D=46, C=26, B=2. B (the highest-quality LO by the placeholder quality score, 95) is effectively never headless-dispatched; D (now quiesced for provider failures) had carried the bulk. The distribution is an artifact of precedence + `can_receive_dispatch` flags, not of a fit-for-purpose objective. This is precisely the "undesirable distribution" the owner wants to fix.

### Finding F — The dispatch attributes are duplicated across two persistent SoTs

Five fields — `can_fire_events`, `can_receive_dispatch`, `dispatch_availability`, `dispatch_cost`, `dispatch_quality` — are stored in **both** `harness-state/harness-registry.json` (the roles/state SoT, a MemBase projection) **and** `config/dispatcher/rules.toml` (hand-maintained dispatcher policy). Neither is declared authoritative for the overlap: `rules.toml` has no provenance header and no generator, and is independently hand-editable (an owner edit on 2026-07-04 set B's `rules.toml` flags while the registry stayed unchanged, producing exactly the drift the doctor's config-drift check flagged). The governance-designated Capabilities SoT (`config/agent-control/harness-capability-registry.toml`) holds **none** of these fields. So harness *state* is un-consolidated across two persistent artifacts — the class `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` (severity: blocking) exists to eliminate — but `rules.toml` slipped that contract by being framed as "config" rather than "state."

### Governing principle (owner-stated, 2026-07-04): a SoT is a singleton

Per owner direction this session: **a Source-of-Truth is a single artifact that is always authoritative — that is the definition of SoT.** The *only* permitted duplication is a **time-limited, short-lived cached copy** that serves as a *derived* SoT for read operations within a given usage context; such a cache is regenerated from the authority and is never independently authoritative or hand-edited. **Aside from these short-lived derived caches, the same information MUST NOT exist in multiple copies: each SoT is a singleton within GT-KB.** The `rules.toml` copy of the five fields fails this test on both counts — it is persistent (not short-lived) and independently editable (not a regenerated read cache) — so it is a genuine SoT violation, not a benign convenience. This principle is the **acceptance test** for the consolidation in WI-1, and PB should formalize it as a GOV specification (extending `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` and `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`) through the owner-approval path.

---

## 4. Part 1 — Best Method for Making the Attribute Values Meaningful and Correct

The method has a prerequisite step, then a repeatable calibration loop.

### 4.0 Prerequisite (blocking): bind attributes to live selection

Before values can be "correct," selection must actually consume them. Two options for the project to weigh:
- **Option P-A:** activate the `lane_scoring.py` utility path (evidence-gated production projection) as the live selector, retiring the `reviewer_precedence`-only sort.
- **Option P-B:** wire `dispatch_quality/cost/availability` (and successors) directly into the `dispatcher_runtime` candidate ranking, and delete the dead `selection_order`/`prefer` fields or make one authoritative.

Either way, **reconcile the three orderings of Finding A into one authoritative representation.** This is WI-1 (selection-binding audit + unify).

### 4.1 Define observable proxies for each attribute (data that already exists)

| Attribute | Observable proxy (available today) | Source |
| --- | --- | --- |
| Responsiveness / availability | success rate; p50/p90 launch→verdict latency; provider-failure & backoff frequency; timeout/exit-code markers | `dispatch-failures.jsonl`; `dispatch-runs/*.stdout/stderr.log`; verdict-file mtime deltas |
| Quality | rework rate (NO-GO→REVISED cycles per thread); verdict durability (VERIFIED that stuck vs later reopened); preflight/gate pass rate; review-depth (methodology trail presence); independent re-review agreement rate | bridge thread chains; verdict artifacts; preflight logs |
| Cost | $/task = (input+output tokens) × model unit price; cost variance | `harness_quality_manifest` REQUIRED_EVIDENCE_FIELDS (input_tokens, output_tokens, estimated_cost); a maintained price table |

### 4.2 Normalize and score (rolling window)

- Compute each proxy over a rolling window (e.g., trailing N days / M dispatches), per (harness, role, activity, stage) cell where sample size permits, else fall back to (harness, role) then (harness).
- Normalize to a common 0-100 scale (min-max or robust z-score) so attributes are comparable and the objective functions in §5 are well-defined.
- Record provenance (window, sample count, source commit) with every derived value — self-optimization must be auditable.

### 4.3 Validate against desired-distribution intents (backtest)

Turn the owner's example intents into **acceptance tests** the calibration must satisfy:
- (PB, build, *) → selects the maximum-quality PB.
- (LO, build, proposal-review) → selects the maximum-quality LO.
- (LO, build, impl-verification) → selects lowest-cost LO meeting a quality floor.
- (LO, ops, verification) → selects lowest-cost LO meeting quality **and** responsiveness floors.

Calibration is "correct" when, replayed against recent history, it would have produced selections consistent with these intents. This backtest is a project WI (§6, WI-7).

### 4.4 Cold-start for weekly-new models (thin data)

Because new models/harnesses arrive ~weekly with no observation history, seed a new lane's attributes from **priors**: vendor/benchmark evidence + parity-evidence status, marked low-confidence, then converge toward observed values as dispatches accumulate. The production gate already requires fresh `parity`/`readiness`/`benchmark` evidence before a lane is live-rankable — reuse that as the cold-start guard so an unproven new harness cannot dominate selection on optimistic priors.

---

## 5. Part 2 — Proposed Harness Descriptive-Attribute Model

### 5.1 The selection objective is per-(role, activity, stage), not a single global utility

The owner's four examples prove the objective **changes by lane and diligence stage**: sometimes maximize quality, sometimes minimize cost subject to floors. A single `quality + availability − cost` scalar (today's shadow utility) cannot express "lowest cost **subject to** quality ≥ floor." The proposed model is **threshold-filter then objective-optimize**:

```
candidates = harnesses where role matches, dispatchable, and all non-functional floors met
           (quality ≥ q_floor[role,activity,stage],
            responsiveness ≥ r_floor[role,activity,stage],
            capacity available)
select     = argmin/argmax over candidates of the lane objective, e.g.
             (PB, build, *)              -> argmax quality
             (LO, build, proposal)       -> argmax quality
             (LO, build, impl-verify)    -> argmin cost
             (LO, ops,   verify)         -> argmin cost
```

The floors encode "fit-for-purpose / sufficiently consistent"; the objective encodes the owner's cost/quality preference for that lane.

### 5.2 Proposed attribute set (superset of today's three)

- **Capability / quality (decomposed, not one number):** reasoning depth; instruction-adherence; domain fit (GT-KB governance fluency); artifact-consistency (does it reliably produce well-formed proposals/verdicts that pass gates first try).
- **Cost:** $/task and cost variance.
- **Responsiveness:** p50/p90 latency; success rate; provider stability.
- **Reliability:** gate/preflight pass rate; rework rate; false-premise / hallucination rate (LO-specific: rate of findings later shown wrong).
- **Fit-for-purpose thresholds:** per-(role, activity, stage) quality and non-functional floors — first-class config, not implicit.
- **Capacity:** max concurrent items; provider rate limits.
- **Freshness / evidence:** parity status; benchmark recency (already in the production gate).
- **Interaction mode:** headless-eligible vs interactive-reserved (see the open question in §7 — this directly determines whether Claude/B should ever be headless-selected).

### 5.3 Consistency requirement

"Sufficiently consistent fit-for-purpose artifacts" implies the model should track **variance**, not just point estimates — a harness that is excellent on average but occasionally produces gate-failing artifacts may be unfit for an unattended stage. Recommend acceptance thresholds expressed as (median AND tail) bounds.

---

## 6. Part 3 + Part 4 — Instruction to Prime Builder: create the umbrella project proposal

**Prime Builder is instructed to file a fresh umbrella project proposal** (suggested name: `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION`) that states the unifying design (threshold-filter + per-lane objective; data-derived, auditable attributes; a weekly adjustment procedure; built on the existing `lane_scoring` shadow foundation advanced toward evidence-gated production activation) and breaks out constituent work items, each sized for an individual implementation proposal under normal adversarial diligence.

**Suggested WI breakdown (PB to refine, not prescriptive):**

1. **WI-1 — Selection-binding + SoT-consolidation audit (do this FIRST; prerequisite for all calibration WIs).** Two coupled deliverables. **(a) Selection binding:** document the true live selection path and reconcile the three orderings (Finding A) into one authoritative representation; decide Option P-A vs P-B (§4.0). **(b) SoT consolidation (Finding F + Governing Principle):** give the five duplicated dispatch/eligibility fields exactly ONE authoritative home (the registry's MemBase source, or the Capabilities SoT `harness-capability-registry.toml`), make `rules.toml` **policy-only** (`selection_order`, `rules`, `budget`, and the future per-lane floors/objectives), and have it **reference** harness attributes through the canonical `harness_projection` reader instead of copying them. Enforce the SoT-singleton principle: no persistent duplicate fields; any dispatcher-side performance cache must be a regenerated, read-only, time-limited derived copy that is never hand-edited. Deliverable: a decision record + a single authoritative home for both selection and attribute truth + a doctor check that fails on any re-introduced persistent duplication (replacing the current drift-*detection* band-aid with drift-*prevention*).
2. **WI-2 — Attribute-observation pipeline.** Turn the §4.1 proxies into normalized, provenance-stamped scores, building on the `harness_quality_*` benchmark scaffold. Read-only over history; writes only to `.gtkb-state` evidence.
3. **WI-3 — Attribute-model redesign.** Implement the §5.2 attribute set + per-(role, activity, stage) floors and objectives as governed config schema.
4. **WI-4 — Live-selection activation.** Wire the model into live dispatch (activate `lane_scoring` production path or bind attributes into `dispatcher_runtime`), evidence-gated and fail-closed.
5. **WI-5 — `gt harness capability-adjust` skill + CLI (the weekly procedure).** Gathers rolling-window data → recomputes attribute values → emits a diff to `rules.toml` **as an implementation proposal** (never auto-applies without a bridge GO, pending the §7 owner decision). This is the repeatable procedure the owner asked for.
6. **WI-6 — Re-parity feedback loop.** When calibration reveals a capability gap (a harness below a lane's floor), emit a re-parity work item so the gap drives harness config/skill changes, not silent exclusion.
7. **WI-7 — Backtest / validation harness.** The §4.3 desired-distribution intents as executable acceptance tests, run each calibration cycle.
8. **WI-8 — Runbook + docs** for the weekly cadence and the self-optimization loop.

The overall architecture is a closed loop: **observe (WI-2) → score (WI-3) → select (WI-4) → adjust weekly (WI-5) → re-parity when needed (WI-6) → validate (WI-7)**, which is the first concrete instance of GT-KB's intended data-driven self-optimization capability.

---

## 7. Required Prime Builder Owner-Grilling Gate

(Per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` / `.claude/rules/peer-solution-advisory-loop.md`. This advisory is classified **adapt** and implies implementation, so PB MUST obtain durable `AskUserQuestion`-recorded answers before filing the umbrella proposal, and land that AUQ evidence in the proposal's `## Owner Decisions / Input` section.)

### Implementation implied
**Yes.** This advisory drives a multi-WI project that will modify dispatcher selection code, config schema, and add a skill/CLI, and may drive harness re-parity.

### Grill-the-owner questions (PB must obtain durable AUQ answers)
1. **Objective functions per lane.** Confirm the four example mappings (§5.1) and enumerate any additional (role, activity, stage) lanes and whether each maximizes quality or minimizes cost subject to floors.
2. **Fit-for-purpose floors.** How is "good enough / sufficiently consistent" defined per stage — who sets the quality and non-functional floors, and are they median-only or median-plus-tail (§5.3)?
3. **Interactive vs headless for Claude (B).** Should Claude ever be headless-dispatched, or is it interactive-reserved? This determines whether B is a selectable headless lane at all and is the direct cause of today's B=2/24h distribution.
4. **Observation authority + window.** Which observed signals are authoritative (token logs, verdict durability, latency), what is the rolling window, and what is the retention/privacy posture for run logs?
5. **Automation scope of the weekly procedure.** Does `gt harness capability-adjust` auto-apply value changes, or always emit a bridge proposal requiring GO (recommended)? Manual-triggered weekly, scheduled, or both?
6. **Re-parity coupling.** When calibration exposes a capability gap, is harness re-parity in-scope for this project or a separate track?
7. **Cost-model source.** Where do per-model $/token prices come from (owner-maintained table?), given weekly model releases?
8. **Authoritative home for the dispatch attributes (SoT-singleton).** Should the single SoT for the five duplicated fields be the harness registry (MemBase projection) or the Capabilities SoT (`harness-capability-registry.toml`, which is arguably their natural home but currently holds none of them)? And confirm the derived-cache rule: any dispatcher-side read cache must be regenerated + read-only + time-limited, never hand-edited (per the owner's SoT-singleton principle).

### Required durable owner decisions before the umbrella proposal is filed
- The per-lane objective/floor table (Q1, Q2).
- The headless-eligibility policy for interactive harnesses (Q3).
- The auto-apply-vs-propose policy for the weekly adjustment (Q5).
- The authoritative home for the dispatch attributes + the derived-cache rule (Q8).

---

## 8. Prime Builder Implementation Context

| Element | Detail |
| --- | --- |
| Objective | A scoped umbrella project delivering data-derived, role/activity/stage-aware dispatch selection + a repeatable weekly capability-adjustment procedure. |
| Preconditions | Owner-grilling-gate AUQ answers (§7) captured; selection-binding audit (WI-1) is the first buildable WI. |
| Evidence paths | `config/dispatcher/rules.toml` (L2, L42-95, L99, L105); `scripts/dispatcher_runtime.py` (`active_matching` sort); `groundtruth_kb/dispatcher/lane_scoring.py`; `scripts/benchmarks/harness_quality_manifest.py`; `.gtkb-state/bridge-poller/dispatch-failures.jsonl`. |
| File touchpoints (project-wide) | dispatcher selection module; `rules.toml` schema; a new `gt harness capability-adjust` CLI/skill; benchmark pipeline; doctor checks; runbook. |
| Verification | Backtest acceptance tests (WI-7) reproducing the §5.1 intents; doctor check that the three orderings are unified; evidence-gated activation is fail-closed. |
| Rollback | Model is shadow/advisory until WI-4 activation; activation is behind the existing production-gate fail-closed path, so rollback = revert to precedence sort. |
| Open decisions | The §7 owner-grilling questions. |

---

## 9. Prior Deliberations

- **No prior deliberations found** for dispatch-attribute calibration or dispatcher self-optimization (searched 2026-07-04: "harness dispatch selection attributes cost quality availability"; "dispatcher self-optimization data-driven"; "harness capability adjustment weekly" — 0 matches). This is novel design territory.
- Related existing artifacts (not deliberations): `lane_scoring.py` shadow lane model; `harness_quality_manifest.py` / `harness_quality_reporting.py` benchmark scaffold (owner-decision anchors DELIB-20263440..447 per the earlier token-accounting advisory); LO advisory `INSIGHTS-2026-07-03-18-32.md` (per-work-item token accounting + harness comparison) — a direct upstream input to WI-2's cost proxy.

---

*Loyal Opposition advisory. Non-mutating; read-only investigation. This report tasks Prime Builder to file an umbrella project proposal after clearing the §7 owner-grilling gate; it does not itself authorize implementation.*

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
