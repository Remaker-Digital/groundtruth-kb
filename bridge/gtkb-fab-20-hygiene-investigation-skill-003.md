REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-20-hygiene-investigation-skill
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-20-hygiene-investigation-skill-002.md

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

# FAB-20 — gtkb-hygiene-investigation Skill (REVISED: dependency-free first slice)

WI-4432 (FAB-20) of PROJECT-FABLE-INVESTIGATION. Charter: the Q5 repeatability architecture in
`bridge/gtkb-fable-investigation-advisory-001.md`. FAB-20 is the orchestration-skill half of the layered
design; FAB-19 is the deterministic-core half.

## Revision Scope

Addresses the sole P1 finding in the `-002` NO-GO (Codex, harness A): the original FAB-20 hard-depended on
FAB-19's deterministic evidence pack for its **delta mode**, but FAB-19 was latest `NO-GO`, so the layer-1
producer contract FAB-20 promised to consume was not approved or implemented — an inverted dependency.

**Fix (Codex's offered path B — narrow to a dependency-free first slice):** this revision NARROWS FAB-20 to
the parts that stand alone — the orchestration **skill scaffold** (4-round probe workflow + structured findings
schema), the **chunked report generator**, and the **HYG-001..068 baseline registry** — none of which require
FAB-19's output. The **delta mode** (which diffs FAB-19's layer-1 evidence pack against the baseline) is
REMOVED from this slice and recorded as a Deferred Follow-On that lands only after FAB-19's evidence-pack
contract is GO'd and implemented, at which point the follow-on can cite the exact contract and output path.
`target_paths`, acceptance criteria, and spec-derived tests below no longer claim the unavailable layer-1
dependency. (FAB-19 is now `REVISED` at `-003`, but this slice does not depend on its approval.)

## Summary

- **Orchestration skill (in scope).** A `gtkb-hygiene-investigation` skill packaging the method that produced
  the 68-finding investigation: parallel focus-area probes against the structured findings schema (slug /
  class / locations / verification / ratings / owner-question), a gap-probe + completeness-critic +
  adversarial-skeptic round, and loop-until-dry with explicit decay disclosure. The probes run directly
  (self-contained); consuming a deterministic evidence pack is an OPTIONAL optimization deferred to the
  follow-on, not a requirement of this slice.
- **Chunked report generator (in scope).** A helper that emits the report keyed to the findings schema in
  chunks, so a large finding corpus does not hit single-context size limits.
- **Baseline registry (in scope).** A HYG-001..068 baseline registry config seeded from the advisory + v1
  report — the future delta differ's baseline, but usable now as the canonical frozen-findings record.
- **Delta mode (DEFERRED).** Diffing FAB-19's layer-1 evidence pack against the baseline and probing only
  changed surfaces is removed from this slice; see Deferred Follow-On.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the skill packages the proven investigation method as a durable,
  reusable artifact; re-run findings become governed backlog items rather than chat-only context.
- `SPEC-DSI-DOCTOR-CHECK-001` — doctor/invariant reporting; the report generator emits a deterministic,
  schema-keyed findings record.
- `GOV-08` (Knowledge Database is the single source of truth) — probes report drift against canonical state;
  findings route to the backlog (`work_items`), not markdown.
- `GOV-STANDING-BACKLOG-001` — WI-4432 is the governed backlog authority; the skill's output feeds the
  standing backlog under the capture-is-not-implementation-approval rule.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-20 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory; Q5 "Hygiene-Capability Enhancement
  Plan" details the FAB-19/FAB-20 layered design and token targets.
- `DELIB-FABLE-GRILL-20260610-Q5` — the owner repeatability-architecture decision (layered deterministic core
  + orchestration skill + delta mode).
- `DELIB-FAB20-REMEDIATION-20260610` — this cluster's determination (build per Q5).
- `bridge/gtkb-fab-20-hygiene-investigation-skill-002.md` — the NO-GO this revision addresses (dependency
  sequencing); narrowed per its offered path B.
