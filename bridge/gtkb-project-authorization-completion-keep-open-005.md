NEW
author_identity: prime-builder/antigravity/C
author_harness_id: C
author_session_context_id: 019ee066-ced1-7220-9f7e-51b39dee4fcc
author_model: Gemini 1.5 Pro
author_model_version: 2026-06-16
author_model_configuration: Antigravity Prime Builder

# Keep-open caller election for complete_project_authorization() (WI-3329) — Implementation Report

bridge_kind: implementation_report
Document: gtkb-project-authorization-completion-keep-open
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-project-authorization-completion-keep-open-004.md
Approved proposal: bridge/gtkb-project-authorization-completion-keep-open-003.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-3329-KEEP-OPEN-OPT-OUT
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3329
Recommended commit type: feat:

## Implementation Claim

The implementation for WI-3329 is complete. We have successfully implemented the keep-open caller election on the project lifecycle service and exposed it as the `--keep-project-open` command option on the `gt projects complete-authorization` CLI subcommand.

This implementation report cites the active work-intent claim for the bridge ID `gtkb-project-authorization-completion-keep-open` and the active packet hash `sha256:e53921b0ae37d2754c8cc7c34266664de97eb253e6831a8500c32145cc7bb937`.

## Scope Boundary

The implementation is strictly limited to the four target paths:
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (added keyword-only `retire_project: bool = True` and gated Step 4 retirement)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (added click option `--keep-project-open`)
- `groundtruth-kb/tests/test_project_artifacts.py` (added service-level keep-open test)
- `platform_tests/scripts/test_project_authorization.py` (added CLI-level keep-open and default-retirement tests)

All changes are fully conformant with the project authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI-3329-KEEP-OPEN-OPT-OUT` (mutation classes `source`, `cli_extension`, and `test_addition`).

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v5) — the governing spec; v5 formalizes the keep-open caller election. Default `retire_project=True` preserves v5's "Rule" (automatic collective retirement) byte-for-byte; `retire_project=False` is the v5 "Keep-open caller election".
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the authorization-completion surface; this implementation makes authorization completion and project retirement independently expressible without altering authorization-completion semantics.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — cites relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification is derived from the linked specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — touches lifecycle/CLI source and tests only; no bridge-protocol change.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the change is durable source + tests + a versioned bridge report.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — defect, owner decision, spec bump, implementation, and verification preserved.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — project/work-item retirement transition is electable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (advisory) — all target paths are under `E:\GT-KB`.

## Owner Decisions / Input

Owner approval is recorded and archives as `DELIB-20265228`.

## Prior Deliberations

- `DELIB-20265228` — owner approval of keep-open opt-out + spec version bump.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v5.
- `DELIB-S353-LO-OPPORTUNITY-RADAR-PROJECT-COMPLETION-2026-05-15` — originating owner keep-open decision.
- `bridge/gtkb-project-authorization-completion-keep-open-001.md` — Initial Prime proposal (NO-GO'd).
- `bridge/gtkb-project-authorization-completion-keep-open-002.md` — Loyal Opposition NO-GO verdict (cited semantics change without spec bump).
- `bridge/gtkb-project-authorization-completion-keep-open-003.md` — REVISED Prime proposal (v5 spec-backed; non-fast-lane re-file).
- `bridge/gtkb-project-authorization-completion-keep-open-004.md` — Loyal Opposition GO verdict.

## Implementation-Start Authorization

The implementation packet was located at `.gtkb-state/implementation-authorizations/by-bridge/gtkb-project-authorization-completion-keep-open.json`.
Hash: `sha256:e53921b0ae37d2754c8cc7c34266664de97eb253e6831a8500c32145cc7bb937`
Expires: `2026-06-19T17:21:27Z`

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v5; default unchanged) | Test `test_complete_sole_active_authorization_retires_project` asserts that calling `complete_project_authorization` with default options retires the project and unlinks its work items. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v5; keep-open election) | Test `test_complete_sole_active_authorization_can_keep_project_open` asserts that calling the service with `retire_project=False` completes the authorization but leaves the project `active` and its work items intact. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v5; CLI surface) | Test `test_complete_authorization_cli_keep_project_open` asserts that calling the CLI with `--keep-project-open` completes the authorization but keeps the project active, and the click output does not print "Project retired." Test `test_complete_authorization_cli_default_retires_project` asserts default CLI call retires. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Service and CLI tests assert that the authorization status updates to `completed` in both keep-open and default retirement paths. |

## Tests And Results

| Command | Result |
| --- | --- |
| `python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q -k "complete and (retire or keep)"` | PASS (8 passed in 45.84s) |
| `python -m pytest platform_tests/scripts/test_project_authorization.py -q -k "keep or retire"` | PASS (2 passed in 28.53s) |
| `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_authorization.py` | PASS (all checks passed) |
| `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_authorization.py` | PASS (4 files already formatted) |

## Acceptance Criteria Status

- PASS: `complete_project_authorization()` accepts keyword-only `retire_project: bool = True` and auto-retires by default.
- PASS: `retire_project=False` completes authorization and keeps the project active.
- PASS: CLI `--keep-project-open` completes authorization, keeps project active, and output does not claim retirement. Default CLI call still retires.
- PASS: `auto_complete_ready_authorizations()` and completion hooks are unchanged (and continue to call without the flag, utilizing default retirement behavior).
- PASS: Formatting and code quality checks pass.

## Risk And Rollback

Risk is extremely low. The default code path behaves identically to the former auto-retirement rule. Rollback is unthreading the `retire_project` parameter and option from click/service code, and deleting the tests.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
