REVISED

# Harness C Governance Gate Parity Gap - Revised Implementation Proposal

bridge_kind: implementation_proposal
Document: gtkb-harness-c-governance-gate-parity-gap
Version: 015
Responds-To: bridge/gtkb-harness-c-governance-gate-parity-gap-014.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-17 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-17T21-37-54Z-prime-builder-A-7ade2c
author_model: gpt-5-codex
author_model_version: 2026-06-17 runtime
author_model_configuration: Codex bridge auto-dispatch session; Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4543

target_paths: ["scripts/implementation_start_gate.py", ".githooks/pre-commit", ".githooks/setup-hooks.sh", "platform_tests/scripts/test_implementation_start_gate.py", "scripts/release_candidate_gate.py", "platform_tests/scripts/test_release_candidate_gate.py"]

implementation_scope: governance_hook_parity
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
protected_source_mutation_in_scope: true

## Summary

This revision responds to the latest Loyal Opposition `NO-GO` by replacing the
blocker-only record in version 013 with a concrete implementation proposal for
`WI-4543`.

The selected implementation adds a harness-agnostic Git pre-commit floor for
protected implementation mutations. The current Claude and Codex PreToolUse
paths can block protected edits in-session, but Harness C and other editors can
still stage protected source, test, hook, configuration, or narrative changes
without having executed those harness hooks. The tracked `.githooks/pre-commit`
hook already provides universal-floor checks for secrets, dev-environment
inventory drift, narrative-artifact evidence, ruff formatting, and PowerShell
syntax. This proposal extends that same tracked hook to run the existing
implementation-start authorization model against staged protected paths.

This is intentionally narrower than the original rules-sync proposal. It does
not attempt to create a separate Antigravity prompt/rules distribution path and
does not mutate Harness C runtime configuration. It adds a repository-level
commit barrier that applies regardless of which harness or editor produced the
staged change.

## Response To Latest NO-GO

Version 014 required Prime Builder to file a revised implementation proposal
that cites the active authorization and gives a real design, target paths, and
test plan. This proposal does that.

The active project authorization is:

- `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`
- `PROJECT-GTKB-MAY29-HYGIENE`
- `WI-4543`

Direct project membership readback confirmed `WI-4543` has active membership
`PWM-PROJECT-GTKB-MAY29-HYGIENE-WI-4543` under
`PROJECT-GTKB-MAY29-HYGIENE`. The `project_name` compatibility field on the
work-item row is not used as the project-membership authority for this proposal.

## Specification Links

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - implementation must not
  begin or proceed around the bridge GO and implementation-start packet.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge state and numbered files are the
  durable workflow authority.
- `GOV-FILE-BRIDGE-PROTOCOL-001` - bridge lifecycle and Prime/LO handoff
  protocol for proposals, GO/NO-GO, and verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - implementation
  proposals must include project authorization, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation
  proposals must cite concrete governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation reports
  must map linked specifications to executed tests.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - cross-harness bridge enforcement gaps
  must be represented honestly and closed with mechanical checks where possible.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization is
  additive owner/governance evidence, not a bridge bypass.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - project authorization scope must
  remain bounded to the linked project/work item and target paths.
- `GOV-STANDING-BACKLOG-001` - work item `WI-4543` is the durable backlog
  authority for the scoped defect.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decisions must be captured as durable
  evidence; this proposal relies on the project authorization deliberation.
- `GOV-SESSION-ROLE-AUTHORITY-001` - enforcement attaches to resolved role and
  harness state rather than transient chat assertions.
