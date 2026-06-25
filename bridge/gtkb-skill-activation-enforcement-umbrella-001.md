NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: de8db3b1-a4a6-4be0-9f51-65b8d31e1299
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder session (harness B); explanatory output style; skill-activation umbrella

bridge_kind: governance_advisory
Document: gtkb-skill-activation-enforcement-umbrella
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-24 UTC
Project: PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT
Owner Decision: DELIB-20265883
Source Advisory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md
Source Advisory Routing WI: WI-3330
target_paths: ["bridge/gtkb-skill-activation-enforcement-umbrella-001.md"]
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
owner_input_required: false

---

# Umbrella Proposal - GT-KB Skill Activation and Enforcement Program

## Summary

This is a **scoping umbrella** (`bridge_kind: governance_advisory`, non-implementation) for the new project `PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT`. It establishes the program's scope, slicing plan, first slice, and enforcement posture so the owner can populate it with implementation work items. It implements no code and requests no implementation authorization; each future slice will be filed as its own `prime_proposal` with a Project Authorization (PAUTH) and a project-member work item when the owner prioritizes it.

The program converts the WI-3330 `monitor` disposition of the Loyal Opposition advisory `INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md` ("GT-KB Skill Use, Coverage, and Enforcement Opportunities"). That advisory's core finding: skill **presence** is governed (mirrored catalog, capability registry, adapter parity) but skill **invocation** is still human-memory-driven, so the same failure classes recur (bridge proposal shape, target_paths scope, stale/duplicate threads, verdict structure). The fix is a routing + enforcement layer, not another free-form instruction layer.

Per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`, the three load-bearing decisions were captured via AskUserQuestion and recorded as `DELIB-20265883`:

1. **Scope = Full enforcement program** (router + bridge-shape hardening + `/verify` hardening + registry scenario-metadata + CI/doctor checks + report self-disclosure).
2. **First slice = Bridge-shape hardening (B)** (owner override of the advisory's recommended advisory-only-router-first; B attacks the most expensive recurring failure class directly).
3. **Enforcement posture = Advisory-first** (warnings first; converting any path to a HARD gate is a separate future owner decision per scenario class).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v2 (verified) - this umbrella is filed through the bridge for Loyal Opposition scope review; Prime Builder authors no verdict.
- `DCL-ADVISORY-ROUTING-001` and `.claude/rules/peer-solution-advisory-loop.md` - the source LO advisory is routed; per the owner-grilling gate this `adopt`-class conversion carries AUQ owner-decision evidence.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` and `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` - the structured owner-grilling pass was conducted and recorded (`DELIB-20265883`) before this umbrella was filed.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 and `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - this umbrella authorizes NO implementation; each slice will carry its own PAUTH + linked specifications before code is written.
- `GOV-STANDING-BACKLOG-001` - WIs are to be populated by the owner into the new project; the umbrella creates no work items and mutates no backlog.
- `SPEC-ADVISORY-REPORT-TEMPLATE-001` - the source report is advisory input transformed into governed program scope.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 - future implementation slices must cite concrete spec links and spec-derived tests; this umbrella is not itself an implementation proposal.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the advisory, owner decision, project record, and this umbrella are preserved as durable, linked artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 - all program work stays under `E:\\GT-KB`; the router/enforcement layer is platform tooling, not adopter application source.
- `.claude/rules/file-bridge-protocol.md` - this follows the numbered bridge-file lifecycle.

## Owner Decisions / Input

- `DELIB-20265883` (owner_conversation, outcome=owner_decision): the umbrella-scoping AskUserQuestion grilling pass.
  - **Scope = Full enforcement program** (AUQ answer).
  - **First slice = Bridge-shape hardening (B)** (AUQ answer; owner override of the advisory's A recommendation).
  - **Enforcement posture = Advisory-first** (AUQ answer).
- Owner directive (2026-06-24, this session): "create that project with an umbrella implementation proposal which we will populate with WI."

No further owner decision blocks this umbrella. Per-slice owner authorization (PAUTH) is a separate, later step taken when the owner populates and prioritizes work items.

## Prior Deliberations

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-15-14-35-skill-usage-advisory.md` - the source advisory (10 skill opportunities + phased enforcement model + suggested first slice).
- `DELIB-20265883` - the owner umbrella-scoping decision captured for this proposal.
- `PROJECT-GTKB-SKILL-MODERNIZATION` (active) - adjacent and complementary: it modernizes existing skill *content* (thin-wrapper migration, skill-health checker, kb-* rewrites). This program builds a new *routing / activation-enforcement* layer. The two are distinct, not duplicative; slices touching the capability registry must reconcile with the modernization project's registry-parity work rather than fork it.
- WI-3330 disposition (`bridge/gtkb-lo-advisory-skill-usage-disposition-001.md`, `monitor`) - the routing disposition that explicitly deferred the router to a separate project (this one).


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Program Scope and Slicing Plan

The program is the deterministic skill-activation & enforcement layer. The owner will populate work items; the candidate slices below are drawn from the advisory's opportunity catalog and grouped by the program's surfaces. **Slice ordering is owner-driven; the only fixed decision is that the FIRST implemented slice is the bridge-shape hardening group (B).**

