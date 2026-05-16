REVISED

# Implementation Proposal - Complete Tier A Managed-Skill Adoption (GTKB-GOV-001)

bridge_kind: implementation_proposal
Document: gtkb-tier-a-managed-skill-adoption-apply
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-001

target_paths: ["groundtruth-kb/templates/managed-artifacts.toml", "groundtruth-kb/templates/skills/bridge/SKILL.md", "groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/show_thread_bridge.py", "groundtruth-kb/tests/test_managed_registry.py", "groundtruth-kb/tests/test_upgrade_skills.py", "groundtruth-kb/tests/test_scaffold_skills.py"]

This REVISED proposal completes Tier A managed-skill adoption by EXTENDING the existing single-source managed-artifact registry (`groundtruth-kb/templates/managed-artifacts.toml`, parsed by `groundtruth_kb.project.managed_registry`, consumed by `gt project upgrade` / scaffold / doctor) with the `bridge` skill records that are currently unmanaged. It does NOT create a parallel registry or a parallel apply CLI.

## Revision Notes

This `-003` revises `-001` (NEW) to address every finding in the `-002` NO-GO. Each finding is mapped to its remedy:

- **F1 (P1 governance drift) — proposal is stale against the VERIFIED Tier A apply thread.** The `-001` proposal claimed it "replaces the pending `gtkb-skills-tier-a-adoption-apply` thread." That premise is stale. `bridge/gtkb-skills-tier-a-adoption-apply-014.md` is a `VERIFIED` Loyal Opposition verification (dated 2026-04-18); the DA records that thread as `DELIB-0852` "Bridge thread: gtkb-skills-tier-a-adoption-apply (14 versions, VERIFIED)". That thread's verification targeted the worktree `E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-e1-apply` — i.e. it was **Agent Red E1 adoption-apply evidence**, not GT-KB upstream Tier A registry coverage, and it is closed/VERIFIED. `-003` corrects the premise (see the Corrected Premise section below): the `gtkb-skills-tier-a-adoption-apply` thread is VERIFIED and is historical Agent Red adoption-apply evidence; what genuinely remains open is GT-KB **upstream** managed-skill coverage — the `bridge` skill is a Tier A bridge-protocol skill that is NOT yet in the managed-artifact registry and has no scaffold template.
- **F2 (P1 architecture/governance drift) — proposed registry/CLI conflicts with the existing single-source managed-artifact model.** The `-001` design added `groundtruth-kb/src/groundtruth_kb/adoption/tier_a_registry.py` + `groundtruth-kb/data/tier_a_registry.toml` + a new `gt adoption apply` CLI. GT-KB already has a single-source managed-artifact registry at `groundtruth-kb/templates/managed-artifacts.toml`, parsed by `groundtruth_kb.project.managed_registry`, and `gt project upgrade` (plus scaffold and doctor) already uses it for the scaffold/upgrade/doctor lifecycle. `groundtruth-kb/tests/test_no_parallel_manifests.py` is an AST gate that actively FORBIDS reintroducing parallel managed manifests. A parallel `tier_a_registry` would be exactly the prohibited second inventory. `-003` redesigns to EXTEND the existing registry: it adds `bridge`-skill records to `groundtruth-kb/templates/managed-artifacts.toml` (same `class = "skill"` schema the registry already uses for `decision-capture`, `bridge-propose`, `spec-intake`) and relies on the existing `gt project upgrade` / scaffold / doctor pipeline. No new registry module, no new data-TOML, no `gt adoption apply` CLI.
- **F3 (P1 implementation authorization gap) — `target_paths` omit the proposed TOML manifest.** The `-001` `target_paths` authorized `tier_a_registry.py`, `cli_adoption.py`, `test_tier_a_adoption.py` but not the `tier_a_registry.toml` it proposed to create. `-003` drops the parallel data-TOML and the new CLI entirely. The corrected `target_paths` list the real touchpoints: `groundtruth-kb/templates/managed-artifacts.toml` (the existing registry, extended), the new `bridge`-skill template files under `groundtruth-kb/templates/skills/bridge/`, and the existing implicated test files.
- **F4 (P2 verification gap) — test plan does not protect existing managed-registry and upgrade contracts.** The `-001` plan covered only a new `test_tier_a_adoption.py`. `-003` removes that file and instead exercises the existing implicated contracts: `groundtruth-kb/tests/test_managed_registry.py` (registry parse / schema / lifecycle-axis invariants — extended for the new `bridge` records), `groundtruth-kb/tests/test_no_parallel_manifests.py` (run to confirm no parallel manifest is introduced — this proposal must keep it green), `groundtruth-kb/tests/test_upgrade_skills.py` and `groundtruth-kb/tests/test_scaffold_skills.py` (upgrade/scaffold of the new managed skill), and `groundtruth-kb/tests/test_doctor.py` (doctor parity).
- **F5 (P2 specification-linkage gap) — applicability preflight found uncited advisory specs.** The `-002` preflight flagged `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` uncited. Both are now cited in Specification Links (managed-artifact adoption IS artifact-lifecycle work).

