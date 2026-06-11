NEW

bridge_kind: prime_proposal
Document: gtkb-fab-20-hygiene-investigation-skill
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4432
Project Authorization: PAUTH-FAB20-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: e45ccf07-99f6-4ad6-b572-570a76a264a2
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: [".claude/skills/gtkb-hygiene-investigation/**", ".codex/skills/gtkb-hygiene-investigation/**", "scripts/hygiene/**", "config/governance/hygiene-baseline-registry.toml", "config/agent-control/harness-capability-registry.toml", "platform_tests/**"]

No KB mutation: all FAB-20 changes are skill files (`.claude/skills` + `.codex` adapter), helper scripts, a baseline-registry config artifact, and tests; no `groundtruth.db` write. `groundtruth.db` is intentionally NOT in target_paths.

---

# FAB-20 — gtkb-hygiene-investigation Skill + Delta Mode

WI-4432 (FAB-20) of PROJECT-FABLE-INVESTIGATION. Charter: the Q5 repeatability architecture in
`bridge/gtkb-fable-investigation-advisory-001.md` ("Hygiene-Capability Enhancement Plan"). FAB-20 is the
orchestration-skill half of the layered design; FAB-19 is the deterministic-core half. This cluster has no
per-finding HYG owner touchpoint — the design is fully chartered by `DELIB-FABLE-GRILL-20260610-Q5`.

Theme: turn the proven 16-subagent / 4-round hygiene investigation (which cost ~3.4M tokens as a manual
first run) into a repeatable, governed skill that consumes FAB-19's deterministic evidence pack and re-runs
at owner-set token targets (<=400K full / <=150K delta).

## Summary

- **Orchestration skill.** A `gtkb-hygiene-investigation` skill packaging the method that produced the
  68-finding investigation: parallel focus-area probes against the structured findings schema (slug / class /
  locations / verification / ratings / owner-question), a gap-probe + completeness-critic + adversarial-skeptic
  round, and loop-until-dry with explicit decay disclosure.
- **Chunked report generator.** A helper that emits the report keyed to the findings schema in chunks, so a
  large finding corpus does not hit single-context size limits (the v1 report alone is ~3,200 lines).
- **Delta mode.** A differ keyed to a new HYG-001..068 baseline registry: diff FAB-19's layer-1 evidence pack
  against the baseline and probe ONLY the changed surfaces, emitting token-target compliance against the Q5
  budgets.
- Probe prompts consume FAB-19's deterministic evidence pack at ~0 tokens instead of re-deriving the census.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the skill packages the proven investigation method as a durable,
  reusable artifact; re-run findings become governed backlog items rather than chat-only context.
- `SPEC-DSI-DOCTOR-CHECK-001` — doctor/invariant reporting; delta mode reports drift against the baseline
  registry in the same spirit (deterministic, evidence-backed).
- `GOV-08` (Knowledge Database is the single source of truth) — probes and delta mode report drift against
  canonical state; findings route to the backlog (`work_items`), not markdown.
- `GOV-STANDING-BACKLOG-001` — WI-4432 is the governed backlog authority; the skill's output feeds the
  standing backlog under the capture-is-not-implementation-approval rule.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-20 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory; Q5 "Hygiene-Capability Enhancement
  Plan" details the FAB-19/FAB-20 layered design and token targets.
- `DELIB-FABLE-GRILL-20260610-Q5` — the owner repeatability-architecture decision (layered deterministic core
  + orchestration skill + delta mode; <=400K full / <=150K delta).
- `DELIB-FAB20-REMEDIATION-20260610` — this cluster's determination (build per Q5; no new owner AUQ).
- `DELIB-FAB19-REMEDIATION-20260610` — the deterministic-core cluster whose expanded sweep/census output is
  FAB-20's layer-1 evidence pack.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive AI work is a defect; the skill + delta mode move
  the re-derivable census into deterministic surfaces.

## Owner Decisions / Input

The skill architecture is owner-chartered by `DELIB-FABLE-GRILL-20260610-Q5` (AskUserQuestion, interactive
owner session 2026-06-10): a layered design of (1) a deterministic CLI detector core (FAB-19), (2) a
`gtkb-hygiene-investigation` orchestration skill (this cluster), and (3) a delta mode keyed to the
HYG-001..068 baseline registry, at token targets **<=400K full re-run** and **<=150K delta** (vs ~3.4M for
the manual first run). No member finding carries an "Owner Touchpoint Required"; the design parameters are
owner-fixed. FAB-20 introduces no new owner decision; the determination is recorded in
`DELIB-FAB20-REMEDIATION-20260610`.

## Requirement Sufficiency

