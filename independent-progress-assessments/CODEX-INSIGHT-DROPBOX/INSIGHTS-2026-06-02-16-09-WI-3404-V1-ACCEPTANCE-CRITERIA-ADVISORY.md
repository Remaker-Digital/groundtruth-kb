# Loyal Opposition Advisory: WI-3404 v1.0 Acceptance Criteria Gate

**Specs:** DELIB-2234, memory/v1-release-strategy-deliberation-S347.md
**WIs:** WI-3404, WI-3401, WI-3402, WI-3403
**Date:** 2026-06-02
**Evaluator:** Codex Loyal Opposition, harness A
**Status:** Advisory report. No bridge verdict and no formal artifact mutation.

---

## Executive Summary

`WI-3404` should be treated as the controlling v1.0 release-readiness gate, not as a prose checklist task. `WI-3401` mechanical enforcement, `WI-3402` spec-corpus distillation, and `WI-3403` Docker isolation validation are important evidence-producing work items, but they do not substitute for the acceptance criteria. They should either proceed in parallel or after `WI-3404`, but their proposals should be checked against the `WI-3404` gate once it exists.

The core Loyal Opposition recommendation is to file a Prime Builder bridge proposal for a versioned v1.0 acceptance-criteria artifact plus a later deterministic readiness check. Until that artifact exists, the owner-approved "quality-driven ship" posture in `DELIB-2234` has no mechanical checkpoint against perpetual rc1 drift.

No owner decision is required to receive this advisory. Future implementation will likely require owner decisions on ambiguous tier placement, waiver authority, and final artifact location.

## Dependency And Precedence Check

`gt backlog show WI-3404` reports `WI-3404` as P0, open, backlogged, and without an acceptance summary. `WI-3401`, `WI-3402`, and `WI-3403` are P1, open, backlogged, and also without acceptance summaries. `DELIB-2234` elevates v1.0 acceptance criteria to a gating item and also authorizes the enforcement gate, spec distillation, and Docker isolation validator.

Recommended ordering:

1. Define the initial `WI-3404` gate artifact now.
2. Let `WI-3401`, `WI-3402`, and `WI-3403` continue as parallel implementation-scope proposals only after they are explicitly mapped to evidence rows in the gate.
3. Do not declare any v1.0 release-readiness state from a single evidence source, including Agent Red, until the full gate can be evaluated.

## Finding 1 (P1): The P0 Checkpoint Has No Durable Gate Surface

### Observation

The owner decision says that v1.0 acceptance criteria are the sole checkpoint against perpetual rc1 risk and are "gating, not advisory" (`.groundtruth/formal-artifact-approvals/2026-05-27-DELIB-2234.json` lines 7-10). The predecessor deliberation states that Hybrid's failure mode is never shipping because some module is never done, and it recommends defining v1.0 acceptance criteria explicitly and early (`memory/v1-release-strategy-deliberation-S347.md` lines 391-402 and 650-652). The live backlog item `WI-3404` has no acceptance summary.

### Deficiency Rationale

A P0 item with no concrete artifact, evidence schema, or terminal evaluation rule cannot perform the role assigned by `DELIB-2234`. If acceptance criteria remain a narrative task, future sessions can keep adding prerequisite work without a shared release boundary.

### Proposed Solution/Enhancement

File a bridge proposal for a versioned v1.0 acceptance-criteria artifact. The proposal should define:

- Criterion ID.
- Stability tier: stable core, scaffold-fork, or experimental.
- Source decision or spec citation.
- Required evidence command, report, or bridge thread.
- Linked work item.
- Terminal pass/fail rule.
- Waiver authority and waiver expiry, if any.

After the artifact is reviewed, implement a deterministic `gt v1 readiness` or equivalent config-driven check. The check should consume the artifact and report pass/fail/waived/blocked states without requiring a fresh manual audit each session.

### Option Rationale

A versioned criteria artifact is lower risk than trying to encode the gate directly into dashboard prose or session-start summaries. The deterministic check should come after the artifact is stable so it automates a known contract instead of freezing premature assumptions.

## Finding 2 (P1): The Three-Tier Model Needs A Surface Inventory

### Observation

`DELIB-2234` adopts a three-tier model: stable core, scaffold-fork, and experimental. The predecessor deliberation names example surfaces: schemas, bridge format, hook payload contracts, `gt` CLI, Python API, templates, rules, skills, named hooks, dashboard interactive features, and single-harness operating mode (`memory/v1-release-strategy-deliberation-S347.md` lines 450-464).

### Deficiency Rationale

The tier model is correct, but examples are not enough for release gating. Without an explicit surface inventory, teams can accidentally smuggle a compatibility promise into an experimental surface or mark a stable-core dependency as scaffold-fork after it breaks an adopter.

### Proposed Solution/Enhancement

The `WI-3404` artifact should include a surface inventory table. At minimum, each row should record:

- Surface name.
- Tier.
- Compatibility promise.
- Owner or source-of-truth artifact.
- Required tests or assertions.
- Promotion path between tiers.

The first pass should classify the known stable-core examples from the deliberation, the scaffold-fork assets inherited at `gt project init`, and the explicitly experimental surfaces. Unknown or disputed surfaces should default to "blocked: tier decision required" instead of silently entering stable core.

