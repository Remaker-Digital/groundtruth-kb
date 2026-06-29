NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1078-0168-7573-8a31-a68af5b9842a
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Prime Builder automation auto-builder; WI-4733 implementation report filing

# GT-KB Bridge Implementation Report - gtkb-wi4733-dispatch-health-stale-runtime-state - 003

bridge_kind: implementation_report
Document: gtkb-wi4733-dispatch-health-stale-runtime-state
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4733-dispatch-health-stale-runtime-state-002.md
Approved proposal: bridge/gtkb-wi4733-dispatch-health-stale-runtime-state-001.md
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4733
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23
Commit: 7c0ad5da117e037e2ea205204c6928f8eccfdd8e
Recommended commit type: feat

## Implementation Claim

Implemented WI-4733 by making bridge dispatch health re-check selected-recipient launch evidence against dispatch-run PID sidecars before treating old persisted `last_result` failure fields as current runtime failure evidence.

The runtime classifier now accepts the dispatch-runs directory, verifies `last_launch.dispatch_id` liveness read-only through `.pid`, `.exit_code`, and `.create_time_epoch` sidecars, and marks stale selected-recipient launch evidence as warning-level stale evidence instead of emitting dispatch runtime failure findings. Existing recipient-mismatch stale evidence remains supported, and current selected-recipient failures with live or unproven launch evidence still produce runtime failure findings.

During final staging, a concurrent harness commit advanced HEAD and incorporated the exact WI-4733 source/test diff before this session could create its own source commit. That commit is `7c0ad5da117e037e2ea205204c6928f8eccfdd8e`; it also contains unrelated WI-4253 bridge files from the concurrent process. No files were reverted or overwritten.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision was required. The implementation used the active project authorization and the latest GO verdict for this bridge thread.

## Prior Deliberations

- `bridge/gtkb-wi4733-dispatch-health-stale-runtime-state-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4733-dispatch-health-stale-runtime-state-002.md` - Loyal Opposition GO verdict.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py --target platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py` passed; `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4733-dispatch-health-stale-runtime-state` passed; `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4733-dispatch-health-stale-runtime-state` passed. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short` passed: 7 tests; `python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short` passed: 39 tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `GOV-STANDING-BACKLOG-001` | The implementation is bounded to the approved WI-4733 source/test targets and preserves bridge audit as append-only. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed only GT-KB platform dispatcher-health source and platform tests; no adopter application files changed. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Dispatcher-health behavior now reflects live runtime sidecar state rather than stale persisted failure state. |
| `SPEC-AUQ-POLICY-ENGINE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | No new owner input, formal artifact mutation, or backlog mutation was required. |

## Commands Run

- `python -m pytest platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4733-dispatch-health-stale-runtime-state`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4733-dispatch-health-stale-runtime-state`
- `python scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py --target platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`

## Observed Results

- Focused CLI tests: 7 passed.
- Existing dispatcher-config regression suite: 39 passed.
- Ruff check: all checks passed.
- Ruff format check: 2 files already formatted.
- Bridge applicability preflight: passed with no missing required specs.
- ADR/DCL clause preflight: passed with no blocking gaps.
- Implementation authorization validation: both target paths authorized.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`

## Recommended Commit Type

- Recommended commit type: `feat`
- Commit containing implementation diff: `7c0ad5da117e037e2ea205204c6928f8eccfdd8e`

```text
groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py  | 132 ++++++++++++++++++++-
platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py  |  45 ++++++-
2 files changed, 170 insertions(+), 7 deletions(-)
```

## Acceptance Criteria Status

- [x] A stale selected-recipient `launch_failed` row whose recorded dispatch has no live worker no longer emits dispatch runtime failure findings.
- [x] Runtime classification includes `stale_failure_evidence`, a concrete stale reason, and a warning finding while pending work exists.
- [x] Existing selected-recipient runtime failure findings remain visible as warning-level dispatch-health findings under the current health semantics.
- [x] Nonselected runtime failures remain ignored.

## Risk And Rollback

Residual risk is moderate-low. The new liveness check is read-only and only suppresses failure fields when a selected recipient row already has failure evidence and the recorded dispatch worker can be proven stale through sidecars or PID liveness. Rollback is a revert of the WI-4733 source/test diff in commit `7c0ad5da117e037e2ea205204c6928f8eccfdd8e`, taking care not to remove unrelated WI-4253 bridge files from the same concurrent commit. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the implementation satisfies the approved proposal, otherwise return NO-GO with findings.
