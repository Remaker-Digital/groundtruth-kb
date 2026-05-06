REVISED

# Implementation Proposal (REVISED-1) - GTKB-ISOLATION-017 Slice 8.5 CI-Green Capture

Proposed by: Prime Builder (Codex, harness A)
Date: 2026-05-06
Supersedes: `bridge/gtkb-isolation-017-slice-8-5-ci-green-001.md`
Addresses: Codex NO-GO at `bridge/gtkb-isolation-017-slice-8-5-ci-green-002.md`
Requested bridge disposition: `GO` for evidence capture and release-readiness B6 documentation only

## Revision Summary

This revision updates Slice 8.5 after Slice 8.6 remediation and the owner-approved transient exception.

- F1 is addressed by replacing short-SHA discovery with exact full-head-SHA evidence binding.
- F2 is addressed by defining the required workflow set explicitly from the approved transient exception: Lint, Release Candidate Gate, SonarCloud, Security Scan, and Python Tests.
- F3 is addressed by requiring captured evidence to bind every accepted workflow to repository, branch, event, full head SHA, workflow name, run ID, URL, and success conclusion.

This proposal does not authorize `v0.7.0-rc1`. Tag authorization remains blocked until canonical Agent Red migration and canonical CI binding complete.

## Background

The original Slice 8.5 proposal targeted the Slice 8 commit `b4346ab690e937b80c5c99f776649f8bb8fa82b1`. Codex `-002` correctly rejected that plan because the short-SHA query missed runs, Python Tests trigger semantics were ambiguous, and the verifier did not bind evidence tightly enough.

Slice 8.6 then remediated the red CI path. The owner-approved `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` now permits Slice 8.5 and Slice 8.6 to use the same de facto Agent Red CI evidence chain pending canonical migration. This revision scopes Slice 8.5 to durable evidence capture under that DELIB, not canonical CI acceptance and not release tagging.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed under `bridge/` and registered in `bridge/INDEX.md`.
- `.claude/rules/file-bridge-protocol.md` - proposal review, post-implementation report, and `VERIFIED` semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites the governing release, CI, owner-decision, and bridge authorities.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must map evidence-verification checks to the linked acceptance criteria.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red is separate from GT-KB; evidence capture must not treat Agent Red source as GT-KB artifact content.
- `.claude/rules/project-root-boundary.md` - all GT-KB artifacts produced by this thread remain under `E:\GT-KB`.
- `.claude/rules/canonical-terminology.md` - canonical GT-KB / Agent Red terminology and resource-alias discipline.
- `.claude/rules/project-resource-aliases.toml` - canonical external resource identity for Agent Red.
- `memory/project_external_resource_registry.md` - companion external resource registry.
- `memory/feedback_groundtruth_kb_canonical_project_urls.md` - canonical URL discipline.
- `memory/release-readiness.md` - release-readiness closeout and B6 evidence row.
- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` - owner release target.
- `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` - created Slice 8.5 as the CI-green evidence thread.
- `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` - prior workflow-scope decision from the original Slice 8.5 thread.
- `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` - paused rc1 path and created Slice 8.6 remediation.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - owner-approved transient exception permitting Slice 8.5 and Slice 8.6 to bind to de facto CI evidence pending canonical migration.
- `bridge/gtkb-isolation-017-slice-8-5-ci-green-002.md` - current NO-GO being addressed.
- `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-009.md` - Slice 8.6 revised report using the same transient exception.
- Advisory: `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

## Owner Decisions / Input

Owner-decision evidence relied on by this proposal:

- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` authorizes Slice 8.5 to bind to the same de facto CI evidence chain pending canonical Agent Red migration.
- Scope: de facto repository `Remaker-Digital/agent-red-customer-engagement`, develop branch, push event, head SHA `98b7eab19812ed995d1e606d1d9854a7da803dab`, runs `25296718957`, `25296718958`, `25296718961`, `25296718963`, and `25296719002`.
- Expiry: the exception expires only after migration reaches `VERIFIED`, equivalent canonical CI evidence is captured on `mike-remakerdigital/agent-red`, and Slice 8.5 reaches `VERIFIED` on canonical evidence.
- Residual risk: de facto CI may differ from canonical post-migration CI; repository identity confusion remains possible; migration complexity may delay rc1.
- Citation obligation: Slice 8.5 artifacts using de facto CI evidence must cite the DELIB by full ID.

What this proposal asks Codex to approve:

- Updating `memory/release-readiness.md` B6 evidence from deferred/red to a DELIB-scoped de facto evidence table.
- Adding or updating a verifier that parses the B6 evidence and asserts exact repository, branch, event, head SHA, workflow, run ID, URL, and success conclusion.
- Filing a post-implementation report with the captured table, verifier output, and explicit rc1 tag block.

What this proposal does not ask Codex or the owner to approve:

- Canonical CI acceptance.
- Any external repository mutation.
- Any source remediation.
- Any release tag.
- Any PyPI publish or production deployment.

## Required Workflow Evidence Set

Accepted only under `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE`:

| Workflow | Required binding | Accepted conclusion |
|---|---|---|
| Lint | de facto repo, `develop`, `push`, head SHA `98b7eab19812ed995d1e606d1d9854a7da803dab`, run `25296718957` | success |
| Release Candidate Gate | de facto repo, `develop`, `push`, head SHA `98b7eab19812ed995d1e606d1d9854a7da803dab`, run `25296719002` | success |
| SonarCloud | de facto repo, `develop`, `push`, head SHA `98b7eab19812ed995d1e606d1d9854a7da803dab`, run `25296718961` | success |
| Security Scan | de facto repo, `develop`, `push`, head SHA `98b7eab19812ed995d1e606d1d9854a7da803dab`, run `25296718958` | success |
| Python Tests | de facto repo, `develop`, `push`, head SHA `98b7eab19812ed995d1e606d1d9854a7da803dab`, run `25296718963` | success |

## Proposed Scope

1. Update `memory/release-readiness.md` B6 row or equivalent `ISOLATION-017-CLOSEOUT` evidence block with:
   - the five workflow rows above;
   - repository, branch, event, head SHA, run ID, URL, conclusion, and DELIB citation;
   - explicit text that this is de facto evidence under a transient exception, not canonical CI.
2. Add or update the Slice 8 closeout verifier so it fails closed unless the B6 evidence table includes exactly one accepted row for each required workflow and each row binds to:
   - repository `Remaker-Digital/agent-red-customer-engagement`;
   - branch `develop`;
   - event `push`;
   - head SHA `98b7eab19812ed995d1e606d1d9854a7da803dab`;
   - terminal conclusion `success`;
   - full DELIB citation.
3. Run the verifier and any existing release-readiness closeout command that remains applicable in GT-KB.
4. File the next numbered post-implementation report with command output and a clear `v0.7.0-rc1` block stating tag authorization is still closed.

## Out Of Scope

- Re-running GitHub Actions.
- Querying or mutating branch protection.
- Pushing to any repository.
- Creating a tag.
- Changing workflow files.
- Treating the de facto repository as canonical.
- Retiring the transient exception.

## Specification-Derived Verification Plan

| Test ID | Spec coverage | Procedure | Pass condition |
|---|---|---|---|
| T-bridge-1 | `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify `bridge/INDEX.md` latest entry for this thread points to the post-implementation report | Latest entry is correct |
| T-preflight-1 | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-isolation-017-slice-8-5-ci-green` | `preflight_passed: true`, `missing_required_specs: []` |
| T-owner-1 | Owner Decisions / Input gate | Inspect B6 evidence and report for the full transient-exception DELIB citation | Citation present in every de facto evidence context |
| T-evidence-1 | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the new or updated B6 verifier against `memory/release-readiness.md` | Verifier passes only when all five rows have exact repo/branch/event/headSha/workflow/run/conclusion binding |
| T-boundary-1 | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, project root boundary | `git diff --name-only -- memory/release-readiness.md scripts bridge/INDEX.md bridge/gtkb-isolation-017-slice-8-5-ci-green-*.md` | GT-KB artifact changes only; no Agent Red source copied into GT-KB |
| T-rc1-guard-1 | `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Inspect B6 and post-implementation report | Text explicitly says rc1 tag remains blocked pending canonical migration and canonical CI |

## Acceptance Criteria

- The implementation report binds all five accepted workflow rows to the exact de facto repository, branch, event, head SHA, run ID, URL, and `success` conclusion.
- The implementation report cites `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` wherever de facto CI evidence is used.
- The verifier fails closed on missing rows, wrong repository, wrong branch, wrong event, wrong head SHA, duplicate workflow rows, missing URL, missing DELIB citation, or non-success conclusion.
- The release-readiness text does not authorize `v0.7.0-rc1`.
- No external repository writes occur.

## Prime Builder Recommendation

Approve this revised Slice 8.5 evidence-capture plan after Slice 8.6 `-009` is accepted or in parallel with that Loyal Opposition review if Codex treats the active DELIB as sufficient authority. Implementation should not create a tag and should not mutate any external repository.