### Option Rationale

Inventory-first gating preserves the Hybrid Variant strategy: existing identifiers and platform internals can survive, while the release layer becomes clean and explicit. It also avoids a broad refactor before the team knows which surfaces need compatibility promises.

## Finding 3 (P1): Agent Red Evidence Must Be Canonical And Clean-Install Based

### Observation

`DELIB-2234` makes Agent Red green-on-clean a v1.0 release-gate dependency. The predecessor deliberation says Agent Red's isolation-validator role is only meaningful if there is a concrete test: install GT-KB version V on a fresh environment E, install Agent Red on top, and verify Agent Red operates (`memory/v1-release-strategy-deliberation-S347.md` lines 423-432 and 491-500). Current release-readiness notes for the separate `v0.7.0-rc1` path warn that PR-head evidence is not tag-authorization evidence and that `v0.7.0-rc1` remains unauthorized pending canonical migration, canonical CI, Docker Scout disposition, and bridge verification (`memory/release-readiness.md` lines 75-121).

### Deficiency Rationale

The v1.0 gate can inherit the current rc1 evidence weakness if it does not define evidence semantics up front. A passing pull-request head, a local checkout, or a same-repo validation run is not the same as proving that an adopter can consume a released GT-KB package in a clean environment.

### Proposed Solution/Enhancement

The `WI-3404` gate should require canonical Agent Red evidence with these minimum properties:

- Accepted canonical Agent Red head, release branch, or tag.
- Fresh environment with no dependency on the GT-KB working tree.
- GT-KB installed from the candidate package or release artifact.
- Agent Red installed or upgraded through the intended adopter path.
- Required application workflows green, including security-scan handling or an explicitly governed full-scan disposition.
- Bridge post-implementation report verified where governance requires it.

The gate should also record the ongoing reference-adopter cadence: Agent Red stays one platform release behind, upgrades periodically, and revalidates after platform schema or contract changes.

### Option Rationale

This keeps Agent Red as the release validator without over-trusting informal evidence. It also aligns the v1.0 gate with the stricter evidence boundary already being used for the current rc1 release-readiness file.

## Finding 4 (P2): Loyal Opposition Authority During The Transition Needs To Be Bound Into The Gate

### Observation

The predecessor deliberation explicitly asks whether Loyal Opposition uses the spec corpus as review authority, what happens if the spec is wrong, and whether LO can NO-GO an implementation that satisfies the spec but does so badly (`memory/v1-release-strategy-deliberation-S347.md` lines 478-489). `DELIB-2234` adopts a promotion model for spec changes and makes the acceptance criteria a gate.

### Deficiency Rationale

The current operating contract already lets Loyal Opposition question cited requirements, but the v1.0 transition will stress that rule. A spec-corpus transition can produce two distinct defects: implementation drift from spec, and bad or incomplete specs. If the acceptance gate does not name how those are handled, bridge verdicts can become inconsistent.

### Proposed Solution/Enhancement

Add a review-authority clause to the `WI-3404` artifact:

- LO may NO-GO an implementation that fails the accepted criteria.
- LO may NO-GO or request requirement disambiguation when criteria are internally inconsistent, untestable, or contradicted by owner decisions.
- Spec-corpus defects must be routed through the promotion model rather than waived informally.
- Any owner waiver must identify the affected criterion and expiry condition.

### Option Rationale

This is a small addition to the acceptance artifact and avoids a later bridge-protocol ambiguity. It does not require changing the operating role contract before the gate can be drafted.

## Implementation Context For Prime Builder

Suggested touchpoints:

- `bridge/gtkb-v1-acceptance-criteria-001.md` or equivalent bridge proposal.
- A future acceptance-criteria artifact under the eventual v1.0 release/spec surface chosen by Prime Builder and approved through the bridge.
- MemBase work items `WI-3404`, `WI-3401`, `WI-3402`, and `WI-3403` for linkage and acceptance-summary updates after approval.
- A later deterministic readiness command or script once the criteria are stable.

Suggested sequence:

1. File a bridge proposal that defines the artifact shape and initial criteria rows.
2. Map `WI-3401`, `WI-3402`, and `WI-3403` to explicit evidence rows.
3. Review the proposal through Loyal Opposition before using it as a release gate.
4. Update backlog acceptance summaries only after the bridge outcome authorizes the concrete artifact.
5. Implement deterministic readiness checking after the artifact is stable enough to automate.

Verification expectations:

- `gt backlog show WI-3404` should show a meaningful acceptance summary after the approved update.
- The criteria artifact should make every pass/fail/waived/blocked state auditable.
- The eventual readiness check should fail closed when a stable-core surface lacks required evidence.
- Standard repository checks should still pass for any implementation slice: targeted pytest, ruff check, and ruff format check where applicable.

Rollback or containment:

- If the proposed artifact shape is wrong, supersede it through a revised bridge proposal before implementing the readiness command.
- If tier placement is disputed, mark the affected row blocked rather than weakening the entire gate.
- If Agent Red evidence is temporarily unavailable, block v1.0 readiness instead of treating local or PR-head evidence as equivalent.

## Open Decisions

No owner decision is required for this advisory report. Future implementation proposals should surface exactly one owner decision at a time if they require tier placement judgment, waiver authority, or artifact-location approval.
