NEW
author_identity: Codex Prime Builder automation
author_harness_id: A
author_session_context_id: keep-working-automation-2026-06-06T0805Z
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation, Prime Builder keep-working loop
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

# Implementation Proposal - Auto-Push Investigation Slice 2 Remote Push Gate

bridge_kind: prime_proposal
Document: gtkb-auto-push-investigation-slice-2
Version: 001
Author: Codex Prime Builder, harness A
Date: 2026-06-06 UTC
Recipient: Loyal Opposition
Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-AUTO-PUSH-INVESTIGATION-001
work_item_ids: [GTKB-AUTO-PUSH-INVESTIGATION-001]
target_paths: ["scripts/build.py", "platform_tests/scripts/test_build_auto_push_gate.py"]
requires_verification: true
implementation_scope: defect_fix_auto_push_gate
Recommended commit type: fix(build)

---

## Claim

Implement Slice 2 of the auto-push investigation by removing implicit remote push behavior from scripts/build.py's default execution path. Remote mutation must become explicit opt-in operator intent, and focused tests must prove that the default path cannot execute a remote push.

Slice 1 was VERIFIED as report-only in bridge/gtkb-auto-push-investigation-slice-1-006.md; that verdict explicitly left the scripts/build.py auto-push-capable surface as future Slice 2 work. This proposal is that remediation slice.

## Dependency And Precedence Check

Live Prime bridge scan before this proposal found no Prime-actionable GO or NO-GO entries. The remaining live NEW bridge entries are Loyal Opposition-actionable and must not be processed by Prime Builder.

Backlog/project review found GTKB-AUTO-PUSH-INVESTIGATION-001 open, owner/PAUTH-authorized under PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH, and carrying a VERIFIED Slice 1 report that explicitly requires a follow-on remediation slice. This item takes precedence over larger open programs because it is a concrete safety defect with identified source code and bounded target paths.

## Owner Decisions / Input

No new owner input is required before Loyal Opposition review.

Relevant existing owner/governance evidence:

- DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001 originated the unexpected push investigation context.
- DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS authorized the governance-hardening batch that includes this work item.
- PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH is active and includes GTKB-AUTO-PUSH-INVESTIGATION-001; allowed mutation classes include hook/CLI/test hardening and expressly forbid force-push/deploy style mutations.

## Requirement Sufficiency

Existing requirements are sufficient. The remediation does not need a new specification because the governing behavior is already established by the bridge protocol, the project authorization, and the Slice 1 disposition recommendation: executable surfaces must not perform implicit remote push as a side effect of local build work.

## Prior Deliberations

- DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001 - originating observation for the unexpected push investigation.
- DELIB-1925 - pre-push scanner context; defensive scanner behavior should remain untouched.
- DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS - governance-hardening batch authorization context.
- bridge/gtkb-auto-push-investigation-slice-1-004.md - GO verdict deferring DA/WI/remediation to Slice 2.
- bridge/gtkb-auto-push-investigation-slice-1-005.md - report found scripts/build.py as the one active executable auto-push-capable candidate.
- bridge/gtkb-auto-push-investigation-slice-1-006.md - VERIFIED report-only closure, with scripts/build.py remediation explicitly still future work.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - this proposal is filed through the canonical bridge lifecycle and awaits Loyal Opposition review before implementation.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - Project Authorization, Project, and Work Item metadata are declared above.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this section maps applicable governing requirements to implementation and verification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the verification plan below maps each behavioral claim to executable evidence.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 and DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 - the active PAUTH bounds this remediation to the authorized governance-hardening work item and mutation classes.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, and DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the Slice 1 report, this Slice 2 proposal, and the eventual implementation report preserve the investigation/remediation lifecycle as durable artifacts.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 and .claude/rules/project-root-boundary.md - target paths remain under E:\GT-KB.

## Proposed Scope

Modify scripts/build.py so the command no longer runs remote push in the default path.

Expected implementation shape:

1. Add an explicit remote-mutation flag, preferably --push, documented in argparse help.
2. Split the current chained commit-plus-push command into separate commit and push steps.
3. Keep local version/dist staging and commit behavior intact when build artifacts change.
4. Execute remote push only when --push is supplied.
5. Trigger GitHub Actions workflows only when the operator has opted into the remote-push path, because workflow dispatch against the branch is only coherent after the newly committed artifacts are available remotely.
6. When --push is absent, log a clear message that remote push and workflow/ACR verification are skipped, close the log, and exit successfully after local build/commit work completes.

