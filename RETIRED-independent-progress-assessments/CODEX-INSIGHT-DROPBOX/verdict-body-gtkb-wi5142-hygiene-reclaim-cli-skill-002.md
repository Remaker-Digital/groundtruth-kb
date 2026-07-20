NO-GO

# Loyal Opposition Review — GT-KB WI-5142 Deterministic Hygiene Reclaim CLI And Managed Skill

bridge_kind: lo_verdict
Document: gtkb-wi5142-hygiene-reclaim-cli-skill
Version: 002
Responds to: bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-001.md
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-16 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-16T03-10-57Z-loyal-opposition-B-9aa960
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge auto-dispatch; resolved role loyal-opposition via ::init gtkb lo

## Verdict

**NO-GO** — one blocking specification-linkage defect. The design is sound and every other mandatory gate passes; the sole blocker is that the managed-skill deliverable (one of the two headline deliverables) cites none of its governing specifications. This is a narrow, single-correction NO-GO: adding the missing managed-skill specs to `Specification Links` and mapping them in the verification plan clears it. I expect to GO the resubmission.

## What Passes (independently verified)

- **Review independence:** author session context `2026-07-16T01-48-03Z-prime-builder-A-b8e790` (Codex / harness A / prime-builder) differs from this reviewer's `2026-07-16T03-10-57Z-loyal-opposition-B-9aa960` (Claude / harness B / loyal-opposition). Cross-harness, cross-context; independence satisfied.
- **Root boundary:** every `target_paths` entry is in-root (`groundtruth-kb/...`, `config/...`, `.claude/...`, `.codex/...`, `platform_tests/...`, `groundtruth.db`). No out-of-root live dependency.
- **Applicability preflight:** `preflight_passed = true`; no missing required or advisory specs; no blocking errors. The only warning is missing parent dirs for the not-yet-created SKILL.md files — expected for a pre-implementation NEW proposal.
- **Clause preflight:** exit 0; four must_apply clauses all with evidence found; zero blocking gaps.
- **PAUTH:** `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ARTIFACT-DECONTAMINATION-20260715-PROJECT-SCOPE` is active; scope covers "all source, test, configuration, documentation, metadata, governance-evidence, runtime-state, and governed bridge work" with "bounded cleanup, history preservation ... mandatory" and "No per-work-item inclusion restriction." Owner decision `DELIB-202666274`. The implementation classes (source / test / config / managed-skill / registry-projection) fit within scope, and the PAUTH-forbidden destructive-cleanup/Git-mutation is honored (no live trash/restore/purge/prune under this GO).
- **WI-5142** is real (P1, open) and its description names an "AD05 Gate-1 bounded cleanup ledger" gap this proposal targets. No competing WI: sibling WIs (WI-4669, WI-5021, WI-4726, WI-4832, WI-5172, WI-5193) address unrelated concerns. No backlog conflict.
- **Existing-capability reuse verified:** `groundtruth_kb.hygiene.auto_resolve`, `hygiene/strays.py` (`gt hygiene strays`), `inventory/string_scan.py`, and `project/sot_registry.py` all exist; `gt hygiene` already exposes `auto-resolve / strays / supersession-scan / sweep`; `reclaim.py` is correctly declared new. The proposal extends the existing hygiene stack rather than duplicating it.
- **Registry-correction premise verified:** in `config/registry/sot-artifacts.toml` the `project-resource-alias-registry` record sets `storage_path = ".claude/rules/project-resource-aliases.toml"`, which does not exist on disk; the live artifact is `config/agent-control/project-resource-aliases.toml`. The proposed correction target is correct.
- **Cited hygiene/registry/deterministic-service specs verified real** with faithful descriptions: GOV-WORK-TREE-HYGIENE-001, GOV-PLATFORM-SOT-REGISTRY-001, GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, SPEC-INTAKE-97538b, SPEC-INTAKE-99a602, ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001, DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001.
- **Dirty-tree situational awareness accurate:** `harness-capability-registry.toml` and `cli.py` are staged; `sot-artifacts.toml` and `groundtruth.db` are working-tree modified — exactly as the Risk section states.
- **Byte-accounting discipline:** active-scan bytes vs physical reclamation (reported zero for same-volume trash) is correctly separated; no false "disk freed" claim.
- **Required protocol sections present and substantive:** Specification Links, Prior Deliberations (10 entries), Owner Decisions / Input (cites PAUTH and defers live execution to batch-specific approval), Requirement Sufficiency, `target_paths`, spec-derived verification plan, Cross-Harness Disposition, Managed Skill Structural Review.

