NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-rc1-canonical-ci-closure
author_model: GPT-5 Codex
author_model_version: 2026-06-02 runtime
author_model_configuration: Codex desktop, Default mode, danger-full-access, approval-policy never
author_model_context_window: not exposed by current harness
author_metadata_source: explicit Codex helper invocation

bridge_kind: implementation_proposal
Document: gtkb-rc1-canonical-ci-closure
Project Authorization: PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH
Project: PROJECT-GTKB-ISOLATION-CLOSEOUT
Work Item: GTKB-ISOLATION-017
target_paths: ["github:mike-remakerdigital/agent-red:.github/workflows/security-scan.yml", "memory/release-readiness.md", "bridge/gtkb-rc1-canonical-ci-closure-*.md"]

# Implementation Proposal - v0.7.0-rc1 Canonical CI Closure

## Summary

The `v0.7.0-rc1` tag authorization gate remains closed because canonical Agent Red repository migration and canonical CI-green evidence are not yet accepted. The canonical Agent Red repository is `mike-remakerdigital/agent-red`; the observed canonical `develop` head for this proposal is `1817db07d8308ffe9730119d26a2019457b98c9f`.

On that head, Lint, Release Candidate Gate, Python Tests, SonarCloud, and Chromatic succeeded. Security Scan run `25468949018` failed because Docker Hub login returned `unauthorized: incorrect username or password` and Dependency Audit reported `pip 26.0.1` vulnerable to `CVE-2026-6357`, fixed in `26.1`.

This proposal implements only the code/config portion Codex can safely own: update canonical Agent Red Security Scan so Dependency Audit upgrades pip to a fixed `26.1+` range before installing/running `pip-audit`, preserving the existing scoped `CVE-2026-3219` waiver and Docker Scout fail-closed behavior. Tag creation remains out of scope.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not add, expose, request, or transform credential values; cite only secret names and fail closed when Docker Hub authentication remains invalid. | Bridge helper credential scan, Agent Red PR diff review, and release evidence review with no credential values in output. |  |
| CQ-PATHS-001 | Yes | Keep GT-KB artifacts under `E:\GT-KB`; apply the workflow change only through a separate canonical Agent Red branch and PR. | GT-KB diff review plus GitHub PR changed-files review for only `.github/workflows/security-scan.yml`. |  |
| CQ-COMPLEXITY-001 | Yes | Use a single workflow setup command before `pip-audit`; avoid new helper programs, branching logic, or release-process rewrites. | Agent Red PR diff review confirms one narrow workflow setup change. |  |
| CQ-CONSTANTS-001 | Yes | Use the explicit range `pip>=26.1,<27` near the audit step with the existing CVE waiver unchanged. | Dependency Audit result no longer reports `CVE-2026-6357`, and diff review confirms `CVE-2026-3219` remains the only pip-audit waiver. |  |
| CQ-SECURITY-001 | Yes | Preserve Docker Scout, preserve the scoped `CVE-2026-3219` waiver, and keep unwaived vulnerabilities fail-closed. | Security Scan run evidence plus workflow diff review. |  |
| CQ-DOCS-001 | Yes | Record rationale in this proposal, the Agent Red PR body, GT-KB release-readiness evidence, and the post-implementation report. | Loyal Opposition review of proposal and post-implementation report. |  |
| CQ-TESTS-001 | Yes | Use canonical GitHub Actions as the authoritative verification surface for Agent Red and bridge preflights for GT-KB governance. | `gh run view` evidence for required workflows on the accepted canonical head plus bridge preflight commands. |  |
| CQ-LOGGING-001 | Yes | Leave GitHub Actions logging behavior unchanged; no new log capture or masking logic is introduced. | Agent Red PR diff review confirms no logging surface changes. |  |
| CQ-VERIFICATION-001 | Yes | Capture canonical CI run IDs, statuses, conclusions, repo, branch, event, and head SHA before release-readiness closure. | Post-implementation report records exact `gh run view` commands and observed results. |  |

## Scope

In GT-KB:

- File this bridge proposal and insert the corresponding `NEW` entry in `bridge/INDEX.md`.
- After Loyal Opposition `GO` and canonical CI success, update `memory/release-readiness.md` with canonical CI evidence.
- File a post-implementation report and wait for Loyal Opposition `VERIFIED` before declaring tag authorization ready.

In canonical Agent Red:

- Create branch `codex/rc1-security-scan-canonical-ci` from the latest canonical `develop` head at execution time.
- Change only `.github/workflows/security-scan.yml`.
- Add `python -m pip install --upgrade "pip>=26.1,<27"` before installing/running `pip-audit` in Dependency Audit.
- Preserve `pip-audit --ignore-vuln CVE-2026-3219`, Docker Scout, and fail-closed unwaived vulnerabilities.
- Open a draft PR for review and canonical CI evidence.

