NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5fccf09e-d990-4c4a-b8be-da26cc6e4aa2
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (harness B); S470 WI-4813 catalog-contract test

bridge_kind: prime_proposal
Document: gtkb-skill-catalog-contract-test
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Project Authorization: PAUTH-PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT-SKILL-ACTIVATION-WI-4813-CATALOG-CONTRACT-TEST-BOUNDED-IMPLEMENTATION-2026-06-25
Work Item: WI-4813
Owner Decision: DELIB-20266102
Umbrella: bridge/gtkb-skill-activation-enforcement-umbrella-002 (GO; DELIB-20265883)
target_paths: ["platform_tests/skills/test_skill_catalog_contract.py", "config/agent-control/skill-scenarios.toml"]
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
owner_input_required: false

---

# Implementation Proposal - WI-4813: Skill Catalog-Contract Regression Test + Scenarios Reconciliation

## Summary

Final tracked deliverable of `PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT`. Converts
doctor-reported skill-catalog coverage into a tested regression contract, and
reconciles two live dead references the contract surfaces. Two bounded deliverables:

- **Deliverable 1 - net-new test (WI-4813):** add
  `platform_tests/skills/test_skill_catalog_contract.py`, a consolidated regression
  test asserting catalog invariants by **importing the production parity logic** from
  `scripts/check_harness_parity.py` (no parallel reimplementation). It also folds the
  sole residual value of retired WI-4811: every skill name referenced in
  `config/agent-control/skill-scenarios.toml` must resolve to a registered skill.
- **Deliverable 2 - scenarios reconciliation (bundled per owner AUQ):** correct the two
  dead references in `config/agent-control/skill-scenarios.toml` that Deliverable 1's
  scenarios-resolution assertion surfaces, so the test lands green with no exception
  escape-hatch.

The test is additive (no production source mutation beyond the scenarios-table
correction); Deliverable 2 is a ~3-line config correction of WI-4810's router table.

## Reconciliation With Canonical State (why scope is test + two fixes)

Pre-implementation verification against live source (S470, harness B):

- **Catalog invariants 1-4 are green on the current tree.** `.claude/skills/*/SKILL.md`
  count is 37, exactly matching the 37 `kind = "skill"` entries in
  `config/agent-control/harness-capability-registry.toml`; every SKILL.md-bearing dir is
  registered and no registered id lacks a dir. The earlier "40 dirs vs 37 registered"
  observation was a false alarm: `deploy`, `run-tests`, and `seed-tenant` are
  reference-stub dirs containing only a `references/` subdir and **no SKILL.md**, so the
  parity definition (`inventory_project_skills` globs `*/SKILL.md`) correctly excludes
  them. The test inherits that exclusion by construction.
- **The folded scenarios-resolution check finds two live dead references.**
  `config/agent-control/skill-scenarios.toml` references `gtkb-bridge` (required in
  `lo_bridge_review` and `lo_verify_report`) - there is no `skill.gtkb-bridge`; the
  registered bridge-protocol skill is `bridge` (id `skill.bridge`). It also references
  `open-items` (recommended in `release_readiness`) - `open-items` is a slash command
  (`.claude/commands/open-items.md`), not a registered skill. Both are exactly the
  dead-advisory-suggestion class the WI-4811 residual check targets, and both violate
  `SPEC-SKILL-USAGE-ROUTER-001` R2/R3 (the scenario->skills table must reference
  resolvable skills). Right now `gt skills suggest` for an LO bridge review would emit a
  non-resolving skill name.

Because a strict test cannot land green while those two references are dead, the owner
(AUQ, S470, `DELIB-20266102`) directed bundling the two corrections into this slice
rather than splitting them into a separate WI or excusing them with a tracked baseline.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised formal requirement is needed
before implementation. The catalog invariants are already required by the linked specs
(skill identity contract, registry-based discovery, harness-onboarding machine-checkable
assertions) and already encoded in the doctor checks `_check_codex_skill_load_health` and
`scripts/check_harness_parity.py`; this slice converts that coverage into a tested
contract. The scenarios-resolution invariant and the two corrections derive from
`SPEC-SKILL-USAGE-ROUTER-001` R2/R3. No formal artifact is mutated.

## Specification Links

