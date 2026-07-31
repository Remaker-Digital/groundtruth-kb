ADVISORY

# Advisory Proposal — Activate Per-Lane (Harness + Provider + Model + Role + Activity) Dispatch Selection

bridge_kind: governance_advisory
Document: gtkb-advisory-proposal-per-lane-harness-model-dispatch-selection
Version: 001
Date: 2026-07-16 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2f6a0618-d857-497d-ac8c-a509f544007e
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive; session-stated resolved role Prime Builder; ::init gtkb pb

## Note On Authorship

Same authorship-boundary situation as the sibling advisory filed earlier this
session (`gtkb-advisory-proposal-dropbox-successor-and-project-lifecycle-fusion`):
this session's resolved role is Prime Builder throughout; ADVISORY entries are
conventionally Loyal-Opposition-authored or owner-directed. Filing authority here
rests on direct owner instruction in this session's transcript.

## Source

Owner-directed live investigation request in this interactive session
(`2f6a0618-d857-497d-ac8c-a509f544007e`), 2026-07-16, immediately following the
dropbox/project-lifecycle advisory. The owner asked for a detailed, investigated
Advisory Proposal — not a green-field design — covering the needed implementation
project and work items, guiding specifications/GOV, relevant deliberations, and
explicitly which past decisions would need to be purged, flagged superseded, or
revoked.

## Owner's Proposal (preserved close to verbatim)

> Each harness is a point of integration with a model provider. In some cases,
> the "harness" is a minimal endpoint for an Anthropic-compliant API. In other
> cases, the desktop UI/CLI provides a richer user environment and makes direct
> access to the cloud service difficult and expensive, since the GUI/CLI
> environment is subsidized with unique flat-rate pricing.
>
> Each "harness" is capable of serving multiple models, which we can select for
> each headless worker that is dispatched. The current dispatcher solution does
> not allow for dispatch target selection with this granularity, but this level
> of control is very valuable, and will allow us to choose models based on:
> quality, configure each model service for the work task at hand, and choose
> the harness based on cost, availability, performance and other distinguishing
> characteristics balanced against time-of-use cost.
>
> For example: Claude Code should be configured to use Sonnet 5, Extra High
> Effort when in the LO role, executing NEW bridge item reviews, but it should
> use Opus 4.6 when filling the role of dispatchable PB. This example is based
> on published benchmarks, but with the information that we collect from real
> work we will be able to optimize dispatch and greatly improve the efficiency,
> scalability and aggregate quality of GT-KB-supported projects.