Out of scope: no `v0.7.0-rc1` tag, no production deployment, no credential lifecycle handling, no Docker Scout weakening, no de facto evidence substitution, no Agent Red source copied into GT-KB, and no unrelated dirty-tree cleanup.

## Specification Links

- `.claude/rules/codex-review-gate.md` - requires Loyal Opposition `GO` before implementation, including configuration and repository-state changes.
- `.claude/rules/file-bridge-protocol.md` - defines the bridge lifecycle, latest-status authority, proposal, implementation report, and verification flow.
- `.claude/rules/project-root-boundary.md` - keeps GT-KB artifacts within `E:\GT-KB` and treats Agent Red as a separate external repository.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - live `bridge/INDEX.md` controls actionable bridge state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites governing specifications before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must map requirements to executed evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red is outside GT-KB and must not be treated as a live GT-KB application artifact.
- `GOV-STANDING-BACKLOG-001` - `GTKB-ISOLATION-017` is the tracked backlog authority for release closeout work.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness depends on governed testing and accepted evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes project authorization, project, and work item metadata.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` - the cited work item must belong to the cited active approved project authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable release evidence and blockers belong in governed artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - this work is represented as a bridge proposal, implementation report, and release-readiness update.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - failed canonical release CI is an artifact lifecycle trigger for corrective bridge work.
- `GOV-CODE-QUALITY-BASELINE-001` - this proposal carries the required code-quality baseline table and verification plan.

## Requirement Sufficiency

Existing requirements sufficient. The owner plan, active project authorization, `GTKB-ISOLATION-017`, release-readiness blocker state, and cited governance specs are enough for this narrow canonical CI unblock. No new or revised requirement is needed before Loyal Opposition review.

## Project Authorization

- Authorization: `PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH`
- Project: `PROJECT-GTKB-ISOLATION-CLOSEOUT`
- Work item: `GTKB-ISOLATION-017`
- Allowed mutation classes used after `GO`: scoped external workflow configuration branch/PR, release-readiness evidence update, post-implementation bridge report.
- Forbidden operations avoided: release tag creation, production deployment, credential lifecycle handling, Docker Scout weakening, de facto repository substitution, unrelated dirty-tree cleanup.

## Owner Decisions / Input

- Current owner direction: implement the `v0.7.0-rc1 Canonical CI Unblock Plan` as the shortest governed path to reopen tag authorization without creating the tag.
- Existing project authorization: `PAUTH-PROJECT-GTKB-ISOLATION-CLOSEOUT-ISOLATION-CLOSEOUT-BATCH` covers `GTKB-ISOLATION-017` under `PROJECT-GTKB-ISOLATION-CLOSEOUT`.
- Release constraint preserved: tag creation remains out of scope until separate explicit owner authorization after evidence closure.
- Credential lifecycle boundary preserved: if Docker Hub authentication remains invalid after the pip audit fix, Codex stops with a release-blocked owner-action notice and does not request or handle secret values.

## Prior Deliberations

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` - active release path and `v0.7.0-rc1` target framing.
- `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` - Slice 8 disposition context for release closeout.
- `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` - transient CI evidence exception context, retained as historical evidence only.
- `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` - prior pause and CI-red handling for release authorization.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - canonical Agent Red repository migration prerequisite.
- `DELIB-S330-SLICE-8-6-ROW-42-PIP-CVE-CHOICE` - dependency-audit CVE disposition context.
- `DELIB-S330-SLICE-8-6-ROW-43-DOCKER-SCOUT-WAIVER` - Docker Scout waiver boundary context.
- Slice 8, Slice 8.5, Slice 8.6, and `agent-red-repo-migration-001` bridge evidence remain historical context; this proposal does not rely on de facto evidence as canonical release evidence.

## Implementation Plan

1. Wait for Loyal Opposition `GO` on this proposal before touching Agent Red or release-readiness evidence.
2. In canonical Agent Red, create branch `codex/rc1-security-scan-canonical-ci` from latest canonical `develop`.
3. Update only `.github/workflows/security-scan.yml` so Dependency Audit upgrades pip with `python -m pip install --upgrade "pip>=26.1,<27"` before installing/running `pip-audit`.
4. Open a draft PR in `mike-remakerdigital/agent-red` and confirm the diff preserves Docker Scout and the scoped `CVE-2026-3219` waiver.
5. Collect PR evidence proving Dependency Audit no longer reports `CVE-2026-6357` and unwaived vulnerabilities remain fail-closed.
6. After merge or accepted canonical head, collect required canonical workflow evidence for Lint, Release Candidate Gate, SonarCloud, Security Scan, and Python Tests on the same canonical head.
7. Prefer push-event evidence; if path filters skip a required workflow, run `workflow_dispatch` on the same head and record the event type explicitly.
8. Update `memory/release-readiness.md` with canonical CI evidence while preserving de facto green evidence only as historical transient-exception evidence.
9. File a post-implementation report and require Loyal Opposition `VERIFIED` before declaring tag authorization ready.

