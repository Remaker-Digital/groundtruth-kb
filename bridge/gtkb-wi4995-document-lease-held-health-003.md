NEW

# WI-4995 Document Lease Held Health Classification -- Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4995-document-lease-held-health
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4995-document-lease-held-health-002.md
Recommended commit type: fix

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f247b-4dc8-7b32-a2ab-25839614d33f
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Extra High reasoning; Codex Desktop interactive Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4995-LEASE-HEALTH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4995

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

---

## Implementation Summary

Implemented the classifier-side repair approved in the GO verdict. A current benign `document_lease_held` non-launch now marks stale recipient failure fields as stale health evidence when there is no separate current failure signal. The dispatcher can therefore preserve historical `failure_class` data while `gt bridge dispatch health` stops reporting a false subprocess failure solely because another LO worker holds the per-document lease.

The implementation intentionally did not mutate daemon state or clear failure history. Real current failures still fail health when present.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

`scripts/gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` were in the approved target set but did not need code changes. The existing daemon regression `test_daemon_live_spawns_do_not_duplicate_lo_documents_across_targets` remains the lease-preservation proof.

## Implementation Details

- Added `DOCUMENT_LEASE_HELD_NONLAUNCH_REASON = "document_lease_held"` in the dispatcher health classifier.
- Added a narrow benign-supersession branch in `_runtime_classification_for_recipient`:
  - it recognizes `document_lease_held` in `last_result` or `last_launch.reason`;
  - it only applies when pending work is visible and stale failure evidence is present;
  - it refuses to suppress a separate current runtime failure signal such as `last_launch.exit_failure_reason`, a runtime-failure `last_result`, a runtime-failure `last_launch.reason`, or a tripped circuit breaker.
- Added unit coverage proving stale `failure_class=subprocess_execution_failed` becomes an explanatory warning, not a failure.
- Added unit coverage proving an explicit current exit failure is still classified as `FAIL`.
- Added CLI report coverage proving the JSON report surfaces the stale-evidence warning and not a false runtime failure.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stable unattended dispatch requires health reports to distinguish genuine harness failures from normal lease arbitration.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher health and lease handling are part of the dispatcher control plane; no direct harness fallback is authorized.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge processing must remain role-correct and avoid duplicate review/implementation through lease/work-intent discipline.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires bounded PAUTH before protected dispatcher source/test mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires PAUTH/project/WI metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete links to all relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires implementation reports to map linked requirements to executed verification.

## Specification-Derived Verification

| Specification / Requirement | Verification Evidence | Executed |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_wi4995_document_lease_held_ignores_stale_failure_class` and `test_bridge_dispatch_report_treats_document_lease_held_as_stale_failure_context` prove lease-held stale failure evidence no longer emits `dispatch runtime failure`. Live `gt bridge dispatch health --json` now reports a warning, not a failure, for the reproduced B row. | yes |
| `ADR-DISPATCHER-ARCHITECTURE-001` | The implementation stays inside dispatcher health/report code and tests. No direct harness launcher or fallback path was added. `ruff check` covered the changed dispatcher health source and approved daemon target. | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Existing daemon test `test_daemon_live_spawns_do_not_duplicate_lo_documents_across_targets` was re-run and passed, proving document leases still suppress duplicate LO launch. | yes |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4995-document-lease-held-health` succeeded before protected source/test mutation; edits stayed within authorized target paths. | yes |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries PAUTH, project, WI, and `target_paths` metadata. | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the approved proposal's governing specification links. | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Exact command evidence is recorded below, including the focused passing test command and the disclosed broader residual test failure. | yes |

## Commands Executed

```text
python scripts\bridge_claim_cli.py claim gtkb-wi4995-document-lease-held-health --ttl-seconds 3600
```

Result: claim acquired by this Prime Builder session with `claim_kind=go_implementation`, `acting_role=prime-builder`, and `ttl_expires_at=2026-07-03T12:44:23Z`.

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4995-document-lease-held-health
```

Result: authorization packet created; PAUTH active; latest bridge status `GO`; target globs matched the approved WI-4995 paths.

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_daemon_live_spawns_do_not_duplicate_lo_documents_across_targets -q --tb=short
```

Observed result: `53 passed in 2.00s`.

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
```

Observed result: `All checks passed!`

```text
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py scripts/gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py
```

Observed result: `5 files already formatted`.

```text
gt bridge dispatch health --json
```

Observed result: health remains `WARN`, but the relevant finding is now:

```text
dispatch runtime warning: loyal-opposition:B stale failure evidence ignored (current document_lease_held non-launch) with pending_count=1
```

No `dispatch runtime failure` is emitted for B's stale `failure_class=subprocess_execution_failed` in the reproduced lease-held condition.

## Broader Test Disclosure

The full proposal-listed pytest command was also run:

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short
```

Observed result: `95 passed, 1 failed`. The failing test was `platform_tests/scripts/test_gtkb_dispatcher_daemon.py::test_daemon_spawn_passes_per_role_lifetime`, asserting a synthetic PB target using harness `D` should receive `5400` seconds while the current harness-specific lifetime profile returns `1800` for harness `D`. This is outside the WI-4995 classifier change; no WI-4995 code path or newly added test failed. I did not broaden WI-4995 to repair that lifetime-test assumption.

## Acceptance Criteria

- Recipient row with pending LO work, `document_lease_held`, and stale `failure_class=subprocess_execution_failed` no longer emits `dispatch runtime failure`: satisfied.
- The condition is now a non-failure warning explaining stale evidence was ignored: satisfied.
- A separate current exit failure remains a `FAIL`: satisfied by `test_wi4995_document_lease_held_does_not_hide_current_exit_failure`.
- Document lease held still suppresses duplicate LO launches: satisfied by existing daemon regression.
- Live `gt bridge dispatch health --json` no longer reports B failed solely because another LO worker holds the document lease: satisfied.
- Focused pytest and ruff checks pass: satisfied, with broader unrelated daemon lifetime failure disclosed above.

## Risk And Rollback

Residual risk: the classifier now emits an explanatory warning for the stale lease-held case rather than a failure. This is intentional; it keeps operator visibility without falsely classifying normal lease arbitration as a subprocess failure.

Rollback: revert the three WI-4995 changed files listed in this report. Bridge files, PAUTH, and MemBase records remain append-only audit evidence.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