**Factual precision note:** the owner's worked example names "Opus 4.6." Current
Anthropic model names (per this assistant's own knowledge and matching the live
config's existing literal `claude-opus-4-8`) are the Claude 5 family: Sonnet 5,
Opus 4.8, Haiku 4.5, Fable 5. There is no "Opus 4.6." This is flagged for
correction in the concrete lane configuration, not silently substituted — the
grilling session should confirm the intended model (most likely Opus 4.8) before
any config lands.

## Executive Finding — This Is An Activation Gap, Not A Green-Field Design

The investigation found the owner already decided this exact target architecture
two weeks ago, and roughly 70% of the mechanism already exists in source. The
central finding: **a fully-built lane-scoring module already computes
`(harness_id, provider, model_route, session_role, activity_type)` as its lane
identity — confirmed by direct source read — but it is a documented
"non-activating shadow." The live dispatcher still ranks by
`reviewer_precedence + harness_id` only, and one day after that shadow status was
documented, a separate VERIFIED work item deliberately flattened the harness-level
quality/cost/availability scores to identical values across five harnesses.**
This proposal is substantially about activating dormant, already-authorized
capability and replacing a deliberate placeholder with real data — not designing
something new.

## Current-State Findings (verified this session, with evidence)

### 1. The owner already decided the target architecture — 2026-07-02

- **`DELIB-20260702-DISPATCH-RANKING-ATOMIC-TARGET`**: "Mike selected
  `harness_id + provider + model + session_role + activity_type` as the atomic
  dispatch ranking target... Model/provider quality and price should therefore be
  visible to dispatcher ranking instead of hidden behind harness-internal
  routing." `spec_id: DCL-DISPATCH-ENVELOPE-RULES-001`.
- **`DELIB-20260702-DISPATCH-LANE-MATRIX-SCOPE`**: selected a complete matrix
  (every role x activity lane per harness/model route, including disabled/
  interactive-only lanes) over a sparse or dispatchable-only matrix, specifically
  so absence never has to stand in for a disabled/unknown/unsupported state.
- **`DELIB-20260702-DISPATCH-DURABLE-ROLE-HARD-GATE`**: durable harness role
  membership remains a hard gate for production dispatch. "The complete lane
  matrix may score every role/activity lane for every harness/model route, but
  production dispatch can select only lanes whose session_role is present in the
  harness's durable role set." This directly resolves a boundary question the
  new proposal would otherwise need fresh owner input on: **model selection is a
  refinement WITHIN an already-role-gated dispatch, not a replacement for role
  gating.** No conflict with the standing role-authority model
  (`GOV-SESSION-ROLE-AUTHORITY-001`) was found.

### 2. The scoring mechanism already exists in source, dormant

`groundtruth_kb/dispatcher/lane_scoring.py` (confirmed via direct read, not
inferred from a title): a frozen dataclass lane identity carrying `provider`,
`model_route`, `activity_type`, and role; a `_route_provider()` /
`_model_route()` resolver pair; a documented "deterministic lane identity for
harness/provider/model/role/activity" computation; and a quality-index lookup
keyed by `(harness_id, role, activity_type)`. This is not a stub — it is a
working implementation of the 2026-07-02 decision.

`WI-5012` ("Selection-binding + SoT-consolidation audit," RESOLVED 2026-07-06)
documented the gap precisely: *"the true live selection path (dispatcher_runtime
active_matching sorts by reviewer_precedence + harness_id; **lane_scoring.py is a
non-activating shadow**) ... decide Option P-A (activate lane_scoring production
path) vs P-B (wire attributes into dispatcher_runtime ranking)."* WI-5012's own
scope was documentation/reconciliation and an SoT-consolidation slice — it is not
clear from this WI's record alone whether P-A or P-B was ever actually chosen and
executed, or whether the decision point is still open. **This is an open
question for the grilling session, not something this advisory resolves.**

### 3. One day later, a VERIFIED work item flattened scoring to remove it as a live signal

`WI-5033` ("Flatten dispatch ranking values to a single Codex baseline
(post-tiebreak)," VERIFIED 2026-07-07,
`bridge/gtkb-wi5033-dispatch-ranking-flattening-004.md`): set
`quality=90 / cost=60 / availability=90 / reviewer_precedence=20` **identically**
on harnesses B, C, D, E, F via the governed `gt bridge dispatch config
set-weights` overlay, depending on `WI-5032`'s uniform-random terminal tiebreak
for the resulting full ties. This is directly confirmed by the harness-registry
data this session already read: every active harness currently shows
`dispatch_quality: 90.0`, most show `dispatch_cost: 60.0` and
`dispatch_availability: 90.0` — the flattened values are live today.

The title's "Codex baseline" phrasing indicates the pre-flattening per-harness
values were arbitrary/uncalibrated rather than evidence-based, and were producing
an unintended systematic bias toward Codex specifically. Read charitably (and
this reading is consistent with WI-5322, filed earlier this session, which
established "start generous/neutral, narrow only from real data" as the governing
philosophy for dispatch caps and timers): **WI-5033 was a reasonable interim
fairness fix given the absence of real evidence, not an architectural rejection
of differentiated scoring.** The owner's new proposal does not need to reverse
WI-5033's intent — it needs to supersede its specific flattened VALUES with real,
benchmark-derived, per-lane values once that evidence exists. This is the
clearest, most concrete answer to "what needs to be flagged as superseded":
**`WI-5033`'s flattened quality/cost/availability/reviewer_precedence values are
superseded in effect (not in governance intent) the moment real per-lane
benchmark data exists to replace them.**