**First slice (owner-selected): Bridge-shape hardening (B).** Make the most expensive recurring failure class mechanically preventable:
- `gt bridge propose` deterministic CLI / proposal-shape hardening: own metadata lines, machine-readable `target_paths` parsing, preflight capture, prior-deliberation prepopulation, owner-decision section scaffolding, and project/WI metadata (advisory opportunity #2; relates to open WI-3318 and the NO-GO'd `gtkb-gt-bridge-propose-deterministic-cli` per the advisory).
- A standalone `target-paths-scope-auditor` used by bridge proposal helpers + implementation authorization, comparing machine-readable `target_paths`, prose file claims, test paths, generated files, and integration surfaces (opportunity #6).
- A stale-thread / duplicate-thread check before NEW proposal filing using live bridge state + Deliberation Archive thread summaries (opportunity #10).

**Subsequent candidate slices (owner-populated, unordered):**
- Skill-usage router: `scripts/skill_usage_router.py` / `gt skills suggest|check` with a static scenario table (role, prompt class, changed paths, bridge status/type, target files, report type → required/recommended skills + rationale), report-only integration into bridge-helper / startup / Stop output (opportunity #1).
- Registry scenario-metadata: extend `config/agent-control/harness-capability-registry.toml` with `trigger_scenarios`, `required_when`, `recommended_when`, `deterministic_helpers`, `evidence_required`, `hard_gate` (advisory F1).
- `/verify` verdict-author hardening + `spec_to_test_mapper.py` (opportunity #3; the GO'd `gtkb-verify-verdict-author-skill-slice-1` is the seam).
- `codex-skill-load-smoke` runtime loadability checker folded into parity/doctor (opportunity #5; open NO-GO `gtkb-codex-skill-loading-failure-cleanup-slice-1`).
- CI/doctor support: `platform_tests/skills/test_skill_catalog_contract.py`, `scripts/check_skill_loadability.py`, and a doctor check for unregistered/missing skills, adapter mismatch/load failure, and scenario-metadata omissions (advisory enforcement model §3).
- Report self-disclosure: a compact `Skills applied` line in LO reports, bridge verdicts, and session wraps (advisory enforcement model §4).
- Supporting helpers as the owner prioritizes: `skill-governance-lifecycle` (opportunity #4), `managed-skill-adoption-review` (opportunity #8), `formal-artifact-packet-helper` (opportunity #9), `advisory-disposition` (opportunity #7).

## Enforcement Posture (advisory-first, owner decision)

- **Phase 1 (this program's default):** advisory warnings only — startup / Stop / bridge-helper output emit "required" and "recommended" skills + rationale; no hard block on ordinary chat or exploratory review.
- **Phase 2 (separate future owner decision per scenario class):** hard gates ONLY where the repo already treats the workflow as governed (bridge proposal filing, bridge verdict filing, formal-artifact mutation, deployment/release, managed-skill/adopter-registry mutation). Each hard-gate conversion requires its own owner AskUserQuestion before it lands.
- This umbrella does NOT authorize any hard gate. It commits the program to advisory-first and routes every hard-gate decision through a future owner AUQ.

## Out of Scope

- Any code implementation in this umbrella (each slice is a separate `prime_proposal` with its own PAUTH + linked specs + spec-derived tests).
- Hard gates of any kind without a future per-scenario-class owner AUQ.
- Forking or duplicating the capability registry, managed-artifact registry, or `PROJECT-GTKB-SKILL-MODERNIZATION`'s registry-parity surfaces.
- LLM-based skill classification (the advisory and GT-KB policy require deterministic routing).
- New project work items (the owner populates WIs; the umbrella creates none).
- Formal GOV/SPEC/ADR/DCL/PB/REQ mutation (slices that need specs capture them through the governed approval path).

## Target Path Rationale

The only target path is this umbrella bridge file. It is the durable program-scoping artifact. It performs no source, test, registry, MemBase, formal-artifact, or work-item change; it defines the program the owner will populate and that future slices will implement under their own authorizations.

## Spec-Derived Verification Plan

This umbrella is a non-implementation `governance_advisory`; it ships no code, so verification is evidence-based rather than test-suite based:
- `gt projects show PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT` confirms the project record exists (created per `DELIB-20265883`).
- `gt deliberations search` / the DA confirms `DELIB-20265883` records the three owner AUQ decisions.
- Applicability and clause preflights pass on this operative file before a GO is recorded.
- Each future implementation slice carries its own spec-derived test plan and is verified independently; nothing here is marked VERIFIED.

## Requested Loyal Opposition Review

Please review whether this umbrella correctly scopes a `governance_advisory` program for `PROJECT-GTKB-SKILL-ACTIVATION-ENFORCEMENT`: full enforcement-program breadth, bridge-shape hardening (B) as the first slice, and an advisory-first posture that routes every hard-gate conversion through a future owner AUQ. A `GO` should confirm the program scope and slicing intent (authorizing no implementation). A `NO-GO` should identify a scope boundary that must be narrowed, an overlap with `PROJECT-GTKB-SKILL-MODERNIZATION` that must be reconciled, or a governance gap before the owner begins populating work items.
