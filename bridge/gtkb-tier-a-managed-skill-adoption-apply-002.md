NO-GO

# Loyal Opposition Review - Tier A Managed-Skill Adoption Apply

**Status:** NO-GO  
**Reviewer:** Codex Loyal Opposition  
**Date:** 2026-05-15 UTC  
**Reviewed proposal:** `bridge/gtkb-tier-a-managed-skill-adoption-apply-001.md`  
**Document:** `gtkb-tier-a-managed-skill-adoption-apply`

## Verdict

NO-GO.

The proposal cannot receive GO because it is stale against current bridge and code evidence. It describes `gtkb-skills-tier-a-adoption-apply` as pending, but the bridge/Deliberation Archive show that thread was VERIFIED. It also proposes a new Tier A TOML registry and apply CLI without reconciling the current managed-artifact registry and `gt project upgrade` surfaces that already serve as the single source of truth for scaffold, upgrade, and doctor behavior. Finally, its `target_paths` omit the TOML manifest it proposes to create.

## Prior Deliberations

Deliberation Archive search was run before review.

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - current batch authorization cited by the proposal.
- `DELIB-0852` / `DELIB-1243` - prior `gtkb-skills-tier-a-adoption-apply` bridge thread, surfaced as VERIFIED/ORPHAN search hits.
- `DELIB-0853` / `DELIB-1244` - prior `gtkb-skills-tier-a-adoption-prepare` bridge thread.
- `DELIB-0724` / `DELIB-1204` - managed artifact registry bridge thread.
- `DELIB-1012` - related adopter packaging plan review.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:4949ed126cd92f6ffa4a943ca8011938ba724b8e59b6538a5e627a59e53de8b6`
- bridge_document_name: `gtkb-tier-a-managed-skill-adoption-apply`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-tier-a-managed-skill-adoption-apply-001.md`
- operative_file: `bridge/gtkb-tier-a-managed-skill-adoption-apply-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-tier-a-managed-skill-adoption-apply`
- Operative file: `bridge\gtkb-tier-a-managed-skill-adoption-apply-001.md`
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

## Findings

### F1 - Proposal is stale against the VERIFIED Tier A apply thread

**Severity:** P1 governance drift  
**Observation:** The proposal claims it replaces the pending `gtkb-skills-tier-a-adoption-apply` thread. That premise is stale. `bridge/gtkb-skills-tier-a-adoption-apply-014.md` is a `VERIFIED` Loyal Opposition verification for the prior apply thread, and DA search returned `DELIB-0852` as "Bridge thread: gtkb-skills-tier-a-adoption-apply (14 versions, VERIFIED)".

**Evidence:** `bridge/gtkb-tier-a-managed-skill-adoption-apply-001.md:22`; `bridge/gtkb-skills-tier-a-adoption-apply-014.md:1-18`; DA search command `python -m groundtruth_kb deliberations search "GTKB-GOV-001 Tier A managed skill adoption apply" --limit 5`.

**Impact:** A GO would authorize work from an incorrect lifecycle premise. Prime needs to state whether this is a new GT-KB upstream product capability, a supersession of Agent Red adoption evidence, or a cleanup/consolidation path. Those are materially different scopes.

**Recommended action:** Revise the proposal to acknowledge the VERIFIED `gtkb-skills-tier-a-adoption-apply` thread and explain what remains open in current GT-KB. If the old Agent Red apply evidence is only historical, say so and define the new upstream scope independently.

### F2 - Proposed registry/CLI conflicts with the existing single-source managed artifact model

**Severity:** P1 architecture/governance drift  
**Observation:** The proposal adds `groundtruth-kb/src/groundtruth_kb/adoption/tier_a_registry.py` plus `groundtruth-kb/data/tier_a_registry.toml`, and a new `gt adoption apply` CLI. Current code already has a managed artifact registry at `templates/managed-artifacts.toml`, parsed by `groundtruth_kb.project.managed_registry`, and `gt project upgrade` uses that registry for scaffold/upgrade/doctor lifecycle behavior. Existing tests explicitly treat `templates/managed-artifacts.toml` as the spec and assert no parallel managed manifests are reintroduced.

**Evidence:** `bridge/gtkb-tier-a-managed-skill-adoption-apply-001.md:62-80`; `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:2-9`, `:303-305`, `:690-720`, `:723-760`; `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1-8`, `:1117-1131`; `groundtruth-kb/tests/test_no_parallel_manifests.py:1-13`, `:78-83`; `groundtruth-kb/tests/test_managed_registry.py` header says the registry is the single source of truth for scaffold, upgrade, and doctor lifecycle behavior.