The WI intent (complete Tier A managed-skill adoption so adopter projects receive the canonical Tier A skills through the governed upgrade pipeline) is preserved; only the mechanism is corrected from a parallel registry to an extension of the existing one.

## Corrected Premise (replaces -001 F1 stale premise)

The `gtkb-skills-tier-a-adoption-apply` bridge thread is **VERIFIED** at `bridge/gtkb-skills-tier-a-adoption-apply-014.md` (Loyal Opposition verification dated 2026-04-18; `DELIB-0852` records "14 versions, VERIFIED"). That thread's `-014` verification names target worktree `E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-e1-apply` — it was an Agent Red E1 adoption-apply exercise. Per the project-root-boundary rule and the Agent-Red-separate-project boundary, that Agent Red adoption-apply evidence is historical; it is not GT-KB upstream Tier A registry coverage and `-003` does not depend on it as a live artifact.

What genuinely remains open in current GT-KB: the GT-KB **upstream** managed-artifact registry (`groundtruth-kb/templates/managed-artifacts.toml`) currently manages 3 skills (`decision-capture`, `bridge-propose`, `spec-intake` — each a SKILL.md record plus a helper record, 6 skill records total). The `bridge` skill — a Tier A bridge-protocol skill present at `.claude/skills/bridge/` with `SKILL.md` and four helper modules (`scan_bridge.py`, `revise_bridge.py`, `impl_report_bridge.py`, `show_thread_bridge.py`) — is NOT in the registry and has no scaffold template under `groundtruth-kb/templates/skills/`. Adopter projects therefore do not receive the `bridge` skill through `gt project upgrade`. Closing that gap is the concrete, current, upstream scope of GTKB-GOV-001 Tier A managed-skill adoption.

## Claim

Extend the existing single-source managed-artifact registry with the `bridge` skill so adopter projects receive it (and keep it drift-repaired) through the existing `gt project upgrade` / scaffold / doctor pipeline. Concretely: ship `groundtruth-kb/templates/skills/bridge/` (SKILL.md + the four helper modules) and add matching `class = "skill"` records to `groundtruth-kb/templates/managed-artifacts.toml`, using the same schema and lifecycle-axis fields the registry already uses for the `decision-capture` / `bridge-propose` / `spec-intake` skill records. No parallel registry, no parallel data-TOML, no new CLI.

## Architecture Reconciliation (corrects -001 F2)

The existing managed-artifact model is the single source of truth and is the model `-003` extends:

- **Registry:** `groundtruth-kb/templates/managed-artifacts.toml` — declarative TOML, currently 56 records (20 hooks, 10 rules, 6 skills, 16 settings-hook-registrations, 4 gitignore patterns). Each record carries `class`, `id`, `template_path`, `target_path`, `initial_profiles`, `managed_profiles`, `doctor_required_profiles`, `ownership`, `upgrade_policy`, `adopter_divergence_policy`, `notes`.
- **Loader:** `groundtruth_kb.project.managed_registry` parses the TOML into typed dataclasses and enforces loader invariants (`managed_profiles ⊆ initial_profiles`, `doctor_required_profiles ⊆ initial_profiles`, per-class key schemas).
- **Consumers:** `gt project upgrade` enforces drift/missing-file repair for `managed_profiles`; scaffold copies for `initial_profiles`; doctor enforces presence for `doctor_required_profiles`.
- **Guard:** `groundtruth-kb/tests/test_no_parallel_manifests.py` is an AST gate forbidding module-level `_MANAGED_*` parallel lists in `src/groundtruth_kb/`.

`-003` adds `bridge`-skill records to that registry using the existing skill-record schema (the registry already manages `bridge-propose`, an exactly analogous skill — SKILL.md record + helper record). No loader change is required: the skill-record schema already exists. No new consumer is required: `gt project upgrade` already dispatches skill records. This is a pure registry extension, fully inside the single-source model.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB` (`groundtruth-kb/...` is the GT-KB platform subtree inside the project root). `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. No path resolves outside `E:\GT-KB`; specifically, no `E:\Claude-Playground` path is a live dependency of this proposal — the VERIFIED Agent Red apply thread is cited only as historical evidence.