## Specification-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md`: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-rc1-canonical-ci-closure` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-rc1-canonical-ci-closure` after filing; expected result is no blocking proposal-spec gaps.
- `.claude/rules/codex-review-gate.md`: run `python scripts/implementation_authorization.py begin --bridge-id gtkb-rc1-canonical-ci-closure` only after latest bridge status is `GO`; expected result is an implementation authorization packet before external repo mutation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: review GT-KB diffs and Agent Red PR changed files; expected result is GT-KB artifacts under `E:\GT-KB` and the Agent Red change isolated to `.github/workflows/security-scan.yml` in the canonical repo.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`: use `gh run view <run-id> --repo mike-remakerdigital/agent-red --json status,conclusion,headSha,headBranch,event,url,name,databaseId` for required workflows on the accepted canonical head; expected result is `status=completed`, `conclusion=success`, matching repo, branch, and head SHA.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: carry all linked specs, exact commands, run IDs, observed results, and spec-to-test mapping into the post-implementation report; expected result is Loyal Opposition can issue `VERIFIED` without relying on unstated evidence.
- `GOV-CODE-QUALITY-BASELINE-001`: review the Agent Red PR diff and Security Scan evidence; expected result is no credential exposure, no Docker Scout weakening, no unscoped waiver, and no new unrelated complexity.

## Acceptance Criteria

- Bridge proposal is filed as `NEW` and receives Loyal Opposition `GO` before implementation starts.
- Agent Red PR changes only `.github/workflows/security-scan.yml` on branch `codex/rc1-security-scan-canonical-ci`.
- Dependency Audit no longer reports `CVE-2026-6357` after pip is upgraded to a fixed range.
- Docker Scout remains enabled and fail-closed; if Docker Hub authentication remains invalid, the release stays blocked without Codex requesting or handling credentials.
- Required canonical workflows are collected on the same accepted canonical head with completed successful conclusions, or explicitly recorded workflow-dispatch evidence on that head when push path filters skip a required workflow.
- `memory/release-readiness.md` records canonical CI evidence separately from historical de facto CI evidence.
- Post-implementation report receives Loyal Opposition `VERIFIED` before any claim that tag authorization is ready.
- `v0.7.0-rc1` is not created by this work.

## Pre-Filing Preflight

- Manual catch-22 check performed before filing: proposal text cites the bridge governance specs, release-readiness governance, project-root boundary, Agent Red isolation boundary, project-linkage specs, artifact lifecycle specs, and code-quality baseline triggered by the named target paths and release-unblock content.
- The Codex helper will run `.claude/hooks/bridge-compliance-gate.py --audit-only` against this in-memory content before writing `bridge/gtkb-rc1-canonical-ci-closure-001.md`.
- The compliance gate also runs the pending-proposal applicability preflight against a scratch content file before accepting the write.
- After filing, Prime Builder will run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-rc1-canonical-ci-closure` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-rc1-canonical-ci-closure`, then revise if either identifies a blocking gap.

## Risk And Rollback

Risk: the pip fix may unblock Dependency Audit while Docker Scout remains red because Docker Hub authentication is invalid. Mitigation: do not weaken Docker Scout and keep the release blocked with a credential-lifecycle owner-action notice if authentication remains invalid.

Risk: canonical workflow path filters may skip one or more required workflows on the accepted head. Mitigation: use `workflow_dispatch` on the same head and record event type explicitly.

Risk: stale de facto evidence could be mistaken for canonical release evidence. Mitigation: update release-readiness evidence with a separate canonical CI section and preserve de facto evidence only as historical transient-exception context.

Rollback: close the Agent Red PR or revert the one-line workflow change before merge if canonical CI behavior is worse. If the release-readiness evidence update is filed after merge and later invalidated, append a corrected bridge/report version rather than rewriting prior evidence. The tag is never created in this thread.

## Requested Review

Loyal Opposition should review whether this proposal is narrow enough to proceed to the Agent Red workflow PR, whether the canonical CI evidence plan is sufficient for release-readiness closure, and whether the Docker Hub credential boundary is correctly preserved.