### 4. A substantially-complete benchmark/quality-KPI infrastructure already exists

`PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1` — 9 of 11 work items
resolved/VERIFIED, including:
- `WI-4791` (VERIFIED): "Quality-KPI subsystem: consensus capture calibrated by
  seeded-flaw fixtures; compute relative quality inside the dispatcher and feed
  TAFE; per-activity quality-required floors."
- `WI-4792` (VERIFIED): "Harness-adaptation impact measurement: versioned
  adaptations + seeded-flaw fixture A/B for attributable KPI deltas."
- `WI-4586` (design-only GO, no implementation required): "Design gated future
  enforcement path for benchmark-informed dispatch" — i.e., a reviewed,
  GO'd design for USING benchmark output to drive dispatch decisions, distinct
  from collecting the benchmark output itself.

This is very likely the mechanism the owner meant by "the information that we
collect from real work." **Open question for the grilling session, not resolved
by this investigation:** does the existing Quality-KPI feed (WI-4791) already
carry model-level granularity, or does it currently attribute quality to the
harness only (pre-dating the 2026-07-02 atomic-target decision)? If the latter,
extending it to the `(harness, provider, model, role, activity)` granularity is
itself an implementation slice, not just a wiring exercise.

### 5. Two different, disconnected model-configuration mechanisms exist today

- **Shim harnesses** (D/ollama, F/openrouter, H/alibaba-cloud-studio; G/goose is
  retired) already have a per-skill model-routing schema:
  `.api-harness/routing.toml`, `[routing.<harness>.skills]` mapping
  `bridge-review` / `verification` / `implementation` to specific models. In
  practice, every skill for every harness currently routes to the same single
  model — the schema supports variation; no harness's data uses it yet.
- **GUI/CLI-native harnesses** (A/codex, B/claude, C/antigravity; E/cursor is
  suspended) have no equivalent at all. Their model is a single hardcoded value
  baked into the harness registry's `invocation_surfaces.headless.argv` (e.g.,
  B currently launches with `--model claude-opus-4-8` unconditionally,
  regardless of role or activity), and duplicated separately in
  `config/dispatcher/rules.toml`'s `[budget.harnesses.B] model = "claude-opus-4-8"`.
  This is the specific gap the owner's Claude Code worked example targets, and it
  is the larger of the two implementation surfaces — the shim harnesses need
  their existing per-skill routing generalized to per-ROLE (not just per-skill)
  and actually populated; the native harnesses need a per-role model-selection
  mechanism built from closer to scratch, since none of their invocation
  machinery is currently conditional on role or activity at all.