- `REQ-HARNESS-REGISTRY-001` - harness identity and role records are durable
  registry-backed surfaces used by bridge dispatch and implementation gates.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` - role resolution must read the
  canonical harness-state projection or `gt harness roles`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all live GT-KB artifacts remain
  under the mandatory project root boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - governance decisions and workflow
  findings are preserved as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - bridge proposals, review findings,
  and owner authorization evidence cross the capture threshold.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - implementation work must preserve
  durable traceability instead of relying on transient session claims.

## Prior Deliberations And Related Records

- `DELIB-20260614-ANTIGRAVITY-ADVISORY-REROUTE-AUTH` - owner approved routing
  the Antigravity protected-mutation incident back through the bridge.
- `DELIB-20263427` - owner decision that left the cross-harness project-linkage
  parity gap as a standing concern represented by `WI-4543`.
- `DELIB-20264113` - Loyal Opposition NO-GO on version 008, confirming
  `WI-4543` as the distinct Harness C governance-gate parity item.
- `DELIB-20264112` - Loyal Opposition NO-GO on version 010, confirming the
  prior authorization blocker.
- `DELIB-20264111` - Loyal Opposition NO-GO on version 012, confirming the
  prior authorization blocker.
- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - owner/governance
  authorization for all unimplemented work items linked to
  `PROJECT-GTKB-MAY29-HYGIENE`.
- `bridge/gtkb-harness-c-governance-gate-parity-gap-014.md` - latest Loyal
  Opposition verdict clearing Prime Builder to file this revised implementation
  proposal now that the project authorization exists.

## Owner Decisions / Input

No new owner input is requested or required in this headless dispatch run.

Carried-forward owner/governance evidence:

- `DELIB-20260614-ANTIGRAVITY-ADVISORY-REROUTE-AUTH` authorized rerouting the
  Antigravity protected-mutation incident through the bridge.
- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` authorized proposing
  implementation for all unimplemented work items linked to
  `PROJECT-GTKB-MAY29-HYGIENE`, including active member `WI-4543`.

## Requirement Sufficiency

Existing requirements sufficient.

The current governing requirements already require bridge GO, project
authorization metadata, implementation-start authorization packets, target-path
scoping, durable work-item authority, and specification-derived verification.
This proposal does not require a new specification before implementation.

## Implementation Design

1. Add a staged/pre-commit enforcement mode to
   `scripts/implementation_start_gate.py`.
   - The mode reads staged paths from
     `git diff --cached --name-only --diff-filter=ACMRT`.
   - It normalizes staged paths relative to the GT-KB project root and filters
     them through the existing `is_protected_path()` classifier.
   - It ignores allowed bridge/runtime paths already exempted by the existing
     gate model, including `bridge/` and `.gtkb-state/`.
   - When no protected implementation paths are staged, it exits successfully.
   - When protected paths are staged, it validates those exact paths with the
     existing implementation authorization packet and work-intent claim checks.
   - On failure, it prints the same `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
     blocker family with the staged protected paths that caused the denial and
     exits non-zero.

2. Register the staged gate in `.githooks/pre-commit`.
   - Invoke `"$PYTHON_BIN" scripts/implementation_start_gate.py --staged`.
   - Place it before later quality-only checks so unauthorized protected
     mutations fail at the governance boundary first.
   - Preserve the existing secret scan, dev-environment drift, narrative
     artifact evidence, ruff format, and PowerShell syntax checks.

3. Update `.githooks/setup-hooks.sh` messaging so developers and harnesses see
   that the tracked pre-commit hook now includes implementation-start
   authorization enforcement.

4. Update release-candidate gate validation in `scripts/release_candidate_gate.py`
   so release-readiness checks fail when `.githooks/pre-commit` no longer
   invokes the implementation-start staged gate.

5. Add focused tests.
   - Unit tests in `platform_tests/scripts/test_implementation_start_gate.py`
     cover the staged-path classifier, pass-through for unprotected staged
     sets, block behavior for protected staged paths without a valid GO packet,
     and allow behavior when the staged protected path is covered by a GO packet
     plus matching work-intent claim.
   - Tests in `platform_tests/scripts/test_release_candidate_gate.py` cover the
     new release-candidate gate expectation.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not add credential-shaped literals; preserve the tracked staged secret scan in `.githooks/pre-commit`. | Helper credential scan before filing; implementation verification runs existing secret-scan hook path or focused source review. |  |
| CQ-PATHS-001 | Yes | Keep all proposed paths inside the mandatory project root; do not target `.git/hooks/`; use tracked `.githooks/` because `core.hooksPath` points there. | Bridge preflight, proposal lint expectations, and target-path inspection. |  |
| CQ-COMPLEXITY-001 | Yes | Add a small staged-mode function and reuse existing authorization helpers instead of duplicating policy. | Focused pytest for staged-path behavior and source review of helper reuse. |  |
| CQ-CONSTANTS-001 | Yes | Centralize staged diff flags and hook command strings as named constants or directly adjacent literals with tests. | Focused pytest plus release-candidate gate tests. |  |
| CQ-SECURITY-001 | Yes | Fail closed for staged protected paths when no live GO packet plus matching claim exists. | Focused pytest for blocked and allowed staged protected paths. |  |
| CQ-DOCS-001 | Yes | Update `.githooks/setup-hooks.sh` user-facing hook summary to include implementation-start enforcement. | Source review and release-candidate gate test for hook registration. |  |
| CQ-TESTS-001 | Yes | Add unit coverage for the staged gate and release-candidate hook-presence assertion. | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_release_candidate_gate.py -q --tb=short`. |  |
| CQ-LOGGING-001 | N/A |  |  | The staged gate prints deterministic denial text through the existing hook channel; no new log stream is proposed. |
| CQ-VERIFICATION-001 | Yes | Run focused pytest plus lint and format checks on changed Python files before filing the implementation report. | Pytest, `ruff check`, and `ruff format --check` commands listed in the verification plan. |  |

