NEW

# gtkb-wi4760-cross-harness-trigger-kill-switch-loud-check - Make the cross-harness trigger kill-switch loud

bridge_kind: prime_proposal
Document: gtkb-wi4760-cross-harness-trigger-kill-switch-loud-check
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-23T20:47:00Z

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ef21d-a27e-7473-9939-21f715631a90
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop, Prime Builder, Windows PowerShell

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4760

target_paths: ["scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/tests/test_doctor_cross_harness_trigger.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: source, test_addition, hook_upgrade, cli_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`WI-4760` documents a recurring silent failure where `GTKB_NO_CROSS_HARNESS_TRIGGER=1` is set at persistent Windows User scope. When that variable is present in the trigger process, `scripts/cross_harness_bridge_trigger.py` short-circuits before dispatch-state evidence is written, so normal PostToolUse/Stop hook invocations can look installed while no cross-harness bridge work is delivered.

This proposal keeps the operator opt-out semantics but makes the disabled state loud and deterministic. The implementation will add a shared, testable kill-switch scope check for process and persistent Windows environment scopes, surface it through `gt bridge dispatch health`, and make the project doctor's cross-harness trigger check fail or warn visibly when the suppressor is active. It will not clear or mutate environment variables; it only reports the condition so dispatch cannot be silently disabled for hours.

Live evidence at proposal time: `[Environment]::GetEnvironmentVariable('GTKB_NO_CROSS_HARNESS_TRIGGER','Process')` and `...,'User'` both returned `1`; `...,'Machine'` returned null. `gt bridge dispatch health --json` was most recently `WARN` with loyal-opposition pending work, which confirms there is bridge pressure while the hook suppressor is active.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires this Prime Builder implementation proposal to move through the bridge and use the numbered bridge file plus dispatcher/TAFE state as workflow authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite every relevant governing specification and derive verification from those specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires `Project Authorization`, `Project`, and `Work Item` metadata lines for this project-scoped implementation proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the eventual implementation report to map linked specifications to executed tests before Loyal Opposition can verify it.
- `GOV-STANDING-BACKLOG-001` — makes `WI-4760` a durable backlog work item and provides the governing work authority for selecting it from the project snapshot.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — requires bridge protocol enforcement to apply across harness paths; a silent trigger suppressor is cross-harness enforcement drift and must be surfaced.
- `GOV-HARNESS-ROLE-PORTABILITY-001` — establishes that Prime Builder and Loyal Opposition are harness-assigned roles, so dispatch health must be visible independent of one vendor harness.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — establishes Codex hook parity and fallback expectations; a Codex-visible health failure is the appropriate fallback when hook-triggered dispatch is suppressed.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — constrains harness dispatch capability floors and health surfaces; a persistent dispatch kill-switch must be visible in those capability checks.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — applies because this proposal touches GT-KB platform source under `groundtruth-kb/src/groundtruth_kb/project/**`; all implementation remains inside the GT-KB root and platform tree.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory for preserving the owner-observed suppressor failure as governed bridge evidence without creating an unapproved formal artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory because the work turns a repeated operational observation into durable source, tests, and bridge evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory because the proposal references owner decisions, work items, verification, and implementation-report lifecycle triggers.

## Prior Deliberations

- `INTAKE-2ce995f2` — relevant because this proposal protects bounded parallel cross-harness auto-dispatch from a persistent local suppressor that currently defeats the dispatch path.
- `DELIB-S422-OR-REGISTRY-INTEGRATION` — relevant because OpenRouter is one active Loyal Opposition dispatch target; dispatch health must report suppressors even when multiple LO harnesses exist.
- `DELIB-20265586` — owner decision authorizing the snapshot-bound `PROJECT-GTKB-MAY29-HYGIENE` implementation campaign that includes `WI-4760`.

## Owner Decisions / Input

- Project authorization: `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-MAY29-HYGIENE-BOUNDED-IMPLEMENTATION-2026-06-23`.
- Owner decision: `DELIB-20265586`.
- Current owner direction, 2026-06-23: "Antigravity and Codex are manually processing LO work." This means the proposal may be filed even while the automatic cross-harness trigger suppressor remains active, because manual Loyal Opposition pickup is available.
- No additional owner decision is required for this proposal because it does not clear User-scope or Process-scope environment variables, add new work items, mutate formal GOV/SPEC/ADR/DCL/PB/REQ artifacts, or expand beyond the authorized `WI-4760` source/test/doctor/CLI scope.

## Requirement Sufficiency

Existing requirements sufficient — `WI-4760` already states the acceptance criterion: eliminate the recurring User-scope reset or make the disable loud through a deterministic doctor and/or SessionStart-visible check so dispatch cannot be silently disabled for hours. The linked bridge, cross-harness, role-portability, hook-parity, and harness-onboarding specifications are sufficient for a source/test implementation that reports the kill-switch state without mutating it.

## Spec-Derived Verification Plan

Implementation will add or update tests so the suppressor is visible in both CLI health and doctor paths:

- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — preflight the filed bridge proposal and confirm `target_paths` remains inline JSON with the project/work authorization metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report will carry this mapping forward with executed command output.
- `GOV-STANDING-BACKLOG-001` — `gt projects show PROJECT-GTKB-MAY29-HYGIENE --json` remains the source of project membership and `WI-4760` authorization.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `GOV-HARNESS-ROLE-PORTABILITY-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001` — tests must show that a process or persistent Windows `GTKB_NO_CROSS_HARNESS_TRIGGER=1` produces a visible `gt bridge dispatch health` finding and a visible doctor finding while preserving the existing operator opt-out behavior and the rule that the disable variable is not propagated to dispatched child harnesses.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — `target_paths` remain inside `E:\GT-KB` and no Agent Red or external repository paths are in scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — verification remains source/test/bridge-evidence only; no formal artifact or new work item mutation is in scope.

```text
python -m pytest groundtruth-kb/tests/test_doctor_cross_harness_trigger.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
ruff check scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_cross_harness_trigger.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
ruff format --check scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_cross_harness_trigger.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```

## Risk / Rollback

Risk is concentrated in false-positive health failures and Windows environment-scope probing. The implementation should isolate platform-specific probing behind a small helper, fail soft when persistent-scope probing is unavailable, and keep existing trigger short-circuit semantics intact. Rollback is a single commit revert restoring the previous health/doctor behavior and tests.

The implementation must not delete or modify the user's persistent `GTKB_NO_CROSS_HARNESS_TRIGGER` setting. Clearing the kill-switch is an owner/environment operation outside this source/test proposal.

## Implementation Plan

1. Add a small helper that reports `GTKB_NO_CROSS_HARNESS_TRIGGER` state for the process scope and, on Windows, the User and Machine persistent environment scopes.
2. Wire that helper into `groundtruth_kb.bridge_dispatch_config.collect_bridge_dispatch_status` so `gt bridge dispatch health --json` and text health output include a visible finding whenever the suppressor is active.
3. Wire equivalent visibility into `groundtruth_kb.project.doctor._check_cross_harness_trigger`, returning a loud warning or failure before a stale `dispatch-state.json present` check can mask the disabled condition.
4. Preserve existing trigger operator opt-out behavior and child-env non-propagation tests.
5. Add focused tests covering process-scope and persistent User-scope suppressor detection without mutating the real workstation environment.

## Pre-Filing Checks

Executed before filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4760-cross-harness-trigger-kill-switch-loud-check-001.md
Result: preflight_passed=true; missing_required_specs=[]; missing_advisory_specs=[]; packet_hash=sha256:3fda2870e76a75291eee73fbec37d891c3aba10feb7c7b8bb08ea249e4a1ca8c.

python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi4760-cross-harness-trigger-kill-switch-loud-check-001.md
Result: blocking gaps=0; must_apply=4; may_apply=1; exit code 0.

python -c "<phantom-spec sweep over cited GOV/DCL/ADR/PB/SPEC/REQ ids>"
Result: missing=none.

python -c "<target_paths inline JSON parse>"
Result: parsed 7 paths.

placeholder-token scan over .gtkb-state/propose-drafts/gtkb-wi4760-cross-harness-trigger-kill-switch-loud-check-001.md
Result: no scaffold placeholders found.
```

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4760-cross-harness-trigger-kill-switch-loud-check`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: the work repairs a silent dispatch-disabled failure mode without introducing a new user-facing feature surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