**Existing requirements sufficient.** The disposition is fixed by `DELIB-FABLE-GRILL-20260610-Q5` and
recorded in `DELIB-FAB20-REMEDIATION-20260610`; the governing specifications
(`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `SPEC-DSI-DOCTOR-CHECK-001`, `GOV-08`, `GOV-STANDING-BACKLOG-001`)
already constrain the artifact-oriented, doctor-reporting, source-of-truth, and backlog surfaces. No new
requirement is needed; the skill encodes an already-executed and verified method.

## Scope and Boundaries

In scope: the `gtkb-hygiene-investigation` SKILL.md + helper scripts (probe orchestration prompts, chunked
report generator, delta-mode differ), the HYG-001..068 baseline-registry config artifact, the Codex adapter,
capability-registry registration, and tests. Out of scope and explicitly excluded: the deterministic detector
core (FAB-19, the layer-1 dependency); any per-finding remediation a re-run surfaces (those become their own
backlog items); actually running the first scheduled re-investigation; deploy/push. This proposal absorbs the
advisory's FAB-20 row (the skill + delta-mode items) and the overlapping 3391 item by describing them here.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`: FAB-20 itself performs **no bulk backlog operation** —
it adds skill/script/config files and writes nothing to `work_items`. The skill's chunked report generator
emits a findings **inventory** artifact (the structured report), and any future bulk routing of re-run
findings into the `work_items` backlog is a separate, owner-gated step under GOV-STANDING-BACKLOG-001
(capture is not implementation approval): such a routing run would carry its own inventory + review packet
and AskUserQuestion evidence. No bulk mutation is authorized by this proposal.

## Proposed Implementation

**Area 1 — orchestration skill.** Author `.claude/skills/gtkb-hygiene-investigation/SKILL.md` packaging the
proven method: parallel focus-area probe prompts using the structured findings schema
(slug / class / locations / verification / impact-effort-confidence ratings / owner-question); a gap-probe +
completeness-critic + adversarial-skeptic round; loop-until-dry with a decay-disclosure rule (report the
new-findings decay curve and the cut round). Probe prompts reference FAB-19's evidence pack as layer-1 input
rather than re-deriving the census.

**Area 2 — chunked report generator.** A helper under `scripts/hygiene/` that renders the findings into the
v1-style report in chunks keyed to the schema, so a large corpus does not exceed single-context limits.

**Area 3 — delta mode + baseline registry.** Create `config/governance/hygiene-baseline-registry.toml`
seeded from the HYG-001..068 frozen findings (the advisory + v1 report). A `scripts/hygiene/` differ diffs
FAB-19's layer-1 evidence pack against the baseline, marks changed surfaces, and the skill probes ONLY those;
the run emits token-consumption against the Q5 targets (<=400K full / <=150K delta).

**Area 4 — Codex adapter + registration.** Generate the `.codex/skills/gtkb-hygiene-investigation/` adapter
(via the existing adapter generator) and register the skill in
`config/agent-control/harness-capability-registry.toml` so parity stays green.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-20 changes are in-root under `E:\GT-KB\` — the skill at
`.claude/skills/gtkb-hygiene-investigation/`, the Codex adapter at `.codex/skills/`, helper scripts under
`scripts/hygiene/`, the baseline registry at `config/governance/hygiene-baseline-registry.toml`, the
capability-registry entry under `config/agent-control/`, tests under `platform_tests/`, and this bridge file
under `E:\GT-KB\bridge\`. The cluster relocates no file, touches no `applications/` subtree, and writes no
out-of-root artifact; the skill investigates the in-root platform and writes its evidence to in-root paths.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (skill packages the method) | test: the skill exists with the structured findings schema + the 4-round (probe / gap / completeness-critic / adversarial-skeptic) workflow + loop-until-dry decay disclosure; the Codex adapter is generated and parity is green |
| `SPEC-DSI-DOCTOR-CHECK-001` + `GOV-08` (delta mode reports drift against canonical baseline) | test: delta mode against the HYG-001..068 baseline registry, given an unchanged layer-1 evidence pack, reports zero changed surfaces and stays within the <=150K delta target; a seeded baseline change is detected and probed |
| `GOV-STANDING-BACKLOG-001` (re-run output routes to the backlog) | test: a generated finding is emitted in a form routable to `work_items` (not markdown-only) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/...` for the report generator + differ + baseline-registry loader; `ruff check` AND `ruff format --check` on changed Python |

## Acceptance Criteria

1. `gtkb-hygiene-investigation` SKILL.md exists with the structured findings schema, the 4-round probe
   workflow, and loop-until-dry decay disclosure; the Codex adapter is generated and capability parity is
   green.
2. The chunked report generator renders the v1-style report from a findings list without exceeding a
   single-context size limit.
3. The HYG-001..068 baseline registry exists; delta mode detects changed surfaces against it and emits
   token-consumption against the Q5 targets (<=400K full / <=150K delta).
4. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-20-hygiene-investigation-skill-001.md` with a matching `NEW` entry at the top of
`bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal
Opposition records `GO`.

## Risk and Rollback

- **Risk — the skill re-derives census the deterministic core should provide (token blow-out):** the skill's
  probe prompts MUST consume FAB-19's evidence pack as layer-1 input; a verification test asserts delta mode
  stays within the <=150K target on an unchanged pack. **Rollback:** the skill is additive (new files only);
  remove the skill dir + adapter + registry entry.
- **Risk — the baseline registry drifts from the report:** it is seeded once from the frozen HYG-001..068
  findings and versioned; re-runs update it deliberately. **Rollback:** revert the config file.
- **Risk — delta mode under-probes a changed surface (false "no change"):** the completeness-critic +
  adversarial-skeptic round is retained in delta runs as a backstop, and the decay-disclosure rule surfaces
  premature termination. **Rollback:** fall back to a full run (the differ is advisory to scope, not a gate).

## Recommended Implementation Routing

**Hybrid.** The SKILL.md probe prompts encode the investigation method and are best authored by Opus/Codex;
the deterministic helpers (chunked report generator, baseline differ, registry loader) are
**cheap-model-draftable** and Opus-finalized. Pairs with FAB-19 (the deterministic evidence pack it
consumes) — FAB-19 should land first.

## Recommended Commit Type

`feat:` — net-new `gtkb-hygiene-investigation` skill, chunked report generator, delta-mode differ, and
HYG-001..068 baseline registry (new repeatable-investigation capability).