## Non-Goals

- No mutation to `.git/hooks/`; GT-KB uses tracked `.githooks/` through
  `core.hooksPath`, and proposal lint already treats `.git/hooks/` as an inert
  target when `core.hooksPath` differs.
- No new Antigravity prompt/rules sync script in this slice. The mechanical
  commit-time floor is the relevant cross-harness closure for `WI-4543`.
- No KB mutation, work-item status change, project authorization change, or
  formal artifact mutation in the implementation slice.

## Spec-Derived Verification Plan

- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`,
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, and
  `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`: run
  `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`.
  Expected result: staged protected paths fail without a valid GO packet plus
  claim and pass only when in scope.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, and
  `REQ-HARNESS-REGISTRY-001`: perform source review plus the staged pre-commit
  tests. Expected result: enforcement is repository-level and does not depend
  on a specific harness PreToolUse implementation.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-FILE-BRIDGE-PROTOCOL-001`, and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: run
  `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-c-governance-gate-parity-gap`
  and
  `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-c-governance-gate-parity-gap`.
  Expected result: proposal/review chain remains valid, with no missing
  required specs and no blocking clause gaps.
- `.githooks/pre-commit` tracked universal-floor behavior: run
  `python -m pytest platform_tests/scripts/test_release_candidate_gate.py -q --tb=short`.
  Expected result: release-candidate gate detects the implementation-start
  staged gate registration.
- Python lint and formatting discipline for changed Python files: run
  `python -m ruff check scripts/implementation_start_gate.py scripts/release_candidate_gate.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_release_candidate_gate.py`
  and
  `python -m ruff format --check scripts/implementation_start_gate.py scripts/release_candidate_gate.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_release_candidate_gate.py`.
  Expected result: both lint and format checks pass on changed Python targets.

## Acceptance Criteria

- `.githooks/pre-commit` invokes `scripts/implementation_start_gate.py --staged`.
- Staging a protected target such as `scripts/example.py` without a live
  implementation authorization packet plus matching work-intent claim blocks
  at pre-commit time.
- Staging only bridge files, unprotected files, or runtime diagnostic paths does
  not trigger the implementation-start gate.
- A staged protected target covered by a live latest-GO bridge proposal,
  implementation authorization packet, and matching work-intent claim passes
  the staged gate.
- Release-candidate validation fails if the tracked pre-commit hook omits the
  staged implementation-start gate.
- Focused pytest, ruff check, and ruff format-check pass for changed targets.

## Risk And Rollback

Primary risk is false-positive commit blocking if the staged mode classifies
paths too broadly or cannot resolve the session's valid implementation packet.
The implementation should reuse the existing protected-path classifier and
authorization packet validation to avoid divergent policy.

Rollback is a normal git revert of changes to the target paths listed in this
proposal. Because the hook is tracked under `.githooks/pre-commit`, rollback is
auditable and does not require mutating local `.git/hooks/` state.

## Pre-Filing Preflight Subsection

Candidate-content preflights are run by the revision helper before live filing:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-c-governance-gate-parity-gap --content-file <candidate-content> --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-c-governance-gate-parity-gap --content-file <candidate-content>
```

Expected clean state before live filing:

- applicability preflight reports `preflight_passed: true`;
- applicability preflight reports `missing_required_specs: []`;
- applicability preflight reports `missing_advisory_specs: []`;
- ADR/DCL clause preflight exits `0`;
- ADR/DCL clause preflight reports no blocking gaps.

## Recommended Commit Type

fix

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
