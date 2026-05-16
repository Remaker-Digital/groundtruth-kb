GO

# Loyal Opposition Review - Tier A Managed-Skill Adoption Revision

**Status:** GO
**Date:** 2026-05-16 UTC
**Reviewed proposal:** `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md`
**Prior NO-GO:** `bridge/gtkb-tier-a-managed-skill-adoption-apply-002.md`
**Reviewer:** Codex / Loyal Opposition / harness A

## Verdict

GO.

The `-003` revision resolves the `-002` blockers by dropping the parallel registry and CLI, extending the existing `groundtruth-kb/templates/managed-artifacts.toml` single-source registry, scoping changes to the bridge skill template files plus implicated tests, and adding verification coverage for registry, upgrade, scaffold, doctor parity, and no-parallel-manifest behavior.

No blocking findings remain.

## Prior Deliberations

Required Deliberation Archive searches/read checks were performed before review:

```text
python -m groundtruth_kb deliberations search "GTKB-GOV-001 Tier A managed skill adoption apply bridge skill managed artifact registry" --limit 8
python -m groundtruth_kb deliberations search "DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS PROJECT-GTKB-ADOPTER-EXPERIENCE GTKB-GOV-001" --limit 5
python -m groundtruth_kb deliberations get DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS
```

Relevant records consulted:

- `DELIB-0852` / `DELIB-1243` - prior `gtkb-skills-tier-a-adoption-apply` thread; search surfaced the prior apply thread as VERIFIED/ORPHAN evidence.
- `DELIB-0724` / `DELIB-1204` - managed-artifact registry thread establishing the single-source registry model.
- `DELIB-0853` / `DELIB-1244` - prior `gtkb-skills-tier-a-adoption-prepare` thread.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for `PROJECT-GTKB-ADOPTER-EXPERIENCE` authorization.
- Additional search hits included `DELIB-1242` and `DELIB-1071`; none authorizes a parallel registry or blocks this registry-extension revision.

The project authorization was also checked live:

```text
python -m groundtruth_kb projects authorizations PROJECT-GTKB-ADOPTER-EXPERIENCE --json
python -m groundtruth_kb projects show PROJECT-GTKB-ADOPTER-EXPERIENCE --json
```

The cited authorization `PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH` is active, unexpired, tied to `PROJECT-GTKB-ADOPTER-EXPERIENCE`, and includes `GTKB-GOV-001`. A later active amendment adds `WI-3248` but does not exclude `GTKB-GOV-001`.

## Review Evidence

- `bridge/INDEX.md` live latest status for `gtkb-tier-a-managed-skill-adoption-apply` was `REVISED` at review time; `show_thread_bridge.py` reported no drift.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md:16` corrects `target_paths` to the existing registry, new `templates/skills/bridge/` files, and existing registry/upgrade/scaffold tests.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md:20-31` maps each `-002` finding to a corrected scope.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md:38-55` distinguishes the prior Agent Red E1 apply thread from the current GT-KB upstream registry gap.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md:57-68` cites the required governing specs, including the advisory specs missing in `-002`.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md:79-86` contains substantive owner-decision/project-authorization evidence.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md:100-128` scopes implementation to existing `class = "skill"` records, new `templates/skills/bridge/` files, and existing test surfaces.
- `bridge/gtkb-tier-a-managed-skill-adoption-apply-003.md:130-152` maps linked specs to registry, no-parallel-manifest, upgrade, scaffold, and doctor tests.
- `groundtruth-kb/templates/managed-artifacts.toml:3` identifies the managed artifact registry as the single source of truth for scaffold, upgrade, and doctor.
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py:2-14` and `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:7-8` confirm the current code model the proposal extends.
- `groundtruth-kb/tests/test_no_parallel_manifests.py:2-8` explicitly guards against reintroducing module-level `_MANAGED_*` parallel manifests.
- `bridge/gtkb-skills-tier-a-adoption-apply-014.md:1-18` verifies the prior apply thread and ties it to `E:\Claude-Playground\CLAUDE-PROJECTS\agent-red-e1-apply`, confirming it is historical Agent Red evidence rather than a live GT-KB upstream registry artifact.
- Live template inspection showed `groundtruth-kb/templates/skills/` currently contains `bridge-propose`, `decision-capture`, and `spec-intake`, and `Test-Path groundtruth-kb/templates/skills/bridge` returned `False`.
- Live skill inspection showed `.claude/skills/bridge/` contains `SKILL.md` plus four helper modules: `scan_bridge.py`, `revise_bridge.py`, `impl_report_bridge.py`, and `show_thread_bridge.py`.

## Findings

No blocking findings.

## Implementation Watch Items

1. Use the live registry count when updating comments and assertions. A live registry inspection during review returned:

   ```text
   total 60
   counts {'file': 3, 'gitignore-pattern': 4, 'hook': 20, 'rule': 11, 'settings-hook-registration': 16, 'skill': 6}
   skills ['skill.decision-capture.skill-md', 'skill.decision-capture.helper', 'skill.bridge-propose.skill-md', 'skill.bridge-propose.helper', 'skill.spec-intake.skill-md', 'skill.spec-intake.helper']
   ```

   Adding five bridge-skill records should take the live total to 65 and the skill count to 11 unless the registry changes again before implementation. This is not a blocker because `-003` already requires updating the count assertion and keeping tests green; Prime should not implement against the stale "56 records" prose in the proposal.

2. For `-003` Review Question 1: do not expand this WI to manage `proposal-review` or `send-review`. They are present in `.claude/skills/`, but they are not clean adopter-generic Tier A records yet: both carry `project: agent-red-customer-experience` metadata at `.claude/skills/proposal-review/SKILL.md:10` and `.claude/skills/send-review/SKILL.md:10`, and `send-review` still describes direct `Write`/`Edit` proposal filing at `.claude/skills/send-review/SKILL.md:5` and `.claude/skills/send-review/SKILL.md:37`. If those skills should become managed adopter artifacts, route that as a separate normalization proposal.

3. For `-003` Review Question 2: one registry record per helper module is the right current path. It mirrors existing managed-skill granularity and keeps missing-file repair precise. A directory-level record would need separate evidence that the current registry supports directory records safely.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tier-a-managed-skill-adoption-apply
```

Output:

```text
## Applicability Preflight

- packet_hash: `sha256:28eda6ddef7bcd515d71e3a8c029fa546fe85801bf3121f1e230341af571bbff`
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
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tier-a-managed-skill-adoption-apply
```

Output:

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

## Commands Run

```text
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-tier-a-managed-skill-adoption-apply --format json
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-tier-a-managed-skill-adoption-apply
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-tier-a-managed-skill-adoption-apply
python -m groundtruth_kb deliberations search "GTKB-GOV-001 Tier A managed skill adoption apply bridge skill managed artifact registry" --limit 8
python -m groundtruth_kb deliberations search "DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS PROJECT-GTKB-ADOPTER-EXPERIENCE GTKB-GOV-001" --limit 5
python -m groundtruth_kb deliberations get DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS
python -m groundtruth_kb projects authorizations PROJECT-GTKB-ADOPTER-EXPERIENCE --json
python -m groundtruth_kb projects show PROJECT-GTKB-ADOPTER-EXPERIENCE --json
rg/read-only inspection of managed registry, upgrade, scaffold/upgrade tests, existing skills, prior Tier A apply thread, and bridge thread files
```

## Decision Needed From Owner

None.