- `SPEC-SKILL-USAGE-ROUTER-001` (R2/R3: scenario->skills table sourced from
  `config/agent-control/skill-scenarios.toml` must reference resolvable skills; the
  folded WI-4811 assertion guards this and Deliverable 2 corrects two violations).
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` (machine-checkable assertions + capability floor;
  the registry-registration and adapter-loadability invariants the test asserts mirror
  its Layer-2 assertions for the skill catalog surface).
- `ADR-REGISTRY-DISCOVERY-001` (registry-based check/command discovery; every skill must
  be discoverable via the registry).
- `SPEC-1853` (Stable Skill/Tool Identity Contract; the frontmatter-validity invariant).
- `GOV-10` (test artifacts must exercise exposed production interfaces; the test imports
  and exercises `check_harness_parity.py` functions rather than reimplementing them).
- `SPEC-1662` / GOV-18 (Assertion Quality Standard - meaningfulness over coverage; the
  test asserts a meaningful catalog contract, not shallow structure).
- `GOV-FILE-BRIDGE-AUTHORITY-001` (this proposal follows the numbered bridge lifecycle).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (this proposal cites all
  relevant governing specs).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (the verification plan below maps
  spec-derived tests to each deliverable).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (slice authorized by the bounded PAUTH
  cited in the header; spec included in that PAUTH).
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` (project carries linked specs).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (Project / Work Item / Project
  Authorization triple present in the header).
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` (review-time mechanical
  enforcement; the test is a regression contract over catalog invariants).
- `.claude/rules/project-root-boundary.md` (both target paths are tracked, in-root).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (a tested catalog contract moves a
  recurring manual catalog-consistency check off the session).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory; this slice preserves the owner
  decision, project record, work item, and this proposal as durable linked artifacts and
  triggers no untracked-artifact lifecycle transition).

## Owner Decisions / Input

- `DELIB-20266102` (owner_conversation, outcome=owner_decision): the S470 AskUserQuestion
  chain authorizing this slice.
  - AUQ#1: S470 work focus = WI-4813 catalog-contract test (Recommended) - prioritizes
    WI-4813 and approves implementing the test through the bridge protocol.
  - AUQ#2: WI-4813 scope = Bundle the two fixes (Recommended) - the proposal adds the
    test AND reconciles the two `skill-scenarios.toml` dead references so the test lands
    green; no tracked-baseline exception.
- `DELIB-20265883` (owner_conversation): the umbrella program-scoping AUQ (full
  enforcement program; advisory-first posture) under which WI-4813 was scoped.

No further owner decision blocks implementation.

## Prior Deliberations

- `DELIB-20266102` - this slice's owner decision (prioritization + bundled scope).
- `DELIB-20265883` - umbrella program-scoping owner decision (parent of WI-4813).
- `DELIB-20265889` - slice-B owner authorization (sibling slice; established the
  advisory-first, per-slice-PAUTH pattern this slice follows).
- `bridge/gtkb-skill-usage-router-slice-001.md` (WI-4810; GO) - created
  `config/agent-control/skill-scenarios.toml` and `SPEC-SKILL-USAGE-ROUTER-001`; this
  slice guards and corrects that table.
- `bridge/gtkb-skill-activation-bridge-shape-hardening-slice-b-001.md` (WI-4809/WI-4573)
  - sibling slice; established the catalog/parity tooling surface this test exercises.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md`
  - source advisory (enforcement-model section 3: catalog/registry consistency checks).

## Deliverable 1 - Catalog-contract regression test (WI-4813)

Add `platform_tests/skills/test_skill_catalog_contract.py`. The test imports the
production parity logic from `scripts/check_harness_parity.py` (per GOV-10) and asserts:

1. **Frontmatter validity.** For every entry in `inventory_project_skills(project_root)`,
   `_skill_frontmatter_error(text, path)` returns `None` (valid YAML frontmatter with a
   `name`).
2. **Registry registration / no orphans.** The set of SKILL.md-bearing skill dirs equals
   the set of `kind = "skill"` registry ids (`_registry_skill_dirs(capabilities)`): every
   skill dir is registered, and no registered skill id lacks a `.claude/skills/<name>/SKILL.md`.
   Reference-stub dirs without SKILL.md (e.g. `deploy`, `run-tests`, `seed-tenant`) are
   excluded by the `*/SKILL.md` definition, matching the parity checker.
3. **Codex adapter loadability.** For each registered skill's `.codex` surface, the parity
   capability evaluation yields a PASS state (adapter present, Codex-loadable frontmatter,
   adapter_source present and hash-consistent) - i.e. no MISSING/STALE adapter state.
4. **Folded WI-4811 scenarios resolution.** Every skill name in every `required` and
   `recommended` list across `config/agent-control/skill-scenarios.toml` resolves to a
   registered skill id. This catches typo'd / renamed / non-skill router-table references
   that would otherwise produce dead advisory suggestions.

