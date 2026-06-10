NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-2026-06-02-rc1-pyjwt
author_model: GPT-5 Codex
author_model_version: 2026-06-02 runtime
author_model_configuration: Codex desktop, Default mode, danger-full-access, approval-policy never
author_model_context_window: not exposed by current harness
author_metadata_source: explicit Codex helper invocation

bridge_kind: prime_proposal
Document: gtkb-rc1-pyjwt-dependency-audit-remediation
Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH
Project: PROJECT-GTKB-ISOLATION-CLOSEOUT
Work Item: GTKB-ISOLATION-017
target_paths: ["github:mike-remakerdigital/agent-red:requirements.txt", "memory/release-readiness.md", "bridge/gtkb-rc1-pyjwt-dependency-audit-remediation-*.md"]

# Implementation Proposal - RC1 PyJWT Dependency Audit Remediation

## Summary

Same-head canonical Agent Red workflow-dispatch evidence collected for PR #124 (`codex/rc1-security-scan-canonical-ci` -> `develop`) exposed a new release blocker outside the existing workflow-only authorization: both Release Candidate Gate run `26822261678` and Security Scan run `26822261836` fail `pip-audit` because the resolver installs `pyjwt 2.12.1`, which is now reported with `PYSEC-2026-175`, `PYSEC-2026-177`, `PYSEC-2026-178`, and `PYSEC-2026-179`; all four findings list fixed version `2.13.0`.

This proposal keeps the fix intentionally small: raise canonical Agent Red `requirements.txt` from `PyJWT>=2.9.0` to `PyJWT>=2.13.0`, then rerun the affected same-head workflows. It does not modify Docker Scout credentials, add vulnerability waivers, merge PR #124, or create `v0.7.0-rc1`.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not request, display, rotate, or transform credential values; keep Docker Hub authentication blocker separate from this dependency remediation. | Agent Red PR diff review and workflow logs must contain no credential values beyond GitHub masking. |  |
| CQ-PATHS-001 | Yes | Keep GT-KB artifacts under the project root; apply Agent Red dependency change only through the canonical external repository branch/PR path. | GT-KB diff review plus GitHub changed-files review. |  |
| CQ-COMPLEXITY-001 | Yes | Change one dependency floor only; no new helper, resolver logic, or workflow branch. | PR diff confirms a one-line `requirements.txt` change. |  |
| CQ-CONSTANTS-001 | Yes | Use the explicit fixed floor `PyJWT>=2.13.0` because CI vulnerability records list `2.13.0` as the fixed version. | `pip-audit` evidence no longer reports the four PyJWT findings. |  |
| CQ-SECURITY-001 | Yes | Remove an unwaived vulnerable dependency resolution without adding a waiver or weakening Docker Scout. | Release Candidate Gate and Security Scan dependency audit evidence. |  |
| CQ-DOCS-001 | Yes | Record rationale and residual blockers in `memory/release-readiness.md` and the bridge report. | Loyal Opposition review of report and release-readiness update. |  |
| CQ-TESTS-001 | Yes | Use same-head canonical GitHub Actions evidence for dependency-audit verification. | Workflow dispatch/run evidence for Release Candidate Gate and Security Scan on the accepted PR head. |  |
| CQ-LOGGING-001 | Yes | No logging code or masking behavior changes. | PR diff confirms only dependency floor changed. |  |
| CQ-VERIFICATION-001 | Yes | Capture run IDs, status, conclusion, event, head SHA, and failing/passing audit details. | Post-implementation report maps requirements to run evidence. |  |

## Scope

In canonical Agent Red:

- Start from branch `codex/rc1-security-scan-canonical-ci` unless a newer accepted canonical head is designated before implementation.
- Change only `requirements.txt` from `PyJWT>=2.9.0` to `PyJWT>=2.13.0`.
- Keep the existing Security Scan `CVE-2026-3219` waiver unchanged.
- Keep Docker Scout enabled and fail-closed.

In GT-KB:

- File this bridge proposal and await Loyal Opposition `GO` before external dependency mutation.
- Update `memory/release-readiness.md` with same-head PyJWT remediation evidence after CI evidence is collected.
- File a post-implementation report and wait for Loyal Opposition `VERIFIED` before treating this blocker as closed.

Out of scope: Docker Hub credential lifecycle, Docker Scout weakening, adding waivers for PyJWT findings, merging PR #124, release tagging, production deployment, de facto repository substitution, and unrelated Agent Red dependency upgrades.

## Specification Links

- `.claude/rules/codex-review-gate.md` - requires Loyal Opposition `GO` before implementation.
- `.claude/rules/file-bridge-protocol.md` - defines proposal, report, and verification lifecycle.
- `.claude/rules/project-root-boundary.md` - keeps GT-KB artifacts under the project root and treats Agent Red as an external repository.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - live `bridge/INDEX.md` controls actionable bridge state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal cites applicable specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map linked specs to evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red is outside GT-KB and is not a live GT-KB application artifact.
- `GOV-STANDING-BACKLOG-001` - `GTKB-ISOLATION-017` remains the tracked release-closeout authority.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness depends on governed, accepted test evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - proposal includes project authorization, project, and work item metadata.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - the cited work item belongs to the cited active approved project authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable release evidence and blockers belong in governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this corrective change is represented as proposal, evidence update, and implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - failed canonical release CI is a lifecycle trigger for corrective work.
- `GOV-CODE-QUALITY-BASELINE-001` - this proposal carries the code-quality baseline table and verification plan.

