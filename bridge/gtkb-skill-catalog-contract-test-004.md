REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5fccf09e-d990-4c4a-b8be-da26cc6e4aa2
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (harness B); S470 WI-4813 REVISED open-items-only

bridge_kind: prime_proposal
Document: gtkb-skill-catalog-contract-test
Version: 004
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds to: bridge/gtkb-skill-catalog-contract-test-003.md (NO-GO)
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

# Implementation Proposal (REVISED) - WI-4813: Skill Catalog-Contract Regression Test + open-items Reconciliation

## Revision Note (responds to -003 NO-GO)

The -003 NO-GO correctly superseded the -002 GO. It found that the -001 reconciliation
narrative misdiagnosed `gtkb-bridge` as a dead scenarios reference. That finding is
**accepted and independently re-verified against canonical state**:

- `config/agent-control/harness-capability-registry.toml` registers `skill.bridge` with
  `canonical_name = "gtkb-bridge"`.
- `.claude/skills/bridge/SKILL.md` frontmatter declares `name: gtkb-bridge`.
- `scripts/check_harness_parity.py` `_registry_skill_dirs()` adds **both** the directory
  name (`bridge`) **and** the `canonical_name` (`gtkb-bridge`) to the resolution set.
- `gt skills suggest --scenario lo_bridge_review --json` returns
  `required: ["gtkb-bridge", "proposal-review"]` and exits 0 - `gtkb-bridge` resolves.

`gtkb-bridge` is therefore a **valid registered skill name** (the canonical identity of
`skill.bridge`), not a dead reference. Deliverable 1 assertion 4 - which imports the
production `_registry_skill_dirs()` - already passes `gtkb-bridge` correctly; the -001
error was confined to the manual reconciliation grep, the unnecessary `gtkb-bridge ->
bridge` edit, and the RED/GREEN narrative. Changing `gtkb-bridge -> bridge` would have
**regressed** the stable canonical identity (`SPEC-1853`), so it is dropped.

This REVISED keeps Deliverable 1 unchanged and scopes Deliverable 2 to the one genuine
dead reference: `open-items`. `target_paths` is unchanged (the scenarios-table edit
shrinks but still touches the same file). The owner's `DELIB-20266102` bundle decision is
preserved - bundle the real fix needed for the test to land green; the corrected count is
one fix, a strict subset of the authorized scope.

## Summary

Final tracked deliverable of `PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT`. Converts
doctor-reported skill-catalog coverage into a tested regression contract, and reconciles
the one live dead reference the contract surfaces. Two bounded deliverables:

- **Deliverable 1 - net-new test (WI-4813), unchanged from -001:** add
  `platform_tests/skills/test_skill_catalog_contract.py`, asserting catalog invariants by
  **importing the production parity logic** from `scripts/check_harness_parity.py` (no
  parallel reimplementation). Folds the residual of retired WI-4811: every skill name in
  `config/agent-control/skill-scenarios.toml` must resolve via the production
  `_registry_skill_dirs()` set (which includes directory names AND canonical_names).
- **Deliverable 2 - open-items reconciliation (scope-corrected):** remove the single dead
  reference `open-items` from `[scenarios.release_readiness].recommended` so the test
  lands green.

## Requirement Sufficiency

**Existing requirements sufficient.** No new or revised formal requirement is needed
before implementation. The catalog invariants are already required by the linked specs
and already encoded in the doctor checks `_check_codex_skill_load_health` and
`scripts/check_harness_parity.py`; this slice converts that coverage into a tested
contract. The scenarios-resolution invariant and the `open-items` correction derive from
`SPEC-SKILL-USAGE-ROUTER-001` R2/R3. No formal artifact is mutated.

## Specification Links

- `SPEC-SKILL-USAGE-ROUTER-001` (R2/R3: scenario->skills table must reference resolvable
  skills; the folded assertion guards this and Deliverable 2 corrects the one violation).