## Specification Links

- `GOV-GTKB-ADOPTION-ENFORCEMENT-001` - the governing specification for GT-KB adoption work; Tier A managed-skill adoption is the capability this spec mandates.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the managed-artifact registry is the artifact-oriented model for adopter scaffolding/upgrade.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; this proposal is a bridge artifact, and the skill being added is the bridge-protocol skill.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic policy-engine surface; relevant because the registry/upgrade pipeline is a deterministic service rather than an LLM-mediated apply.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root and no Agent Red / Claude-Playground path is a live dependency.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the VERIFIED step to rest on executed spec-derived tests; the Specification-Derived Verification Plan maps each linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - GTKB-GOV-001 is a tracked backlog work item; this is a single-WI implementation, not a bulk backlog operation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the managed-artifact registry IS the artifact-graph model for adopter artifacts, and this proposal extends it. Cited per `-002` F5.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; adding a managed skill is artifact-lifecycle work (scaffold trigger, upgrade trigger, doctor trigger). Cited per `-002` F5.

## Prior Deliberations

- `DELIB-0852` - records the `gtkb-skills-tier-a-adoption-apply` bridge thread as VERIFIED (14 versions). This is the deliberation establishing that the thread the `-001` proposal called "pending" is in fact VERIFIED; `-003` corrects the premise accordingly.
- `DELIB-1243` - records the same `gtkb-skills-tier-a-adoption-apply` thread (surfaced as ORPHAN/VERIFIED in DA search); confirms the thread is closed and is historical Agent Red adoption-apply evidence.
- `DELIB-0724` - records the `gtkb-managed-artifact-registry` bridge thread as VERIFIED (10 versions). This is the deliberation that established the single-source managed-artifact registry `-003` extends; it is the architectural authority the `-001` design conflicted with and `-003` now aligns to.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization context for the project-authorization batch under which `PROJECT-GTKB-ADOPTER-EXPERIENCE` work proceeds.

No prior deliberation authorizes a parallel managed-artifact registry; `DELIB-0724` establishes the single-source registry as canonical, and `-003` extends it rather than competing with it.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by the following owner decision:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-ADOPTER-EXPERIENCE` project authorization (`PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH`), whose `included_work_item_ids` include `GTKB-GOV-001`. The authorization is live and active in MemBase (`current_project_authorizations`), with `allowed_mutation_classes` `["hook_upgrade", "cli_extension", "test_addition", "spec_status_promotion"]`. GTKB-GOV-001 is an active member of `PROJECT-GTKB-ADOPTER-EXPERIENCE` (membership `PWM-PROJECT-GTKB-ADOPTER-EXPERIENCE-GTKB-GOV-001`).
- Owner-decision evidence: `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`. Formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`.

No new owner decision is required for this `-003` revision; the revision corrects the stale premise and the parallel-registry architecture error within the already-authorized GTKB-GOV-001 scope. Per the `-002` NO-GO ("A future owner decision may be required if Prime proposes to supersede the current managed artifact registry architecture rather than extend it"): `-003` EXTENDS the registry and does NOT supersede it, so no such owner decision is triggered.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-GTKB-ADOPTION-ENFORCEMENT-001` specifies the adoption-enforcement requirement, and `DELIB-0724`'s managed-artifact registry is the existing implemented mechanism. Adding the `bridge` skill to the registry is implementation work within that already-specified mechanism. No new or revised requirement or specification is created by this work. No new public API or CLI surface is introduced (the `-001` `gt adoption apply` CLI is dropped).

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single work item GTKB-GOV-001 and its governed filing path only. The applicable evidence pattern is a single-WI implementation proposal with formal-artifact-approval discipline preserved unchanged. The review-packet inventory is one bridge thread: IP-1 (registry extension) + IP-2 (bridge-skill templates) + IP-3 (tests). No formal artifact (GOV/ADR/DCL/SPEC) is created or mutated; the registry TOML is a managed-artifact data file, not a formal specification artifact.

## Bridge INDEX Maintenance

`bridge/INDEX.md` is the canonical bridge workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`. This `-003` REVISED file is recorded by inserting a `REVISED: bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md` line at the top of the existing `Document: gtkb-tier-a-managed-skill-adoption-apply` entry, above the `-002` NO-GO and `-001` NEW lines. The append-only version chain (`-001` NEW, `-002` NO-GO, `-003` REVISED) is preserved; no prior file or INDEX line is deleted or rewritten.

## Proposed Scope

### IP-1: Extend the managed-artifact registry with the `bridge` skill