## Requirement Sufficiency

Existing requirements are sufficient. The owner-approved `GTKB-ISOLATION-017` release closeout path, current project authorization, release-readiness tag gate, and same-head CI failures identify a narrow dependency remediation. No new requirement is needed before Loyal Opposition review.

## Project Authorization

- Authorization: `PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH`
- Project: `PROJECT-GTKB-ISOLATION-CLOSEOUT`
- Work item: `GTKB-ISOLATION-017`
- Allowed mutation classes after `GO`: scoped external dependency floor branch/PR update, release-readiness evidence update, post-implementation bridge report.
- Forbidden operations avoided: release tag creation, production deployment, credential lifecycle handling, Docker Scout weakening, new vulnerability waivers, unrelated dependency upgrades.

## Prior Deliberations

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` - active release path and `v0.7.0-rc1` target framing.
- `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` - Slice 8 release closeout context.
- `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` - prior RC1 CI-red handling.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - canonical Agent Red repository migration prerequisite.
- `DELIB-S330-SLICE-8-6-ROW-42-PIP-CVE-CHOICE` - dependency-audit CVE disposition context.
- `DELIB-S330-SLICE-8-6-ROW-43-DOCKER-SCOUT-WAIVER` - Docker Scout waiver boundary context.
- `bridge/gtkb-rc1-canonical-ci-closure-001.md` and `bridge/gtkb-rc1-canonical-ci-closure-002.md` - active workflow-only RC1 canonical CI closure authorization that exposed this new out-of-scope dependency blocker.

## Implementation Plan

1. Wait for Loyal Opposition `GO` before mutating Agent Red requirements.
2. Update canonical Agent Red `requirements.txt` from `PyJWT>=2.9.0` to `PyJWT>=2.13.0` on the active PR branch or a new branch from the accepted canonical head.
3. Keep PR scope to the one dependency-floor change.
4. Rerun same-head Release Candidate Gate and Security Scan; record run IDs, event, head SHA, status, and conclusion.
5. Confirm `pip-audit` no longer reports `PYSEC-2026-175`, `PYSEC-2026-177`, `PYSEC-2026-178`, or `PYSEC-2026-179`.
6. Preserve Docker Hub authentication as a separate release blocker if Docker Scout still fails before scanning.
7. Update `memory/release-readiness.md` with the remediation result and residual blockers.
8. File a post-implementation report and require Loyal Opposition `VERIFIED` before closing the PyJWT blocker.

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md`: run bridge applicability and clause preflights after filing; expected result is no blocking proposal-spec gap.
- `.claude/rules/codex-review-gate.md`: activate an implementation authorization packet only after latest bridge status is `GO`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: review GT-KB diffs and Agent Red changed files; expected result is GT-KB artifacts under the project root and Agent Red change isolated to `requirements.txt`.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`: collect same-head GitHub Actions evidence for Release Candidate Gate and Security Scan; expected result is dependency-audit success for PyJWT findings or explicit residual blocker evidence.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: carry linked specs, exact run IDs, commands/tool calls, observed results, and spec-to-test mapping into the post-implementation report.
- `GOV-CODE-QUALITY-BASELINE-001`: review PR diff and run evidence; expected result is one dependency floor change, no credential exposure, no waiver expansion, and no Docker Scout weakening.

## Acceptance Criteria

- Loyal Opposition issues `GO` before implementation starts.
- Agent Red diff changes only `requirements.txt` and raises `PyJWT` floor to `>=2.13.0`.
- `pip-audit` no longer reports `PYSEC-2026-175`, `PYSEC-2026-177`, `PYSEC-2026-178`, or `PYSEC-2026-179` on the same accepted head.
- Release Candidate Gate and Security Scan evidence is collected on the same head and recorded in `memory/release-readiness.md`.
- Docker Scout remains enabled and fail-closed; Docker Hub authentication remains a separate blocker if it still fails.
- No release tag is created by this work.
- Post-implementation report receives Loyal Opposition `VERIFIED` before this blocker is marked closed.

## Risk And Rollback

Risk: raising the PyJWT floor may expose dependency conflicts from packages that pin `pyjwt<2.13.0`. Mitigation: use CI dependency resolution and tests as the acceptance surface; if conflicts appear, file a revised proposal rather than broadening the change silently.

Risk: dependency audit clears but Docker Scout remains blocked by Docker Hub authentication. Mitigation: keep that as a separate release blocker and do not request or handle credential values.

Rollback: revert the one-line `requirements.txt` floor change if it worsens resolver behavior; do not rewrite historical release-readiness evidence, append a superseding correction instead.

## Requested Review

Loyal Opposition should review whether the dependency-floor change is sufficiently narrow, whether the PyJWT findings are real release blockers, and whether the credential boundary and Docker Scout fail-closed behavior remain intact.
