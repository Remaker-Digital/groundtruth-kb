NEW

# Implementation Proposal - AGENT-RED-REPO-MIGRATION-001: Canonical Agent Red Repository Migration

**Author:** Prime Builder (Codex, harness A)
**Drafted:** 2026-05-05
**Type:** Repository migration and release-evidence proposal
**Risk tier:** High (external GitHub repository migration, canonical CI binding, rc1 tag gate)
**Backlog candidate:** `AGENT-RED-REPO-MIGRATION-001`

---

## Background

Slice 8.6 surfaced a release-evidence gap: the substantive Agent Red CI evidence
was on the de facto repository
`https://github.com/Remaker-Digital/agent-red-customer-engagement`, while the
canonical Agent Red repository is `https://github.com/mike-remakerdigital/agent-red`.
The report said the de facto codebase is about 700 commits ahead of the split
point and the canonical repository has about 102 mostly Dependabot commits
ahead. Loyal Opposition rejected the Slice 8.6 report because the claimed
transient exception and canonical CI binding were not sufficient for
verification.

This proposal files the standalone migration thread that the Slice 8.6 report
identified as necessary. It does not fetch, push, force-push, or mutate any
external repository before `GO` and any required owner/repo authorization.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and
  registered in `bridge/INDEX.md` with latest status `NEW`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites
  required specs, repository identity records, and Slice 8.6 evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation must map
  migration verification and CI evidence to the cited requirements.
- `GOV-STANDING-BACKLOG-001`, `PB-STANDING-BACKLOG-CONTINUITY-001`, and
  `ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001` - this is a release-path
  follow-on candidate surfaced by Slice 8.6 and owner Phase 4-B disposition.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the migration must preserve durable
  evidence, explicit waiver scope, and terminal states.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
  `.claude/rules/project-root-boundary.md`, and
  `.claude/rules/canonical-terminology.md` - Agent Red is a separate project;
  GT-KB bridge artifacts remain under `E:\GT-KB`, and Agent Red source must not
  be treated as live GT-KB artifact content.
- `.claude/rules/project-resource-aliases.toml` and
  `memory/project_external_resource_registry.md` - canonical external resource
  identity surfaces.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`
  - owner-approved transient exception and migration prerequisite surfaced by
  the latest deliberation search.
- `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-008.md` - latest
  Loyal Opposition `NO-GO` requiring durable waiver/evidence correction.

## Prior Deliberations

Search performed:

```powershell
python -m groundtruth_kb deliberations search "Agent Red repo migration canonical repo de facto repo 700 commits canonical CI evidence" --limit 8
```

Relevant result: `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`.
The latest bridge evidence is still `NO-GO`, so this proposal treats the
deliberation as migration authority context, not as permission to skip review.

## Proposed Scope

1. Confirm repository identities and remotes:
   - canonical: `mike-remakerdigital/agent-red`
   - de facto: `Remaker-Digital/agent-red-customer-engagement`
2. Produce a non-mutating migration plan:
   - common ancestor;
   - de facto ahead commits;
   - canonical ahead commits;
   - protected branches and required checks;
   - conflict inventory;
   - Dependabot commit disposition.
3. After review/authorization, migrate the de facto Agent Red codebase into the
   canonical repository using the least destructive method available.
4. Preserve both histories where practical. Avoid force-push unless owner
   explicitly approves it for the canonical repository.
5. Run required CI on the canonical repository and capture workflow evidence.
6. Feed canonical CI evidence back into Slice 8.5 / Slice 8.6 release evidence.

## Acceptance Criteria

- Canonical Agent Red repository contains the substantive de facto codebase.
- The migration records how the 102 canonical-ahead commits were handled.
- Required workflows run on the canonical repository and bind to the migrated
  commit SHA.
- Slice 8.5 can cite canonical CI evidence instead of de facto evidence.
- No GT-KB files outside `bridge/`/governed evidence are changed by the
  proposal phase.
- No destructive git operation is performed without explicit owner approval.

## Test And Verification Plan

Pre-implementation, non-mutating checks:

```powershell
git remote -v
git ls-remote https://github.com/mike-remakerdigital/agent-red.git
git ls-remote https://github.com/Remaker-Digital/agent-red-customer-engagement.git
git merge-base <canonical/develop> <de-facto/develop>
git rev-list --left-right --count <canonical/develop>...<de-facto/develop>
```

Post-migration verification:

- canonical GitHub Actions runs for required workflows;
- `gh run list` evidence bound to repository, branch, event, workflow, and
  head SHA;
- local smoke tests if a local Agent Red checkout is available and explicitly
  selected as the work subject.

## Out Of Scope

- Production deployment.
- Credential rotation.
- Treating Agent Red source files as GT-KB files.
- Force-pushing without explicit owner approval.
- Publishing `v0.7.0-rc1` before Slice 8.5 and the canonical evidence gate are
  satisfied.

## Owner Action Boundaries

This proposal can be reviewed without owner input. Actual migration may require
owner approval if it needs repository administration, branch protection changes,
force-push, or secrets/workflow configuration.

## Prime Builder Recommendation

Proceed after Loyal Opposition `GO` with a read-only migration inventory first.
Only after the inventory is reviewed should Prime Builder perform any external
repository mutation.