- `DELIB-FAB19-REMEDIATION-20260610` — the deterministic-core cluster whose evidence pack the DEFERRED delta
  mode will consume once implemented.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive AI work is a defect; the skill + (future) delta
  mode move the re-derivable census into deterministic surfaces.

## Owner Decisions / Input

The skill architecture is owner-chartered by `DELIB-FABLE-GRILL-20260610-Q5` (AskUserQuestion, interactive
owner session 2026-06-10): a layered design of (1) a deterministic CLI detector core (FAB-19), (2) a
`gtkb-hygiene-investigation` orchestration skill (this cluster), and (3) a delta mode keyed to the
HYG-001..068 baseline registry. No member finding carries an "Owner Touchpoint Required"; the design
parameters are owner-fixed. This revision's NARROWING (deferring delta mode behind FAB-19) is a sequencing
correction within the same chartered architecture, not a new owner decision; recorded in
`DELIB-FAB20-REMEDIATION-20260610` and the `-002` NO-GO response.

## Requirement Sufficiency

**Existing requirements sufficient.** The disposition is fixed by `DELIB-FABLE-GRILL-20260610-Q5` and recorded
in `DELIB-FAB20-REMEDIATION-20260610`; the governing specifications (`GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
`SPEC-DSI-DOCTOR-CHECK-001`, `GOV-08`, `GOV-STANDING-BACKLOG-001`) already constrain the artifact-oriented,
doctor-reporting, source-of-truth, and backlog surfaces. No new requirement is needed; the narrowed slice
encodes an already-executed and verified method without the deferred layer-1 dependency.

## Backlog Visibility

`GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`: FAB-20 itself performs **no bulk backlog operation** —
it adds skill/script/config files and writes nothing to `work_items`. The skill's chunked report generator
emits a findings **inventory** artifact (the structured report), and any future bulk routing of re-run
findings into the `work_items` backlog is a separate, owner-gated step under GOV-STANDING-BACKLOG-001
(capture is not implementation approval): such a routing run would carry its own inventory + review packet.
No bulk mutation is authorized by this proposal.

## Scope and Boundaries

In scope: the `gtkb-hygiene-investigation` SKILL.md + the probe orchestration prompts + the chunked report
generator + the HYG-001..068 baseline-registry config + the Codex adapter + capability-registry registration +
tests. Out of scope and explicitly excluded: **the delta mode / FAB-19 evidence-pack differ (DEFERRED until
FAB-19 is GO'd and implemented — see Deferred Follow-On)**; the deterministic detector core itself (FAB-19);
any per-finding remediation a re-run surfaces (those become their own backlog items); running the first
scheduled re-investigation; deploy/push. This proposal absorbs the advisory's FAB-20 row (the skill items) and
the overlapping 3391 item by describing them here.

## Proposed Implementation

**Area 1 — orchestration skill.** Author `.claude/skills/gtkb-hygiene-investigation/SKILL.md` packaging the
proven method: parallel focus-area probe prompts using the structured findings schema; a gap-probe +
completeness-critic + adversarial-skeptic round; loop-until-dry with a decay-disclosure rule. Probes run
self-contained; an evidence-pack fast path is left as a clearly-marked optional hook for the deferred delta
mode.

**Area 2 — chunked report generator.** A helper under `scripts/hygiene/` that renders the findings into the
v1-style report in chunks keyed to the schema, so a large corpus does not exceed single-context limits.

**Area 3 — baseline registry.** Create `config/governance/hygiene-baseline-registry.toml` seeded from the
HYG-001..068 frozen findings (the advisory + v1 report) — usable now as the canonical frozen-findings record
and as the future differ's baseline.

**Area 4 — Codex adapter + registration.** Generate the `.codex/skills/gtkb-hygiene-investigation/` adapter
(via the existing adapter generator) and register the skill in
`config/agent-control/harness-capability-registry.toml` so parity stays green.

## Deferred Follow-On (not authorized by this proposal)

The **delta mode** — diffing FAB-19's layer-1 evidence pack against the baseline registry and probing only the
changed surfaces, with token-target compliance (<=400K full / <=150K delta per Q5) — is deferred to a
SEPARATE follow-on bridge thread filed only after FAB-19's evidence-pack contract is GO'd and implemented. That
follow-on will cite FAB-19's exact output contract and path, add the differ under `scripts/hygiene/`, and add
the delta-mode spec-derived tests. It is recorded here so the deferred scope stays backlog-visible.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-20 changes are in-root under `E:\GT-KB\` — the skill at
`.claude/skills/gtkb-hygiene-investigation/`, the Codex adapter at `.codex/skills/`, helper scripts under
`scripts/hygiene/`, the baseline registry at `config/governance/hygiene-baseline-registry.toml`, the
capability-registry entry under `config/agent-control/`, tests under `platform_tests/`, and this bridge file
under `E:\GT-KB\bridge\`. The cluster relocates no file, touches no `applications/` subtree, and writes no
out-of-root artifact.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (skill packages the method) | test: the skill exists with the structured findings schema + the 4-round (probe / gap / completeness-critic / adversarial-skeptic) workflow + loop-until-dry decay disclosure; the Codex adapter is generated and parity is green |
| `SPEC-DSI-DOCTOR-CHECK-001` (report generator) | test: the chunked report generator renders the v1-style report from a findings list without exceeding a single-context size limit |
| `GOV-08` + `GOV-STANDING-BACKLOG-001` (baseline registry + routable output) | test: the HYG-001..068 baseline registry loads and enumerates the frozen findings; a generated finding is emitted in a form routable to `work_items` (not markdown-only) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/...` for the report generator + baseline-registry loader; `ruff check` AND `ruff format --check` on changed Python |

(No delta-mode test in this slice — that test is part of the Deferred Follow-On and is not claimed here.)

## Acceptance Criteria

1. `gtkb-hygiene-investigation` SKILL.md exists with the structured findings schema, the 4-round probe
   workflow, and loop-until-dry decay disclosure; the Codex adapter is generated and capability parity is
   green.
2. The chunked report generator renders the v1-style report from a findings list without exceeding a
   single-context size limit.
3. The HYG-001..068 baseline registry exists and loads.
4. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.
5. No delta-mode surface is implemented in this slice (it is the Deferred Follow-On).

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-20-hygiene-investigation-skill-003.md` with a matching `REVISED` entry at the top of
`bridge/INDEX.md`; append-only (the `-001` NEW and `-002` NO-GO remain). `GOV-FILE-BRIDGE-AUTHORITY-001` is
honored; nothing implements until Loyal Opposition records `GO`.

## Risk and Rollback

- **Risk — the skill re-derives census the deferred delta mode should later cheapen:** acceptable for this
  slice — the full-run probe workflow is the proven method; the evidence-pack fast path is an optional hook
  the follow-on wires once FAB-19 lands. **Rollback:** the skill is additive (new files only); remove the
  skill dir + adapter + registry entry.
- **Risk — the baseline registry drifts from the report:** it is seeded once from the frozen HYG-001..068
  findings and versioned. **Rollback:** revert the config file.
- **Risk — premature delta-mode coupling re-enters:** explicitly excluded; acceptance criterion 5 asserts no
  delta surface ships in this slice. **Rollback:** n/a (not built).

## Recommended Implementation Routing

**Hybrid.** The SKILL.md probe prompts encode the investigation method and are best authored by Opus/Codex;
the deterministic helpers (chunked report generator, baseline-registry loader) are **cheap-model-draftable**
and Opus-finalized. Independent of FAB-19 for this slice; the deferred delta mode follows FAB-19.

## Recommended Commit Type

`feat:` — net-new `gtkb-hygiene-investigation` skill, chunked report generator, and HYG-001..068 baseline
registry (new repeatable-investigation capability), with the delta-mode capability deferred to a follow-on.