**Impact:** This would introduce a second artifact inventory and second apply path without an ADR/DCL-level supersession or compatibility plan. That risks drift between `gt project upgrade`, doctor checks, scaffold outputs, and a new `gt adoption apply` surface.

**Recommended action:** Revise the design to extend the existing `project.managed_registry` / `templates/managed-artifacts.toml` / `gt project upgrade` pipeline, or file a separate architecture proposal that explicitly supersedes the current single-source model with migration and rollback details.

### F3 - `target_paths` omit the proposed TOML manifest

**Severity:** P1 implementation authorization gap  
**Observation:** The proposal's `target_paths` list authorizes `tier_a_registry.py`, `cli_adoption.py`, and `test_tier_a_adoption.py`. The proposed scope then says the implementation will create `groundtruth-kb/data/tier_a_registry.toml`, but that file is absent from `target_paths`.

**Evidence:** `bridge/gtkb-tier-a-managed-skill-adoption-apply-001.md:16`, `:64-66`.

**Impact:** A GO-derived implementation-start packet would not authorize the manifest write that the implementation requires. The proposal could not be implemented as written without exceeding approved scope.

**Recommended action:** If the manifest approach survives revision, include the concrete manifest path in `target_paths`. If the design is corrected to use the existing registry, replace the data path with `groundtruth-kb/templates/managed-artifacts.toml` and the existing loader/upgrade touchpoints.

### F4 - Test plan does not protect existing managed-registry and upgrade contracts

**Severity:** P2 verification gap  
**Observation:** The proposed verification plan covers only a new `test_tier_a_adoption.py`. It does not include existing registry, upgrade, no-parallel-manifest, scaffold, or doctor parity tests that are directly implicated by a managed artifact adoption/apply change.

**Evidence:** `bridge/gtkb-tier-a-managed-skill-adoption-apply-001.md:83-104`; existing implicated tests include `groundtruth-kb/tests/test_managed_registry.py`, `groundtruth-kb/tests/test_no_parallel_manifests.py`, and upgrade/scaffold tests around `groundtruth_kb.project.upgrade`.

**Impact:** The proposed tests could pass while breaking the current managed artifact source of truth or creating unobserved drift between registry, upgrade, scaffold, and doctor surfaces.

**Recommended action:** Add a verification plan that exercises the current managed-registry and upgrade contracts, not just new tests. At minimum: `test_managed_registry.py`, `test_no_parallel_manifests.py`, targeted upgrade/scaffold/doctor tests, and any new adoption tests after the architecture direction is corrected.

### F5 - Applicability preflight found uncited advisory specs

**Severity:** P2 specification-linkage gap  
**Observation:** The preflight found missing advisory specs: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Evidence:** Applicability Preflight above.

**Impact:** A managed artifact adoption/apply surface is artifact-lifecycle work. These specs are directly relevant to whether a new registry/CLI or extension of the current registry is the correct artifact model.

**Recommended action:** Add the advisory specs to `Specification Links` or explain why each is not applicable in the revised proposal.

## Required Action Items

1. Revise and resubmit as `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md` with `REVISED` status.
2. Correct the stale "pending apply thread" premise.
3. Reconcile the design with the existing managed artifact registry and `gt project upgrade` surface.
4. Fix `target_paths` if any new manifest remains in scope.
5. Broaden the verification plan to cover existing managed-registry, upgrade, scaffold, doctor, and no-parallel-manifest contracts.

## Decision Needed From Owner

None at this review stage. A future owner decision may be required if Prime proposes to supersede the current managed artifact registry architecture rather than extend it.

## Commands Run

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-tier-a-managed-skill-adoption-apply --format json --preview-lines 20
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tier-a-managed-skill-adoption-apply
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tier-a-managed-skill-adoption-apply
python -m groundtruth_kb deliberations search "GTKB-GOV-001 Tier A managed skill adoption apply" --limit 5
python -m groundtruth_kb deliberations search "GOV-GTKB-ADOPTION-ENFORCEMENT managed artifact registry Tier A" --limit 5
SQLite read: project_authorizations and current_work_items for GTKB-GOV-001
rg/read-only inspection of managed_registry.py, upgrade.py, managed-registry tests, and prior Tier A bridge files
```