- `SPEC-1853` (Stable Skill/Tool Identity Contract; the frontmatter-validity invariant AND
  the canonical-identity reason the `gtkb-bridge` edit is correctly dropped).
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` (machine-checkable assertions + capability floor;
  registry-registration and adapter-loadability invariants the test asserts).
- `ADR-REGISTRY-DISCOVERY-001` (registry-based check/command discovery).
- `GOV-10` (test artifacts must exercise exposed production interfaces; the test imports
  and exercises `check_harness_parity.py` functions including `_registry_skill_dirs`).
- `SPEC-1662` / GOV-18 (Assertion Quality Standard - meaningfulness over coverage).
- `GOV-FILE-BRIDGE-AUTHORITY-001` (this proposal follows the numbered bridge lifecycle).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (cites all relevant specs).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (verification plan maps spec-derived
  tests to each deliverable).
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
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory; preserves owner decision, project
  record, work item, and this proposal as durable linked artifacts).

## Owner Decisions / Input

- `DELIB-20266102` (owner_conversation, outcome=owner_decision): the S470 AskUserQuestion
  chain authorizing this slice.
  - AUQ#1: S470 work focus = WI-4813 catalog-contract test (Recommended) - prioritizes
    WI-4813 and approves implementing the test through the bridge protocol.
  - AUQ#2: WI-4813 scope = Bundle the fixes (Recommended) - bundle the scenarios fix(es)
    needed for the test to land green. The corrected diagnosis reduces the bundled fixes
    to one (`open-items`); the `gtkb-bridge` edit is dropped as incorrect. The owner's
    bundle-the-needed-fix intent is preserved (one fix, strict subset of the AUQ scope).
- `DELIB-20265883` (owner_conversation): the umbrella program-scoping AUQ.

The corrected scope shrinks within the existing owner authorization; no fresh owner
decision blocks implementation.

## Prior Deliberations

- `DELIB-20266102` - this slice's owner decision (prioritization + bundled scope).
- `DELIB-20265883` - umbrella program-scoping owner decision (parent of WI-4813).
- `DELIB-20265889` - slice-B owner authorization (sibling slice; per-slice-PAUTH pattern).
- `bridge/gtkb-skill-catalog-contract-test-002.md` (GO, superseded) and `-003.md` (NO-GO)
  - the in-thread correction that scoped Deliverable 2 to `open-items` only.
- `bridge/gtkb-skill-usage-router-slice-001.md` (WI-4810; GO) - created
  `config/agent-control/skill-scenarios.toml` and `SPEC-SKILL-USAGE-ROUTER-001`.
- `bridge/gtkb-skill-activation-bridge-shape-hardening-slice-b-001.md` (WI-4809/WI-4573)
  - sibling slice; established the catalog/parity tooling surface this test exercises.

## Deliverable 1 - Catalog-contract regression test (WI-4813, unchanged)

Add `platform_tests/skills/test_skill_catalog_contract.py`. The test imports the
production parity logic from `scripts/check_harness_parity.py` (per GOV-10) and asserts:

1. **Frontmatter validity.** For every entry in `inventory_project_skills(project_root)`,
   `_skill_frontmatter_error(text, path)` returns `None`.
2. **Registry registration / no orphans.** Every SKILL.md-bearing skill dir resolves
   inside `_registry_skill_dirs(capabilities)` (which contains both directory names and
   canonical_names), and every registered skill id has a backing
   `.claude/skills/<name>/SKILL.md`. Reference-stub dirs without SKILL.md (`deploy`,
   `run-tests`, `seed-tenant`) are excluded by the `*/SKILL.md` definition.
3. **Codex adapter loadability.** For each registered skill's `.codex` surface, the parity
   capability evaluation yields a PASS state (no MISSING/STALE adapter).
4. **Folded WI-4811 scenarios resolution.** Every skill name in every `required` and
   `recommended` list across `config/agent-control/skill-scenarios.toml` is a member of
   `_registry_skill_dirs(capabilities)`. Because that set includes canonical_names,
   `gtkb-bridge` (canonical_name of `skill.bridge`) resolves correctly; the only pre-fix
   failure is `open-items`.

Reusing the canonical parity functions ensures the test's notion of "resolves" cannot
drift from the production resolution surface it formalizes.

## Deliverable 2 - open-items reconciliation (scope-corrected)

Correct the single dead reference in `config/agent-control/skill-scenarios.toml` that
Deliverable 1 assertion 4 surfaces:

- `[scenarios.release_readiness]` `recommended`: remove `open-items` (a slash command at
  `.claude/commands/open-items.md`, not a registered skill), leaving the recommended list
  empty for that scenario.

No other scenario lists are touched. `gtkb-bridge` is left unchanged in `lo_bridge_review`
and `lo_verify_report` (it is the registered canonical identity of `skill.bridge`).

## Spec-Derived Verification Plan

| Spec / requirement | Deliverable | Test (spec-derived) |
|---|---|---|
| `SPEC-1853`, `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `ADR-REGISTRY-DISCOVERY-001` | D1 (assertions 1-3) | `test_skill_catalog_contract.py`: every skill has valid frontmatter; SKILL.md skill dirs resolve in `_registry_skill_dirs` (no orphans/extras); every registered skill has a PASS-state Codex adapter; SKILL.md-less stub dirs excluded |
| `SPEC-SKILL-USAGE-ROUTER-001` R2/R3 | D1 (assertion 4) + D2 | `test_skill_catalog_contract.py`: every required/recommended skill name in `skill-scenarios.toml` is a member of `_registry_skill_dirs`; pre-fix the assertion fails only on `open-items`; after D2 it passes (`gtkb-bridge` already passed via canonical_name) |
| `GOV-10` | D1 | the test imports `check_harness_parity.py` production functions (incl. `_registry_skill_dirs`) rather than reimplementing catalog logic |

