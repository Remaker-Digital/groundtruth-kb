GO
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: keep-working-2026-06-02T14-08Z-lo
author_model: GPT-5
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; dual-role authority active
author_metadata_source: explicit automation environment

# Loyal Opposition Review - RC1 PyJWT Dependency Audit Remediation - 002

bridge_kind: lo_verdict
Document: gtkb-rc1-pyjwt-dependency-audit-remediation
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-02 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-rc1-pyjwt-dependency-audit-remediation-001.md

## Verdict

GO.

The proposal is a narrow release-blocker remediation for the current Agent Red PR-head dependency audit failures. It raises only the `PyJWT` floor from `>=2.9.0` to `>=2.13.0`, keeps Docker Scout enabled and fail-closed, does not request or handle credentials, does not add vulnerability waivers, does not merge PR #124, and does not create `v0.7.0-rc1`.

Implementation may proceed only within the target scope in `-001`: canonical Agent Red `requirements.txt`, GT-KB `memory/release-readiness.md` evidence, and this bridge thread. No unrelated dependency upgrades are approved.

## Applicability Preflight

- command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-rc1-pyjwt-dependency-audit-remediation`
- exit: 0
- packet_hash: `sha256:8ca5c0702e00bbeb872c0f33a47666d74290d5721c87a2d40d85103ed7cf99c3`
- preflight_passed: true
- warnings.missing_parent_dirs: [`github:mike-remakerdigital/agent-red:requirements.txt`]
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-rc1-pyjwt-dependency-audit-remediation`
- exit: 0
- clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0

## Prior Deliberations

- `DELIB-S327-RELEASE-PATH-CLEAN-ADOPTER-PRODUCTIZATION` - active release path and `v0.7.0-rc1` target framing.
- `DELIB-S330-ISOLATION-017-SLICE8-DISPOSITION-CHOICE` - release closeout context.
- `DELIB-S330-RC1-CI-RED-PAUSE-AND-SLICE-8-6-DISPOSITION` - prior RC1 CI-red handling.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` - canonical Agent Red repository boundary.
- `DELIB-S330-SLICE-8-6-ROW-42-PIP-CVE-CHOICE` - earlier dependency-audit CVE handling pattern: fix audit environment rather than weakening the audit.
- `DELIB-S330-SLICE-8-6-ROW-43-DOCKER-SCOUT-WAIVER` - Docker Scout waiver boundary and fail-closed context.
- Deliberation searches for `PyJWT dependency audit release candidate Agent Red` and `RC1 dependency audit Docker Scout PyJWT` returned no more-specific PyJWT owner decision that changes this scope.

## Evidence Reviewed

- `bridge/gtkb-rc1-pyjwt-dependency-audit-remediation-001.md` full proposal.
- `bridge/gtkb-rc1-canonical-ci-closure-003.md` blocked implementation report identifying the PyJWT failures.
- GitHub PR #124 metadata for `mike-remakerdigital/agent-red`: open draft, one changed file, two additions, one deletion, head `ea632196b0f2cbcb73589aafb40c1072a14c3d65`.
- GitHub PR #124 diff: changes only `.github/workflows/security-scan.yml` for the prior pip audit setup.
- Agent Red branch `codex/rc1-security-scan-canonical-ci` `requirements.txt`: current line is `PyJWT>=2.9.0`.
- `scripts/bridge_proposal_pattern_lint.py --bridge-id gtkb-rc1-pyjwt-dependency-audit-remediation`: 0 findings.

## Specifications Carried Forward

- `.claude/rules/codex-review-gate.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/project-root-boundary.md`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-CODE-QUALITY-BASELINE-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `show_thread_bridge.py gtkb-rc1-pyjwt-dependency-audit-remediation --format json --preview-lines 160` | yes | Latest `NEW`; drift `[]`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-rc1-pyjwt-dependency-audit-remediation` | yes | Exit 0; no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Proposal verification plan review plus clause preflight | yes | Spec-derived verification plan maps CI audit evidence and post-implementation report requirements. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-rc1-pyjwt-dependency-audit-remediation` | yes | Exit 0; no blocking gaps. |
| `GOV-CODE-QUALITY-BASELINE-001` | Code-quality baseline table plus proposal pattern lint | yes | Baseline table present; pattern lint found 0 issues. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | GitHub PR/head evidence review | yes | Proposal requires same-head Release Candidate Gate and Security Scan evidence before closure; no tag authorization granted here. |

## Implementation Constraints

- Before mutating, Prime must mint an implementation authorization packet for `gtkb-rc1-pyjwt-dependency-audit-remediation`.
- Change only Agent Red `requirements.txt` from `PyJWT>=2.9.0` to `PyJWT>=2.13.0`.
- Preserve existing Security Scan waivers exactly; do not add PyJWT waivers.
- Preserve Docker Scout enabled and fail-closed.
- Do not request, display, rotate, transform, or upload credential values.
- Do not merge PR #124, mark it ready, create `v0.7.0-rc1`, or claim release readiness from this GO alone.
- If same-head CI reveals additional blockers, record them as residual blockers or file separate bridge work rather than broadening this patch silently.

## Findings

No blocking findings.

## Owner Action Required

No owner action required for this GO. Docker Hub credential lifecycle remains outside Codex scope if Docker Scout authentication remains blocked after the PyJWT remediation.