In `groundtruth-kb/templates/managed-artifacts.toml`, add `class = "skill"` records for the `bridge` skill, modeled exactly on the existing `skill.bridge-propose.skill-md` and `skill.bridge-propose.helper` records:

- `skill.bridge.skill-md` — `template_path = "skills/bridge/SKILL.md"`, `target_path = ".claude/skills/bridge/SKILL.md"`.
- One helper record per `bridge` helper module: `skill.bridge.helper.scan`, `skill.bridge.helper.revise`, `skill.bridge.helper.impl-report`, `skill.bridge.helper.show-thread` — `template_path`/`target_path` pointing to `skills/bridge/helpers/<module>.py` / `.claude/skills/bridge/helpers/<module>.py`.

All new records use `initial_profiles = ["dual-agent", "dual-agent-webapp"]`, `managed_profiles = ["dual-agent", "dual-agent-webapp"]`, `doctor_required_profiles = []`, `ownership = "gt-kb-managed"`, `upgrade_policy = "overwrite"`, `adopter_divergence_policy = "warn"` — identical to the existing `bridge-propose` skill records (the `bridge` skill is a bridge-protocol skill in the same `bridge` profile group). The loader invariants (`managed_profiles ⊆ initial_profiles`) are satisfied by construction. The registry header comment count line is updated to reflect the new record total.

### IP-2: Ship the `bridge` skill scaffold templates

Create `groundtruth-kb/templates/skills/bridge/`:

- `SKILL.md` — the scaffold template for the `bridge` skill, sourced from the current canonical `.claude/skills/bridge/SKILL.md` with adopter-generic placeholders applied consistently with how `templates/skills/bridge-propose/SKILL.md` is templated.
- `helpers/scan_bridge.py`, `helpers/revise_bridge.py`, `helpers/impl_report_bridge.py`, `helpers/show_thread_bridge.py` — the scaffold templates for the four `bridge` helper modules, sourced from the current `.claude/skills/bridge/helpers/` modules.

These template files are what scaffold/upgrade copy into an adopter's `.claude/skills/bridge/`.

### IP-3: Tests — protect existing contracts and cover the new records

Test changes are confined to existing test files (no new parallel test tree):

- `groundtruth-kb/tests/test_managed_registry.py` — extend to assert the new `bridge`-skill records parse, satisfy the lifecycle-axis invariants, and have correct `template_path`/`target_path` pairs; update any record-count assertion to the new total.
- `groundtruth-kb/tests/test_no_parallel_manifests.py` — run unchanged; this proposal must keep it green (it confirms no parallel manifest is introduced — the direct evidence that `-002` F2 is resolved).
- `groundtruth-kb/tests/test_upgrade_skills.py` — extend to cover `gt project upgrade` delivering / drift-repairing the `bridge` skill.
- `groundtruth-kb/tests/test_scaffold_skills.py` — extend to cover scaffold copying the `bridge` skill for the `dual-agent` profiles.
- `groundtruth-kb/tests/test_doctor.py` — run to confirm doctor parity is unaffected by the new records.

## Specification-Derived Verification Plan

Each linked specification maps to at least one executed test or verification command. Test changes are confined to the existing test files listed in `target_paths`.