Execution commands:

```
.venv/Scripts/python -m pytest platform_tests/skills/test_skill_catalog_contract.py -q --tb=short
.venv/Scripts/python -m ruff check platform_tests/skills/test_skill_catalog_contract.py
.venv/Scripts/python -m ruff format --check platform_tests/skills/test_skill_catalog_contract.py
```

The pytest run is expected RED before Deliverable 2 (assertion 4 fails only on
`open-items`) and GREEN after Deliverable 2 - demonstrating the test's value and the one
correction's sufficiency.

## Target Path Rationale

- `platform_tests/skills/test_skill_catalog_contract.py` - net-new test (Deliverable 1);
  `platform_tests/skills/` is the established home for skill tests.
- `config/agent-control/skill-scenarios.toml` - the single-reference correction
  (Deliverable 2). Editing this config table is sanctioned by `SPEC-SKILL-USAGE-ROUTER-001`
  R2 ("Retuning the table SHALL NOT require a router source-code change").

Both paths are tracked, in-root, and within the PAUTH's `test_addition` + `source`
mutation classes. The realized scope is a strict subset of the authorized scope.

## Risk / Rollback

- **Risk:** the test couples to private parity helpers (`_skill_frontmatter_error`,
  `_registry_skill_dirs`). Mitigation: that coupling is the intent (GOV-10); if a helper
  is renamed, the test breaks loudly at the catalog contract - the desired regression
  signal.
- **Risk:** removing `open-items` empties `release_readiness.recommended`. Mitigation:
  acceptable - a non-skill reference is removed; the router is report-only (no hard gate).
- **Rollback:** reverting the two files fully removes the slice. The test is additive; the
  scenarios correction is a one-line config revert.

## Requested Loyal Opposition Review

Please confirm (1) the corrected diagnosis (`gtkb-bridge` resolves via canonical_name;
only `open-items` is dead) is reflected throughout; (2) Deliverable 1 is unchanged and its
assertion 4 correctly uses `_registry_skill_dirs`; (3) Deliverable 2 is scoped to
`open-items` removal only; and (4) the spec-derived test plan covers each deliverable. A
`GO` authorizes implementation within the two declared `target_paths`.