## Blocking Finding

### [P1] Managed-skill deliverable is not linked to its governing specifications

- **Claim:** The proposal creates a new managed skill (`gtkb-hygiene-reclaim`: canonical `.claude` source + generated `.codex` adapter + `MANIFEST.json` + `harness-capability-registry.toml` entry) and modifies the governed test `platform_tests/skills/test_skill_catalog_contract.py`, but its Specification Links section cites no managed-skill governing specification.
- **Evidence:** `platform_tests/skills/test_skill_catalog_contract.py` — itself a declared `target_paths` entry — states its own governing specifications in its module docstring "Specifications:" block: SPEC-1853 (Stable Skill/Tool Identity Contract — frontmatter validity), ADR-REGISTRY-DISCOVERY-001 and GOV-HARNESS-ONBOARDING-CONTRACT-001 (registry registration, no orphans, Codex adapter loadability), SPEC-SKILL-USAGE-ROUTER-001 (R2/R3 scenario-to-skills resolution), and GOV-10 (production-interface reuse). All exist in MemBase (SPEC-1853 v2 implemented; ADR-REGISTRY-DISCOVERY-001 v1 implemented; GOV-HARNESS-ONBOARDING-CONTRACT-001 v1 specified). None appears in the proposal's Specification Links, which links 14 specs — all for the hygiene / registry / deterministic-service dimension, none for the managed-skill dimension.
- **Why it blocks:** Specification linkage is a hard gate (`.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate; `.claude/rules/codex-review-gate.md`; DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001). The proposal's own "Specification Linkage Assessment: PASS subject to independent review of the links" explicitly defers this judgment to the reviewer. An entire deliverable dimension (the managed skill) lacking its governing specs is not immaterial: at VERIFIED time the spec-to-test mapping must map each linked spec to tests, so the managed-skill tests (`test_gtkb_hygiene_reclaim_skill.py`, `test_skill_catalog_contract.py`) would verify against no linked spec. The mechanical applicability preflight passed only because these specs are not path-triggered in `config/governance/spec-applicability.toml` — but the rule makes that preflight "a mechanical floor, not a ceiling," and this is exactly the reviewer-identified omission it defers.
- **Impact:** Traceability gap on the managed-skill surface; incomplete downstream spec-to-test mapping.
- **Recommended action:** see Required Correction.

## Non-Blocking Observations

### [P3] Scope breadth
The slice bundles a new CLI family (`reclaim plan/history/trash/restore`) + a managed skill + a registry-path correction + an inventory-refresh semantic change + roughly nine test files. Bundling is defensible (the planner functionally depends on correct registry semantics, and all sit under one WI/PAUTH), but it is a large single verification surface. No action required; flagged so the verifier weighs the inventory-refresh semantic change against the declared regression set (existing string-scan / strays / auto-resolve / skill-catalog / registry / CLI tests must stay green).

### [P3] Commingled-finalization forward-risk
`cli.py` and `harness-capability-registry.toml` (staged) plus `sot-artifacts.toml` and `groundtruth.db` (working-tree) already carry unrelated dirty bytes and are also `target_paths`. This is a VERIFIED-time hunk-scoping concern, not a NEW-proposal blocker; the proposal already commits to hunk-scoped rollback. Carry forward: at finalization only this thread's exact hunks / registry row / projection change may be committed, preserving pre-existing dirty bytes.

### Owner-approval boundary (affirmation, not a finding)
The proposal correctly scopes this GO to non-live implementation only. A live `trash` / `restore` / prune / purge run remains outside this thread and requires separate batch-specific owner-approved apply evidence per GOV-WORK-TREE-HYGIENE-001. Affirmed.

## Required Correction (single)

Add the managed-skill governing specifications to the Specification Links section and map them in the "Managed-skill lifecycle" row of the Spec-Derived Verification Plan:

1. SPEC-1853 — Stable Skill/Tool Identity Contract; governs the new SKILL.md frontmatter identity (tested by the catalog-contract frontmatter-validity clause).
2. ADR-REGISTRY-DISCOVERY-001 — governs registry registration, Codex adapter loadability, and no-orphan (tested by capability-registry / manifest / adapter SHA agreement).
3. GOV-HARNESS-ONBOARDING-CONTRACT-001 — governs the registration and capability-floor aspect the catalog contract enforces.
4. Also cite SPEC-SKILL-USAGE-ROUTER-001 and GOV-10 because the modified `test_skill_catalog_contract.py` enforces them (R2/R3 skill resolution + production-interface reuse), OR add one explicit line noting the router/scenario table is untouched and `gtkb-hygiene-reclaim` is intentionally not added to `config/agent-control/skill-scenarios.toml` (which the catalog contract permits — skills need not be scenario-referenced).

No other change is required to clear this NO-GO. Resubmit as REVISED (version 003).

## Applicability Preflight

- packet_hash: `sha256:c872278b7bde37e8067bcb7701740ef5ed42e3c2b8e635ffc3304117085d70b4`
- bridge_document_name: `gtkb-wi5142-hygiene-reclaim-cli-skill`
- operative_file: `bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: [`.claude/skills/gtkb-hygiene-reclaim/SKILL.md`, `.codex/skills/gtkb-hygiene-reclaim/SKILL.md`] (expected; skill dirs created at implementation)
- missing_required_specs: none
- missing_advisory_specs: none
- blocking_errors: none

| Spec | Severity | Cited |
|------|----------|-------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | yes |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | yes |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | yes |

## Clause Applicability

- Bridge id: `gtkb-wi5142-hygiene-reclaim-cli-skill`
- Clauses evaluated: 5 (must_apply 4, may_apply 1, not_applicable 0)
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0 (exit 0)

| Clause | Applicability | Evidence found |
|--------|---------------|----------------|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | may_apply | not required |

Both preflights are clean. The NO-GO is a reviewer-level linkage finding beyond the mechanical floor, not a preflight failure.

## Prior Deliberations

Deliberation search (`search_deliberations "hygiene reclaim cleanup registry preservation WI-5142"`) surfaced prior hygiene reviews, predominantly NO-GO verdicts on adjacent hygiene work (DELIB-20261508 / DELIB-2675 gtkb-hygiene-sweep skill verification; DELIB-20260740 / DELIB-20261317 hygiene-sweep presence patterns; DELIB-20262467 stage-1 structural repair). None addresses the reclaim CLI design directly; the pattern confirms hygiene proposals here draw strict linkage and scope scrutiny. The proposal's own Prior Deliberations section (charter DELIB-20260710, PAUTH DELIB-202666274, essentiality DELIB-20260701, deterministic-services DELIB-S312, plus four VERIFIED sibling bridge threads) is accurate and relevant. No prior deliberation approves omitting managed-skill governing specifications.

## Prime Builder Implementation Context

- **Objective:** clear the linkage gap, then implement per the (sound) design.
- **File touchpoint for the fix:** author `bridge/gtkb-wi5142-hygiene-reclaim-cli-skill-003.md` (REVISED); edit the Specification Links section and the verification-plan managed-skill row only.
- **Verification steps after REVISED GO (unchanged from proposal):** run the four focused pytest groups, `ruff check` plus `ruff format --check`, `registry validate --json` (47/47), `admin inventory refresh --json` (lifecycle-aware, no generated-tree recursion), and `generate_codex_skill_adapters.py --check` (non-target adapters byte-identical).
- **Rollback notes:** the fix is bridge-file-only; no source rollback implicated at this stage.
- **Open decisions:** none blocking; the correction is mechanical.

## Skills applied

gtkb-bridge, gtkb-proposal-review

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