| Linked specification | Verification |
|---|---|
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `test_managed_registry.py` (extended) — the `bridge`-skill records parse, satisfy lifecycle-axis invariants, and are part of the single-source registry; adopter projects receive the `bridge` skill via the governed registry. |
| `DELIB-0724` single-source registry constraint (architecture authority for F2) | `test_no_parallel_manifests.py` — run and green; confirms no parallel managed manifest was introduced. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (scaffold/upgrade triggers) | `test_upgrade_skills.py` (extended), `test_scaffold_skills.py` (extended) — `gt project upgrade` and scaffold deliver/drift-repair the `bridge` skill. |
| `GOV-GTKB-ADOPTION-ENFORCEMENT-001` (doctor parity) | `test_doctor.py` — doctor parity unaffected by the new records. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | the skill being added IS the bridge-protocol skill; managing it through the registry preserves bridge-skill availability for adopters. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | satisfied structurally by this Specification-Derived Verification Plan and the embedded preflights. |
| `GOV-STANDING-BACKLOG-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `SPEC-AUQ-POLICY-ENGINE-001` | governance/framing specs; satisfied by the single-WI artifact-graph framing and in-root placement; no separate runtime test. |

Verification commands:

```
python -m pytest groundtruth-kb/tests/test_managed_registry.py -v
python -m pytest groundtruth-kb/tests/test_no_parallel_manifests.py -v
python -m pytest groundtruth-kb/tests/test_upgrade_skills.py groundtruth-kb/tests/test_scaffold_skills.py -v
python -m pytest groundtruth-kb/tests/test_doctor.py -q
python -m ruff check .
python -m ruff format --check .
```

## Acceptance Criteria

1. IP-1: `bridge`-skill records (`skill.bridge.skill-md` + four helper records) added to `groundtruth-kb/templates/managed-artifacts.toml` using the existing skill-record schema; loader invariants satisfied; registry header count updated.
2. IP-2: `groundtruth-kb/templates/skills/bridge/` created with `SKILL.md` and the four helper-module templates.
3. No parallel registry module, no parallel data-TOML, no new `gt adoption apply` CLI is created; `test_no_parallel_manifests.py` is green.
4. IP-3: `test_managed_registry.py`, `test_upgrade_skills.py`, `test_scaffold_skills.py` extended for the new records; `test_doctor.py` confirms doctor parity; all listed tests pass.
5. `ruff check` and `ruff format --check` are clean.
6. Both bridge preflights pass on this proposal (embedded below).

## Files Expected To Change

- `groundtruth-kb/templates/managed-artifacts.toml` — extended with five `bridge`-skill records (IP-1).
- `groundtruth-kb/templates/skills/bridge/SKILL.md` — new `bridge` skill scaffold template (IP-2).
- `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py` — new helper template (IP-2).
- `groundtruth-kb/templates/skills/bridge/helpers/revise_bridge.py` — new helper template (IP-2).
- `groundtruth-kb/templates/skills/bridge/helpers/impl_report_bridge.py` — new helper template (IP-2).
- `groundtruth-kb/templates/skills/bridge/helpers/show_thread_bridge.py` — new helper template (IP-2).
- `groundtruth-kb/tests/test_managed_registry.py` — extended assertions for the new records (IP-3).
- `groundtruth-kb/tests/test_upgrade_skills.py` — extended upgrade coverage (IP-3).
- `groundtruth-kb/tests/test_scaffold_skills.py` — extended scaffold coverage (IP-3).

## Risks / Rollback

- Risk: the registry header carries a record-count comment; a stale count would mislead future readers. Mitigation: IP-1 updates the count; `test_managed_registry.py` asserts the record total.
- Risk: a `bridge` skill helper imports a module not available in a scaffolded adopter. Mitigation: the templates are sourced from the live `.claude/skills/bridge/helpers/` modules which already run in this project; `test_upgrade_skills.py` / `test_scaffold_skills.py` exercise delivery into a temp adopter, surfacing any import gap.
- Risk: `test_no_parallel_manifests.py` could regress if a future edit reintroduces a `_MANAGED_*` list. Mitigation: this proposal introduces no module-level list; the test is run as an explicit acceptance criterion.
- Rollback: remove the five `bridge`-skill records from `managed-artifacts.toml`, delete `groundtruth-kb/templates/skills/bridge/`, and revert the test extensions. Adopter projects continue without the registry-managed `bridge` skill (the pre-proposal state). Fully reversible; no data migration.

## Recommended Commit Type

`feat:` — extends the managed-artifact registry with a new managed skill (the `bridge` skill) plus its scaffold templates and test coverage. New managed-artifact coverage for adopters; registry-data + template files + test extensions.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tier-a-managed-skill-adoption-apply`

```text
## Applicability Preflight

- packet_hash: `sha256:53a9959c75d9473128c06b91e83672d84cc860c0b5289f63f4bbf7dcedfc23e0`
- bridge_document_name: `gtkb-tier-a-managed-skill-adoption-apply`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md`
- operative_file: `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. The two advisory specs the `-002` preflight flagged uncited (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`) are now cited.

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tier-a-managed-skill-adoption-apply`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-tier-a-managed-skill-adoption-apply`
- Operative file: `bridge\gtkb-tier-a-managed-skill-adoption-apply-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

Result: exit 0; 5/5 `must_apply` clauses with evidence; 0 blocking gaps.

## Review Questions for Loyal Opposition

1. Is the `bridge` skill the correct (and complete) remaining-open Tier A managed-skill, or should additional skills (e.g., `proposal-review`, `send-review`) also be brought under registry management in this WI? `-003` scopes to the `bridge` skill because it is the one Tier A bridge-protocol skill present in `.claude/skills/` with helpers but absent from both the registry and `templates/skills/`.
2. The helper records: should each `bridge` helper module be its own registry record (as `-003` proposes, mirroring the granularity the registry uses elsewhere), or should the four helpers be covered by directory-level records if the registry supports that?

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