- The duplication between the registry's `invocation_surfaces.headless.argv`
  model and `rules.toml`'s `[budget.harnesses.*].model` is itself an instance of
  the SoT-duplication class WI-5012 was generally chartered to close ("give the
  five duplicated dispatch/eligibility fields ONE authoritative home"). Whether
  "model" was one of the five fields already consolidated, or is a sixth
  instance the audit did not cover, was not confirmed and is a grilling
  candidate.

### 6. Cost differentiation is schema-ready but data-empty, matching the quality gap

Every harness's `budget.harnesses.*` entry shows `pricing: "priced"` but
`estimated_usd_per_dispatch: 0.0` — cost is structurally modeled but currently
uniformly zero for all harnesses, mirroring the quality-flattening finding above.
The owner's "GUI/CLI subsidized flat-rate vs. metered cloud API" distinction is
real and currently unmodeled: Claude Code and Codex Desktop plausibly run under
flat-rate subscription economics, while OpenRouter and direct Anthropic-API
routes (Ollama's cloud routing, Alibaba Cloud Studio) are metered per-call. No
existing mechanism distinguishes these today; `estimated_usd_per_dispatch: 0.0`
for every harness is the same "no evidence yet" placeholder state as the
flattened quality scores.

## Needed Implementation Project And Work Items (shape, not filed)

Presented as candidate scope for the grilling session to confirm, adjust, or
reject — not as pre-authorized work:

1. **Resolve the P-A/P-B activation decision** (WI-5012's own open fork):
   activate `lane_scoring.py` as the live selection path inside
   `dispatcher_runtime.active_matching`, or port its lane-dimensional model
   directly into the existing ranking function. Requires confirming which (if
   either) was already chosen.
2. **Extend WI-4791's Quality-KPI feed to lane granularity** if it does not
   already carry `(harness, provider, model, role, activity)` attribution —
   contingent on the open question in Finding 4.
3. **Generalize `.api-harness/routing.toml`'s per-skill routing to per-role**,
   and build the equivalent mechanism for the GUI/CLI-native harnesses (A/B/C),
   consolidating the registry-argv vs. rules.toml model duplication into one SoT
   as part of the same slice.
4. **Populate the first real, differentiated lane configuration** using the
   owner's own worked example as the seed case (Claude/B: Sonnet 5 XHigh for
   loyal-opposition + NEW-review activity; Opus 4.8 for dispatchable
   prime-builder activity) — superseding WI-5033's flattened values for harness B
   specifically, without necessarily touching C/D/E/F until their own real data
   exists.
5. **Replace `estimated_usd_per_dispatch: 0.0` placeholders with real cost data**
   distinguishing flat-rate-subsidized vs. metered-API routes, so "cost" becomes
   a meaningful ranking dimension per `selection_order`.
6. **Coordinate with `WI-5322`** (filed earlier this session: live, provider-
   backed load testing to set concurrency caps and timer floors via a
   generous-start/narrow-with-real-data methodology) — per-model timer floors and
   per-model concurrency behavior are adjacent, coupled tuning surfaces to this
   proposal's per-model selection work, and the two should likely share
   benchmark/telemetry infrastructure rather than duplicate it.

## Guiding Specifications And GOV

- `DCL-DISPATCH-ENVELOPE-RULES-001` (status: `specified`, not implemented) —
  the associated design constraint for the dispatch-envelope/rule-registry
  program; its schema (`id/trigger/target/activity_gate/payload/persist`)
  notably does NOT match the live `config/dispatcher/rules.toml` schema
  (`selection_order`/`[budget]`/`[harnesses]`/`[[rules]]`) found this session —
  a discrepancy worth surfacing to the grilling session, since it suggests this
  DCL's design and the live file diverged at some point.
- `ADR-DISPATCHER-ARCHITECTURE-001` — architecture of record for the dispatcher;
  cited as governing by the above DCL.
- `GOV-SESSION-ROLE-AUTHORITY-001` — the durable-role-as-hard-gate decision is
  filed under this spec; confirmed compatible, not superseded, by this proposal.
- `GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`,
  `GOV-HARNESS-ONBOARDING-CONTRACT-001` — govern harness/role assumptions this
  proposal's implementation must remain compatible with (role portability is
  about which ROLE a harness may hold, independent of which model it uses inside
  that role — no conflict found, but not exhaustively verified against every
  clause).
- `GOV-AUTOMATION-VALUE-VS-COST-001` — directly relevant to a cost-optimization
  dispatch proposal; not read in full this session.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — the dispatcher's core governing spec.
- `GOV-STANDING-BACKLOG-001` — governs where any resulting work items land.

## Prior Deliberations

- `DELIB-20260702-DISPATCH-RANKING-ATOMIC-TARGET`,
  `DELIB-20260702-DISPATCH-LANE-MATRIX-SCOPE`,
  `DELIB-20260702-DISPATCH-DURABLE-ROLE-HARD-GATE` — the 2026-07-02 decision
  cluster establishing the target architecture this proposal would activate.
  Three sibling decisions from the same date
  (`DELIB-20260702-DISPATCH-SCORING-SNAPSHOT-PROMOTION`,
  `DELIB-20260702-DISPATCH-SCORING-REGISTRY-SOT`,
  `DELIB-20260702-DISPATCH-LANE-ACTIVITY-VOCAB-V1`) were identified by reference
  but not read in full this session — the grilling session or a follow-on
  investigation slice should cover them before implementation scoping locks in.
- `DELIB-20263440` (2026-06-16) — full cross-role benchmark coverage decision
  underpinning `PROJECT-HARNESS-TESTING-AND-QUALITY-BENCHMARKING-1`.
- WI-5012, WI-5032, WI-5033 bridge threads and their governing project
  `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION` — the most directly
  relevant prior implementation activity; only three work items deep, actively
  authorized, immediately adjacent in scope.
- Deliberation search performed before drafting (four distinct queries covering
  cross-role benchmarking, model-pin drift, harness benchmark matrix, and this
  proposal's own topic) returned no other directly duplicating record.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Open Questions (explicitly unresolved — grilling candidates)

1. Was WI-5012's P-A (activate `lane_scoring.py`) vs. P-B (port attributes into
   `dispatcher_runtime`) fork ever actually decided and executed, or does it
   remain open? This determines the shape of implementation-slice 1 above.
2. Does WI-4791's Quality-KPI feed already carry model-level attribution, or
   harness-level only? Determines whether slice 2 above is a wiring task or a
   fresh measurement-extension task.
3. Scope: does this become its own new project, or a follow-on slice inside the
   existing, actively-authorized `PROJECT-GTKB-DISPATCH-SELECTION-SELF-
   OPTIMIZATION`?
4. Beyond the one worked example (Claude/B: Sonnet 5 XHigh LO / Opus 4.8 PB),
   which other harness/model/role combinations should the first implementation
   slice cover, versus leaving for later real-data-driven iterations?
5. Confirm the model name: Opus 4.8 (matching current naming and the existing
   config literal), or does the owner mean something else by "Opus 4.6"?
6. Should cost-model population (item 5 above) be sequenced before or after
   quality-model population, given both are currently zero/flat placeholders?
7. Coordination boundary with `WI-5322`'s load-testing program: shared
   benchmark/telemetry infrastructure, or independently scoped and only loosely
   coupled?

## Required Prime Builder Owner-Grilling Gate

### Implementation implied
Yes — activating `lane_scoring.py`, extending the Quality-KPI feed, generalizing
`.api-harness/routing.toml`, building native-harness per-role model selection,
and superseding WI-5033's flattened values all require source, config, and
possibly MemBase schema changes.

### Grill-the-owner questions
The seven Open Questions above, plus:
8. Is there appetite to also resolve the `DCL-DISPATCH-ENVELOPE-RULES-001` /
   live-`rules.toml`-schema discrepancy as part of this program, or should that
   be tracked as a fully separate hygiene item?

### Required durable owner decisions
Resolution of Open Questions 1-8 via AskUserQuestion before an implementation
proposal is filed, plus explicit project/scope disposition (Open Question 3).

## Non-Approval Statement

This advisory is NOT implementation approval. It does not open an
implementation-start packet, authorize protected edits, or bypass the bridge,
project-authorization, owner-decision, root-boundary, credential-safety,
formal-artifact, or verification gates. Any derived implementation proposal
requires a normal Prime Builder proposal, independent Loyal Opposition GO, a
matching work-intent claim, and implementation-start authorization before any
code, config, or schema change.

## Owner Decisions / Input

- Owner directly instructed this investigation and advisory in this session's
  transcript (2026-07-16), including the explicit instruction to identify past
  decisions requiring supersession/revocation.
- No AskUserQuestion has yet been run for this proposal's Open Questions; none
  of the candidate implementation scope above is authorized.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
