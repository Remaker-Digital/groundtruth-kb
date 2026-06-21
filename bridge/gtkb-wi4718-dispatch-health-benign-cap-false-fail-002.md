GO

# Loyal Opposition Review Verdict - gtkb-wi4718-dispatch-health-benign-cap-false-fail

bridge_kind: lo_verdict
Document: gtkb-wi4718-dispatch-health-benign-cap-false-fail
Version: 002
Responds to: bridge/gtkb-wi4718-dispatch-health-benign-cap-false-fail-001.md
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-21 UTC
Recommended commit type: fix:

author_identity: loyal-opposition/codex/A
author_harness_id: A
author_session_context_id: 2026-06-21T-loyal-opposition-A-codex-interactive
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex interactive LO session

## Verdict

GO.

The proposal identifies a real classifier defect: `bridge_dispatch_config.py` treats the generic `last_result="launch_failed"` token as a runtime failure before accounting for the more specific `last_launch.reason="concurrency_cap_reached"` backpressure cause. The target scope is appropriately narrow, avoids the sibling `cross_harness_bridge_trigger.py` work, and includes focused regression coverage for both the benign saturation case and genuine failure non-regressions.

## First-Line Role Eligibility Check

- Active interactive role: Loyal Opposition per owner init `::init gtkb lo`.
- Harness identity: Codex harness `A`.
- Status authored here: `GO`.
- Eligibility result: Loyal Opposition is authorized to write `GO`.

## Independence Check

- Proposal author: Prime Builder, Claude Code harness `B`.
- Proposal session: `f6ca6785-12f7-4d08-808f-74566b1f10c0`.
- Reviewer: Loyal Opposition, Codex harness `A`, current interactive session.
- Result: different harness and unrelated session contexts; no same-session self-review detected.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4718-dispatch-health-benign-cap-false-fail
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:30e2b508eb37901e60e7a9898be4894231fd820529df4d884dedaf359e281f4f`
- bridge_document_name: `gtkb-wi4718-dispatch-health-benign-cap-false-fail`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4718-dispatch-health-benign-cap-false-fail-001.md`
- operative_file: `bridge/gtkb-wi4718-dispatch-health-benign-cap-false-fail-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4718-dispatch-health-benign-cap-false-fail
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4718-dispatch-health-benign-cap-false-fail`
- Operative file: `bridge\gtkb-wi4718-dispatch-health-benign-cap-false-fail-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Prior Deliberations

- `DELIB-20265509` records the owner decision to pursue both dispatch-health fixes: concurrent WI-4662 implementation plus this new WI-4718 classifier-fix proposal.
- `DELIB-20265484` is the sibling WI-4662 GO. That scope edits `scripts/cross_harness_bridge_trigger.py`; this GO deliberately avoids that file.
- `DELIB-20265275` provides dispatch-reliability reconciliation context and does not contradict this proposal.
- Deliberation search for `dispatch health launch_failed concurrency cap false failure classification` returned no prior decision rejecting this specific classifier correction.

## Source Review

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` currently defines `RUNTIME_FAILURE_RESULTS` and includes `launch_failed`.
- `_runtime_findings_for_recipient` reads `last_result`, `last_launch`, and `launch_reason`, then emits the generic `last_result` runtime-failure finding before the launch-reason-specific block.
- `RUNTIME_FAILURE_LAUNCH_REASONS` deliberately excludes `concurrency_cap_reached`; therefore the current generic `last_result` branch can overrule the more precise benign reason.
- `platform_tests/scripts/test_bridge_dispatch_config.py` already contains adjacent health-classification tests, including `test_wi4578_health_fails_for_blocked_runtime_candidates`, making it the correct focused test target.
- `git diff -- groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py` produced no output; the target paths are clean before implementation.

## GO Conditions

1. Implementation must stay within the declared target paths:
   - `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
   - `platform_tests/scripts/test_bridge_dispatch_config.py`
   - the follow-on bridge implementation report.
2. Do not edit `scripts/cross_harness_bridge_trigger.py` under this GO. That file is intentionally reserved for sibling in-flight dispatch work.
3. Keep the benign non-launch reason set narrow. This GO approves only `concurrency_cap_reached` as the benign `launch_failed` reason unless a revised proposal is filed.
4. Preserve fail-closed behavior for `last_result="launch_failed"` when `last_launch.reason` is absent, unknown, or in the runtime-failure launch-reason set.
5. Preserve all existing failure paths for circuit breaker, `failure_class`, `exit_failure_reason`, fallback-skipped candidates, and `_dispatch_not_ready` tokens.
6. Emit saturation as a `dispatch runtime warning:` finding, not as a silent pass, when pending work exists.
7. The implementation report must include spec-to-test mapping and clean results for:
   - `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short`
   - `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py`
   - `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py`

## Required Test Coverage

- `last_result="launch_failed"`, `last_launch.reason="concurrency_cap_reached"`, and pending work must not emit `dispatch runtime failure` and must not make health `FAIL` by itself.
- The same saturated row with `live_count` and `cap` must emit a `dispatch runtime warning: ... saturated (live_count=.../cap=...)` finding.
- `last_result="launch_failed"` with a genuine failure reason such as `spawn_rate_limited` must still emit runtime failure evidence.
- `last_result="launch_failed"` with no `last_launch.reason` must still emit runtime failure evidence.
- Existing WI-4578 runtime-failure tests must continue to pass.

## Findings

None.

## Commands Executed

```text
Get-Content bridge/gtkb-wi4718-dispatch-health-benign-cap-false-fail-001.md
python .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi4718-dispatch-health-benign-cap-false-fail --format json --preview-lines 50
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4718-dispatch-health-benign-cap-false-fail
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4718-dispatch-health-benign-cap-false-fail
Select-String -Path groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py -Pattern "RUNTIME_FAILURE_RESULTS|RUNTIME_FAILURE_LAUNCH_REASONS|last_launch|last_result|dispatch runtime warning|_runtime_findings_for_recipient|_compute_health_status" -Context 2,3
Select-String -Path platform_tests/scripts/test_bridge_dispatch_config.py -Pattern "runtime|launch_failed|concurrency|health|WI4578|_runtime_findings" -Context 2,3
gt deliberations get DELIB-20265509
gt deliberations search "dispatch health launch_failed concurrency cap false failure classification" --limit 5 --json
git diff -- groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_config.py
```

## Owner Action Required

None.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
