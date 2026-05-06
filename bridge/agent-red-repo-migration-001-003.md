REVISED

# Implementation Proposal (REVISED-1) - AGENT-RED-REPO-MIGRATION-001 Read-Only Migration Inventory

Author: Prime Builder (Codex, harness A)
Drafted: 2026-05-06
Type: Read-only migration inventory and release-evidence planning
Risk tier: Medium for inventory; high-risk external repository mutation is explicitly out of scope
Supersedes: `bridge/agent-red-repo-migration-001-001.md`
Addresses: Codex NO-GO at `bridge/agent-red-repo-migration-001-002.md`
Requested bridge disposition: `GO` for read-only inventory only

## Revision Summary

This revision addresses both blocking findings from Codex `-002`.

- F1: Adds a required `Owner Decisions / Input` section that enumerates the governing DELIB, its scope, expiry, residual risk, citation obligation, and authorization limits.
- F2: Narrows this proposal to read-only migration inventory. External repository mutation, branch protection changes, force-push, secrets/workflow configuration, and release tagging are out of scope and require a later owner-approved mutation plan.

## Background

Slice 8.6 surfaced a release-evidence gap: substantive CI evidence exists on the de facto Agent Red repository, while the owner-designated canonical Agent Red repository is `https://github.com/mike-remakerdigital/agent-red`.

The active transient exception `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` permits Slice 8.6 and Slice 8.5 verification to use de facto CI evidence while the migration is pending, but it explicitly does not authorize the `v0.7.0-rc1` tag. The tag remains gated on canonical migration and canonical CI binding.

This proposal creates the next safe step: produce a read-only inventory that makes the migration shape, risks, and owner-approval needs explicit before any repository mutation is attempted.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and registered in `bridge/INDEX.md`.
- `.claude/rules/file-bridge-protocol.md` - status semantics, proposal review, and post-implementation report requirements.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing bridge, owner-decision, root-boundary, release, and artifact lifecycle authorities.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - any inventory implementation report must map executed checks back to this proposal's acceptance criteria.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red is separate from GT-KB; inventory must not treat Agent Red source files as GT-KB artifacts.
- `.claude/rules/project-root-boundary.md` - all GT-KB artifacts produced by this work remain under `E:\GT-KB`; no Agent Red project files are created under GT-KB as live dependencies.
- `.claude/rules/canonical-terminology.md` - canonical project-resource alias handling and GT-KB / Agent Red terminology.
- `.claude/rules/project-resource-aliases.toml` - canonical external resource identity for Agent Red.
- `memory/project_external_resource_registry.md` - human-readable resource registry companion.
- `memory/feedback_groundtruth_kb_canonical_project_urls.md` - canonical URL discipline.
- `GOV-ARTIFACT-APPROVAL-001` - any later mutation or waiver artifact requiring owner approval must use the formal approval path.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - owner-approved transient exception and migration prerequisite.
- `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-008.md` - NO-GO that required durable exception and canonical CI correction.
- `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-009.md` - revised Slice 8.6 report citing the active exception.
- Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Owner Decisions / Input

Owner-decision evidence relied on by this proposal:

- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` records the owner-approved transient exception after Codex `-008`.
- Scope: Slice 8.6 and Slice 8.5 may cite de facto Agent Red CI evidence from `Remaker-Digital/agent-red-customer-engagement` while canonical migration is pending.
- Expiry: the exception expires only after the migration thread reaches `VERIFIED`, equivalent canonical CI evidence is captured on `mike-remakerdigital/agent-red`, and Slice 8.5 reaches `VERIFIED` on canonical evidence.
- Residual risk: de facto CI may diverge from canonical post-migration CI; repository identity confusion remains possible; migration complexity may delay rc1.
- Citation obligation: Slice 8.6 / Slice 8.5 artifacts using de facto CI evidence must cite the DELIB by full ID.

What this proposal asks Codex to approve:

- Read-only inspection of configured remotes and public/authorized remote metadata.
- Non-destructive local analysis of already-available or fetched git object metadata when needed to compute commit graph facts.
- A post-implementation inventory report in the same bridge thread.

What this proposal does not ask Codex or the owner to approve:

- Pushing, force-pushing, merging, rebasing, cherry-picking, or tagging in any external repository.
- Changing GitHub repository settings, branch protection, workflow secrets, environments, or deployment configuration.
- Treating Agent Red source files as live GT-KB artifacts.
- Creating `v0.7.0-rc1`.
- Accepting canonical CI before it actually runs on `mike-remakerdigital/agent-red`.

## Proposed Scope

Produce a read-only migration inventory that answers:

1. Repository identity:
   - canonical repository URL and develop head;
   - de facto repository URL and develop head;
   - local GT-KB remote configuration relevant to those external resources.
2. Commit-graph shape:
   - common ancestor if computable from local or fetched metadata;
   - de facto-ahead and canonical-ahead counts;
   - whether a fast-forward, clean merge, or cherry-pick path appears viable.
3. Workflow and release-evidence shape:
   - required workflow names for Slice 8.5 / Slice 8.6 evidence;
   - whether equivalent workflow files appear present on canonical and de facto heads;
   - the de facto run IDs currently accepted only under the transient exception.
4. Conflict and risk inventory:
   - path-level categories likely to conflict;
   - Dependabot or dependency-update commits requiring disposition;
   - security scan and secrets-gate implications.
5. Follow-on approval plan:
   - exact external mutations likely required;
   - owner approvals required before those mutations;
   - proposed sequencing to reach canonical CI evidence without weakening the bridge semantics.

## Explicit Out Of Scope

- No external repository writes.
- No force-push.
- No branch protection or repository settings changes.
- No secrets, environments, or credential changes.
- No production deployment.
- No release tag.
- No migration commit, merge, rebase, cherry-pick, or PR creation.
- No copying Agent Red source files into GT-KB as live project files.

## Permitted Read-Only Procedures

The implementation may use commands equivalent to:

```powershell
git remote -v
git ls-remote --heads https://github.com/mike-remakerdigital/agent-red.git
git ls-remote --heads https://github.com/Remaker-Digital/agent-red-customer-engagement.git
git show --no-patch --format=fuller <sha>
git merge-base <canonical-ref-or-sha> <de-facto-ref-or-sha>
git rev-list --left-right --count <canonical-ref-or-sha>...<de-facto-ref-or-sha>
git diff --name-status --find-renames <canonical-ref-or-sha>...<de-facto-ref-or-sha>
```

If fresh object metadata is required, the implementation may fetch remote-tracking refs or a temporary analysis ref into local git metadata, provided it records the command and does not push or alter external repositories. Any temporary local analysis ref must be named as temporary and removed or clearly reported before the implementation report is filed.

## Acceptance Criteria

- The inventory report identifies canonical and de facto repository URLs and develop heads.
- The inventory report records whether common ancestor and ahead/behind counts were computable, with exact commands and observed outputs.
- The inventory report separates facts from recommendations.
- The inventory report lists migration options without selecting or executing an external mutation path.
- The inventory report identifies owner approvals required for each mutation option.
- The inventory report states whether Slice 8.5 can proceed under the transient exception before canonical migration completes.
- The inventory report confirms no external repository writes were performed.
- The inventory report confirms no Agent Red source files were added to GT-KB.

## Specification-Derived Verification Plan

| Test ID | Spec coverage | Procedure | Pass condition |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify `bridge/INDEX.md` latest entry for this thread points to the post-implementation inventory report | Latest entry is correct |
| T-preflight-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id agent-red-repo-migration-001` | `preflight_passed: true`, `missing_required_specs: []` |
| T-owner-1 | Owner Decisions / Input gate | Inspect the report for DELIB scope, expiry, residual risk, citation obligation, and authorization limits | Non-empty section with the required fields |
| T-boundary-1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, project root boundary | `git diff --name-only -- bridge/INDEX.md bridge/agent-red-repo-migration-001-*.md` plus implementation notes | Only GT-KB bridge/report artifacts changed; no Agent Red source copied into GT-KB |
| T-readonly-1 | External mutation separation | Review command log for `push`, `tag`, branch-protection, settings, secrets, or deployment operations | No external write operation present |
| T-inventory-1 | Acceptance criteria | Review inventory tables for repo heads, commit graph, workflow shape, conflict/risk categories, and follow-on approvals | All required inventory sections present |

## Prime Builder Recommendation

Approve this read-only inventory proposal. Do not approve repository mutation in this thread. After the inventory report is reviewed, file a separate mutation proposal or owner-action approval packet for the exact migration strategy.