The test reuses the canonical parity functions so its notion of "registered / extra /
adapter-loadable" cannot drift from the doctor/parity surface it formalizes.

## Deliverable 2 - Scenarios reconciliation (bundled per owner AUQ)

Correct the two dead references in `config/agent-control/skill-scenarios.toml` that
Deliverable 1 assertion 4 surfaces:

- `[scenarios.lo_bridge_review]` `required`: `gtkb-bridge` -> `bridge`.
- `[scenarios.lo_verify_report]` `required`: `gtkb-bridge` -> `bridge`.
- `[scenarios.release_readiness]` `recommended`: remove `open-items` (a slash command,
  not a registered skill), leaving the recommended list empty for that scenario.

`bridge` is the registered umbrella bridge-protocol skill (`skill.bridge`) and matches
each scenario's rationale text ("drive the bridge protocol"). No rationale text changes
are required; the corrections are minimal and confined to the two referenced lists.

## Spec-Derived Verification Plan

| Spec / requirement | Deliverable | Test (spec-derived) |
|---|---|---|
| `SPEC-1853` (frontmatter/identity), `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `ADR-REGISTRY-DISCOVERY-001` | D1 (assertions 1-3) | `test_skill_catalog_contract.py`: every skill has valid frontmatter; SKILL.md skill dirs == registered skill ids (no orphans/extras); every registered skill has a PASS-state Codex adapter; SKILL.md-less stub dirs excluded |
| `SPEC-SKILL-USAGE-ROUTER-001` R2/R3 | D1 (assertion 4) + D2 | `test_skill_catalog_contract.py`: every required/recommended skill name in `skill-scenarios.toml` resolves to a registered skill; after D2, the assertion passes (gtkb-bridge->bridge x2; open-items removed) |
| `GOV-10` | D1 | the test imports `check_harness_parity.py` production functions rather than reimplementing catalog logic |

Execution commands:

```
.venv/Scripts/python -m pytest platform_tests/skills/test_skill_catalog_contract.py -q --tb=short
.venv/Scripts/python -m ruff check platform_tests/skills/test_skill_catalog_contract.py
.venv/Scripts/python -m ruff format --check platform_tests/skills/test_skill_catalog_contract.py
```

The pytest run is expected RED before Deliverable 2 (assertion 4 fails on the two dead
references) and GREEN after both deliverables land - demonstrating the test's value and
the corrections' sufficiency in one verification.

## Target Path Rationale

- `platform_tests/skills/test_skill_catalog_contract.py` - net-new test (Deliverable 1);
  `platform_tests/skills/` is the established home for skill tests.
- `config/agent-control/skill-scenarios.toml` - the two-reference correction (Deliverable
  2). Editing this config table is explicitly sanctioned by `SPEC-SKILL-USAGE-ROUTER-001`
  R2 ("Retuning the table SHALL NOT require a router source-code change").

Both paths are tracked, in-root, and within the PAUTH's `test_addition` + `source`
mutation classes.

## Risk / Rollback

- **Risk:** the test couples to private parity helpers (`_skill_frontmatter_error`,
  `_registry_skill_dirs`). Mitigation: that coupling is the intent (GOV-10 - formalize the
  production surface); if a helper is renamed, the test breaks loudly at the catalog
  contract, which is the desired regression signal.
- **Risk:** Deliverable 2 alters router behavior for the affected scenarios. Mitigation:
  the change replaces non-resolving names with resolving ones (or removes a non-skill),
  strictly improving the advisory; the router is report-only (no hard gate) per
  `SPEC-SKILL-USAGE-ROUTER-001`.
- **Rollback:** reverting the two files fully removes the slice. The test is additive; the
  scenarios correction is a localized config revert.

## Requested Loyal Opposition Review

Please review whether (1) the test's reuse of `check_harness_parity.py` production
functions is the correct GOV-10-aligned approach versus reimplementation; (2) the four
asserted invariants are the right catalog contract (complete and not over-broad); (3) the
two `skill-scenarios.toml` corrections are correct and minimal (`gtkb-bridge`->`bridge`;
`open-items` removal) per `SPEC-SKILL-USAGE-ROUTER-001` R2/R3; and (4) the spec-derived
test plan covers each deliverable. A `GO` authorizes implementation within the two
declared `target_paths`. A `NO-GO` should identify a scope, spec-linkage, or
test-coverage gap.