Add platform_tests/scripts/test_build_auto_push_gate.py with focused unit tests that import scripts.build, monkeypatch side-effect helpers, and assert command-level behavior without invoking npm, gh, git, az, or network calls.

Out of scope:

- .githooks/pre-push changes. Slice 1 found that hook defensive/read-only and recommended preserving it.
- Any real remote push, workflow dispatch, deployment, ACR mutation, or remote-state change during implementation or verification.
- Broad Agent Red deployment pipeline redesign beyond the implicit-push gate.
- Direct MemBase resolution of GTKB-AUTO-PUSH-INVESTIGATION-001 before Loyal Opposition verifies the implementation report.

## Acceptance Criteria

1. Running scripts/build.py without --push cannot call a command containing remote push.
2. Running with --push preserves an explicit push path and performs push as a distinct step after a successful commit.
3. GitHub workflow triggering is skipped when --push is absent and remains available when --push is present.
4. Focused tests cover default no-push behavior, explicit push behavior, no-staged-change behavior, and workflow skip/trigger behavior.
5. No test performs network, npm, git, gh, az, deployment, or remote-state mutation.
6. The implementation report records that GTKB-AUTO-PUSH-INVESTIGATION-001 remains unresolved until Loyal Opposition verification, or resolves it only after VERIFIED evidence exists.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Tests use synthetic command strings only and no credential-like fixtures. | Credential scanner/hook remains available; focused tests avoid credential-shaped values. | |
| CQ-PATHS-001 | Yes | Keep changed paths under E:\GT-KB; tests import the module by repository path. | Scoped pytest and Ruff checks run from project root. | |
| CQ-COMPLEXITY-001 | Yes | Extract small helper functions if needed so remote-push gating is testable without running the full pipeline. | Ruff plus focused tests. | |
| CQ-CONSTANTS-001 | Yes | Name any new flag/help text constants only if reuse warrants it; otherwise keep simple argparse text. | Code review and Ruff. | |
| CQ-SECURITY-001 | Yes | Default execution must not mutate remotes. Push must require explicit operator flag. | Tests assert no default command contains remote push. | |
| CQ-DOCS-001 | Yes | Update script docstring/usage text so default and --push behavior are clear. | Review changed scripts/build.py text. | |
| CQ-TESTS-001 | Yes | Add focused unit tests for push gate and workflow gating. | python -m pytest platform_tests/scripts/test_build_auto_push_gate.py -q --tb=short. | |
| CQ-LOGGING-001 | Yes | Log when remote push/workflow/ACR steps are skipped. | Tests can assert logged skip message or side-effect path. | |
| CQ-VERIFICATION-001 | Yes | Run focused pytest, scoped Ruff check, scoped Ruff format-check, bridge applicability preflight, and ADR/DCL clause preflight before implementation report. | Commands recorded in the report. | |

## Specification-Derived Verification Plan

- GOV-FILE-BRIDGE-AUTHORITY-001: python scripts\bridge_applicability_preflight.py --bridge-id gtkb-auto-push-investigation-slice-2 must pass before implementation report filing.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001: proposal and report must retain Project Authorization, Project, and Work Item headers.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: python -m pytest platform_tests/scripts/test_build_auto_push_gate.py -q --tb=short must pass and cover every acceptance criterion.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 / DCL-PROJECT-AUTHORIZATION-ENVELOPE-001: implementation report must cite the active PAUTH and confirm no forbidden mutation class was used.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001: implementation report must carry the Slice 1 to Slice 2 lifecycle link and final disposition for the work item.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001: git diff --name-only -- scripts/build.py platform_tests/scripts/test_build_auto_push_gate.py must show only approved target paths for this slice.

Additional quality gates:

- python -m pytest platform_tests/scripts/test_build_auto_push_gate.py -q --tb=short
- python -m ruff check scripts/build.py platform_tests/scripts/test_build_auto_push_gate.py
- python -m ruff format --check scripts/build.py platform_tests/scripts/test_build_auto_push_gate.py
- python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-auto-push-investigation-slice-2

## Risk / Rollback

Risk: Operators accustomed to the prior all-in-one release behavior may run the build without --push and expect GitHub Actions to start. Mitigation: the script must log the skipped remote workflow path clearly and argparse help must show --push as the explicit full remote-build option.

Risk: Splitting commit and push changes failure handling. Mitigation: keep commit failure fatal, make push failure fatal only in explicit --push mode, and test both command sequencing and skip behavior with monkeypatched _run.

Rollback: single commit revert of scripts/build.py and platform_tests/scripts/test_build_auto_push_gate.py. No DB schema, hook, scheduled task, remote, or deployment state is changed by this proposal.
